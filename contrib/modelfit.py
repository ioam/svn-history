from topo.pattern.basic import Gabor, SineGrating, Gaussian
import __main__
import numpy
import pylab
from numpy import array, size, mat, shape, ones, arange
from topo.misc.numbergenerator import UniformRandom, BoundedNumber, ExponentialDecay
#from topo.base.functionfamily import IdentityTF
from topo.transferfn.basic import PiecewiseLinear, DivisiveNormalizeL1, IdentityTF, ActivityAveragingTF, AttributeTrackingTF,PatternCombine,Sigmoid, HalfRectify
from topo.base.cf import CFSheet
from topo.projection.basic import CFProjection, SharedWeightCFProjection
from fixedpoint import FixedPoint
import topo
from topo.command.pylabplots import matrixplot
from topo.sheet import GeneratorSheet 
from topo.base.boundingregion import BoundingBox
from topo.pattern.image import FileImage
import contrib.jacommands
from topo.misc.filepath import normalize_path, application_path

class ModelFit():
    weigths = []
    retina_diameter=1.2
    density=24
    epochs = 500
    learning_rate = 0.00001
    DC = 0
    reliable_indecies=[]
    momentum=0.0
    num_of_units=0
    
    def init(self):
        self.reliable_indecies = ones(self.num_of_units)

    def calculateModelOutput(self,inputs,index):
        return self.weigths*inputs[index].T+self.DC.T

    def trainModel(self,inputs,activities,validation_inputs,validation_activities,stop=None):
        
        if stop==None:
           stop = numpy.ones(numpy.shape(activities[0])).copy()*1000000000000000000000
        
        delta=[]
        self.DC=numpy.array(activities[0]).copy()*0.0

        self.weigths=numpy.mat(numpy.zeros((size(activities,1),size(inputs[0],1))))
        best_weights = self.weigths.copy()

        mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
        first_val_error=0
        val_err=0
        min_err=1000000000
        min_val_err=1000000000000
        min_val_err_array = ones(self.num_of_units)*10000000000000000000
        first_val_err_array = []
        err_hist = []
        val_err_hist = []

        
        for k in xrange(0,self.epochs):
            
            stop_learning = (stop>k)*1.0
            sl = numpy.mat(stop_learning).T
            for i in xrange(1, size(inputs[0],1)):
                sl = numpy.concatenate((sl,numpy.mat(stop_learning).T),axis=1)
            
            mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            validation_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            tmp_weigths=numpy.mat(numpy.zeros((size(activities,1),size(inputs[0],1))))
            for i in xrange(0,len(inputs)):
                error = ((activities[i].T - self.weigths*inputs[i].T - self.DC.T))
                
                tmp_weigths = tmp_weigths + (error * inputs[i])
                mean_error=mean_error+numpy.power(error,2)
            
            err_hist.append(mean_error)
            
            if k == 0:
               delta = tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            else:
               delta = self.momentum*delta + (1.0-self.momentum)*tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            
            delta = numpy.multiply(delta/numpy.sqrt(numpy.sum(numpy.power(delta,2))),sl)
                   
            self.weigths = self.weigths + self.learning_rate*delta
            err = numpy.sum(mean_error)/len(inputs)/len(mean_error)    
            
            for i in xrange(0,len(validation_inputs)):
                error = ((validation_activities[i].T - self.weigths*validation_inputs[i].T - self.DC.T))
                validation_error=validation_error+numpy.power(error,2)
            val_err_hist.append(validation_error)
            val_err = numpy.sum(validation_error)/len(validation_inputs)/len(validation_error)    
            
               
            if val_err < min_val_err:
               min_val_err = val_err
            if err < min_err:
               min_err = err
               
            for i in xrange(0,len(min_val_err_array)):
                if min_val_err_array[i] > numpy.array(validation_error)[i][0]:
                   min_val_err_array[i] = numpy.array(validation_error)[i][0]
                #!!!!!!!!!!!!!
                best_weights[i,:] = self.weigths[i,:]
                
            if k == 0:
               first_val_error=val_err
               first_val_err_array = min_val_err_array.copy()

            print (k,err,val_err)
        print "First val error:" + str(first_val_error) + "\n Minimum val error:" + str(min_val_err) +        "\n Last val error:" + str(val_err) + "\nImprovement:" + str((first_val_error - min_val_err)/first_val_error * 100) + "%" + "\nBest cell by cell error:" + str(numpy.sum(min_val_err_array)/len(min_val_err_array)/len(validation_inputs)) + "\nBest cell by cell error improvement:" + str((first_val_err_array - min_val_err_array)/len(validation_inputs)/first_val_err_array)

        # plot error evolution
        a = err_hist[0].T/self.epochs
        b = val_err_hist[0].T/self.epochs
        
        for i in xrange(1,len(err_hist)):
            a = numpy.concatenate((a,err_hist[i].T/self.epochs))
            b = numpy.concatenate((b,val_err_hist[i].T/self.epochs))
        
        a = numpy.mat(a).T
        b = numpy.mat(b).T
        pylab.figure()
        for i in xrange(0,size(activities,1)):
            pylab.hold(True)
            pylab.plot(numpy.array(a[i])[0])

        pylab.figure()    
        for i in xrange(0,size(activities,1)):
            pylab.hold(True)
            pylab.plot(numpy.array(b[i])[0])

        # recalculate a new model DC based on what we have learned
        self.DC*=0.0
         
        # set weights to the minimum ones
        self.weigths = best_weights
        for i in xrange(0,len(validation_inputs)):
            self.DC+=(validation_activities[i].T - self.weigths*validation_inputs[i].T).T
        self.DC = self.DC/len(validation_inputs)   
        

        return (min_val_err,numpy.argmin(b.T,axis=0),min_val_err_array/len(validation_inputs))
    
    def calculateReliabilities(self,inputs,activities,top_percentage):
        err=numpy.zeros(self.num_of_units)
        modelResponses=[]
        modelActivities=[]
            
        for i in xrange(0,len(inputs)):
           if i == 0: 
               modelActivities = self.calculateModelOutput(inputs,i)
           else:
               a = self.calculateModelOutput(inputs,i)
               modelActivities = numpy.concatenate((modelActivities,a),axis=1)
           
        modelActivities = numpy.mat(modelActivities)
        
        #for i in xrange(0,self.num_of_units):
        #    corr_coef[i] = numpy.corrcoef(modelActivities[i], activities.T[i])[0][1]
        #print numpy.shape(modelActivities)
        #print numpy.shape(activities)
        for i in xrange(0,self.num_of_units):
            err[i] = numpy.sum(numpy.power(modelActivities[i]- activities.T[i],2))

        t = []
        import operator
        for i in xrange(0,self.num_of_units):
            t.append((i,err[i]))
        t=sorted(t, key=operator.itemgetter(1))
        self.reliable_indecies*=0     
        
        for i in xrange(0,self.num_of_units*top_percentage/100):   
            self.reliable_indecies[t[i][0]] = 1
            #print t[self.num_of_units-1-i][0]
            #pylab.figure()
            #pylab.show._needmain=False            
            #pylab.subplot(3,1,1)
            #pylab.plot(numpy.array(activities.T[t[self.num_of_units-1-i][0]][0].T))
            #pylab.plot(numpy.array(modelActivities[t[self.num_of_units-1-i][0]][0].T))
	    #pylab.show()

    def testModel(self,inputs,activities,target_inputs=None):
        modelActivities=[]
        modelResponses=[]
        error = 0
        
        if target_inputs == None:
           target_inputs = [a for a in xrange(0,len(inputs))]

        for index in range(len(inputs)):
            modelActivities.append(self.calculateModelOutput(inputs,index))
            
        tmp = []
        correct = 0
        for i in target_inputs:
            tmp = []
            for j in target_inputs:
                 tmp.append(numpy.sum(numpy.power(numpy.multiply(activities[i].T-modelActivities[j],numpy.mat(self.reliable_indecies).T),2)))
                 
                 #tmp.append(numpy.sum(numpy.abs(                                    numpy.multiply(activities[i].T  - modelActivities[j],numpy.mat(self.reliable_indecies).T))                                    ))
                 #tmp.append(numpy.corrcoef(modelActivities[j].T, activities[i])[0][1])
            x = numpy.argmin(array(tmp))

            #x = numpy.argmax(array(tmp))
            x = target_inputs[x]
            #print (x,i)
            
            if (i % 1) ==1:
                pylab.show._needmain=False
                pylab.figure()
                pylab.subplot(3,1,1)
                pylab.plot(numpy.array(activities[i])[0],'o',label='traget')
                pylab.plot(numpy.array(modelActivities[x].T)[0], 'o',label='predicted model')
                pylab.plot(numpy.array(modelActivities[i].T)[0], 'o',label='correct model')
                pylab.legend()
                #pylab.show()

            if x == i:
                 correct+=1.0
                
        print correct, " correct out of ", len(target_inputs)                  
        print "Percentage of correct answers:" ,correct/len(target_inputs)*100, "%"


    def testModelBiased(self,inputs,activities,t):
        modelActivities=[]
        modelResponses=[]
        error = 0

        (num_inputs,act_len)= numpy.shape(activities)
        print (num_inputs,act_len)

        for index in range(num_inputs):
            modelActivities.append(self.calculateModelOutput(inputs,index))

        m = numpy.mean(activities,0)
        
        tmp = []
        correct = 0
        for i in xrange(0,num_inputs):
            tmp = []
            significant_neurons=numpy.zeros(numpy.shape(activities[0]))       
            for z in xrange(0,act_len):
                if activities[i,z] >= m[0,z]*t: significant_neurons[0,z]=1.0
            
            for j in xrange(0,num_inputs):

                 tmp.append(numpy.sum(numpy.power(numpy.multiply(numpy.multiply(activities[i].T-modelActivities[j],numpy.mat(self.reliable_indecies)),numpy.mat(significant_neurons).T),2))/ numpy.sum(significant_neurons))
            
            x = numpy.argmin(array(tmp))
            if x == i: correct+=1.0
                
        print correct, " correct out of ", num_inputs                  
        print "Percentage of correct answers:" ,correct/num_inputs*100, "%"


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
  
      def calculateModelResponse(self,inputs,index):
            if self.real_time:
                res = []
                for (gabor1,gabor2) in self.filters:
                    r1 = 0
                    r2 = 0
                    r=0
                    l = len(gabor1)
                    for i in xrange(0,numpy.min([index+1,l])): 
                        r1 += numpy.sum(numpy.multiply(gabor1[l-1-i],inputs[index-i]))
                        r2 += numpy.sum(numpy.multiply(gabor2[l-1-i],inputs[index-i]))
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
                        r1 += numpy.sum(numpy.multiply(gabor1[l-1-numpy.mod(i,l)],inputs[index][li-1-i]))
                        r2 += numpy.sum(numpy.multiply(gabor2[l-1-numpy.mod(i,l)],inputs[index][li-1-i]))
                        #r += numpy.sqrt(r1*r1+r2*r2)
                    res.append(numpy.sqrt(r1*r1+r2*r2))
                    #res.append(r)
            
            
            return numpy.mat(res)    
      
