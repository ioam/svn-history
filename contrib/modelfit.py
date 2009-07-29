from topo.pattern.basic import Gabor, SineGrating, Gaussian
import __main__
import numpy
import pylab
from numpy import array, size, mat, shape, ones, arange
from topo.misc.numbergenerator import UniformRandom, BoundedNumber, ExponentialDecay
from topo.base.functionfamily import IdentityTF
from topo.transferfn.basic import PiecewiseLinear, DivisiveNormalizeL1, IdentityTF, ActivityAveragingTF, AttributeTrackingTF,PatternCombine,Sigmoid, HalfRectify
from topo.base.cf import CFSheet
from topo.projection.basic import CFProjection, SharedWeightCFProjection
from fixedpoint import FixedPoint
import topo
from topo.command.pylabplots import matrixplot
from topo.sheet import GeneratorSheet 
from topo.base.boundingregion import BoundingBox
from topo.pattern.image import Image
import contrib.jacommands

class ModelFit():
    
    filters = []
    weigths = []
    retina_diameter=1.0
    density=24
    epochs = 500
    learning_rate = 0.00001
    inputDC = 0
    modelDC = 0
    meanModelResponses=[]
    reliable_indecies=[]
    momentum=0.0
    num_of_units=0
    
    def init(self):
        self.reliable_indecies = ones(self.num_of_units)
        for freq in [16.0]:
        #for freq in [8.0]:
            for xpos in xrange(0,int(freq)):
                for ypos in xrange(0,int(freq)):
                    x=xpos*(self.retina_diameter/freq)-self.retina_diameter/2 + self.retina_diameter/freq/2 
                    y=ypos*(self.retina_diameter/freq)-self.retina_diameter/2 + self.retina_diameter/freq/2
                    for orient in xrange(0,8):
                        g1 = Gabor(bounds=BoundingBox(radius=self.retina_diameter/2),frequency=freq,x=x,y=y,xdensity=self.density,ydensity=self.density,size=1/freq,orientation=numpy.pi/8*orient,phase=0.0)
                        g2 = Gabor(bounds=BoundingBox(radius=self.retina_diameter/2),frequency=freq,x=x,y=y,xdensity=self.density,ydensity=self.density,size=1/freq,orientation=numpy.pi/8*orient,phase=numpy.pi/2)
                        self.filters.append((g1(),g2()))  

    def calculateModelResponse(self,inputs,index):
        res = []
        inn = inputs[index] - self.inputDC
        for (gabor1,gabor2) in self.filters:
            r1 = numpy.sum(numpy.multiply(gabor1,inn))
            r2 = numpy.sum(numpy.multiply(gabor2,inn))
            #res.append(numpy.sqrt(r1*r1+r2*r2))
            res.append(r1)
            res.append(r2)
        # the constant luminance wavelet
        #res.append(numpy.sum(inn))
        # allow DC substractions (eg threshold in NN) 
        #res.append(1.0)
        return numpy.mat(res)    
    
    def calculateInputDC(self,inputs):
        avg = 0
        for i in inputs:
            avg = avg + numpy.sum(i)/(size(i,1)*size(i,0))
        avg = avg/len(inputs)
        self.inputDC = avg
        print avg    
        
    def calculateModelOutput(self,inputs,index):
        modelResponse = self.calculateModelResponse(inputs,index) - self.meanModelResponses
        return self.weigths*modelResponse.T + self.modelDC.T
        
    
    def trainModel(self,inputs,activities,validation_inputs,validation_activities):
        self.calculateInputDC(inputs)
        modelResponses=[]
        validationModelResponses=[]
        delta=[]
        self.meanModelResponses=numpy.array(self.calculateModelResponse(inputs,0)).copy()*0.0
        self.modelDC=numpy.array(activities[0]).copy()*0.0
        
        
        # calculate the model responses and their average to the set of inputs
        for i in xrange(len(inputs)):
            modelResponses.append(numpy.array(self.calculateModelResponse(inputs,i)))
            self.meanModelResponses = self.meanModelResponses + modelResponses[len(modelResponses)-1] 
        self.meanModelResponses = self.meanModelResponses/len(inputs)
       
        # calculate modelResponses to validation set
        for i in xrange(len(validation_inputs)):
            validationModelResponses.append(numpy.array(self.calculateModelResponse(validation_inputs,i)))
       
        # substract the mean from model responses
        for i in xrange(0,len(modelResponses)):
            modelResponses[i] = modelResponses[i] - self.meanModelResponses
            
        # substract the mean from validation responses
        for i in xrange(0,len(validationModelResponses)):
            validationModelResponses[i] = validationModelResponses[i] - self.meanModelResponses
        
        #calculate the initial model DC as the mean of the target activities
        for a in activities:
            self.modelDC+=a
        
        self.modelDC = self.modelDC/len(activities)    
            
                    
        self.weigths=numpy.mat(numpy.zeros((size(activities,1),size(modelResponses[0],1))))
        
        mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
        
        old_error = 10000000 * ones(shape(activities[0]))
        
        first_val_error=0
        val_err=0
        
        for k in xrange(0,self.epochs):
            mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            validation_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            tmp_weigths=numpy.mat(numpy.zeros((size(activities,1),size(modelResponses[0],1))))
            for i in xrange(0,len(inputs)):
                error = ((activities[i].T - self.weigths*modelResponses[i].T - self.modelDC.T))
                
                tmp_weigths = tmp_weigths + (error * modelResponses[i])
                mean_error=mean_error+numpy.power(error,2)
            
            for i in xrange(0,len(validation_inputs)):
                error = ((validation_activities[i].T - self.weigths*validationModelResponses[i].T - self.modelDC.T))
                validation_error=validation_error+numpy.power(error,2)
        
                
            if k == 0:
               delta = tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            else:
               delta = self.momentum*delta + (1.0-self.momentum)*tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            
            delta = delta/numpy.sqrt(numpy.sum(numpy.power(delta,2)))
                   
            self.weigths = self.weigths + self.learning_rate*delta
            err = numpy.sum(mean_error)/len(inputs)/len(mean_error)    
            val_err = numpy.sum(validation_error)/len(validation_inputs)/len(validation_error)    
            
            if k == 0:
               first_val_error=val_err
            
            # adjust learning rates based on new errors
            print (k,err,val_err)
            #print delta[0]
            #print mean_error[0]/len(inputs)
            
            #ii =  (mean_error.T/len(inputs)) > old_error
            
            #print shape(ii)
            #learning_rates -= numpy.multiply((learning_rates/10.0), ii)
            #old_error=mean_error.T/len(inputs)
            #print (learning_rates[0][0]) 
        #print mean_error/len(inputs)
        print "First val error:" + str(first_val_error) + "\nLast val error:" + str(val_err) + "\nImprovement:" + str((first_val_error - val_err)/first_val_error * 100) + "%"
        
        # recalculate a new model DC based on what we have learned
        self.modelDC*=0.0
        #for i in xrange(0,len(inputs)):
        #    self.modelDC+=(activities[i].T - self.weigths*modelResponses[i].T).T
        #self.modelDC = self.modelDC/len(inputs)    
        
        for i in xrange(0,len(validation_inputs)):
            self.modelDC+=(validation_activities[i].T - self.weigths*validationModelResponses[i].T).T
        self.modelDC = self.modelDC/len(validation_inputs)   
    
    def calculateReliabilities(self,inputs,activities,top_percentage):
        corr_coef=numpy.zeros(self.num_of_units)
        modelResponses=[]
        modelActivities=[]
            
        for i in xrange(0,len(inputs)):
           a = self.calculateModelOutput(inputs,i)
           if i == 0: 
               modelActivities = a
           else:
               modelActivities = numpy.concatenate((modelActivities,a),axis=1)
           
        modelActivities = numpy.mat(modelActivities)
        
        for i in xrange(0,self.num_of_units):
            corr_coef[i] = numpy.corrcoef(modelActivities[i], activities.T[i])[0][1]

        # calcualte the top_percentage-ith score
        t = []
        import operator
        for i in xrange(0,self.num_of_units):
            t.append((i,corr_coef[i]))
        t=sorted(t, key=operator.itemgetter(1))
        self.reliable_indecies*=0     
        
        for i in xrange(0,self.num_of_units*top_percentage/100):   
            self.reliable_indecies[t[self.num_of_units-1-i][0]] = 1
            #print t[self.num_of_units-1-i][0]
            #pylab.figure()            
            #pylab.plot(numpy.array(activities.T[t[self.num_of_units-1-i][0]][0].T))
            #pylab.plot(numpy.array(modelActivities[t[self.num_of_units-1-i][0]][0].T))
            #pylab.show._needmain=False
            #pylab.show()

    def testModel(self,inputs,activities,target_inputs=None):
        modelActivities=[]
        modelResponses=[]
        error = 0
        
        if target_inputs == None:
           target_inputs = [a for a in xrange(0,len(inputs))]

        for index in range(len(inputs)):
            modelActivities.append(self.calculateModelOutput(inputs,index))
            
        #for i in xrange(0,len(modelResponses)):
        #    if self.reliable_indecies[i]==1.0:    
            
    
        tmp = []
        correct = 0
        #pylab.figure()
        
        #print shape(numpy.abs(activities[0].T - modelActivities[0]))
        #print shape(numpy.mat(self.reliable_indecies).T)
        #print numpy.multiply(numpy.abs(activities[0].T - modelActivities[0]),numpy.mat(self.reliable_indecies).T)        
        #print numpy.sum(numpy.multiply(numpy.abs(activities[0].T - modelActivities[0]),numpy.mat(self.reliable_indecies).T))
    
        for i in target_inputs:
            tmp = []
            for j in target_inputs:
                
                tmp.append(numpy.sum(
                                     numpy.multiply(numpy.abs(activities[i].T - modelActivities[j]),numpy.mat(self.reliable_indecies).T)
                                    ))
            x = numpy.argmin(array(tmp))
            x = target_inputs[x]
            print (x,i)

            #print (i, x)#, array(tmp))
            #print numpy.sum(numpy.multiply(numpy.power(activities[i].T - modelActivities[i],2),self.reliable_indecies.T))/len(activities[0])
            #print numpy.sum(numpy.multiply(numpy.power(activities[i].T - modelActivities[x],2),self.reliable_indecies.T))/len(activities[0])
            if x == i:
                 correct+=1.0
            if i%2 == 10:
                #print "figure"                
                pylab.subplot(5,15,i/2+1)
                #the original activities
                b  = numpy.multiply(activities[i]+self.modelDC,self.reliable_indecies)
                pylab.imshow(toMatrix(b.T.A,14,13),vmin=-0.1,vmax=0.1)
                pylab.subplot(5,15,15+i/2+1)
                # what the model predicts for given stimuli
                b = numpy.multiply(modelActivities[i].T+self.modelDC,self.reliable_indecies)
                pylab.imshow(toMatrix(b.T.A,14,13),vmin=-0.1,vmax=0.1)
                pylab.subplot(5,15,30+i/2+1)
                # the model activities most similar to the original activities
                b = numpy.multiply(modelActivities[x].T+self.modelDC,self.reliable_indecies)
                pylab.imshow(toMatrix(b.T.A,14,13),vmin=-0.1,vmax=0.1)
                pylab.subplot(5,15,45+i/2+1)
                # the given stimuly
                #pylab.imshow(inputs[i],vmin=0,vmax=0.4)
                pylab.imshow(inputs[i])
                # the stimuly which would correspons to the most similar model output
                pylab.subplot(5,15,60+i/2+1)
                pylab.imshow(inputs[x])
                
        print correct, " correct out of ", len(target_inputs)                  
        print "Percentage of correct answers:" ,correct/len(target_inputs)*100, "%"



