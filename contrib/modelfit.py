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
        return self.weigths*inputs[index].T+self.DC

    def trainModel(self,inputs,activities,validation_inputs,validation_activities):
        delta=[]
        self.DC=numpy.array(activities[0]).copy()*0.0
        print self.DC

        self.weigths=numpy.mat(numpy.zeros((size(activities,1),size(inputs[0],1))))

        mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
        first_val_error=0
        val_err=0

        for k in xrange(0,self.epochs):
            mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            validation_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            tmp_weigths=numpy.mat(numpy.zeros((size(activities,1),size(inputs[0],1))))
            for i in xrange(0,len(inputs)):
                error = ((activities[i].T - self.weigths*inputs[i].T - self.DC.T))
                
                tmp_weigths = tmp_weigths + (error * inputs[i])
                mean_error=mean_error+numpy.power(error,2)
            
            for i in xrange(0,len(validation_inputs)):
                error = ((validation_activities[i].T - self.weigths*validation_inputs[i].T - self.DC.T))
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

            print (k,err,val_err)
        print "First val error:" + str(first_val_error) + "\nLast val error:" + str(val_err) + "\nImprovement:" + str((first_val_error - val_err)/first_val_error * 100) + "%"
        
        # recalculate a new model DC based on what we have learned
        self.DC*=0.0
         
        for i in xrange(0,len(validation_inputs)):
            self.DC+=(validation_activities[i].T - self.weigths*validation_inputs[i].T).T
        self.DC = self.DC/len(validation_inputs)   
    
    def calculateReliabilities(self,inputs,activities,top_percentage):
        corr_coef=numpy.zeros(self.num_of_units)
        modelResponses=[]
        modelActivities=[]
            
        for i in xrange(0,len(inputs)):
           a = inputs[i]
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
                
                 tmp.append(numpy.sum(numpy.power(
                                     numpy.multiply(activities[i].T  - modelActivities[j],numpy.mat(self.reliable_indecies).T),2)
                                    ))
                 #tmp.append(numpy.corrcoef(modelActivities[j].T, activities[i])[0][1])
            x = numpy.argmin(array(tmp))

            #x = numpy.argmax(array(tmp))
            x = target_inputs[x]
            print (x,i)
            
            if (i % 30) ==1:
                pylab.show._needmain=False
                pylab.figure()
                pylab.subplot(3,1,1)
                pylab.plot(numpy.array(activities[i])[0],'o',label='traget')
                pylab.plot(numpy.array(modelActivities[x].T)[0], 'o',label='predicted model')
                pylab.plot(numpy.array(modelActivities[i].T)[0], 'o',label='correct model')
                pylab.legend()
                pylab.show()

            if x == i:
                 correct+=1.0
                
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

class BasicModelFit(ModelFit):
      def init(self):
          self.reliable_indecies = ones(self.num_of_units)
      
class BasicBPModelFit(BasicModelFit):
 
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

def generateInputs(dataset,directory,image_matching_string,density,aspect):
    (index,data) = dataset

    # ALERT ALERT ALERT We do not handle repetitions yet!!!!!
    
    image_filenames=[directory+image_matching_string %(i) for i in index]
    inputs=[Image(filename=f,size=0.55, x=0,y=0)   for f in image_filenames]
    
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
            for p in xrange(0,num_phase):
                g = Gabor(bounds=BoundingBox(radius=0.5),frequency=1.0,x=0.0,y=0.0,xdensity=size/freq,ydensity=size/freq,size=0.3,orientation=numpy.pi/8*orient,phase=p*2*numpy.pi/num_phase)
                filters.append(g())

    return filters

    

def apply_filters(inputs, filters, spacing):
    (sizex,sizey) = numpy.shape(inputs[0])
    out = []
    for i in inputs:
        o  = []
        for f in filters:
            (s,tresh) = numpy.shape(f)
            step = int(s*spacing)
            x=0
            y=0
            while (x*step + s) < sizex:
                while (y*step + s) < sizey:
                    o.append(numpy.sum(numpy.sum(numpy.multiply(f,i[x*step:x*step+s,y*step:y*step+s]))))
                    y+=1 
                x+=1
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
    for d in data_set:
        avg += d
    avg = avg/(len(data_set)*1.0)
    
    mins = numpy.min(data_set,axis=0)
    maxs = numpy.max(data_set,axis=0)
    print shape(mins)
    print shape(data_set)
    return (avg,mins,maxs)
    