class BasicBPModelFit(ModelFit):
 
    def init(self):
          self.reliable_indecies = ones(self.num_of_units)
          import libfann
          self.ann = libfann.neural_net()
    
    def calculateModelOutput(self,inputs,index):
        import libfann
        return numpy.mat(self.ann.run(numpy.array(inputs[index].T))).T
    
    def trainModel(self,inputs,activities,validation_inputs,validation_activities):
        import libfann
        delta=[]

        connection_rate = 1.0
        num_input = len(inputs[0])
        num_neurons_hidden = numpy.size(activities,1)
        num_output = numpy.size(activities,1)
        
        print (num_input,num_neurons_hidden,num_output)
        
        desired_error = 0.000001
        max_iterations = 1000
        iterations_between_reports = 1
        self.ann.create_sparse_array(connection_rate, (num_input, num_neurons_hidden, num_output))
        self.ann.set_learning_rate(self.learning_rate)
        self.ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC)
        
        train_data  = libfann.training_data()
        test_data = libfann.training_data()
        print shape(inputs)
        print shape(activities)
        train_data.set_train_dataset(numpy.array(inputs),numpy.array(activities))
        test_data.set_train_dataset(numpy.array(validation_inputs),numpy.array(validation_activities))
        
        self.ann.reset_MSE()
        self.ann.test_data(test_data)
        print "MSE error on test data: %f" % self.ann.get_MSE()
        self.ann.reset_MSE()
        self.ann.test_data(train_data)
        print "MSE error on train data: %f" % self.ann.get_MSE()
        self.ann.reset_MSE()

        for i in range(0,self.epochs):
            e = self.ann.train_epoch(train_data)
            self.ann.reset_MSE()
            self.ann.test_data(test_data)
            print "%d > MSE error on train/test data: %f / %f" % (i,e,self.ann.get_MSE())
        
        self.ann.reset_MSE()
        self.ann.test_data(test_data)
        print "MSE error on test data: %f" % self.ann.get_MSE()
        self.ann.reset_MSE()


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
            