class MotionModelFit(ModelFit):
    
      real_time=True
          
      def init(self):
          self.reliable_indecies = ones(self.num_of_units)
          for freq in [1.0,2.0,4.0,8.0]:
             for xpos in xrange(0,int(freq)):
                for ypos in xrange(0,int(freq)):
                    x=xpos*(self.retina_diameter/freq)-self.retina_diameter/2 + self.retina_diameter/freq/2 
                    y=ypos*(self.retina_diameter/freq)-self.retina_diameter/2 + self.retina_diameter/freq/2
                    for orient in xrange(0,8):
                        g1 = []
                        g2 = []
                        t = 2
                        sigma = 1.0
                        for speed in [3,6,30]:
                            for p in xrange(0,speed):
                                #temporal_gauss = numpy.exp(-(p-(t+1))*(p-(t+1)) / 2*sigma)
                                temporal_gauss=1.0
                                g1.append(temporal_gauss*Gabor(bounds=BoundingBox(radius=self.retina_diameter/2),frequency=freq,x=x,y=y,xdensity=self.density,ydensity=self.density,size=1/freq,orientation=2*numpy.pi/8*orient,phase=p*(numpy.pi/(speed)))())
                                g2.append(temporal_gauss*Gabor(bounds=BoundingBox(radius=self.retina_diameter/2),frequency=freq,x=x,y=y,xdensity=self.density,ydensity=self.density,size=1/freq,orientation=2*numpy.pi/8*orient,phase=p*(numpy.pi/(speed))+numpy.pi/2)())
                            self.filters.append((g1,g2))  

      def calculateInputDC(self,inputs):
          if self.real_time:
              ModelFit.calculateInputDC(self,inputs)
          else:
              avg = 0
              length=0
              for i in inputs:
                  for j in i:
                      avg = avg + numpy.sum(j)/(size(j,1)*size(j,0))
                      length+=1
              avg = avg/length
              self.inputDC = avg
  
      def calculateModelResponse(self,inputs,index):
            if self.real_time:
                res = []
                for (gabor1,gabor2) in self.filters:
                    r1 = 0
                    r2 = 0
                    r=0
                    l = len(gabor1)
                    for i in xrange(0,numpy.min([index+1,l])): 
                        r1 += numpy.sum(numpy.multiply(gabor1[l-1-i],inputs[index-i]- self.inputDC))
                        r2 += numpy.sum(numpy.multiply(gabor2[l-1-i],inputs[index-i]- self.inputDC))
                    res.append(numpy.sqrt(r1*r1+r2*r2))
                    #res.append(r)
                    #numpy.max([res.append(r1),res.append(r2)])
            else: 
                res = []
                for (gabor1,gabor2) in self.filters:
                    r1 = 0
                    r2 = 0
                    r=0
                    li = len(inputs[index])
                    l = len(gabor1)
                    for i in xrange(0,li): 
                        r1 += numpy.sum(numpy.multiply(gabor1[l-1-numpy.mod(i,l)],inputs[index][li-1-i]- self.inputDC))
                        r2 += numpy.sum(numpy.multiply(gabor2[l-1-numpy.mod(i,l)],inputs[index][li-1-i]- self.inputDC))
                        #r += numpy.sqrt(r1*r1+r2*r2)
                    res.append(numpy.sqrt(r1*r1+r2*r2))
                    #res.append(r)
            
            
            return numpy.mat(res)    