def normalize_data_set(data_set,avg,mins,maxs):
    a = numpy.max([mins,maxs],axis=0)
    print shape(a)
    for i in xrange(0,len(data_set)):
        data_set[i]-=avg
        data_set[i]=numpy.divide(data_set[i],a) 
    return data_set



def runModelFit():
   
    density=__main__.__dict__.get('density', 200)
    
    #dataset = loadRandomizedDataSet("Flogl/JAN1/20090707__retinotopy_region1_stationary_testing01_1rep_125stim_ALL",6,15,125,60)
    dataset = loadSimpleDataSet("Flogl/DataSep2009/testing_01_02_03.dat",375,58)

    #this dataset has images numbered from 1
    (index,data) = dataset
    index+=1
    dataset=(index,data)
     
    #print shape(dataset[1])
    #dataset = clump_low_responses(dataset,__main__.__dict__.get('ClumpMag',0.1))
    print shape(dataset[1])
    dataset = averageRangeFrames(dataset,0,1)
    print shape(dataset[1])
    dataset = averageRepetitions(dataset)
    print shape(dataset[1])
    
    (dataset,validation_data_set) = splitDataset(dataset,0.9)
    (dataset,testing_data_set) = splitDataset(dataset,0.9)

    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"Flogl/DataSep2009","/testing_01_02_03/testing01_02_030%03d.tif",density,1.8)
    
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"Flogl/DataSep2009","/testing_01_02_03/testing01_02_030%03d.tif",density,1.8)
    
    testing_set = generateTrainingSet(testing_data_set)
    testing_inputs=generateInputs(testing_data_set,"Flogl/DataSep2009","/testing_01_02_03/testing01_02_030%03d.tif",density,1.8)
    
    #print numpy.shape(training_inputs[0])
    #compute_spike_triggered_average_rf(training_inputs,training_set,density)
    #pylab.figure()
    #pylab.imshow(training_inputs[0])
    #pylab.show()
    #return

    
    if __main__.__dict__.get('Gabor',True):
        
        fil = generate_pyramid_model(__main__.__dict__.get('num_or',4),__main__.__dict__.get('freq',[2,4,8]),__main__.__dict__.get('num_phase',4),numpy.min(numpy.shape(training_inputs[0])))
        training_inputs = apply_filters(training_inputs, fil, __main__.__dict__.get('spacing',0.5))
        testing_inputs = apply_filters(testing_inputs, fil, __main__.__dict__.get('spacing',0.5))
        validation_inputs = apply_filters(validation_inputs, fil, __main__.__dict__.get('spacing',0.5))
    
    if __main__.__dict__.get('NormalizeActivities',True):
        (a,mi,ma) = compute_average_min_max(training_set)
        training_set = normalize_data_set(training_set,a,mi,ma)
        validation_set = normalize_data_set(validation_set,a,mi,ma)
        testing_set = normalize_data_set(testing_set,a,mi,ma)
    
    print shape(training_set)
    print shape(training_inputs)
    
    
    #mf = BasicBPModelFit()
    #mf = BasicModelFit()
    mf = ModelFit()
    mf.retina_diameter = 1.2
    mf.density = density
    mf.learning_rate = __main__.__dict__.get('lr',0.001)
    mf.epochs=__main__.__dict__.get('epochs',273)
    mf.num_of_units = 58
    mf.init()

    mf.trainModel(mat(training_inputs),numpy.mat(training_set),mat(validation_inputs),numpy.mat(validation_set))
    mf.testModel(mat(training_inputs),numpy.mat(training_set))
    mf.testModel(mat(validation_inputs),numpy.mat(validation_set))
    mf.testModel(mat(testing_inputs),numpy.mat(testing_set))
    
    mf.calculateReliabilities(validation_inputs,numpy.mat(validation_set),20)
    mf.testModel(testing_inputs,numpy.mat(testing_set))
    
    mf.calculateReliabilities(validation_inputs,numpy.mat(validation_set),5)
    mf.testModel(testing_inputs,numpy.mat(testing_set))
    
    mf.calculateReliabilities(validation_inputs,numpy.mat(validation_set),1)
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