def loadSimpleDataSet(filename,num_stimuli,n_cells):
    f = file(filename, "r") 
    data = [line.split() for line in f]
    f.close()

    dataset = [([[] for i in xrange(0,num_stimuli)]) for i in xrange(0,n_cells)]
    print shape(dataset)
    #(num_stimuli,n_cells) = shape(data)
    
    for k in xrange(0,n_cells):
        for i in xrange(0,num_stimuli):
            f = []
            for fr in xrange(0,1):
                        f.append(float(data[i+fr][k]))
            dataset[k][i].append(f)
    print shape(dataset)
    return (numpy.arange(0,num_stimuli),dataset)
            

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

def averageRepetitions(dataset,reps=None):
    (index,data) = dataset
    (num_cells,num_stim,num_rep,num_frames) = shape(data)

    if reps==None:
       reps = numpy.arange(0,num_rep,1)

    for cell in data:
        for stimulus in xrange(0,num_stim):
            r = [0 for i in range(0,num_frames)]
            for rep in reps:
                for f in xrange(0,num_frames):
                    r[f]+=cell[stimulus][rep][f]/len(reps)
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

def generateInputs(dataset,directory,image_matching_string,density,aspect,offset):
    (index,data) = dataset

    # ALERT ALERT ALERT We do not handle repetitions yet!!!!!
    
    image_filenames=[directory+image_matching_string %(i+offset) for i in index]
    inputs=[FileImage(filename=f,size=0.55, x=0,y=0)   for f in image_filenames]
    
    ins=[]
    for j in xrange(0,len(index)):
        inp = inputs[j](xdensity=density,ydensity=density) 
        (x,y) = shape(inp)
        z=(x - x / aspect)/2
        ins.append(inp[z:x-z,:])
 
    
    #training_inputs=[]
    #for s in range(len(data[0])):
    #    for rep in data[0][s]:
    #        for frame in rep:
    #            training_inputs.append(inputs[s])
    return ins

def generate_pyramid_model(num_or,freqs,num_phase,size):
    filters=[]
    for freq in freqs:
        for orient in xrange(0,num_or):
            g1 = Gabor(bounds=BoundingBox(radius=0.5),frequency=1.0,x=0.0,y=0.0,xdensity=size/freq,ydensity=size/freq,size=0.3,orientation=numpy.pi/8*orient,phase=numpy.pi)
            g2 = Gabor(bounds=BoundingBox(radius=0.5),frequency=1.0,x=0.0,y=0.0,xdensity=size/freq,ydensity=size/freq,size=0.3,orientation=numpy.pi/8*orient,phase=0)
            filters.append((g1(),g2()))
            #for p in xrange(0,num_phase):
            #    g = Gabor(bounds=BoundingBox(radius=0.5),frequency=1.0,x=0.0,y=0.0,xdensity=size/freq,ydensity=size/freq,size=0.3,orientation=numpy.pi/8*orient,phase=p*2*numpy.pi/num_phase)
            #    filters.append(g())

    return filters

def generate_raw_training_set(inputs):
    out = []
    for i in inputs:
        out.append(i.flatten())
    return numpy.array(out)

def apply_filters(inputs, filters, spacing):
    (sizex,sizey) = numpy.shape(inputs[0])
    out = []
    for i in inputs:
        o  = []
        for f in filters:
            (f1,f2) = f
            (s,tresh) = numpy.shape(f1)
            step = int(s*spacing)
            x=0
            y=0
            while (x*step + s) < sizex:
                while (y*step + s) < sizey:
                    a = numpy.sum(numpy.sum(numpy.multiply(f1,i[x*step:x*step+s,y*step:y*step+s])))
                    b = numpy.sum(numpy.sum(numpy.multiply(f2,i[x*step:x*step+s,y*step:y*step+s])))
                    o.append(numpy.sqrt(a*a+b*b))
                    y+=step 
                x+=step
        print len(o)
        out.append(numpy.array(o))
    return numpy.array(out)
                
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

def compute_average_min_max(data_set):
    avg = numpy.zeros(shape(data_set[0]))
    var = numpy.zeros(shape(data_set[0]))
    
    for d in data_set:
        avg += d
    avg = avg/(len(data_set)*1.0)
    
    for d in data_set:
        var += numpy.multiply((d-avg),(d-avg))
    var = var/(len(data_set)*1.0)
    return (avg,var)
    
def normalize_data_set(data_set,avg,var):
    print shape(avg)
    for i in xrange(0,len(data_set)):
        data_set[i]-=avg
        data_set[i]=numpy.divide(data_set[i],numpy.sqrt(var)) 
    return data_set

def compute_average_input(inputs):
    avgRF = numpy.zeros(shape(inputs[0]))

    for i in inputs:
        avgRF += i
    avgRF = avgRF/(len(inputs)*1.0)
    return avgRF

def normalize_image_inputs(inputs,avgRF):
    for i in xrange(0,len(inputs)):
        inputs[i]=numpy.divide(inputs[i],avgRF)

    return inputs