class BasicModelFit(ModelFit):
      def init(self):
          self.reliable_indecies = ones(self.num_of_units)
      def calculateModelResponse(self,inputs,index):
          return  numpy.mat(inputs[index].flatten().tolist())
      
class BasicBPModelFit(BasicModelFit):
 
    def init(self):
          self.reliable_indecies = ones(self.num_of_units)
          import libfann
          self.ann = libfann.neural_net()
    
    def calculateModelOutput(self,inputs,index):
        import libfann
        modelResponse = self.calculateModelResponse(inputs,index) - self.meanModelResponses
        return self.ann.run(numpy.array(modelResponse.T))
    
    def trainModel(self,inputs,activities,validation_inputs,validation_activities):
        import libfann
        self.calculateInputDC(inputs)
        modelResponses=[]
        validationModelResponses=[]
        delta=[]
        self.meanModelResponses=numpy.array(self.calculateModelResponse(inputs,0)).copy()*0.0
        self.modelDC=numpy.array(activities[0]).copy()*0.0
        
        
        # calculate the model responses and their average to the set of inputs
        for i in xrange(len(inputs)):
            modelResponses.append(numpy.array(self.calculateModelResponse(inputs,i)))
            self.meanModelResponses = self.meanModelResponses + modelResponses[len(modelResponses)-1] 
        self.meanModelResponses = self.meanModelResponses/len(inputs)
       
        # calculate modelResponses to validation set
        for i in xrange(len(validation_inputs)):
            validationModelResponses.append(numpy.array(self.calculateModelResponse(validation_inputs,i)))
       
        # substract the mean from model responses
        for i in xrange(0,len(modelResponses)):
            modelResponses[i] = modelResponses[i] - self.meanModelResponses
            
        # substract the mean from validation responses
        for i in xrange(0,len(validationModelResponses)):
            validationModelResponses[i] = validationModelResponses[i] - self.meanModelResponses
        
        #calculate the initial model DC as the mean of the target activities
        for a in activities:
            self.modelDC+=a
        
        self.modelDC = self.modelDC/len(activities)
        print shape(modelResponses)

        connection_rate = 1
        learning_rate = 0.01
        num_input = numpy.size(modelResponses[0],1)
        num_neurons_hidden = numpy.size(activities,1)*2
        num_output = numpy.size(activities,1)
        
        print (num_input,num_neurons_hidden,num_output)
        
        desired_error = 0.0001
        max_iterations = 1000
        iterations_between_reports = 1
        self.ann.create_sparse_array(connection_rate, (num_input, num_neurons_hidden, num_output))
        self.ann.set_learning_rate(learning_rate)
        self.ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC_STEPWISE)
        
        print numpy.min(activities)
        print numpy.max(activities)
        
        train_data  = libfann.training_data()
        test_data = libfann.training_data()
        
        set_fann_dataset(train_data,modelResponses,activities)
        set_fann_dataset(test_data,validationModelResponses,validation_activities)
        self.ann.train_on_data(train_data, max_iterations, iterations_between_reports, desired_error)
        print self.ann.test_data(test_data)
        
        #ann.save("nets/xor_float.net")