def runModelFit():
   
    density=__main__.__dict__.get('density', 20)
    
    #dataset = loadRandomizedDataSet("Flogl/JAN1/20090707__retinotopy_region1_stationary_testing01_1rep_125stim_ALL",6,15,125,60)
    dataset = loadSimpleDataSet("Flogl/DataNov2009/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_2700images_on_&_off_response",2700,50)

    #this dataset has images numbered from 1
    (index,data) = dataset
    index+=1
    dataset=(index,data)
     
    #print shape(dataset[1])
    #dataset = clump_low_responses(dataset,__main__.__dict__.get('ClumpMag',0.0))
    print shape(dataset[1])
    dataset = averageRangeFrames(dataset,0,1)
    print shape(dataset[1])
    dataset = averageRepetitions(dataset)
    print shape(dataset[1])
    
    (testing_data_set,dataset) = splitDataset(dataset,0.015)    
    (validation_data_set,dataset) = splitDataset(dataset,0.1)



    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    
    testing_set = generateTrainingSet(testing_data_set)
    testing_inputs=generateInputs(testing_data_set,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    

    
    #print numpy.shape(training_inputs[0])
    #compute_spike_triggered_average_rf(training_inputs,training_set,density)
    #pylab.figure()
    #pylab.imshow(training_inputs[0])
    #pylab.show()
    #return
    
    if __main__.__dict__.get('NormalizeInputs',True):
       avgRF = compute_average_input(training_inputs)
       training_inputs = normalize_image_inputs(training_inputs,avgRF)
       validation_inputs = normalize_image_inputs(validation_inputs,avgRF)
       testing_inputs = normalize_image_inputs(testing_inputs,avgRF)
    
    
    (x,y)= numpy.shape(training_inputs[0])
    training_inputs = cut_out_images_set(training_inputs,int(y*0.4),(int(x*0.1),int(y*0.4)))
    validation_inputs = cut_out_images_set(validation_inputs,int(y*0.4),(int(x*0.1),int(y*0.4)))
    testing_inputs = cut_out_images_set(testing_inputs,int(y*0.4),(int(x*0.1),int(y*0.4)))
    #training_inputs = cut_out_images_set(training_inputs,int(density*0.33),(0,int(density*0.33)))
    #validation_inputs = cut_out_images_set(validation_inputs,int(density*0.33),(0,int(density*0.33)))
    #testing_inputs = cut_out_images_set(testing_inputs,int(density*0.33),(0,int(density*0.33)))
    
    sizex,sizey=numpy.shape(training_inputs[0])
    
    print sizex,sizey
    
    if __main__.__dict__.get('Gabor',True):
        fil = generate_pyramid_model(__main__.__dict__.get('num_or',8),__main__.__dict__.get('freq',[1,2,4]),__main__.__dict__.get('num_phase',8),numpy.min(numpy.shape(training_inputs[0])))
        
        print len(fil)
        training_inputs = apply_filters(training_inputs, fil, __main__.__dict__.get('spacing',0.1))
        testing_inputs = apply_filters(testing_inputs, fil, __main__.__dict__.get('spacing',0.1))
        validation_inputs = apply_filters(validation_inputs, fil, __main__.__dict__.get('spacing',0.1))
    else:
        training_inputs = generate_raw_training_set(training_inputs)
        testing_inputs = generate_raw_training_set(testing_inputs)
        validation_inputs = generate_raw_training_set(validation_inputs)
    
    if __main__.__dict__.get('NormalizeActivities',True):
        (a,v) = compute_average_min_max(numpy.concatenate((training_set,validation_set),axis=0))
        training_set = normalize_data_set(training_set,a,v)
        validation_set = normalize_data_set(validation_set,a,v)
        testing_set = normalize_data_set(testing_set,a,v)
    
    print shape(training_set)
    print shape(training_inputs)
    
    
    #mf = BasicBPModelFit()
    mf = ModelFit()
    #mf.retina_diameter = 1.2
    mf.density = density
    mf.learning_rate = __main__.__dict__.get('lr',0.1)
    mf.epochs=__main__.__dict__.get('epochs',1000)
    mf.num_of_units = 50
    mf.init()
    
    pylab.hist(training_set.flatten())

    (err,stop,min_errors) = mf.trainModel(mat(training_inputs),numpy.mat(training_set),mat(validation_inputs),numpy.mat(validation_set))
    print "\nStop criterions", stop
    print "\nNon-zero stop criterions",numpy.nonzero(stop)
    print "\nMinimal errors per cell",numpy.nonzero(min_errors)
    
    print "Model test with all neurons"
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),0.1)
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),0.3)
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),0.6)
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),1.0)
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),2.0)
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),3.0)
    mf.testModelBiased(mat(testing_inputs),numpy.mat(testing_set),4.0)
    
    print "Model test with double weights"
    mf.weigths*=2.0
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))
    mf.weigths/=2.0
    
    print "Model test on validation inputs"
    mf.testModel(mat(validation_inputs),numpy.mat(validation_set))
    
    #print "Model test on training inputs"
    #mf.testModel(mat(training_inputs),mat(training_set))
    
    
    
    mf.calculateReliabilities(mat(testing_inputs),numpy.mat(testing_set),95)
    print "95: " , mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))

    mf.calculateReliabilities(mat(testing_inputs),numpy.mat(testing_set),90)
    print "90: " , mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))

    mf.calculateReliabilities(mat(testing_inputs),numpy.mat(testing_set),50)
    print "50: " , mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))
    
    mf.calculateReliabilities(mat(testing_inputs),numpy.mat(testing_set),40)
    print "40: " , mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))

    mf.calculateReliabilities(mat(testing_inputs),numpy.mat(testing_set),30)
    print "30: " , mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))

    mf.calculateReliabilities(mat(testing_inputs),numpy.mat(testing_set),20)
    print "20: " , mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))
    
    mf.reliable_indecies=(stop>=100.0)*1.0
    print mf.reliable_indecies
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))

    lookForCorrelations(mf, numpy.mat(training_set),numpy.mat(training_inputs))
    lookForCorrelations(mf, numpy.mat(validation_set),numpy.mat(validation_inputs))
    
    pylab.show()
    return (mf,mat(testing_inputs),mat(testing_set))

def showRF(mf,indexes,x,y):
    pylab.figure()
    pylab.show._needmain=False
    #pylab.subplot(9,7,1)
    print numpy.min(numpy.min(mf.weigths))
    print numpy.max(numpy.max(mf.weigths))
    for i in indexes:
        pylab.subplot(9,7,i+1)
        w = mf.weigths[i].reshape(x,y)
         
        pylab.imshow(w,vmin=numpy.min(mf.weigths[i]),vmax=numpy.max(mf.weigths[i]),cmap=pylab.cm.RdBu)
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
    

def ridge_regression_rf(inputs,activities,sizex,sizey,delta,alpha,theta,validation_inputs,validation_activities,display=False,size=0.2,ni=100):
    
    p = len(inputs[0])
    np = len(activities[0])
    inputs = numpy.mat(inputs)
    activities = numpy.mat(activities)
    validation_inputs = numpy.mat(validation_inputs)
    validation_activities = numpy.mat(validation_activities)
    S = inputs
    
    for x in xrange(0,sizex):
        for y in xrange(0,sizey):
            norm = numpy.mat(numpy.zeros((sizex,sizey)))
            locality = numpy.mat(numpy.zeros((sizex,sizey)))
            norm[x,y]=4
            if x > 0:
               norm[x-1,y]=-1
            if x < sizex-1:
               norm[x+1,y]=-1   
            if y > 0:
               norm[x,y-1]=-1
            if y < sizey-1:
               norm[x,y+1]=-1
            S = numpy.concatenate((S,alpha*norm.flatten()),axis=0)
    
    #for x in xrange(0,sizex):
    #    for y in xrange(0,sizey):
    #        locality = numpy.mat(numpy.zeros((sizex,sizey)))
    #        for xx in xrange(0,sizex):
    #            for yy in xrange(0,sizey):
    #                if numpy.sqrt((x-xx)*(x-xx) + (y-yy)*(y-yy)) < sizex*size:
    #                    locality[xx,yy] = -1
    #                else:
    #                    locality[xx,yy] = 1 
    #        S = numpy.concatenate((S,theta*locality.flatten()),axis=0)

    
    activities = numpy.concatenate((activities,numpy.mat(numpy.zeros((sizey*sizex,np)))),axis=0)
    #activities = numpy.concatenate((activities,numpy.mat(-1*numpy.zeros((sizey*sizex,np)))),axis=0)
    #A = S.T * S + delta*numpy.mat(numpy.eye(p))
    #X = numpy.linalg.pinv(A)
    #Z = X*S.T*activities
    Z = numpy.linalg.pinv(S)*activities
    Z=Z.T
    ma = numpy.max(numpy.max(Z))
    mi = numpy.min(numpy.min(Z))
    m = max([abs(ma),abs(mi)])
    RFs=[]
    if display:
        av=[]
        pylab.figure()
        pylab.title(str(delta), fontsize=16)
        for i in xrange(0,50):
            av.append(numpy.sum(numpy.power(Z[i],2)))
            pylab.subplot(7,8,i+1)
            w = numpy.array(Z[i]).reshape(sizex,sizey)
            RFs.append(w)
            pylab.show._needmain=False
            pylab.imshow(w,vmin=-m,vmax=m,cmap=pylab.cm.RdBu)
        pylab.savefig(normalize_path("RFs_"+str(ni)+"_normalized"))
        print "AV:", av
        pylab.figure()
        pylab.hist(av)
        
        pylab.figure()
        pylab.title(str(delta), fontsize=16)
        for i in xrange(0,50):
            pylab.subplot(7,8,i+1)
            w = numpy.array(Z[i]).reshape(sizex,sizey)
            pylab.show._needmain=False
            m = numpy.max([abs(numpy.min(numpy.min(w))),abs(numpy.max(numpy.max(w)))])
            pylab.imshow(w,vmin=-m,vmax=m,cmap=pylab.cm.RdBu)
        pylab.savefig(normalize_path("RFs_"+str(ni)))
            
            
    error = numpy.sum(numpy.sqrt(numpy.sum(numpy.power(validation_activities - validation_inputs*Z.T,2),axis=1)))
    
    # prediction
    predicted_activities = validation_inputs*Z.T
    correct=0
    for i in xrange(0,len(validation_inputs)):
        tmp = []
        for j in xrange(0,len(validation_inputs)):
            tmp.append(numpy.sqrt(numpy.sum(numpy.power(validation_activities[i]-predicted_activities[j],2))))
        x = numpy.argmin(tmp)
        if (x == i): correct+=1 
    return (error,correct,RFs) 


def lasso_regression_rf(inputs,activities,sizex,sizey,delta,alpha,theta,validation_inputs,validation_activities,display=False,size=0.2):
    
    p = len(inputs[0])
    np = len(activities[0])
    inputs = numpy.mat(inputs)
    activities = numpy.mat(activities)
    validation_inputs = numpy.mat(validation_inputs)
    validation_activities = numpy.mat(validation_activities)
    from scipy.io import write_array 
    write_array("inputs.txt",inputs)
    write_array("activities.txt",activities)
    write_array("valdation_inputs.txt",validation_inputs)
    write_array("valdation_activities.txt",validation_activities)
    
    from monte.arch import lasso
    pylab.show._needmain=False
    
    l = lasso.Lasso(p)
    print numpy.shape(inputs.T)
    print numpy.shape(activities[:,0].T)
    l.train(inputs.T,activities[:,0].T,15.0)
    pylab.clf()
    plot(abs(l.getparams()[0]), label='model')
    pylab.show()
    
    return 

    
    if display:
        pylab.figure()
        pylab.title(str(delta), fontsize=16)
        for i in xrange(0,49):
            pylab.subplot(7,7,i+1)
            w = numpy.array(Z[i]).reshape(sizex,sizey)
            pylab.show._needmain=False
            pylab.imshow(w,vmin=numpy.min(w),vmax=numpy.max(w),cmap=pylab.cm.RdBu)
    error = numpy.sum(numpy.sqrt(numpy.sum(numpy.power(validation_activities - validation_inputs*Z.T,2),axis=1)))
    
    # prediction
    predicted_activities = validation_inputs*Z.T
    correct=0
    for i in xrange(0,len(validation_inputs)):
        tmp = []
        for j in xrange(0,len(validation_inputs)):
            tmp.append(numpy.sqrt(numpy.sum(numpy.power(validation_activities[i]-predicted_activities[j],2))))
        x = numpy.argmin(tmp)
        if (x == i): correct+=1 
    return (error,correct) 


def cut_out_images_set(inputs,size,pos):
    (sizex,sizey) = numpy.shape(inputs[0])
    
    print sizex,sizey
    print size,pos
    (x,y) = pos
    inp = []
    if (x+size <= sizex) and (y+size <= sizey):
        for i in inputs:
                inp.append(i[x:x+size,y:y+size])
    else:
        print "cut_out_images_set: out of bounds"
    return inp
    
#def cut_training_set(t_s,rang):
#    ts = []
#    (mmin,mmax) = rang
#    for t in t_s:
#        ts.append(
    
    