def showMotionEnergyPatterns():

    topo.sim['Retina']=GeneratorSheet(nominal_density=24.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))
    mf = MotionModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density
    mf.init()
 
 
 
    for i in xrange(0,8):
        g1,g2 = mf.filters[i]
        pylab.figure()
        for g in g1:
            pylab.imshow(g)
            pylab.show._needmain=False
            pylab.show()



def calculateReceptiveField(RFs,weights):
    RF = numpy.zeros(shape(RFs[0][0]))
    i = 0
    for (rf1,rf2) in RFs:
        RF += weights.T[i,0]*rf1
        #RF += weights.T[i,0]*rf2
        i+=1
    return RF
              
def toMatrix(array,x,y):
    matrix = []
    if x*y == len(array):
        tmp = numpy.zeros((x,y))
        for i in xrange(0,x):
            for j in xrange(0,y):
                tmp[i][j] = (array[i*y+j])
    else:
        print "Size of array doesn't match specified matrix dimensions\n" 
        return
               
    return tmp

def loadRandomizedDataSet(directory,num_rep,num_frames,num_stimuli,n_cells):
    f = file(directory + "/combined_data", "r") 
    data = [line.split() for line in f]
    f.close()

    f = file(directory +"/image_sequence", "r") 
    random = [line.split() for line in f]
    random=numpy.array(random)
    random = random[0]
    f.close()
    r=[]
    for j in random:
        r.append(int(float(j)))
    random = r

    dataset = [([[] for i in xrange(0,num_stimuli)]) for i in xrange(0,n_cells)]

    (recordings,num_cells) = shape(data)

    assert recordings == (num_rep * num_stimuli * num_frames)
    assert recordings / num_frames == len(random)
    assert n_cells == num_cells
    
    for k in xrange(0,num_cells):
        for i in xrange(0,num_rep*num_stimuli):
            f = []
            for fr in xrange(0,num_frames):
                        f.append(float(data[i*num_frames+fr][k]))
            dataset[k][random[i]-1].append(f)

    return (numpy.arange(0,num_stimuli),dataset)
    
def averageRangeFrames(dataset,min,max):
    (index,data) = dataset
    for cell in data:
        for stimulus in cell:
            for r in xrange(0,len(stimulus)):
                stimulus[r]=[numpy.average(stimulus[r][min:max])]
    return (index,data)

def averageRepetitions(dataset):
    (index,data) = dataset
    (num_cells,num_stim,num_rep,num_frames) = shape(data)
    for cell in data:
        for stimulus in xrange(0,num_stim):
            r = [0 for i in range(0,num_frames)]
            for rep in xrange(0,num_rep):
                for f in xrange(0,num_frames):
                    r[f]+=cell[stimulus][rep][f]/num_rep
            cell[stimulus]=[r]
    return (index,data)


def splitDataset(dataset,ratio):
    (index,data) = dataset
    (num_cells,num_stim,trash1,trash2) = shape(data)

    dataset1=[]
    dataset2=[]
    index1=[]
    index2=[]

    for i in xrange(0,num_stim):
        if i < numpy.floor(num_stim*ratio):
            index1.append(index[i])
        else:    
            index2.append(index[i])
    
    for cell in data:
        d1=[]
        d2=[]
        for i in xrange(0,num_stim):
            if i < numpy.floor(num_stim*ratio):
               d1.append(cell[i])
            else:    
               d2.append(cell[i])
        dataset1.append(d1)
        dataset2.append(d2)

    return ((index1,dataset1),(index2,dataset2))