def runRFPositionPrediction(sf,stepsize):
    density=__main__.__dict__.get('density', 50)
    dataset = loadSimpleDataSet("Flogl/DataOct2009/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_2700images",2700,50)
    (index,data) = dataset
    index+=1
    dataset=(index,data)
    dataset = averageRangeFrames(dataset,0,1)
    dataset = averageRepetitions(dataset)
    
    (dataset,validation_data_set) = splitDataset(dataset,0.9)

    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000) 
    (sizex,sizey) = numpy.shape(training_inputs[0])
    size=int(density*sf)
    
    m = numpy.zeros((int((sizex-size)/(size*stepsize)+1),int((sizey-size)/(size*stepsize)+1)))
    print "BBBB",numpy.shape(m)
    if __main__.__dict__.get('NormalizeActivities',True):
        (a,mi,ma) = compute_average_min_max(training_set)
        training_set = normalize_data_set(training_set,a,mi,ma)
        validation_set = normalize_data_set(validation_set,a,mi,ma)
        
    for neuron in xrange(0,len(training_set[0])):
        x=0
        y=0
        while x  < (sizex-size): 
            y=0
            while y  < (sizey-size):
                tr_in = cut_out_images_set(training_inputs,size,(x,y))
                val_in = cut_out_images_set(validation_inputs,size,(x,y))
                if __main__.__dict__.get('NormalizeInputs',True):
                    avgRF = compute_average_input(tr_in)
                    tr_in = normalize_image_inputs(tr_in,avgRF)
                    val_in = normalize_image_inputs(val_in,avgRF)
                tr_in = generate_raw_training_set(tr_in)
                val_in = generate_raw_training_set(val_in)
                mf = ModelFit()
                mf.learning_rate = __main__.__dict__.get('lr',0.00001)
                mf.epochs=__main__.__dict__.get('epochs',1000)
                mf.init()
                m[x/int(size*stepsize),y/int(size*stepsize)]=          mf.trainModel(mat(tr_in),numpy.mat(training_set)[:,neuron:neuron+1],mat(val_in),numpy.mat(validation_set)[:,neuron:neuron+1])
                y+=int(size*stepsize)
            x+=int(size*stepsize)
        
        pylab.show._needmain=False
        pylab.figure()
        pylab.imshow(m)
        pylab.colorbar()
        from topo.misc.filepath import normalize_path, application_path
        pylab.savefig(normalize_path("Flogl/DataSep2009/Neuron:"+str(neuron)+"RFlocation.png"))
        numpy.save("Flogl/DataSep2009/Neuron:"+str(neuron)+"RFlocation.dat", m)

    

def runRFinference():
    density=__main__.__dict__.get('density', 20)
    #dataset = loadSimpleDataSet("Flogl/DataOct2009/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_2700images",2700,50)
    dataset = loadSimpleDataSet("Flogl/DataNov2009/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_2700images_on_&_off_response",2700,50)
    (index,data) = dataset
    index+=1
    dataset = (index,data)
    dataset = averageRangeFrames(dataset,0,1)
    dataset = averageRepetitions(dataset)
    
    (dataset,validation_data_set) = splitDataset(dataset,0.9)
    #(dataset,rubish) = splitDataset(dataset,0.25)

    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    
    if __main__.__dict__.get('NormalizeInputs',False):
       avgRF = compute_average_input(training_inputs)
       training_inputs = normalize_image_inputs(training_inputs,avgRF)
       validation_inputs = normalize_image_inputs(validation_inputs,avgRF)
    
    if __main__.__dict__.get('NormalizeActivities',True):
        (a,v) = compute_average_min_max(numpy.concatenate((training_set,validation_set),axis=0))
        training_set = normalize_data_set(training_set,a,v)
        validation_set = normalize_data_set(validation_set,a,v)
    
    if True:
        print numpy.shape(training_inputs[0])
        (x,y)= numpy.shape(training_inputs[0])
        training_inputs = cut_out_images_set(training_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))
        validation_inputs = cut_out_images_set(validation_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))
        print numpy.shape(training_inputs[0])
        (sizex,sizey) = numpy.shape(training_inputs[0])
    
    (sizex,sizey) = numpy.shape(training_inputs[0])
    training_inputs = generate_raw_training_set(training_inputs)
    validation_inputs = generate_raw_training_set(validation_inputs)


    
    #lasso_regression_rf(training_inputs,training_set,sizex,sizey,0,20,2.21,validation_inputs,validation_set,True,0.28)
    
    #return
    
    a = ridge_regression_rf(training_inputs,training_set,sizex,sizey,0,2000,0.0,validation_inputs,validation_set,True,0.28,"OnOff_spikes")    
    
    
    
    if True:
        e = []
        c = []
        b = []
        x = 0.2
        for i in xrange(0,10):
            print i
            x = 1500 + i*100  
            (e1,c1,RFs) = ridge_regression_rf(training_inputs,training_set,sizex,sizey,0,x,0.0,validation_inputs,validation_set,False,0.28)
            e.append(e1)
            c.append(c1)
            b.append(x)
            #x = x*2
        pylab.figure()
        #pylab.semilogx(b,e)
        pylab.plot(b,e)
        pylab.figure()
        #pylab.semilogx(b,c)
        pylab.plot(b,c)
        pylab.show()
    
    pylab.show()
    return a

    

def compute_spike_triggered_average_rf(inputs,activities,density):
    (num_inputs,num_activities) = shape(activities)
    RFs = [numpy.zeros(shape(inputs[0])) for j in xrange(0,num_activities)] 
    avgRF = numpy.zeros(shape(inputs[0]))
    for i in xrange(0,num_inputs):
        for j in xrange(0,num_activities):
            RFs[j] += activities[i][j]*inputs[i]

    for i in inputs:
        avgRF += i
    avgRF = avgRF/(num_inputs*1.0)
    
    activity_avg = numpy.zeros((num_activities,1))
    
    for z in xrange(0,num_activities):
        activity_avg[z] = numpy.sum(activities.T[z])
    
    activity_avg = activity_avg.T[0]
    
    pylab.figure()
    for j in xrange(0,10):
        fig = pylab.figure()
        pylab.show._needmain=False
        
        pylab.subplot(1,5,1)
        RFs[j]/= activity_avg[j]
        pylab.imshow(RFs[j],vmin=numpy.min(RFs[j]),vmax=numpy.max(RFs[j]))
        pylab.colorbar()
        
        pylab.subplot(1,5,2)
        pylab.imshow(RFs[j] - avgRF,vmin=numpy.min(RFs[j]- avgRF),vmax=numpy.max(RFs[j]- avgRF))
        pylab.colorbar()
        
        pylab.subplot(1,5,3)
        pylab.imshow(RFs[j]/avgRF,vmin=numpy.min(RFs[j]/avgRF),vmax=numpy.max(RFs[j]/avgRF))
        pylab.colorbar()

        pylab.subplot(1,5,4)
        pylab.imshow(avgRF,vmin=numpy.min(avgRF),vmax=numpy.max(avgRF))
        pylab.colorbar()
        pylab.show()
        #w = mf.weigths[j].reshape(density*1.2,density*1.2)
        #pylab.subplot(1,5,5)
        #pylab.imshow(w,vmin=numpy.min(w),vmax=numpy.max(w))
        #pylab.colorbar()                
        #

def lookForCorrelations(model, validation_activities,validation_inputs):
    modelResponses = model.calculateModelOutput(validation_inputs,0).T
    print numpy.shape(modelResponses)
    
    for index in range(1,len(validation_inputs)):
           modelResponses =  numpy.concatenate((modelResponses,model.calculateModelOutput(validation_inputs,index).T),axis=0)
    print numpy.shape(modelResponses)
    mR = numpy.matrix(modelResponses).T
    bR = numpy.matrix(validation_activities).T
    
    print numpy.shape(mR)
    print numpy.shape(bR)
    pylab.figure()
    pylab.subplot(7,8,1)
    for i in xrange(0,50):
        pylab.subplot(7,8,i+1)
        pylab.scatter(numpy.array(mR[i])[0],numpy.array(bR[i])[0])
        pylab.show._needmain=False

    pylab.figure()    
    avg = numpy.zeros(numpy.shape(numpy.array(bR[0])[0]))
    for i in xrange(0,50):        
        pylab.hold(True)
        pylab.plot(numpy.array(bR[i])[0])
        avg = avg + numpy.array(bR[i])[0]
    
    pylab.plot(avg/58.0,lw=5)
    
    pylab.show()     
    

def induce_rf_postion(num_of_cells,):
    image_filenames=["Flogl/DataSep2009/Neuron:%dRFlocation.dat.npy" %(i) for i in xrange(0,num_of_cells)]
    from topo.base.arrayutil import array_argmax
    for file in image_filenames:
        a= numpy.load(file)
        pylab.figure()
        print array_argmax(a)
        pylab.imshow(a)
    pylab.show()



def analyze_rf_possition(w,level):
    import matplotlib
    from matplotlib.patches import Circle
    a= pylab.figure().gca()
    (sx,sy) = numpy.shape(w[0])
    
    X = numpy.zeros((sx,sy))
    Y = numpy.zeros((sx,sy))
        
    for x in xrange(0,sx):
        for y in xrange(0,sy):
            X[x][y] = x
            Y[x][y] = y
    
    cgs = []
    RFs=[]
    
    for i in xrange(0,len(w)):
            pylab.subplot(7,8,i+1)
            mi=numpy.min(numpy.min(w[i]))
            ma=numpy.max(numpy.max(w[i]))
            z = ((w[i]<=(mi-mi*level))*1.0) * w[i] + ((w[i]>=(ma-ma*level))*1.0) * w[i] 
            RFs.append(z)  
            cgx = numpy.sum(numpy.sum(numpy.multiply(X,numpy.power(z,2))))/numpy.sum(numpy.sum(numpy.power(z,2)))
            cgy = numpy.sum(numpy.sum(numpy.multiply(Y,numpy.power(z,2))))/numpy.sum(numpy.sum(numpy.power(z,2)))
            
            print cgx/sx,cgy/sy
            cgs.append((cgx/sx,cgy/sy))
            r = numpy.max([numpy.abs(numpy.min(numpy.min(z))),numpy.abs(numpy.max(numpy.max(z)))])
            cir = Circle( (cgy,cgx), radius=1)
            pylab.gca().add_patch(cir)
            
            pylab.show._needmain=False
            pylab.imshow(z,vmin=-r,vmax=r,cmap=pylab.cm.RdBu)
    pylab.show()
    return (cgs,RFs)


def fitGabor(weights):
    from matplotlib.patches import Circle
    from scipy.optimize import leastsq,fmin,fmin_tnc,anneal
    from topo.base.arrayutil import array_argmax
    
    (x,y) = numpy.shape(weights[0])
    weights  = cut_out_images_set(weights,int(y*0.49),(int(x*0.1),int(y*0.4)))
    (denx,deny) = numpy.shape(weights[0])
    centers,RFs = analyze_rf_possition(weights,0.4)
    
    # determine frequency
    
    freqor = []
    for w in RFs:
        ff = pylab.fftshift(pylab.fft2(w))
        (x,y) = array_argmax(numpy.abs(ff))
        (n,rubish) = shape(ff)
        print x,y,n
        freq = numpy.sqrt((x - n/2)*(x - n/2) + (y - n/2)*(y - n/2))
        phase = numpy.arctan(ff[x,y].imag/ff[x,y].real)
        
        if (x - n/2) != 0:
            print (y - n/2)/(x - n/2)
            
            orr = numpy.arctan((y - n/2)/(x - n/2))
        else:
            orr = numpy.pi/2
        
        if phase < 0:
           phase = phase+numpy.pi
        if orr < 0:
           orr = orr+numpy.pi
        print orr    
            
        freqor.append((freq,orr,phase))
    
    parameters=[]
    
    for j in xrange(0,len(RFs)):
        minf = numpy.max([freqor[j][0]-2,0])
        (x,b,c) = fmin_tnc(gab,[centers[j][0],centers[j][1],0.10,freqor[j][1],freqor[j][0],freqor[j][2],0.1],bounds=[(centers[j][0]*0.9,centers[j][0]*1.1),(centers[j][0]*0.9,centers[j][0]*1.1),(0.01,0.2),(0.0,numpy.pi),(minf,freqor[j][0]+2),(0.0,numpy.pi/2),(0.1,1.0)],args=[weights[j]], xtol=0.0000000001,scale=[0.5,0.5,0.5,2.0,0.5,2.0,0.5],maxCGit=1000, ftol=0.0000000001,approx_grad=True,maxfun=100000,eta=0.01)
        parameters.append(x)
    
    pylab.figure()
    for i in xrange(0,len(parameters)):
            pylab.subplot(7,8,i+1)
            (x,y,sigma,angle,f,p,alpha) = tuple(parameters[i])
            
            g = Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=y-0.5,y=0.5-x,xdensity=denx,ydensity=deny,size=sigma,orientation=angle,phase=p)() * alpha
            m = numpy.max([-numpy.min(g),numpy.max(g)])
            pylab.show._needmain=False
            pylab.imshow(g,vmin=-m,vmax=m,cmap=pylab.cm.RdBu)
    
    
    
    analyze_rf_possition(weights,1.0)
    pylab.show()
    return parameters
    
    