def generateTrainingSet(dataset):
    (index,data) = dataset

    training_set=[]
    for cell in data:
        cell_set=[]
        for stimuli in cell:
           for rep in stimuli:
                for frame in rep:
                    cell_set.append(frame)
        training_set.append(cell_set)
    return numpy.array(numpy.matrix(training_set).T)

def generateInputs(dataset,directory,image_matching_string,density,LGN=False,LGN_size=1.0):
    (index,data) = dataset

    image_filenames=[directory+image_matching_string %(i) for i in index]
    inputs=[Image(filename=f,size=0.55, x=0,y=0)   for f in image_filenames]
    combined_inputs =contrib.jacommands.SequenceSelector(generators=inputs)

    topo.sim['Retina']=GeneratorSheet(nominal_density=density,  
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5+0.1))
                                  
    ## DoG weights for the LGN
    centerg   = Gaussian(size=0.005*LGN_size,aspect_ratio=1.0,output_fns=[DivisiveNormalizeL1()])
    surroundg = Gaussian(size=0.02*LGN_size,aspect_ratio=1.0,output_fns=[DivisiveNormalizeL1()])
        
    on_weights = topo.pattern.basic.Composite(
        generators=[centerg,surroundg],operator=numpy.subtract)
    
    topo.sim["Retina"].input_generator.index=0
    topo.sim['LGNOn'] = CFSheet(nominal_density=density/2,nominal_bounds=BoundingBox(radius=0.5),                    output_fns=[HalfRectify()],measure_maps=False)

    topo.sim.connect('Retina','LGNOn',delay=FixedPoint("0.05"),
                 connection_type=SharedWeightCFProjection,strength=locals().get('ret_strength',2.33),
                 nominal_bounds_template=BoundingBox(radius=0.1),name='Afferent',
                 weights_generator=on_weights)

    inputs=[]
    topo.sim['Retina'].set_input_generator(combined_inputs)
    for j in xrange(0,len(index)):
        topo.sim.run(1)
        if LGN:
            inputs.append(topo.sim["LGNOn"].activity.copy())
        else: 
            inputs.append(topo.sim["Retina"].activity.copy())
    training_inputs=[]
    
    for s in range(len(data[0])):
        for rep in data[0][s]:
            for frame in rep:
                training_inputs.append(inputs[s])
    return inputs

def clump_low_responses(dataset,threshold):
    (index,data) = dataset
    
    avg=0
    count=0
    
    for cell in data:
        for stimuli in cell:
           for rep in stimuli:
                for frame in rep:
                    avg+=frame
                    count+=1
    avg = avg/count
   
    for index1, cell in enumerate(data): 
        for index2, stimulus in enumerate(cell):
            for index3, repetition in enumerate(stimulus):
                for index4, frame in enumerate(repetition):
                    if frame>=avg*(1.0+threshold):
                       repetition[index4]=frame
                    else:
                       repetition[index4]=0
                       
    return (index,data)
    