def gab(z,w,display=False):
    from matplotlib.patches import Circle
    print z
    (x,y,sigma,angle,f,p,alpha) = tuple(z)
    
    a = numpy.zeros(numpy.shape(w))
    (dx,dy) = numpy.shape(w)
    den = numpy.max([dx,dy])
    
    g =  Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=y-0.5,y=0.5-x,xdensity=den,ydensity=den,size=sigma,orientation=angle,phase=p)() * alpha
    
    if display:
        pylab.subplot(2,1,1)
        
        m = numpy.max([-numpy.min(g[0:dx,0:dy]),numpy.max(g[0:dx,0:dy])])
        cir = Circle( (y*dy,x*dx), radius=1)
        pylab.gca().add_patch(cir)
        pylab.imshow(g[0:dx,0:dy],vmin=-m,vmax=m,cmap=pylab.cm.RdBu)
        pylab.colorbar()
        pylab.subplot(2,1,2)
        m = numpy.max([-numpy.min(w),numpy.max(w)])
        cir = Circle( (y*dy,x*dx), radius=1)
        pylab.gca().add_patch(cir)
        pylab.imshow(w,vmin=-m,vmax=m,cmap=pylab.cm.RdBu)
        pylab.show._needmain=False
        pylab.colorbar()
        pylab.show()

    #print numpy.sum(numpy.power(g[0:dx,0:dy] - w,2))
    
    return numpy.sum(numpy.power(g[0:dx,0:dy] - w,2)) 


def runSTC():
    density=__main__.__dict__.get('density', 20)
    dataset = loadSimpleDataSet("Flogl/DataNov2009/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_2700images_on_&_off_response",2700,50)
    (index,data) = dataset
    index+=1
    dataset = (index,data)
    dataset = averageRangeFrames(dataset,0,1)
    dataset = averageRepetitions(dataset)
    dataset = clump_low_responses(dataset,__main__.__dict__.get('ClumpMag',0.1))
    
    
    (dataset,validation_data_set) = splitDataset(dataset,0.99)

    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"/afs/inf.ed.ac.uk/user/s05/s0570140/workspace/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    
    if __main__.__dict__.get('NormalizeInputs',False):
       avgRF = compute_average_input(training_inputs)
       training_inputs = normalize_image_inputs(training_inputs,avgRF)
       validation_inputs = normalize_image_inputs(validation_inputs,avgRF)
    
    if __main__.__dict__.get('NormalizeActivities',True):
        (a,v) = compute_average_min_max(numpy.concatenate((training_set,validation_set),axis=0))
        training_set = normalize_data_set(training_set,a,v)
        validation_set = normalize_data_set(validation_set,a,v)
    
    if True:
        print numpy.shape(training_inputs[0])
        (x,y)= numpy.shape(training_inputs[0])
        training_inputs = cut_out_images_set(training_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))
        validation_inputs = cut_out_images_set(validation_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))
        print numpy.shape(training_inputs[0])
        (sizex,sizey) = numpy.shape(training_inputs[0])
    
    (sizex,sizey) = numpy.shape(training_inputs[0])
    training_inputs = generate_raw_training_set(training_inputs)
    validation_inputs = generate_raw_training_set(validation_inputs)
    
    a = STC(training_inputs,training_set,validation_inputs,validation_set)

    pylab.subplot(10,10,1)
    j=0
    
    m = []    
    for (ei,vv) in a:
        ind = numpy.argsort(numpy.abs(vv))
        w = numpy.array(ei[ind[len(ind)-1],:].real)
        m.append(numpy.max([-numpy.min(w),numpy.max(w)]))
    
    m = numpy.max(m)
        
    for (ei,vv) in a:
        ind = numpy.argsort(numpy.abs(vv))
        
        pylab.subplot(10,10,j+1) 
        w = numpy.array(ei[ind[len(ind)-1],:].real).reshape(38,38)
        m = numpy.max([-numpy.min(w),numpy.max(w)])
        pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
        
        pylab.subplot(10,10,j+2)
        w = numpy.array(ei[ind[len(ind)-2],:].real).reshape(38,38)
        m = numpy.max([-numpy.min(w),numpy.max(w)])
        pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
        j = j+2
        
    pylab.show()
    return a

def STC(inputs,activities,validation_inputs,validation_activities,cutoff=95,display=False):
    from scipy import linalg
    print "input size:",numpy.shape(inputs)
    
    (num_in,input_len) = numpy.shape(inputs)
    (num_in,act_len) = numpy.shape(activities)
    
    for i in xrange(0,num_in):
        inputs[i]-=1.0
    
    CC = numpy.mat(numpy.zeros((input_len,input_len)))
    U  = numpy.mat(numpy.zeros((input_len,input_len)))
    N  = numpy.mat(numpy.zeros((input_len,input_len)))
       
    for i in xrange(0,num_in):
            CC = CC + numpy.mat(inputs[i,:]).T * numpy.mat(inputs[i,:]) 
    CC = CC / num_in
    
    v,la = linalg.eig(CC)
    la = numpy.mat(la)
    ind = numpy.argsort(numpy.abs(v))
    for j in xrange(0,input_len*cutoff/100):
        v[ind[j]]=1.0
    
    for i in xrange(0,input_len):
        N[i,i] = 1/numpy.sqrt(v[i])
        
    U = la * N
    SW = numpy.matrix(inputs) * U
    
    act_len=50
    C= []
    for a in xrange(0,act_len):
        C.append(numpy.zeros((input_len,input_len)))
   
    for i in xrange(0,num_in):
        for j in xrange(0,act_len):
            C[j] += (numpy.mat(SW[i,:]).T * numpy.mat(SW[i,:])) * activities[i,j] 
    
    for j in xrange(0,act_len):
        C[j] = C[j] / num_in

    pylab.figure()
    pylab.imshow(C[0])

    eis = []
    for j in xrange(0,act_len):
        vv,ei = linalg.eig(C[j])
        ei=numpy.mat(ei).T
        ei = ei*N*linalg.inv(la)
        eis.append((ei,vv))
    
    return eis