def runModelFit():
    
    density=__main__.__dict__.get('density', 200)
    
    dataset = loadRandomizedDataSet("Flogl/JAN1/20090707__retinotopy_region1_stationary_testing01_1rep_125stim_ALL",6,15,125,60)
    
     
    print shape(dataset[1])
    dataset = clump_low_responses(dataset,__main__.__dict__.get('ClumpMag',0.1))
    print shape(dataset[1])
    dataset = averageRangeFrames(dataset,0,15)
    print shape(dataset[1])
    dataset = averageRepetitions(dataset)
    print shape(dataset[1])
    
    
    (dataset,validation_data_set) = splitDataset(dataset,0.9)
    (dataset,testing_data_set) = splitDataset(dataset,0.9)

    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"Flogl/JAN1/20090707__retinotopy_region1_stationary_testing01_1rep_125stim_ALL","/images/testing01_%03d.tif",density,LGN=__main__.__dict__.get('LGNOn',False),LGN_size=__main__.__dict__.get('LGNSize',1.0))
    
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"Flogl/JAN1/20090707__retinotopy_region1_stationary_testing01_1rep_125stim_ALL","/images/testing01_%03d.tif",density,LGN=__main__.__dict__.get('LGNOn',False),LGN_size=__main__.__dict__.get('LGNSize',1.0))
    
    testing_set = generateTrainingSet(testing_data_set)
    testing_inputs=generateInputs(testing_data_set,"Flogl/JAN1/20090707__retinotopy_region1_stationary_testing01_1rep_125stim_ALL","/images/testing01_%03d.tif",density,LGN=__main__.__dict__.get('LGNOn',False),LGN_size=__main__.__dict__.get('LGNSize',1.0))
    
    
    print shape(training_set)
    print shape(validation_set)
    print shape(testing_set)
    
    #pylab.plot(numpy.array(numpy.mat(training_set).T)[0])
    #pylab.plot(numpy.array(numpy.mat(training_set).T)[1])
    #matrixplot(training_inputs[0])
    #matrixplot(training_inputs[1])
    #matrixplot(validation_inputs[0])
    #matrixplot(validation_inputs[1])
    #pylab.show()
    
    #mf = BasicBPModelFit()
    mf = BasicModelFit()
    mf.retina_diameter = 1.0
    mf.density = density
    mf.learning_rate = __main__.__dict__.get('lr',0.00001)
    mf.epochs=__main__.__dict__.get('epochs',2000)
    mf.num_of_units = 60
    mf.init()

    mf.trainModel(training_inputs,numpy.mat(training_set),validation_inputs,numpy.mat(validation_set))
    mf.testModel(training_inputs,numpy.mat(training_set))
    mf.testModel(testing_inputs,numpy.mat(testing_set))
    

    mf.calculateReliabilities(training_inputs,numpy.mat(training_set),50)
    mf.testModel(testing_inputs,numpy.mat(testing_set))
    
    mf.calculateReliabilities(training_inputs,numpy.mat(training_set),40)
    mf.testModel(testing_inputs,numpy.mat(testing_set))

    mf.calculateReliabilities(training_inputs,numpy.mat(training_set),30)
    mf.testModel(testing_inputs,numpy.mat(testing_set))

    mf.calculateReliabilities(training_inputs,numpy.mat(training_set),10)
    mf.testModel(testing_inputs,numpy.mat(testing_set))
    
    return mf

def showRF(mf,index,density):
    w = mf.weigths[index].reshape(density,density)
    pylab.figure()
    pylab.show._needmain=False
    pylab.imshow(w,vmin=numpy.min(mf.weigths[index]),vmax=numpy.max(mf.weigths[index]))
    pylab.show()
    

def analyseDataSet(data_set):
#        for cell in dataset:
        for z in xrange(0,10):
                pylab.figure()
                pylab.plot(numpy.arange(0,num_im,1),a[z],'bo')  
        pylab.show()

def set_fann_dataset(td,inputs,outputs):
    import os
    f = open("./tmp.txt",'w')
    f.write(str(len(inputs))+" "+str(size(inputs[0],1))+" "+ str(size(outputs,1)) + "\n")
    
    
    for i in range(len(inputs)):
        for j in range(size(inputs[0],1)):
            f.write(str(inputs[i][0][j]))
            f.write('\n')
        for j in range(size(outputs,1)):
            f.write(str(outputs[i,j]))
            f.write('\n')
    f.close()
    
    td.read_train_from_file("./tmp.txt")
