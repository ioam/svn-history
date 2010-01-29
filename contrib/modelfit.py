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

from topo.sheet import GeneratorSheet 
from topo.base.boundingregion import BoundingBox
from topo.pattern.image import FileImage
import contrib.jacommands
from topo.misc.filepath import normalize_path, application_path
from topo.misc.numbergenerator import UniformRandom, BoundedNumber, ExponentialDecay
import contrib.dd

from helper import *

#dd = contrib.dd.DB()
#dd.load_db("modelfitDB.dat")


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

        #self.weigths=numpy.mat(numpy.zeros((size(activities,1),size(inputs[0],1))))
	self.weigths=numpy.mat(numpy.identity(size(inputs[0],1)))
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
	
        val_pve = []
	
	validation_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
	variance=numpy.mat(numpy.zeros(shape(activities[0].T)))
	for i in xrange(0,len(validation_inputs)):
                error = ((validation_activities[i].T - self.weigths*validation_inputs[i].T - self.DC.T))
                validation_error=validation_error+numpy.power(error,2)
		variance = variance + numpy.power((validation_activities[i] - numpy.mean(validation_activities,axis=0)),2).T
		
	print "INITIAL VALIDATION ERROR", numpy.sum(validation_error)/len(validation_inputs)/len(validation_error)
	print "INITIAL FEV on validation set", numpy.mean(1.0-numpy.divide(validation_error,variance))   
        
        for k in xrange(0,self.epochs):
            
            stop_learning = (stop>k)*1.0
            sl = numpy.mat(stop_learning).T
            for i in xrange(1, size(inputs[0],1)):
                sl = numpy.concatenate((sl,numpy.mat(stop_learning).T),axis=1)
            
            mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            validation_error=numpy.mat(numpy.zeros((len(activities[0].T),1)))
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
                if min_val_err_array[i] > validation_error[i,0]:
                   min_val_err_array[i] = validation_error[i,0]
                   #!!!!!!!!!!!!!
                   best_weights[i,:] = self.weigths[i,:]
                
            if k == 0:
               first_val_error=val_err
               first_val_err_array = min_val_err_array.copy()

            print (k,err,val_err)
        print "First val error:" + str(first_val_error) + "\n Minimum val error:" + str(min_val_err) +        "\n Last val error:" + str(val_err) + "\nImprovement:" + str((first_val_error - min_val_err)/first_val_error * 100) + "%" #+ "\nBest cell by cell error:" + str(numpy.sum(min_val_err_array)/len(min_val_err_array)/len(validation_inputs)) + "\nBest cell by cell error improvement:" + str((first_val_err_array - min_val_err_array)/len(validation_inputs)/first_val_err_array)

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
        #for i in xrange(0,len(validation_inputs)):
        #    self.DC+=(validation_activities[i].T - self.weigths*validation_inputs[i].T).T
        #self.DC = self.DC/len(validation_inputs)   
        
	#!!!!!!!!!
	validation_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
	variance=numpy.mat(numpy.zeros(shape(activities[0].T)))
	for i in xrange(0,len(validation_inputs)):
                error = ((validation_activities[i].T - self.weigths*validation_inputs[i].T - self.DC.T))
                validation_error=validation_error+numpy.power(error,2)
		variance = variance + numpy.power((validation_activities[i].T - numpy.mean(validation_activities,axis=0).T),2) 
	
	print "FINAL VALIDATION ERROR", numpy.sum(validation_error)/len(validation_inputs)/len(validation_error)
	print "FINAL FEV on validation set", numpy.mean(1-numpy.divide(validation_error,variance))   
	
        return (min_val_err,numpy.argmin(b.T,axis=0),min_val_err_array/len(validation_inputs))
    
    def returnPredictedActivities(self,inputs):
        for i in xrange(0,len(inputs)):
           if i == 0: 
               modelActivities = self.calculateModelOutput(inputs,i)
           else:
               a = self.calculateModelOutput(inputs,i)
               modelActivities = numpy.concatenate((modelActivities,a),axis=1)
           
        return numpy.mat(modelActivities).T
        
    
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

        m = numpy.array(numpy.mean(activities,0))[0]
        
        tmp = []
        correct = 0
        for i in xrange(0,num_inputs):
            tmp = []
            significant_neurons=numpy.zeros(numpy.shape(activities[0]))       
            for z in xrange(0,act_len):
                if activities[i,z] >= m[z]*t: significant_neurons[0,z]=1.0
            
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
              
            
def loadSimpleDataSet(filename,num_stimuli,n_cells,num_rep=1,transpose=False):
    f = file(filename, "r") 
    data = [line.split() for line in f]
    
    if transpose:
       data = numpy.array(data).transpose()	    
    
    f.close()
    print "Dataset shape:", shape(data)

    dataset = [([[] for i in xrange(0,num_stimuli)]) for j in xrange(0,n_cells)]
    print shape(dataset)
    
    
    for k in xrange(0,n_cells):
        for i in xrange(0,num_stimuli):
	    for rep in xrange(0,num_rep):
		f = []
            	for fr in xrange(0,1):
                       f.append(float(data[num_stimuli*rep+i][k]))
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

def mergeDatasets(dataset1,dataset2):
    print "Warning: Indexes must match"
    (index,data1) = dataset1
    (index,data2) = dataset2		
    for cell in data2:
	data1.append(cell)
    return (index,data1)
 
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

    print reps
    
    for cell in data:
        for stimulus in xrange(0,num_stim):
            r = [0 for i in range(0,num_frames)]
            for rep in reps:
                for f in xrange(0,num_frames):
                    r[f]+=cell[stimulus][rep][f]/(len(reps)*1.0)
            cell[stimulus]=[r]
    return (index,data)

def analyse_reliability(dataset,params):
    (index,data) = dataset
    (num_cells,num_stim,num_rep,num_frames) = shape(data)	
    
    c = []

    for cell in data:
	fano_factors=[]    
	for stimuli in cell:
	    z = [] 	
	    for rep in stimuli:
		z.append(numpy.mean(rep))
	    z=numpy.array(z)
	    fano_factors.append(numpy.array(z).var()/numpy.mean(z))
	c.append(numpy.mean(fano_factors))
    
    #dd.add(params,"FanoFactors",c)
    	
    pylab.figure()
    pylab.hist(c)
    return c

def splitDataset(dataset,ratio):
    (index,data) = dataset
    (num_cells,num_stim,trash1,trash2) = shape(data)

    dataset1=[]
    dataset2=[]
    index1=[]
    index2=[]

    if ratio<=1.0:
    	tresh = num_stim*ratio
    else:
	tresh = ratio

    for i in xrange(0,num_stim):
        if i < numpy.floor(tresh):
            index1.append(index[i])
        else:    
            index2.append(index[i])
    
    for cell in data:
        d1=[]
        d2=[]
        for i in xrange(0,num_stim):
            if i < numpy.floor(tresh):
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
        inputs[j].pattern_sampler.whole_pattern_output_fns=[]
        inp = inputs[j](xdensity=density,ydensity=density) /255.0
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
        inputs[i]=inputs[i]-avgRF

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
    training_inputs=generateInputs(dataset,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    
    validation_set = generateTrainingSet(validation_data_set)
    validation_inputs=generateInputs(validation_data_set,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    
    testing_set = generateTrainingSet(testing_data_set)
    testing_inputs=generateInputs(testing_data_set,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",density,1.8,offset=1000)
    

    
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
    
    #mf.retina_diameter = 1.2
    mf = ModelFit()
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
    

def regulerized_inverse_rf(inputs,activities,sizex,sizey,alpha,validation_inputs,validation_activities,dd,display=False):
    p = len(inputs[0])
    np = len(activities[0])
    inputs = numpy.mat(inputs)
    activities = numpy.mat(activities)
    validation_inputs = numpy.mat(validation_inputs)
    validation_activities = numpy.mat(validation_activities)
    S = numpy.mat(inputs).copy()
    
    for x in xrange(0,sizex):
        for y in xrange(0,sizey):
            norm = numpy.mat(numpy.zeros((sizex,sizey)))
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
	    
    activities_padded = numpy.concatenate((activities,numpy.mat(numpy.zeros((sizey*sizex,np)))),axis=0)
    Z = numpy.linalg.pinv(S)*activities_padded
    Z=Z.T
    ma = numpy.max(numpy.max(Z))
    mi = numpy.min(numpy.min(Z))
    m = max([abs(ma),abs(mi)])
    RFs=[]
    of = run_nonlinearity_detection(activities,inputs*Z.T,10,display)
     
    predicted_activities = inputs*Z.T
    validation_predicted_activities = validation_inputs*Z.T
    
    tf_predicted_activities = apply_output_function(predicted_activities,of)
    tf_validation_predicted_activities = apply_output_function(validation_predicted_activities,of)
    
    print numpy.shape(validation_activities)
    print numpy.shape(validation_predicted_activities)
    
    errors = numpy.sum(numpy.power(validation_activities - validation_predicted_activities,2),axis=0)
    tf_errors = numpy.sum(numpy.power(validation_activities - tf_validation_predicted_activities,2),axis=0)
    
    
    mean_mat = numpy.array(numpy.mean(validation_activities,axis=1).T)[0]
    
    
    corr_coef=[]
    corr_coef_tf=[]
    for i in xrange(0,np):
            corr_coef.append(numpy.corrcoef(validation_activities[:,i].T, validation_predicted_activities[:,i].T)[0][1])
	    corr_coef_tf.append(numpy.corrcoef(validation_activities[:,i].T, tf_validation_predicted_activities[:,i].T)[0][1])
    
    
    print numpy.shape(array([mean_mat,]*np))
    print numpy.shape(validation_activities)
    
    act_var = numpy.sum(numpy.power(validation_activities-array([mean_mat,]*np).T,2),axis=0)
    normalized_errors = 1-numpy.array(errors / act_var)[0]
    tf_normalized_errors = 1-numpy.array(tf_errors / act_var)[0]
    error = numpy.mean(errors)
    normalized_error = numpy.mean(normalized_errors)


    for i in xrange(0,np):
        RFs.append(numpy.array(Z[i]).reshape(sizex,sizey))
	    
    if display:
        av=[]
        pylab.figure()
        pylab.title(str(alpha), fontsize=16)
        for i in xrange(0,np):
            av.append(numpy.sqrt(numpy.sum(numpy.power(Z[i],2))))
            pylab.subplot(10,11,i+1)
            w = numpy.array(Z[i]).reshape(sizex,sizey)
            pylab.show._needmain=False
            pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
	    pylab.axis('off')
            
        pylab.figure()
        pylab.title("relationship", fontsize=16)    
        for i in xrange(0,np):
            pylab.subplot(10,11,i+1)
            pylab.plot(validation_predicted_activities.T[i],validation_activities.T[i],'ro')
            
        pylab.figure()
        pylab.title("relationship_tf", fontsize=16)    
        for i in xrange(0,np):
            pylab.subplot(10,11,i+1)
            pylab.plot(numpy.mat(tf_validation_predicted_activities).T[i],validation_activities.T[i],'ro')
        
	pylab.figure()
        pylab.hist(av)
        pylab.xlabel("rf_magnitued")
        
        pylab.figure()
        print shape(av)
        print shape(normalized_errors)
        pylab.plot(av,normalized_errors,'ro')
        pylab.xlabel("rf_magnitued")
        pylab.ylabel("normalized error")
        
        pylab.figure()
        pylab.plot(av,tf_normalized_errors,'ro')
        pylab.xlabel("rf_magnitued")
        pylab.ylabel("tf_normalized error")
        
        pylab.figure()
        pylab.title(str(alpha), fontsize=16)
        for i in xrange(0,np):
            pylab.subplot(10,11,i+1)
            w = numpy.array(Z[i]).reshape(sizex,sizey)
            pylab.show._needmain=False
            m = numpy.max([abs(numpy.min(numpy.min(w))),abs(numpy.max(numpy.max(w)))])
            pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
            pylab.axis('off')
    
        pylab.figure()
        pylab.hist(normalized_errors)
        pylab.xlabel("normalized_errors")
        
        pylab.figure()
        pylab.hist(tf_normalized_errors)
        pylab.xlabel("tf_normalized_errors")
    
        pylab.figure()
        pylab.hist(corr_coef)
        pylab.xlabel("Correlation coefficient")
	
	pylab.figure()
        pylab.hist(corr_coef_tf)
        pylab.xlabel("Correlation coefficient with transfer function")
    
    
    # prediction
    
    correct=0
    for i in xrange(0,len(validation_inputs)):
        tmp = []
        for j in xrange(0,len(validation_inputs)):
            tmp.append(numpy.sqrt(numpy.sum(numpy.power(validation_activities[i]-validation_predicted_activities[j],2))))
        x = numpy.argmin(tmp)
        if (x == i): correct+=1
         
    tf_correct=0
    for i in xrange(0,len(validation_inputs)):
        tmp = []
        for j in xrange(0,len(validation_inputs)):
            tmp.append(numpy.sqrt(numpy.sum(numpy.power(validation_activities[i]-tf_validation_predicted_activities[j],2))))
        x = numpy.argmin(tmp)
        if (x == i): tf_correct+=1
    
    
    #saving section
    dd.add_data("ReversCorrelationRFs",RFs,force=True)
    dd.add_data("ReversCorrelationCorrectPercentage",correct*1.0 / len(validation_inputs)* 100,force=True)
    dd.add_data("ReversCorrelationTFCorrectPercentage",tf_correct*1.0 / len(validation_inputs) *100,force=True)
    dd.add_data("ReversCorrelationPredictedActivities",predicted_activities,force=True)
    dd.add_data("ReversCorrelationPredictedActivities+TF",tf_predicted_activities,force=True)
    dd.add_data("ReversCorrelationPredictedValidationActivities",validation_predicted_activities,force=True)
    dd.add_data("ReversCorrelationPredictedValidationActivities+TF",tf_validation_predicted_activities,force=True)
    dd.add_data("ReversCorrelationNormalizedErrors",normalized_errors,force=True)
    dd.add_data("ReversCorrelationNormalizedErrors+TF",tf_normalized_errors,force=True)
    dd.add_data("ReversCorrelationCorrCoefs",corr_coef,force=True)
    dd.add_data("ReversCorrelationCorrCoefs+TF",corr_coef_tf,force=True)
    dd.add_data("ReversCorrelationTransferFunction",of,force=True)
    dd.add_data("ReversCorrelationRFMagnitude",av,force=True)
    
    print "Correct:", correct ," out of ", len(validation_inputs), " percentage:", correct*1.0 / len(validation_inputs)* 100 ,"%"
    print "TFCorrect:", tf_correct, " out of ", len(validation_inputs), " percentage:", tf_correct*1.0 / len(validation_inputs) *100 ,"%"
    print "Normalized_error:", normalized_error
    return (normalized_errors,tf_normalized_errors,correct,tf_correct,RFs,predicted_activities,validation_predicted_activities,corr_coef,corr_coef_tf) 

def run_nonlinearity_detection(activities,predicted_activities,num_bins=20,display=False):
            (num_act,num_neurons) = numpy.shape(activities)
            
            os = []
            if display:
               pylab.figure()
            for i in xrange(0,num_neurons):
                min_pact = numpy.min(predicted_activities[:,i])
                max_pact = numpy.max(predicted_activities[:,i])
                bins = numpy.arange(0,num_bins+1,1)/(num_bins*1.0)*(max_pact-min_pact) + min_pact
                bins[-1]+=0.000001
                ps = numpy.zeros(num_bins)
                pss = numpy.zeros(num_bins)
                    
                for j in xrange(0,num_act):
                    bin = numpy.nonzero(bins>=predicted_activities[j,i])[0][0]-1
                    ps[bin]+=1
                    pss[bin]+=activities[j,i] 
                
		idx = numpy.nonzero(ps==0)
                ps[idx]=1.0
                tf = pss/ps
                tf[idx]=0.0
                
                if display:
                   pylab.subplot(13,13,i+1)
                   pylab.plot(bins[0:-1],ps)
                   pylab.plot(bins[0:-1],pss)
                   pylab.plot(bins[0:-1],tf*1000)
                
                os.append((bins,tf))
            return os

def apply_output_function(activities,of):
    (x,y) = numpy.shape(activities)
    acts = numpy.zeros(numpy.shape(activities))
    for i in xrange(0,x):
        for j in xrange(0,y):
            (bins,tf) = of[j]
            
            if activities[i,j] >= numpy.max(bins):
                acts[i,j] = tf[-1]
            elif activities[i,j] <= numpy.min(bins):
                 acts[i,j] = tf[0]
            else:
                bin = numpy.nonzero(bins>=activities[i,j])[0][0]-1
                # do linear interpolation
                a = bins[bin]
                b = bins[bin+1]
                alpha = (activities[i,j]-a)/(b-a)
                
                if bin!=0:
                   c = (tf[bin]+tf[bin-1])/2
                else:
                   c = tf[bin]
                
                if bin!=len(tf)-1:
                   d = (tf[bin]+tf[bin+1])/2
                else:
                   d = tf[bin]
                
                acts[i,j] = c + (d-c)* alpha
    
    return acts

def fit_sigmoids_to_of(activities,predicted_activities,display=True):
	
    (num_in,num_ne) = numpy.shape(activities)	
    from scipy import optimize 	
    pylab.figure()

    fitfunc = lambda p, x: p[2] + p[3] * 1 / (1 + numpy.exp(-p[0]*(x-p[1]))) # Target function
    errfunc = lambda p,x, y: numpy.mean(numpy.power(fitfunc(p, x) - y,2)) # Distance to the target function
    
    params=[]
    for i in xrange(0,num_ne):
    	p0 = [3.0,0.5,-0.4,2.0] # Initial guess for the parameters
	(p,success,c)=optimize.fmin_tnc(errfunc,p0[:],bounds=[(-20,20),(-1,1),(-10,10),(-10,10)],args=(numpy.array(predicted_activities[:,i].T)[0],numpy.array(activities[:,i].T)[0]),approx_grad=True,messages=0)
        params.append(p)
	if display:
		pylab.subplot(13,13,i+1)
	        pylab.plot(numpy.array(predicted_activities[:,i].T)[0],numpy.array(activities[:,i].T)[0],'go')
        	pylab.plot(numpy.array(predicted_activities[:,i].T)[0],fitfunc(p,numpy.array(predicted_activities[:,i].T)[0]),'bo')

    return params
    
def apply_sigmoid_output_function(activities,of):
    sig = lambda p, x: p[2] + p[3] * 1 / (1 + numpy.exp(-p[0]*(x-p[1]))) # Target function
    (x,y) = numpy.shape(activities)	
    new_acts = numpy.zeros((x,y))
    
    for i in xrange(0,y):
	new_acts[:,i] = sig(of[i],numpy.array(activities[:,i].T)[0]).T
    return new_acts

def later_interaction_prediction(activities,predicted_activities,validation_activities,validation_predicted_activities,display=True):
    
    (num_pres,num_neurons) = numpy.shape(activities)
    
    cor_orig = numpy.zeros((num_neurons,num_neurons))
    cor = numpy.zeros((num_neurons,num_neurons))
    
    residues = activities - predicted_activities
    
    for i in xrange(0,num_neurons):
        for j in xrange(0,num_neurons):
            cor[i,j] = numpy.corrcoef(numpy.array(residues[:,i].T),numpy.array(residues[:,j].T))[0][1]
    
    pylab.figure()
    pylab.imshow(cor,vmin=-0.1,vmax=0.5,interpolation='nearest')
    pylab.colorbar()
    
    for i in xrange(0,num_neurons):
        for j in xrange(0,num_neurons):
            cor_orig[i,j] = numpy.corrcoef(numpy.array(activities[:,i].T),numpy.array(activities[:,j].T))[0][1]
    
    pylab.figure()
    pylab.imshow(cor_orig,vmin=-0.1,vmax=0.5,interpolation='nearest')
    pylab.colorbar()
    
    
    mf = ModelFit()
    mf.learning_rate = __main__.__dict__.get('lr',0.01)
    mf.epochs=__main__.__dict__.get('epochs',100)
    mf.num_of_units = num_neurons
    mf.init()
    
    (err,stop,min_errors) = mf.trainModel(mat(predicted_activities[0:num_pres*0.9]),numpy.mat(activities[0:num_pres*0.9]),mat(predicted_activities[num_pres*0.9:-1]),numpy.mat(activities[num_pres*0.9:-1]))
    print "\nStop criterions", stop
    print "Model test with all neurons"
    mf.testModel(mat(validation_predicted_activities),numpy.mat(validation_activities))
    mf.testModelBiased(mat(validation_predicted_activities),numpy.mat(validation_activities),1.0)
    mf.testModelBiased(mat(validation_predicted_activities),numpy.mat(validation_activities),1.1)
    mf.testModelBiased(mat(validation_predicted_activities),numpy.mat(validation_activities),1.2)
    mf.testModelBiased(mat(validation_predicted_activities),numpy.mat(validation_activities),1.5)
    mf.testModelBiased(mat(validation_predicted_activities),numpy.mat(validation_activities),2.0)
    
    model_predicted_activities = mf.returnPredictedActivities(mat(predicted_activities))
    model_validation_predicted_activities = mf.returnPredictedActivities(mat(validation_predicted_activities))
    
    if display:
	pylab.figure()
	print "Weight shape",numpy.shape(mf.weigths)
    	pylab.imshow(numpy.array(mf.weigths),vmin=-1.0,vmax=1.0,interpolation='nearest')
	pylab.colorbar()
    
        pylab.figure()
        pylab.title("model_relationship", fontsize=16)    
        for i in xrange(0,num_neurons):
            pylab.subplot(13,13,i+1)
            pylab.plot(model_validation_predicted_activities.T[i],numpy.mat(validation_activities).T[i],'ro')

    return (model_predicted_activities,model_validation_predicted_activities)
	
	
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

def runRFinference():
    #d = contrib.dd.DB2(None)
    	
	
    f = open("modelfitDB2.dat",'rb')
    import pickle
    d = pickle.load(f)
    f.close()
    
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = sortOutLoading(d)
    params={}
    params["alpha"] = __main__.__dict__.get('Alpha',50)
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    e = []
    c = []
    b = []
    if False:
        x = 0.2
        for i in xrange(0,20):
            print i
            x = i*20
            (e1,te1,c1,tc1,RFs,pa,pva) = regulerized_inverse_rf(training_inputs,training_set,sizex,sizey,x,validation_inputs,validation_set,db_node,False)
            e.append(e1)
            c.append(c1)
            b.append(x)
            #x = x*2
        pylab.figure()
        #pylab.semilogx(b,e)
        pylab.plot(b,numpy.mat(e))
        pylab.figure()
        #pylab.semilogx(b,c)
        pylab.plot(b,c)
    	
    #return (e,c,b)
    
    if False:
        alphas=[120, 290,  50, 240, 290, 260, 120, 100, 290, 130, 290, 290, 230,170, 120, 190, 290, 100, 140, 290, 290,  60, 290, 290,  80, 210,50, 250, 170, 290, 290, 290,  60, 290, 290,  60, 260, 290, 290,290,  60,  90, 290, 120, 290,  80, 270, 120, 290, 290]
    	 
	RFs = []
        e = []
	c = []
	te = []
	tc = []
	pa = []
	pva = []
	for i in xrange(0,len(alphas)):
	      print numpy.shape(training_set)
	      print numpy.shape(training_set[:,i:i+1])
	      (e1,te1,c1,tc1,RF,pa1,pva1) = regulerized_inverse_rf(training_inputs,training_set[:,i:i+1],sizex,sizey,alphas[i],validation_inputs,validation_set[:,i:i+1],False)
	      
	      print numpy.shape(RF)
	      RFs.append(RF[0])
	      e.append(e1)
	      c.append(c1)
     	      te.append(te1)
	      tc.append(tc1)
	      pa.append(pa1)
	      pva.append(pva1)
	 
	pylab.figure()
	pylab.hist(e)
	pylab.figure()
	pylab.hist(c)
	pylab.figure()
	pylab.hist(te)
	pylab.figure()
	pylab.hist(tc)
	      
	      
    	return (e,te,c,tc,RFs,pa,pva)
	      
    (e,te,c,tc,RFs,pa,pva,corr_coef,corr_coef_tf) = regulerized_inverse_rf(training_inputs,training_set,sizex,sizey,params["alpha"],validation_inputs,validation_set,db_node,True)
    later_interaction_prediction(training_set,pa,validation_set,pva)
    
    pylab.figure()
    pylab.xlabel("fano factor")
    pylab.ylabel("normalized error")
    pylab.plot(ff,e,'ro')
    
    pylab.figure()
    pylab.xlabel("fano factor")
    pylab.ylabel("tf normalized error")
    pylab.plot(ff,te,'ro')
    
    pylab.figure()
    pylab.xlabel("fano factor")
    pylab.ylabel("correlation coef")
    pylab.plot(ff,corr_coef,'ro')
    
    pylab.figure()
    pylab.xlabel("fano factor")
    pylab.ylabel("correlation coef after transfer function")
    pylab.plot(ff,corr_coef_tf,'ro')
    
    f = open("modelfitDB2.dat",'wb')
    pickle.dump(d,f,-2)
    f.close()
    
    return (training_set,pa,validation_set,pva)


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
            pylab.subplot(10,11,i+1)
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
    
    #(x,y) = numpy.shape(weights[0])
    #weights  = cut_out_images_set(weights,int(y*0.49),(int(x*0.1),int(y*0.4)))
    (denx,deny) = numpy.shape(weights[0])
    centers,RFs = analyze_rf_possition(weights,0.4)
    RFs=weights
    # determine frequency
    
    freqor = []
    for w in RFs:
        ff = pylab.fftshift(pylab.fft2(w))
        (x,y) = array_argmax(numpy.abs(ff))
        (n,rubish) = shape(ff)
        freq = numpy.sqrt((x - n/2)*(x - n/2) + (y - n/2)*(y - n/2))
        #phase = numpy.arctan(ff[x,y].imag/ff[x,y].real)
        phase = numpy.angle(ff[x,y])
	
        if (x - n/2) != 0:
            print (y - n/2.0)/(x - n/2.0)
            orr = numpy.arctan((y - n/2.0)/(x - n/2.0))
        else:
            orr = numpy.pi/2
        
        if orr < 0:
           orr = orr+numpy.pi
	   
	#if phase < 0:
        #   phase = phase+2*numpy.pi
            
        freqor.append((freq,orr,phase))
    
    parameters=[]
    
    for j in xrange(0,len(RFs)):
        minf = numpy.max([freqor[j][0]-2,0])
        
        x = centers[j][0]
        y = centers[j][1] 
        
	#pylab.figure()
	#gab([x,y,0.2,freqor[j][1],freqor[j][0],freqor[j][2],1.0,0.001],weights[j]/numpy.sum(numpy.abs(weights[j])),display=True)
	
	rand = UniformRandom(seed=513)
	
	min_x = []
	min_err = 100000000000000
	
	for r in xrange(0,100): 
		x0 = [x,y,0.2,freqor[j][1],freqor[j][0],freqor[j][2],1.5,0.001]
		x1 = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
		
		x1[0] += 2.0*(rand()-0.5)*0.1*x0[0]
		x1[1] += 2.0*(rand()-0.5)*0.1*x0[1]
		x1[2] =  rand()*0.2
		x1[3] = x0[3]+2.0*(rand()-0.5)*(numpy.pi/4)
		x1[4] = x0[4]
		x1[5] = rand()*2*numpy.pi
		x1[6] = 1.0+3.0*rand()
		x1[7] = x0[7]
		
		(z,b,c) = fmin_tnc(gab,x1,bounds=[(x-x*0.1,x+x*0.1)        ,(y-y*0.1,y+y*0.1),(0.005,0.3),(0.0,numpy.pi),(minf,freqor[j][0]+2),(0,numpy.pi*2),(1.0,2.0),(0.0001,0.01)],args=[weights[j]/numpy.sum(numpy.abs(weights[j]))], xtol=0.0000000001,scale=[0.5,0.5,0.5,2.0,0.5,2.0,2.0,2.0],maxCGit=1000, ftol=0.000001,approx_grad=True,maxfun=10000,eta=0.01)
		e = gab(z,weights[j]/numpy.sum(numpy.abs(weights[j])),display=False)
		if(e  < min_err):
		   min_err = e
		   min_x = z	
        
	#pylab.figure()
        #gab(min_x,weights[j]/numpy.sum(numpy.abs(weights[j])),display=True)
        parameters.append(min_x)
        
        
    pylab.figure()
    for i in xrange(0,len(parameters)):
            pylab.subplot(15,15,i+1)
            (x,y,sigma,angle,f,p,ar,alpha) = tuple(parameters[i])
            g = Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=y-0.5,y=0.5-x,xdensity=denx,ydensity=deny,size=sigma,orientation=angle,phase=p,aspect_ratio=ar)() * alpha
            m = numpy.max([-numpy.min(g),numpy.max(g)])
            pylab.show._needmain=False
            pylab.imshow(g,vmin=-m,vmax=m,cmap=pylab.cm.RdBu)
    pylab.show()
    return parameters
    
    
def gab(z,w,display=False):
    from matplotlib.patches import Circle
    print z
    (x,y,sigma,angle,f,p,ar,alpha) = tuple(z)
    
    a = numpy.zeros(numpy.shape(w))
    (dx,dy) = numpy.shape(w)
    
    g =  Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=y-0.5,y=0.5-x,xdensity=dx,ydensity=dy,size=sigma,orientation=angle,phase=p,aspect_ratio=ar)() * alpha
    
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
	
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)
    f.close()	
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = sortOutLoading(dd)

    #params={}
    #params["alpha"] = __main__.__dict__.get('Alpha',50)
    #db_node = db_node.get_child(params)

    
			
    rfs = db_node.children[0].data["ReversCorrelationRFs"]
    
    a = STC(training_inputs-0.5,training_set[:,0:103],validation_inputs,validation_set,rfs)
    
    db_node.add_data("STCrfs",a,True)
    
    #return a
    pylab.figure()
    pylab.subplot(16,14,1)
    j=0
    
    m = []    
    for (ei,vv,vva,em,ep) in a:
        ind = numpy.argsort(numpy.abs(vv))
        w = numpy.array(ei[ind[len(ind)-1],:].real)
        m.append(numpy.max([-numpy.min(w),numpy.max(w)]))
    
    m = numpy.max(m)
    s = numpy.sqrt(sizey)     
    
     
    i=0
    acts=[]
    ofs=[]
    for (ei,vv,avv,em,ep) in a:
	ind = numpy.argsort(vv)
        pylab.figure()

	#if len(avv) == 0:
	#   acts.append([])	
	#   continue
		
	j=0
	act=[]
	act_val=[]
	of = []
		
	pylab.subplot(10,1,9)
	pylab.plot(numpy.sort(vv)[len(vv)-30:],'ro')
    	pylab.plot(em[len(vv)-30:])
	pylab.plot(ep[len(vv)-30:])
	
	pylab.subplot(10,1,10)
	pylab.plot(numpy.sort(vv)[0:20],'ro')
    	pylab.plot(em[0:20])
	pylab.plot(ep[0:20])
	
	for v in avv:
		w = numpy.array(ei[v,:].real).reshape(sizex,sizey)
		m = numpy.max([-numpy.min(w),numpy.max(w)])
		pylab.subplot(10,1,j)
		pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')
       	
		o = run_nonlinearity_detection((training_inputs*ei[v,:].T),numpy.mat(training_set[:,i]).T,10,display=False)
		of.append(o)
		(bins,tf) = o[0]    
		act.append(apply_output_function(training_inputs*ei[v,:].T,o))
		act_val.append(apply_output_function(validation_inputs*ei[v,:].T,o))
		pylab.subplot(10,1,j+1)
		pylab.plot(bins[0:-1],tf)
		j = j+2
	
	
	
	acts.append((act,act_val,of))

	#print "corr_coef =", numpy.corrcoef(act.T, training_set.T[i])[0][1]
	#print "PVE =",   1-numpy.sum(numpy.power(act.T- training_set.T[i],2)) / numpy.sum(numpy.power(numpy.mean(training_set.T[i])- training_set.T[i],2))
	#pylab.plot(numpy.array((training_inputs*ei[ind[len(ind)-1],:].real.T)),numpy.array(numpy.mat(training_set[:,i]).T),'ro')
	i = i+1

    db_node.add_data("STCact",acts,True)
    
    f = open("modelfitDB2.dat",'wb')
    import pickle
    dd = pickle.dump(dd,f)
    f.close()
    
    #pylab.show()
    return a

def STC(inputs,activities,validation_inputs,validation_activities,STA,cutoff=85,display=False):
    from scipy import linalg
    print "input size:",numpy.shape(inputs)
    t,s = numpy.shape(inputs)
    s = numpy.sqrt(s)
    
    (num_in,input_len) = numpy.shape(inputs)
    (num_in,act_len) = numpy.shape(activities)
    
    print numpy.mean(activities)
    
    tt = numpy.mat(numpy.zeros(numpy.shape(inputs[0])))
    
    SWa = []
    laa = []
    Ninva = []
    C = []
    eis = []
    
    for a in xrange(0,act_len):
	CC = numpy.mat(numpy.zeros((input_len,input_len)))
	U  = numpy.mat(numpy.zeros((input_len,input_len)))
	N  = numpy.mat(numpy.zeros((input_len,input_len)))
	Ninv  = numpy.mat(numpy.zeros((input_len,input_len)))
	
	for i in xrange(0,num_in):
		CC = CC + (numpy.mat(inputs[i,:]) - STA[a].flatten()/num_in).T * (numpy.mat(inputs[i,:]- STA[a].flatten()/num_in)) 
	CC = CC / num_in
	
	v,la = linalg.eigh(CC)
	la = numpy.mat(la)
	ind = numpy.argsort(v)
	for j in xrange(0,int(input_len*(cutoff/100.0))):
		v[ind[j]]=0.0
	
	for i in xrange(0,input_len):
		if v[i] != 0:     
			N[i,i] = 1/numpy.sqrt(v[i])
			Ninv[i,i] = numpy.sqrt(v[i])
		else: 
			N[i,i]=0.0
			Ninv[i,i] = 0.0
	
	U = la * numpy.mat(N)
	SW = numpy.matrix(inputs) * U
	SWa.append(SW)
	laa.append(la)
	Ninva.append(Ninv)
	
	if a == 0:
	        SW1 = SW*linalg.inv(la)
		F = numpy.mat(numpy.zeros((s,s)))
		for i in xrange(0,num_in):
			F += abs(pylab.fftshift(pylab.fft2(inputs[i,:].reshape(s,s)-STA[0])))
		pylab.figure()
		pylab.imshow(F.A,interpolation='nearest',cmap=pylab.cm.gray)
		
		
		F = numpy.mat(numpy.zeros((s,s)))
		for i in xrange(0,num_in):
			F += abs(pylab.fftshift(pylab.fft2(SW1[i,:].reshape(s,s))))
		pylab.figure()
		pylab.imshow(F.A,interpolation='nearest',cmap=pylab.cm.gray)

		
	#do significance testing
	vv=[]
	for r in xrange(0,50):
	    from numpy.random import shuffle
	    act = numpy.array(activities[:,a].T).copy()
	    shuffle(act)
	    C = numpy.zeros((input_len,input_len))	    	
	    for i in xrange(0,num_in):
	    	C += (numpy.mat(SWa[a][i,:]).T * numpy.mat(SWa[a][i,:])) * act[i]
	    C = C / num_in
	    v,ei = linalg.eigh(C)
	    vv.append(numpy.sort(v))
	vv = numpy.mat(vv)
	
	mean_diff = []
	for i in xrange(0,50):
	    for j in xrange(0,input_len-1):
		mean_diff.append(numpy.abs(vv[i,j]-vv[i,j+1]))
	
	diff_min = numpy.mean(mean_diff) - 15*numpy.std(mean_diff)
	diff_max = numpy.mean(mean_diff) + 15*numpy.std(mean_diff)
	
	error_minus = numpy.array(numpy.mean(vv,axis=0)-3.0*numpy.std(vv,axis=0))[0]	
	error_plus = numpy.array(numpy.mean(vv,axis=0)+3.0*numpy.std(vv,axis=0))[0]
	
	C = numpy.zeros((input_len,input_len))		
	for i in xrange(0,num_in):
   	    C += (numpy.mat(SWa[a][i,:]).T * numpy.mat(SWa[a][i,:])) * activities[i,a] 
	
	C = C / num_in
	
	if a == 0:
		pylab.figure()
		pylab.imshow(C)
	
	vv,ei = linalg.eigh(C)
	
	ind = numpy.argsort(vv)
	accepted=[]
	for i in xrange(len(vv)-30,len(vv)):
	    if (vv[ind[i]] >= error_plus[i]) or (vv[ind[i]] <= error_minus[i]):
	       accepted.append(i)
	
	accepted_vv=[]
	
	flag=False
	for i in accepted:
	    if i != 0:
	    	if (vv[ind[i]]-vv[ind[i-1]] >= diff_max):
	       		flag=True
	    if flag:
	       accepted_vv.append(ind[i])	
	    	
		
	print len(accepted_vv)
	
	ei=numpy.mat(ei).T
	ei = ei*(Ninva[a]*linalg.inv(laa[a]))
	eis.append((ei,vv,accepted_vv,error_minus,error_plus))
    
    return eis

def fitting():
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)


    rfs = dd.children[0].children[0].data["ReversCorrelationRFs"]

    print len(rfs)
    params = fitGabor(rfs)
    
    m = numpy.max(numpy.abs(numpy.min(rfs)),numpy.abs(numpy.max(rfs)))
    
    pylab.figure()
    for i in xrange(0,len(rfs)):
        pylab.subplot(15,15,i+1)
        w = numpy.array(rfs[i])
        pylab.show._needmain=False
        pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
	pylab.axis('off')
    pylab.figure()

    return (params)

def tiling():
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)

   
    rfs = [dd.children[0].children[0].data["ReversCorrelationRFs"],
    	   dd.children[1].children[0].data["ReversCorrelationRFs"],
	   dd.children[3].children[0].data["ReversCorrelationRFs"]]
    
    m=0
    for r in rfs:
        m = numpy.max(numpy.max(numpy.abs(numpy.min(r)),numpy.abs(numpy.max(r))),m)
    loc = []
    
    f = file("./Mice/2009_11_04/region3_cell_locations", "r")
    loc.append([line.split() for line in f])
    f.close()
		
    f = file("./Mice/2009_11_04/region5_cell_locations", "r")
    loc.append([line.split() for line in f])
    f.close()
			
    f = file("./Mice/20090925_14_36_01/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_cell_locations.txt", "r")
    loc.append([line.split() for line in f])
    f.close()
    
    param=[]
    f = open("./Mice/2009_11_04/region=3_fitting_rep=100","rb")
    import pickle
    param.append(pickle.load(f))
    f.close()
    f = open("./Mice/2009_11_04/region=5_fitting_rep=100","rb")
    param.append(pickle.load(f))
    f.close()    		
    f = open("./Mice/20090925_14_36_01/region=2_fitting_rep=100","rb")
    param.append(pickle.load(f))
    f.close()    		
		
		
    for locations in loc:
	(a,b) = numpy.shape(locations)
	for i in xrange(0,a):
		for j in xrange(0,b):
			locations[i][j] = float(locations[i][j])
			
    loc[0] = numpy.array(loc[0])/256.0*261.0
    loc[1] = numpy.array(loc[1])/256.0*261.0
    loc[2] = numpy.array(loc[2])/256.0*230.0
    
    fitted_corr=[]
    for rf in rfs:
	f=[]	    	     
	for i in xrange(0,len(rf)):
		#(x,y,sigma,angle,f,p,ar,alpha) = tuple(params[i])
		#(dx,dy) = numpy.shape(rfs[0])
		#g = Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=y-0.5,y=0.5-x,xdensity=dx,ydensity=dy,size=sigma,orientation=angle,phase=p,aspect_ratio=ar)() * alpha    
		f.append(numpy.sum(numpy.power(rf[i].flatten()- numpy.mean(rf[i].flatten()),2)))
	fitted_corr.append(f)
	
    for i in xrange(0,len(rfs)):
	to_delete = numpy.nonzero((numpy.array(fitted_corr[i]) < 0.04)*1.0)[0]
	rfs[i] = numpy.delete(rfs[i],to_delete,axis=0)
	loc[i] = numpy.delete(numpy.array(loc[i]),to_delete,axis=0)
	param[i] = numpy.delete(numpy.array(param[i]),to_delete,axis=0)

    rc=[]
    for rf in rfs:
	r=[]
	for idx in xrange(0,len(rf)):
	    r.append(numpy.array(centre_of_gravity(numpy.power(rf[idx],2)))*1000)
        rc.append(r)


    pylab.figure()
    pylab.hist(fitted_corr)

    membership=[]
    membership1=[]
    locs = []
    for i in xrange(0,len(rfs)):
	m = []
	m1 = []
	l = []
	for j in xrange(0,len(rfs[i])):
    	    if (circular_distance(param[i][j][3],0) <= numpy.pi/8):
		m.append(0)
		m1.append(0)
		l.append(loc[i][j])     	
    	    elif (circular_distance(param[i][j][3],numpy.pi/4) <= numpy.pi/8):
	    	m1.append(1)     	
    	    elif (circular_distance(param[i][j][3],numpy.pi/2) <= numpy.pi/8):
		m.append(2)
		m1.append(2)
		l.append(loc[i][j])     	
    	    elif (circular_distance(param[i][j][3],3*numpy.pi/4) <= numpy.pi/8):
	    	m1.append(3)
	         	
	membership.append(m)
	membership1.append(m1)
	locs.append(l)
				
    ors=[]
    orrf=[]		
    orrphase=[]		
    for (p,rf) in zip(param,rfs):
	ors.append(numpy.array(p[:,3].T)) 				
        orrf.append(zip(numpy.array(p[:,3].T),rf))
	orrphase.append(zip(numpy.array(p[:,3].T),numpy.array(p[:,5].T)))
	
    #monte_carlo(rc,orrphase,histogram_of_phase_dist_correl_of_cooriented_neurons,100)  
    #monte_carlo(rc,orrf,histogram_of_RF_correl_of_cooriented_neurons,100)
    #monte_carlo(rc,ors,average_or_histogram_of_proximite,100)
    #monte_carlo(rc,ors,average_or_diff,100)	
	
    monte_carlo(loc,ors,average_or_diff,100)	
    monte_carlo(loc,orrf,average_cooriented_RF_corr,100)
    monte_carlo(loc,orrf,average_RF_corr,100)
    
    return
    
    monte_carlo(loc,orrphase,histogram_of_phase_dist_correl_of_cooriented_neurons,100)  
    monte_carlo(loc,orrf,histogram_of_RF_correl_of_cooriented_neurons,100)
    monte_carlo(loc,ors,average_or_histogram_of_proximite,100)
    return
    monte_carlo(locs,membership,number_of_same_neighbours,100)				
    monte_carlo(loc,membership1,number_of_same_neighbours,100)
        		    
    
    return
    
    colors=[]
    xx=[]
    yy=[]
    d1=[]
    d2=[]
    d3=[]

    for r,l in zip(rfs,loc):
    	for i in xrange(0,len(r)):
	    for j in xrange(i+1,len(r)):
		d3.append(distance(l,i,j))
		
    for i in xrange(0,len(rfs)):
	colors=[]
	xx=[]
    	yy=[]
	for idx in xrange(0,len(rfs[i])):
		if (circular_distance(param[i][idx][3],0) <= numpy.pi/12):
			xx.append(loc[i][idx][0])
			yy.append(loc[i][idx][1])
			colors.append(0.9)
	    		for j in xrange(idx+1,len(rfs[i])):
			    if (circular_distance(param[i][j][3],0) <= numpy.pi/12):
			        d1.append(distance(loc[i],idx,j))	    	
				d2.append(distance(loc[i],idx,j))					    	
			    if (circular_distance(param[i][j][3],numpy.pi/2) <= numpy.pi/12):
				d2.append(distance(loc[i],idx,j))


		if (circular_distance(param[i][idx][3],numpy.pi/2) <= numpy.pi/12): 
			xx.append(loc[i][idx][0])
			yy.append(loc[i][idx][1])
			colors.append(0.1)
			for j in xrange(idx+1,len(rfs[i])):
			    if (circular_distance(param[i][j][3],numpy.pi/2) <= numpy.pi/12):
			        d1.append(distance(loc[i],idx,j))
				d2.append(distance(loc[i],idx,j))					    	
			    if (circular_distance(param[i][j][3],0) <= numpy.pi/12):
				d2.append(distance(loc[i],idx,j))
			
	pylab.figure(figsize=(5,5))
	pylab.scatter(xx,yy,c=colors,s=200,cmap=pylab.cm.RdBu)
	pylab.colorbar()
    print "Average distance of colinear", numpy.mean(numpy.power(d1,2))
    print "Average distance of horizontal and vertical", numpy.mean(numpy.power(d2,2))
    print "Average distance of whole population", numpy.mean(numpy.power(d3,2))


def monte_carlo(locations,property,property_measure,reps):
    from numpy.random import shuffle	
    for (l,m) in zip(locations,property):
    	a = property_measure(l,m)
	curves = numpy.zeros((reps,len(a)))
	
	for x in xrange(0,reps):
		mm = list(m) 
		shuffle(mm)
		curves[x,:] = property_measure(l,mm)
		
	f = numpy.median(curves,axis=0)
	f_m = a
	#std = numpy.std(curves,axis=0,ddof=1)
	err_bar_upper = numpy.sort(curves,axis=0)[int(reps*0.95),:]
	err_bar_lower = numpy.sort(curves,axis=0)[int(reps*0.05),:]
	
	pylab.figure()
	pylab.plot(f,'b')
	pylab.plot(f_m,'g')
	pylab.plot(err_bar_lower,'r')
	pylab.plot(err_bar_upper,'r')
	
def number_of_same_neighbours(locations,membership):	
    curve = [0 for i in xrange(0,30)]
    for dist in xrange(0,30):
	for i in xrange(0,len(locations)):
		for j in xrange(0,len(locations)):
			if i!=j:
				if distance(locations,i,j) < (dist+1)*10:
					if membership[i] == membership[j]:
						curve[dist] += 1
	curve[dist]/= len(locations)	
    return curve
						
def average_or_diff(locations,ors):
    curve = [0 for i in xrange(0,30)]
    for dist in xrange(0,30):
	n = 0    
	for i in xrange(0,len(locations)):
		for j in xrange(0,len(locations)):
			if i!=j:
				if distance(locations,i,j) < (dist+1)*10:
					curve[dist]+=circular_distance(ors[i],ors[j])
					n+=1
	if n!=0:				
		curve[dist]/=n	
    return curve

def average_cooriented_RF_corr(locations,data):
    (ors,rfs) = zip(*data)
    curve = [0 for i in xrange(0,30)]
    for dist in xrange(0,30):
	n = 0    
	for i in xrange(0,len(locations)):
		for j in xrange(0,len(locations)):
			if i!=j:
				if distance(locations,i,j) < (dist+1)*10:
					if circular_distance(ors[i],ors[j]) < (numpy.pi/12.0):
						curve[dist]+=numpy.corrcoef(rfs[i].flatten(),rfs[j].flatten())[0][1]
						n+=1
	if n!=0:				
		curve[dist]/=n	
    return curve
	
def average_RF_corr(locations,data):
    (ors,rfs) = zip(*data)
    curve = [0 for i in xrange(0,30)]
    for dist in xrange(0,30):
	n = 0    
	for i in xrange(0,len(locations)):
		for j in xrange(0,len(locations)):
			if i!=j:
				if distance(locations,i,j) < (dist+1)*10:
						curve[dist]+=numpy.corrcoef(rfs[i].flatten(),rfs[j].flatten())[0][1]
						n+=1
	if n!=0:				
		curve[dist]/=n	
    return curve

	
def average_or_histogram_of_proximite(locations,ors):
    curve = []
    for i in xrange(0,len(locations)):
	for j in xrange(0,len(locations)):
		if i!=j:
			if distance(locations,i,j) < 50:
				curve.append(circular_distance(ors[i],ors[j]))
    if len(curve) != 0:					
    	return numpy.histogram(curve,range=(0.0,numpy.pi/2))[0]/(len(curve)*1.0)
    else: 
    	return [0 for i in xrange(0,10)]

def histogram_of_RF_correl_of_cooriented_neurons(locations,data):
    (ors,rfs) = zip(*data)
    difs=[]
    for i in xrange(0,len(locations)):
	for j in xrange(0,len(locations)):
	    if i!=j:
		if circular_distance(ors[i],ors[j]) < (numpy.pi/8.0):
			if distance(locations,i,j) < 50:
				difs.append(numpy.corrcoef(rfs[i].flatten(),rfs[j].flatten())[0][1])
    if len(difs) != 0:						    
    	return numpy.histogram(difs,range=(-1.0,1.0),bins=10)[0]/(len(difs)*1.0)
    else:
	return [0 for i in xrange(0,10)]

def histogram_of_phase_dist_correl_of_cooriented_neurons(locations,data):
    (ors,phase) = zip(*data)
    difs=[]
    for i in xrange(0,len(locations)):
	for j in xrange(0,len(locations)):
	    if i!=j:
		if circular_distance(ors[i],ors[j]) < (numpy.pi/12.0):
			if distance(locations,i,j) < 40:
				dif = numpy.abs(phase[i] - phase[j])
				if dif > numpy.pi:
				   dif = 2*numpy.pi - dif	
				difs.append(dif)
    if len(difs) != 0:						    
    	return numpy.histogram(difs,range=(0,numpy.pi),bins=10)[0]/(len(difs)*1.0)
    else:
	return [0 for i in xrange(0,10)]


def RF_correlations():
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)

   
    rfs = [dd.children[0].children[0].data["ReversCorrelationRFs"],
    	   dd.children[1].children[0].data["ReversCorrelationRFs"],
	   dd.children[3].children[0].data["ReversCorrelationRFs"]]
    
    m=0
    for r in rfs:
        m = numpy.max(numpy.max(numpy.abs(numpy.min(r)),numpy.abs(numpy.max(r))),m)
    loc = []
    
    f = file("./Mice/2009_11_04/region3_cell_locations", "r")
    loc.append([line.split() for line in f])
    f.close()
		
    f = file("./Mice/2009_11_04/region5_cell_locations", "r")
    loc.append([line.split() for line in f])
    f.close()
			
    f = file("./Mice/20090925_14_36_01/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_cell_locations.txt", "r")
    loc.append([line.split() for line in f])
    f.close()

			
		
    param=[]
    
    f = open("./Mice/2009_11_04/region=3_fitting_rep=100","rb")
    import pickle
    param.append(pickle.load(f))
    f.close()
    f = open("./Mice/2009_11_04/region=5_fitting_rep=100","rb")
    param.append(pickle.load(f))
    f.close()    		
    f = open("./Mice/20090925_14_36_01/region=2_fitting_rep=100","rb")
    param.append(pickle.load(f))
    f.close()    		
		
		
    for locations in loc:
	(a,b) = numpy.shape(locations)
	for i in xrange(0,a):
		for j in xrange(0,b):
			locations[i][j] = float(locations[i][j])
			
    loc[0] = numpy.array(loc[0])/256.0*261.0
    loc[1] = numpy.array(loc[1])/256.0*261.0
    loc[2] = numpy.array(loc[2])/256.0*230.0
    
    fitted_corr=[]
    for rf in rfs:
	f=[]	    	     
	for i in xrange(0,len(rf)):
		#(x,y,sigma,angle,f,p,ar,alpha) = tuple(params[i])
		#(dx,dy) = numpy.shape(rfs[0])
		#g = Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=y-0.5,y=0.5-x,xdensity=dx,ydensity=dy,size=sigma,orientation=angle,phase=p,aspect_ratio=ar)() * alpha    
		f.append(numpy.sum(numpy.power(rf[i].flatten()- numpy.mean(rf[i].flatten()),2)))
	fitted_corr.append(f)
	
    pylab.title("The histogram of the variability of RFs")
    pylab.hist(flatten(fitted_corr))
    pylab.xlabel('RF variability')
    
    
    for i in xrange(0,len(fitted_corr)):
	pylab.figure()
	z = numpy.argsort(fitted_corr[i])
	b=0	    
	for j in z:	    
		pylab.subplot(15,15,b+1)
		pylab.show._needmain=False
		pylab.imshow(rfs[i][j],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')	
		b+=1
 
    for i in xrange(0,len(rfs)):
	to_delete = numpy.nonzero((numpy.array(fitted_corr[i]) < 0.04)*1.0)[0]
	rfs[i] = numpy.delete(rfs[i],to_delete,axis=0)
	loc[i] = numpy.delete(numpy.array(loc[i]),to_delete,axis=0)
	param[i] = numpy.delete(numpy.array(param[i]),to_delete,axis=0)

    rc=[]
    for rf in rfs:
	r=[]
	for idx in xrange(0,len(rf)):
	    r.append(numpy.array(centre_of_gravity(numpy.power(rf[idx],2)))*1000)
        rc.append(r)

    for i in xrange(0,len(rfs)):
	pylab.figure()
	b=0	    
	for j in rfs[i]:	    
		pylab.subplot(15,15,b+1)
		pylab.show._needmain=False
		pylab.imshow(j,vmin=-m*0.5,vmax=m*0.5,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')	
		b+=1
	pylab.savefig('RFsGrid'+str(i)+'.png')	


    rf_cross=[]
    for r in rfs:
	print len(r)
	rf_cros = numpy.zeros((len(r),len(r)))	    
	for i in xrange(0,len(rfs)):
		for j in xrange(0,len(rfs)):
			rf_cros[i,j] = numpy.corrcoef(r[i].flatten(),r[j].flatten())[0][1]
	rf_cross.append(rf_cros)
    i=0		
    for (r,locations) in zip(rfs,loc):
        pylab.figure(figsize=(5,5))
	pylab.axes([0.0,0.0,1.0,1.0])
    	for idx in xrange(0,len(r)):
		x = locations[idx][0]/300
		y = locations[idx][1]/300
		pylab.axes([x-0.02,y-0.02,0.04,0.04])
		pylab.imshow(r[idx],vmin=-m*0.5,vmax=m*0.5,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')
    	pylab.savefig('RFsLocalized'+str(i)+'.png')
	i+=1
  
    
    
    from matplotlib.lines import Line2D   
    from matplotlib.patches import Circle
    i=0
    for (r,locations,p) in zip(rfs,loc,param):
	pylab.figure(figsize=(5,5))
    	pylab.axes([0.0,0.0,1.0,1.0])
	
    	for idx in xrange(0,len(r)):
		x = locations[idx][0]/300
		y = locations[idx][1]/300
		pylab.axes([x-0.02,y-0.02,0.04,0.04])
		pylab.imshow(r[idx],vmin=-m*0.5,vmax=m*0.5,interpolation='nearest',cmap=pylab.cm.RdBu)
		pylab.axis('off')
		ax = pylab.axes([0.0,0.0,1.0,1.0])
		cir = Circle( (x,y), radius=0.01)
		pylab.gca().add_patch(cir)
		l = Line2D([x-numpy.cos(p[idx][3])*0.03,x+numpy.cos(p[idx][3])*0.03],[y-numpy.sin(p[idx][3])*0.03,y+numpy.sin(p[idx][3])*0.03],transform=ax.transAxes,linewidth=5.1, color='g')
		pylab.gca().add_line(l)
	pylab.savefig('RFsLocalizedOR'+str(i)+'.png')
	i+=1

    for (r,locations,p) in zip(rfs,loc,param):
	pylab.figure(figsize=(5,5))
    	pylab.axes([0.0,0.0,1,1])
    	for idx in xrange(0,len(r)):
		if circular_distance(p[idx][3],0)<= numpy.pi/8:    
			x = locations[idx][0]/300
			y = locations[idx][1]/300
			pylab.axes([x-0.02,y-0.02,0.04,0.04])
			pylab.imshow(r[idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
			pylab.axis('off')
			ax = pylab.axes([0.0,0.0,1,1])
			cir = Circle( (x,y), radius=0.01)
			pylab.gca().add_patch(cir)
			l = Line2D([x-numpy.cos(p[idx][3])*0.03,x+numpy.cos(p[idx][3])*0.03],[y-numpy.sin(p[idx][3])*0.03,y+numpy.sin(p[idx][3])*0.03],transform=ax.transAxes,linewidth=5.1, color='g')
			pylab.gca().add_line(l)

	pylab.figure(figsize=(5,5))
    	pylab.axes([0.0,0.0,1,1])
    	for idx in xrange(0,len(r)):
		if circular_distance(p[idx][3],numpy.pi/4)<= numpy.pi/8:    
			x = locations[idx][0]/300
			y = locations[idx][1]/300
			pylab.axes([x-0.02,y-0.02,0.04,0.04])
			pylab.imshow(r[idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
			pylab.axis('off')
			ax = pylab.axes([0.0,0.0,1,1])
			cir = Circle( (x,y), radius=0.01)
			pylab.gca().add_patch(cir)
			l = Line2D([x-numpy.cos(p[idx][3])*0.03,x+numpy.cos(p[idx][3])*0.03],[y-numpy.sin(p[idx][3])*0.03,y+numpy.sin(p[idx][3])*0.03],transform=ax.transAxes,linewidth=5.1, color='g')
			pylab.gca().add_line(l)


	pylab.figure(figsize=(5,5))
    	pylab.axes([0.0,0.0,1,1])
    	for idx in xrange(0,len(r)):
		if circular_distance(p[idx][3],numpy.pi/2)<= numpy.pi/8:    
			x = locations[idx][0]/300
			y = locations[idx][1]/300
			pylab.axes([x-0.02,y-0.02,0.04,0.04])
			pylab.imshow(r[idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
			pylab.axis('off')
			ax = pylab.axes([0.0,0.0,1,1])
			cir = Circle( (x,y), radius=0.01)
			pylab.gca().add_patch(cir)
			l = Line2D([x-numpy.cos(p[idx][3])*0.03,x+numpy.cos(p[idx][3])*0.03],[y-numpy.sin(p[idx][3])*0.03,y+numpy.sin(p[idx][3])*0.03],transform=ax.transAxes,linewidth=5.1, color='g')
			pylab.gca().add_line(l)

	pylab.figure(figsize=(5,5))
    	pylab.axes([0.0,0.0,1,1])
    	for idx in xrange(0,len(r)):
		if circular_distance(p[idx][3],3*numpy.pi/4)<= numpy.pi/8:    
			x = locations[idx][0]/300
			y = locations[idx][1]/300
			pylab.axes([x-0.02,y-0.02,0.04,0.04])
			pylab.imshow(r[idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu)
			pylab.axis('off')
			ax = pylab.axes([0.0,0.0,1,1])
			cir = Circle( (x,y), radius=0.01)
			pylab.gca().add_patch(cir)
			l = Line2D([x-numpy.cos(p[idx][3])*0.03,x+numpy.cos(p[idx][3])*0.03],[y-numpy.sin(p[idx][3])*0.03,y+numpy.sin(p[idx][3])*0.03],transform=ax.transAxes,linewidth=5.1, color='g')
			pylab.gca().add_line(l)


    
    for i in xrange(0,len(rfs)):
	colors=[]
	xx=[]
    	yy=[]
	for idx in xrange(0,len(rfs[i])):
		xx.append(loc[i][idx][0])
		yy.append(loc[i][idx][1])
		colors.append(param[i][idx][3]/numpy.pi)
    
	pylab.figure(figsize=(5,5))
	pylab.scatter(xx,yy,c=colors,s=200,cmap=pylab.cm.hsv)
	pylab.colorbar()
	
    for i in xrange(0,len(rfs)):
	colors=[]
	xx=[]
    	yy=[]
	for idx in xrange(0,len(rfs[i])):
		xx.append(rc[i][idx][0])
		yy.append(rc[i][idx][1])
		colors.append(param[i][idx][3]/numpy.pi)
    
	pylab.figure(figsize=(5,5))
	pylab.scatter(xx,yy,c=colors,s=200,cmap=pylab.cm.hsv)
	pylab.colorbar()
	
	
	
    c = []
    rf_dist = []
    c_cut = []
    d = []
    
    orr_diff = []
    phase_diff_of_colinear20 = []
    phase_diff_of_colinear30 = []
    phase_diff_of_colinear50 = []
    phase_diff_of_colinear100 = []
    phase_diff_of_colinear1000 = []
    for (r,locations,params) in zip(rfs,loc,param):
	for i in xrange(0,len(r)):
		for j in xrange(i+1,len(r)):
			corr1= numpy.corrcoef(r[i].flatten(),r[j].flatten())[0][1]	
			c.append(corr1)
			rf_dist.append(numpy.mean(numpy.power(r[i].flatten()-r[j].flatten(),2)))
			c_cut.append(RF_corr_centered(r[i],r[j],0.3,display=False))
			dist = distance(locations,i,j)
			d.append(dist)
			a = circular_distance(params[i][3],params[j][3])
				
			if a < numpy.pi/16:
				pd = numpy.abs(params[i][5] - params[j][5])
				if pd > numpy.pi:
					pd = 2*numpy.pi - pd
				
				if dist <= 20:     
					phase_diff_of_colinear20.append(pd)  
				if dist <= 40:     
					phase_diff_of_colinear30.append(pd)  
				if dist <= 60:     
					phase_diff_of_colinear50.append(pd)  
				if dist <= 100:     
					phase_diff_of_colinear100.append(pd)  
				if dist <= 300:     
					phase_diff_of_colinear1000.append(pd)	
			orr_diff.append(numpy.abs(circular_distance(params[i][3],params[j][3])))
    
    print len(d)
    print len(c)
  
    nn_orr_diff=[]
    nn_corr=[]
    nn_rf_dist=[]
    
    all_orr_diff=[]
    all_corr=[]
    all_rf_dist=[]
    for (r,locations,params) in zip(rfs,loc,param):
	for i in xrange(0,len(r)):
		dst = []
		for j in xrange(0,len(r)):
			dst.append(distance(locations,i,j))
			if i != j:
			   all_orr_diff.append(circular_distance(params[i][3],params[j][3]))
			   all_corr.append(numpy.corrcoef(r[i].flatten(),r[j].flatten())[0][1])
		           all_rf_dist.append(numpy.mean(numpy.power(r[i].flatten()-r[j].flatten(),2)))				
		
		idx = (numpy.argsort(dst))[1]
		nn_orr_diff.append(circular_distance(params[i][3],params[idx][3]))
		nn_corr.append(numpy.corrcoef(r[i].flatten(),r[idx].flatten())[0][1])
		nn_rf_dist.append(numpy.mean(numpy.power(r[i].flatten()-r[idx].flatten(),2)))

		
    pylab.figure()
    pylab.title('Nearest neighbour orrientation difference')
    pylab.hist([nn_orr_diff,all_orr_diff],normed=True)
    
    pylab.figure()
    pylab.title('Nearest neighbour RFs correlation')
    pylab.hist([nn_corr,all_corr],normed=True)
    
    pylab.figure()
    pylab.title('Nearest neighbour RF distance')
    pylab.hist([nn_rf_dist,all_rf_dist],normed=True)
    
    
	
    #angle_dif50 = []
    #angle50 = []
    #corr50 = []
    #for i in xrange(0,len(new_rfs)):
	#for j in xrange(i+1,len(new_rfs)):
	      #dist = distance(locations,new_rfs_idx[i],new_rfs_idx[j])
	      
	      #if (dist < 50) and (circular_distance(params[i][3],params[j][3])<numpy.pi/6):
		        #a = numpy.arccos((locations[new_rfs_idx[j]][0]-locations[new_rfs_idx[i]][0])/dist) 
			#a = a * numpy.sign(locations[new_rfs_idx[j]][1]-locations[new_rfs_idx[i]][1])
			
			#if a < 0: 
			   #a = a + numpy.pi
			
			#angle_dif50.append(a)
		        #angle50.append(params[i][3])
			#corr50.append(numpy.corrcoef(new_rfs[i].flatten(),new_rfs[j].flatten())[0][1])
    
    
    #angle_dif100 = []
    #angle100 = []
    #corr100= []
    #for i in xrange(0,len(new_rfs)):
	#for j in xrange(i+1,len(new_rfs)):
	      #dist = distance(locations,new_rfs_idx[i],new_rfs_idx[j])
	      
	      #if (dist < 100) and (circular_distance(params[i][3],params[j][3])<numpy.pi/6):
			#a = numpy.arccos((locations[new_rfs_idx[j]][0]-locations[new_rfs_idx[i]][0])/dist) 
			#a = a * numpy.sign(locations[new_rfs_idx[j]][1]-locations[new_rfs_idx[i]][1])
			
			#if a < 0: 
			   #a = a + numpy.pi			
			
			#angle_dif100.append(a)
		        #angle100.append(params[i][3])
    			#corr100.append(numpy.corrcoef(new_rfs[i].flatten(),new_rfs[j].flatten())[0][1])
    #data=[]
    #dataset = loadSimpleDataSet("Mice/2009_11_04/region3_stationary_180_15fr_103cells_on_response_spikes",1800,103)
    #(index,data) = dataset
    #index+=1
    #dataset = (index,data)
    #dataset = averageRangeFrames(dataset,0,1)
    #dataset = averageRepetitions(dataset)
    #dataset = generateTrainingSet(dataset)
    #(a,v) = compute_average_min_max(dataset)
    #dataset = normalize_data_set(dataset,a,v)
    #data.append(dataset) 
    
    #cor_orig = []
    #for i in xrange(0,len(new_rfs)):
	#for i in xrange(0,len(new_rfs)):
		#for j in xrange(i+1,len(new_rfs)):
		#cor_orig.append(numpy.corrcoef(dataset[:,new_rfs_idx[i]].T,dataset[:,new_rfs_idx[j]].T)[0][1])
    
    print len(phase_diff_of_colinear20)
    pylab.figure()
    pylab.title('Histogram of phase difference of co-oriented proximite <0.1 neurons')
    pylab.hist(phase_diff_of_colinear20)
    
    pylab.figure()
    pylab.title('Histogram of phase difference of co-oriented proximite <0.2 neurons')
    pylab.hist(phase_diff_of_colinear30)

    pylab.figure()
    pylab.title('Histogram of phase difference of co-oriented proximite <0.3 neurons')
    pylab.hist(phase_diff_of_colinear50)
    
    pylab.figure()
    pylab.title('Histogram of phase difference of co-oriented proximite <0.4 neurons')
    pylab.hist(phase_diff_of_colinear100)
    
    
    
    pylab.figure()
    pylab.title('Histogram of phase difference of co-oriented proximite <0.1 neurons normalized against histogram of all couples')
    (h,b) = numpy.histogram(phase_diff_of_colinear30)
    (h2,b) = numpy.histogram(phase_diff_of_colinear1000)
    pylab.plot((h*1.0/numpy.sum(h))/(h2*1.0/numpy.sum(h2)))
    
    pylab.figure()
    pylab.title('Histogram of phase difference of co-oriented proximite <0.1 neurons normalized against histogram of all couples')
    (h,b) = numpy.histogram(phase_diff_of_colinear30)
    (h2,b) = numpy.histogram(phase_diff_of_colinear1000)
    pylab.plot((h*1.0/numpy.sum(h))-(h2*1.0/numpy.sum(h2)))
    
    pylab.figure()
    pylab.title('Histogram of phases')
    a = numpy.concatenate([numpy.mat(param[0])[:,5].flatten(),numpy.mat(param[1])[:,5].flatten(),numpy.mat(param[2])[:,5].flatten()],axis=1).flatten()
    pylab.hist(a.T)
    
    import contrib.jacommands
    pylab.figure()
    pylab.title('Correlation between distance and raw RFs average distance')
    pylab.plot(d,rf_dist,'ro')
    pylab.plot(d,contrib.jacommands.weighted_local_average(d,rf_dist,30),'go')
    
    pylab.figure(facecolor='w')
    pylab.title('Correlation between distance and raw RFs correlations')
    ax = pylab.axes() 
    ax.plot(d,c,'ro')
    ax.plot(d,contrib.jacommands.weighted_local_average(d,c,30),'go')
    ax.axhline(0,linewidth=4)
    for tick in ax.xaxis.get_major_ticks():
  	  tick.label1.set_fontsize(18)
    for tick in ax.yaxis.get_major_ticks():
    	tick.label1.set_fontsize(18)
    pylab.savefig('RFsCorrelationsVsDistance.png')
	
    pylab.xlabel("distance",fontsize=18)
    pylab.ylabel("correlation coefficient",fontsize=18)
    #pylab.plot(d,contrib.jacommands.weighted_local_average(d,numpy.abs(c),30),'bo')
    
    pylab.figure()
    pylab.title('Correlation between distance and centered raw RFs correlations')
    pylab.plot(d,c_cut,'ro')
    pylab.plot(d,contrib.jacommands.weighted_local_average(d,c_cut,30),'go')
    pylab.plot(d,contrib.jacommands.weighted_local_average(d,numpy.abs(c_cut),30),'bo')
    
    pylab.figure()
    pylab.title('Correlation between distance and orr preference')
    pylab.plot(d,orr_diff,'ro')
    pylab.axhline(numpy.pi/4)
    pylab.plot(d,contrib.jacommands.weighted_local_average(d,orr_diff,30),'go')
    
    #pylab.figure()
    #pylab.title('Correlation between firing rate correlations and raw RFs correlations')
    #pylab.plot(c,cor_orig,'ro')
    
    #pylab.figure()
    #pylab.title('Correlation between firing rate correlations and distance')
    #pylab.plot(d,cor_orig,'ro')
    
    #pylab.figure()
    #pylab.title('Angular difference against orientation of proximit (<50) co-oriented pairs of cells')
    #pylab.scatter(angle50,angle_dif50,s=numpy.abs(corr50)*100,marker='o',c='r',cmap=pylab.cm.RdBu)
    #pylab.xlabel("average orienation of pair")
    #pylab.ylabel("angular difference")
    	 
    #pylab.figure()
    #pylab.title('Angular difference against orientation of proximit (<100) co-oriented pairs of cells')
    #pylab.scatter(angle100,angle_dif100,s=numpy.abs(corr100)*100,marker='o',cmap=pylab.cm.RdBu)
    #pylab.xlabel("average orienation of pair")
    #pylab.ylabel("angular difference")
	 
    pylab.figure()
    pylab.title('Histogram of orientations')
    pylab.hist(numpy.matrix(params)[:,3])
	 
def distance(locations,x,y):
    return  numpy.sqrt(numpy.power(locations[x][0] - locations[y][0],2)+numpy.power(locations[x][1] - locations[y][1],2))
  	 
def circular_distance(angle_a,angle_b):
    c= abs(angle_a - angle_b)
    if c > numpy.pi/2:
       c = numpy.pi-c
    return c		 

def RF_corr_centered(RF1,RF2,fraction,display=True):
    sx,sy = numpy.shape(RF1)	
	
    X = numpy.zeros((sx,sy))
    Y = numpy.zeros((sx,sy))
        
    for x in xrange(0,sx):
        for y in xrange(0,sy):
            X[x][y] = x
            Y[x][y] = y
    
    cgs = []
    RFs=[]
    
    cg1x = numpy.round(numpy.sum(numpy.sum(numpy.multiply(X,numpy.power(RF1,2))))/numpy.sum(numpy.sum(numpy.power(RF1,2))))
    cg1y = numpy.round(numpy.sum(numpy.sum(numpy.multiply(Y,numpy.power(RF1,2))))/numpy.sum(numpy.sum(numpy.power(RF1,2))))
    cg2x = numpy.round(numpy.sum(numpy.sum(numpy.multiply(X,numpy.power(RF2,2))))/numpy.sum(numpy.sum(numpy.power(RF2,2))))
    cg2y = numpy.round(numpy.sum(numpy.sum(numpy.multiply(Y,numpy.power(RF2,2))))/numpy.sum(numpy.sum(numpy.power(RF2,2))))
    
    
    RF1c = RF1[cg1x-sx*fraction:cg1x+sx*fraction,cg1y-sy*fraction:cg1y+sy*fraction]
    RF2c = RF2[cg2x-sx*fraction:cg2x+sx*fraction,cg2y-sy*fraction:cg2y+sy*fraction]
    
    if display:
	pylab.figure()
	pylab.subplot(2,1,1)
	pylab.imshow(RF1c,cmap=pylab.cm.RdBu)
	pylab.subplot(2,1,2)
	pylab.imshow(RF2c,cmap=pylab.cm.RdBu)
    
    return numpy.corrcoef(RF1c.flatten(),RF2c.flatten())[0][1]

def centre_of_gravity(matrix):
    sx,sy = numpy.shape(matrix)	
	
    X = numpy.zeros((sx,sy))
    Y = numpy.zeros((sx,sy))
    for x in xrange(0,sx):
        for y in xrange(0,sy):
            X[x][y] = x
            Y[x][y] = y
    
    x = numpy.sum(numpy.sum(numpy.multiply(X,matrix)))/numpy.sum(numpy.sum(matrix))/sx
    y = numpy.sum(numpy.sum(numpy.multiply(Y,matrix)))/numpy.sum(numpy.sum(matrix))/sy
    
    return (x,y)
	

def low_power(image,t): 
    z = numpy.fft.fft2(image)
    z = numpy.fft.fftshift(z)
    y = numpy.zeros(numpy.shape(z))
    (x,trash) = numpy.shape(y)
    c = x/2
    
    for i in xrange(0,x):
	for j in xrange(0,x):
	    if numpy.sqrt((c-i)*(c-i) + (c-j)*(c-j)) <= t:
	       y[i,j]=1.0
    z = numpy.multiply(z,y)
    z = numpy.fft.ifftshift(z)
    #pylab.figure()
    #pylab.imshow(y)
    #pylab.figure()
    #pylab.imshow(image)
    #pylab.colorbar()
    #pylab.figure()
    #pylab.imshow(numpy.fft.ifft2(z).real)
    #pylab.colorbar()
    return contrast(numpy.fft.ifft2(z).real) 
    
def band_power(image,t,t2): 
    z = numpy.fft.fft2(image)
    z = numpy.fft.fftshift(z)
    y = numpy.zeros(numpy.shape(z))
    (x,trash) = numpy.shape(y)
    c = x/2
    for i in xrange(0,x):
	for j in xrange(0,x):
	    if numpy.sqrt((c-i)*(c-i) + (c-j)*(c-j)) <= t:
	       if numpy.sqrt((c-i)*(c-i) + (c-j)*(c-j)) >= t2:		    
	       		y[i,j]=1.0
    z = numpy.multiply(z,y)
    z = numpy.fft.ifftshift(z)
    return contrast(numpy.fft.ifft2(z).real) 
    

def contrast(image):
    im = image - numpy.mean(image)
    return numpy.sqrt(numpy.mean(numpy.power(im,2)))	


def run_LIP():
	from scipy import linalg
	f = open("modelfitDB2.dat",'rb')
	import pickle
	dd = pickle.load(f)

	rfs_area1  = dd.children[0].children[0].data["ReversCorrelationRFs"]
	rfs_area2  = dd.children[1].children[0].data["ReversCorrelationRFs"]
	
	
	pred_act_area1  = dd.children[0].children[0].data["ReversCorrelationPredictedActivities"][0:1260,:]
	pred_act_area2  = dd.children[1].children[0].data["ReversCorrelationPredictedActivities"]
	
	
	print numpy.shape(pred_act_area1)
	print numpy.shape(pred_act_area2)
	
	print numpy.shape(rfs_area2)
	print numpy.shape(rfs_area1)
	
	rfs = numpy.concatenate((rfs_area1,rfs_area2),axis=0) 
	
	pred_act = numpy.concatenate((pred_act_area1,pred_act_area2),axis=1)
	
	
	
	corr_coef = []
	
	params={}
    	params["normalize_activities"] = __main__.__dict__.get('NormalizeActivities',True)
	params["cut_out"] = __main__.__dict__.get('CutOut',False)

	
	dataset_area1 = loadSimpleDataSet("Mice/2009_11_04/region3_stationary_180_15fr_103cells_on_response_spikes",1260,103)
	dataset_area2 = loadSimpleDataSet("Mice/2009_11_04/region5_stationary_180_15fr_103cells_on_response_spikes",1260,55)
	dataset = mergeDatasets(dataset_area1,dataset_area2)
	
	
        (index,data) = dataset
        index+=1
    	dataset = (index,data)
    	
	
	dataset = averageRangeFrames(dataset,0,1)
    	dataset = averageRepetitions(dataset)
	
	
        if False:	
		(validation_data_set,dataset) = splitDataset(dataset,200)
		validation_inputs=generateInputs(validation_data_set,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",100,1.8,offset=1000)
        else:
		validation_data_set_area1 = loadSimpleDataSet("Mice/2009_11_04/region3_50stim_10reps_15fr_103cells_on_response_spikes",50,103,10)
		validation_data_set_area2 = loadSimpleDataSet("Mice/2009_11_04/region5_50stim_10reps_15fr_103cells_on_response_spikes",50,55,8)
		
		
		#(validation_data_set_area1,trash) = splitDataset(validation_data_set_area1,40)
		#(validation_data_set_area2,trash) = splitDataset(validation_data_set_area2,40)
	        ff1  = analyse_reliability(validation_data_set_area1,{})
		ff2  = analyse_reliability(validation_data_set_area2,{})
		ff = numpy.append(numpy.array(ff1),numpy.array(ff2))
		
		validation_data_set_area1 = averageRangeFrames(validation_data_set_area1,0,1)
		validation_data_set_area1 = averageRepetitions(validation_data_set_area1)
		
		validation_data_set_area2 = averageRangeFrames(validation_data_set_area2,0,1)
		validation_data_set_area2 = averageRepetitions(validation_data_set_area2)
		
		validation_data_set = mergeDatasets(validation_data_set_area1,validation_data_set_area2)
		
		validation_inputs=generateInputs(validation_data_set,"/home/antolikjan/topographica/topographica/Mice/2009_11_04/","/20091104_50stimsequence/50stim%04d.tif",100,1.8,offset=0)
	
	training_set = generateTrainingSet(dataset)
	validation_set = generateTrainingSet(validation_data_set)
		
        #discard low image mean images
	image_mean=[]	
	for i in xrange(0,len(validation_inputs)):
	    image_mean.append(numpy.mean(validation_inputs[i]))
	idx = numpy.argsort(image_mean)[0:14]
	#idx=[]
	
	print idx
	print "Deleting trials with low mean of images"
	validation_inputs = numpy.delete(validation_inputs, idx, axis = 0)	
	validation_set = numpy.delete(validation_set, idx, axis = 0)
		
	#compute neurons mean before normalization
	neuron_mean = numpy.mean(training_set,axis=0)
	neuron_mean_val = numpy.mean(validation_set,axis=0)
	if params["normalize_activities"]:
		(a,v) = compute_average_min_max(training_set)
		training_set = normalize_data_set(training_set,a,v)
		validation_set = normalize_data_set(validation_set,a,v)
	
	if params["cut_out"]:
		(x,y)= numpy.shape(validation_inputs[0])
		validation_inputs = cut_out_images_set(validation_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))

	#generate predicted activities
	pred_val_act = numpy.zeros((len(validation_inputs),len(rfs)))
	for inp in xrange(0,len(validation_inputs)):
            for rf in xrange(0,len(rfs)):
		pred_val_act[inp,rf] = numpy.sum(numpy.multiply(numpy.mat(validation_inputs[inp]),numpy.mat(rfs[rf])))

	#of = run_nonlinearity_detection(numpy.mat(training_set),pred_act,10,False)
	ofs = fit_sigmoids_to_of(numpy.mat(training_set),numpy.mat(pred_act))
	
	pred_act_t = apply_sigmoid_output_function(numpy.mat(pred_act),ofs)
	pred_val_act_t= apply_sigmoid_output_function(numpy.mat(pred_val_act),ofs)
		
    	(num_pres,num_neurons) = numpy.shape(training_set)
    
        pve = []
        for i in xrange(0,158):
	    corr_coef.append(numpy.corrcoef(pred_act_t.T[i], training_set.T[i])[0][1])
	    pve.append(1-numpy.sum(numpy.power(pred_act_t.T[i]- training_set.T[i],2)) / numpy.sum(numpy.power(numpy.mean(training_set.T[i])- training_set.T[i],2)))
	    
	print "The mean FEV : ", numpy.mean(pve)
	print "The mean correltation coefficient : ", numpy.mean(corr_coef)
	
	print "Mean variance of training set:", numpy.mean(numpy.power(numpy.std(training_set,axis=0),2))
	print "Mean variance of validation set:", numpy.mean(numpy.power(numpy.std(validation_set,axis=0),2))
	
	val_pve = []
	val_corr_coef = []
        for i in xrange(0,158):
	    val_corr_coef.append(numpy.corrcoef(pred_val_act_t.T[i], validation_set.T[i])[0][1])
	    val_pve.append(1-numpy.sum(numpy.power(pred_val_act_t.T[i]- validation_set.T[i],2)) / numpy.sum(numpy.power(numpy.mean(validation_set.T[i])- validation_set.T[i],2)))
	print "The mean FEV on validation set: ", numpy.mean(val_pve)
	print "The mean correlation coeficient on validation set: ", numpy.mean(val_corr_coef)
	
	pylab.figure()
	pylab.title("Histogram of explained variance")
	pylab.hist(pve)
	
	pylab.figure()
	pylab.title("Histogram of neural response means")
	pylab.hist(neuron_mean)
	
    	#discard low correlation neurons
	r=[]
	corr=[]
	tresh=[]
        for i in xrange(0,30):
		f = numpy.nonzero((numpy.array(pve) < ((i-10.0)/50.0))*1.0)[0]
	        tresh.append(((i-10.0)/50.0))
		training_set_good = numpy.delete(training_set, f, axis = 1)
		pred_act_good = numpy.delete(pred_act_t, f, axis = 1)
		validation_set_good = numpy.delete(validation_set, f, axis = 1)
    		pred_val_act_good = numpy.delete(pred_val_act_t, f, axis = 1)
		(rank,correct,tr) = performIdentification(validation_set_good,pred_val_act_good)
		r.append(numpy.mean(rank))
		corr.append(correct)
	
	f = numpy.nonzero((numpy.array(pve) < 0.22)*1.0)[0]
	print f 
	#f = []
	training_set = numpy.delete(training_set, f, axis = 1)
	pred_act = numpy.delete(pred_act, f, axis = 1)
	pred_act_t = numpy.delete(pred_act_t, f, axis = 1)
	validation_set = numpy.delete(validation_set, f, axis = 1)
    	pred_val_act_t = numpy.delete(pred_val_act_t, f, axis = 1)
	pred_val_act = numpy.delete(pred_val_act, f, axis = 1)

	(num_pres,num_neurons) = numpy.shape(training_set)
	
	pylab.figure()
	pylab.xlabel("tresh")
	pylab.ylabel("correct")
	pylab.plot(tresh,corr)
	
	pylab.figure()
	pylab.xlabel("tresh")
	pylab.ylabel("rank")
	pylab.plot(tresh,r)
	
	pylab.figure()
	pylab.title('Histogram of fraction of explained variance on validation set')
	pylab.hist(val_pve)
	
	pylab.figure()
	pylab.title("Correlation between neuronal mean response and training set FVE")
	pylab.xlabel("neuronal response mean")
	pylab.ylabel("FVE")
	pylab.plot(neuron_mean,pve,'ro')

	pylab.figure()
	pylab.title("Correlation between neuronal mean response and validation set FVE")
	pylab.xlabel("neuronal response mean")
	pylab.ylabel("FVE")
	pylab.plot(neuron_mean,val_pve,'ro')

	pylab.figure()
	pylab.title("Correlation between neuronal mean on validation set response and validation set FVE")
	pylab.xlabel("neuronal response mean")
	pylab.ylabel("FVE")
	pylab.plot(neuron_mean_val,val_pve,'ro')
	
	pylab.figure()
	pylab.title('scatter plot of fraction of explained variance on training set against validation set')
	pylab.plot(val_pve,pve,'ro')
	pylab.xlabel('validation set')
	pylab.ylabel('training set')
	
	(ranks,correct,tr) = performIdentification(validation_set,pred_val_act)
	(tf_ranks,tf_correct,pred) = performIdentification(validation_set,pred_val_act_t)
	
	print "Correct:", correct , "Mean rank:", numpy.mean(ranks) 
	print "TFCorrect:", tf_correct , "Mean tf_rank:", numpy.mean(tf_ranks)
	
	pylab.figure()
	pylab.title("Ranks histogram")
	pylab.xlabel("ranks")
	pylab.hist(tf_ranks,bins=numpy.arange(0,len(tf_ranks),1))
	
	errors=[]
	bp=[]
	lp5=[]
	lp6=[]
	lp7=[]
	lp8=[]
	lp9=[]
	lp10=[]
	
	image_contrast=[]
	response_mean=[]
	image_mean=[]
	corr_of_pop_resp=[]
	
	
	for i in xrange(0,len(pred_val_act)):
	    errors.append(numpy.sum(numpy.power(pred_val_act_t[i] - validation_set[i],2)) / 
	                  numpy.sum(numpy.power(validation_set[i] - numpy.mean(validation_set[i]),2)))
			  
	    corr_of_pop_resp.append(numpy.corrcoef(pred_val_act_t[i],validation_set[i],2)[0][1])
	    bp.append(band_power(validation_inputs[i],7,3))
	    lp5.append(low_power(validation_inputs[i],5))
	    lp6.append(low_power(validation_inputs[i],6))
	    lp7.append(low_power(validation_inputs[i],7))
	    lp8.append(low_power(validation_inputs[i],8))
	    lp9.append(low_power(validation_inputs[i],9))
	    lp10.append(low_power(validation_inputs[i],10))
	    image_contrast.append(contrast(validation_inputs[i]))
	    response_mean.append(numpy.mean(training_set[i]))
	    image_mean.append(numpy.mean(validation_inputs[i]))
 	
	pylab.figure()
	pylab.title("Correlation between prediction error and contrast of band-passed images")
	pylab.plot(errors,bp,'ro')
	pylab.xlabel("prediction error")
	pylab.ylabel("band pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between prediction error and contrast of low-passed images")
	pylab.plot(errors,lp7,'ro')
	pylab.xlabel("prediction error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between prediction error and basic contrast of images")
	pylab.plot(errors,image_contrast,'ro')
	pylab.xlabel("prediction error")
	pylab.ylabel("basic contrast")

	pylab.figure()
	pylab.title("Correlation between correlation of pop resp and contrast of band-passed images")
	pylab.plot(corr_of_pop_resp,bp,'ro')
	pylab.xlabel("correlation of pop resp")
	pylab.ylabel("band pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between correlation of pop resp and contrast of low-passed images")
	pylab.plot(corr_of_pop_resp,lp7,'ro')
	pylab.xlabel("correlation of pop resp")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between correlation of pop resp and basic contrast of images")
	pylab.plot(corr_of_pop_resp,image_contrast,'ro')
	pylab.xlabel("correlation of pop resp")
	pylab.ylabel("basic contrast")

	pylab.figure()
	pylab.xlabel("fano factor")
	pylab.ylabel("correlation coef")
	pylab.plot(ff,corr_coef,'ro')
	
	pylab.figure()
	pylab.xlabel("neuronal response mean")
	pylab.ylabel("correlation coef")
	pylab.plot(neuron_mean,corr_coef,'ro')
	
	pylab.figure()
	pylab.xlabel("neuronal response mean")
	pylab.ylabel("fano factor")
	pylab.plot(neuron_mean,ff,'ro')
	
	pylab.figure()
	pylab.title("Correlation between fano factor and FVE")
	pylab.xlabel("fano factor")
	pylab.ylabel("FVE")
	pylab.plot(ff,pve,'ro')

	
	print "final training set shape: ", pylab.shape(training_set)
	
        pylab.figure()
	pylab.hist(tf_ranks,bins=numpy.arange(0,len(tf_ranks),1))
    	pylab.title("Histogram of ranks after application of transfer function")
	
	pylab.figure()
	pylab.title("Correlation between correlation of pop resp and rank")
	pylab.plot(corr_of_pop_resp,tf_ranks,'ro')
	pylab.xlabel("correlation of pop resp")
	pylab.ylabel("rank") 
	
	pylab.figure()
	pylab.title("Correlation between rand and  prediction error")
	pylab.plot(tf_ranks,errors,'ro')
	pylab.ylabel("prediction error")
	pylab.xlabel("rank")

	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of band-passed images")
	pylab.plot(tf_ranks,bp,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("band pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of low-passed images, tresh=5")
	pylab.plot(tf_ranks,lp5,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of low-passed images, tresh=6")
	pylab.plot(tf_ranks,lp6,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of low-passed images, tresh=7")
	pylab.plot(tf_ranks,lp7,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of low-passed images, tresh=8")
	pylab.plot(tf_ranks,lp8,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of low-passed images, tresh=9")
	pylab.plot(tf_ranks,lp9,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and contrast of low-passed images, tresh=10")
	pylab.plot(tf_ranks,lp10,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("low pass contrast")
	
	pylab.figure()
	pylab.title("Correlation between rank error and basic contrast of images")
	pylab.plot(tf_ranks,image_contrast,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("basic contrast")
	
	print "Bad images"
	print image_mean[11]
	
	pylab.figure()
	pylab.title("Correlation between rank error and mean of images")
	pylab.plot(tf_ranks,image_mean,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("image mean")

        pylab.figure()
	pylab.title("Correlation between rank error and measured response mean")
	pylab.plot(tf_ranks,response_mean,'ro')
	pylab.xlabel("rank error")
	pylab.ylabel("measured response mean")
	
	pylab.figure()
	pylab.title("Correlation between correlation of pop resp and response mean")
	pylab.plot(corr_of_pop_resp,response_mean,'ro')
	pylab.xlabel("correlation of pop resp")
	pylab.ylabel("response mean")
	
	pylab.figure()
	pylab.title("Correlation between correlation of pop resp and image mean")
	pylab.plot(corr_of_pop_resp,image_mean,'ro')
	pylab.xlabel("correlation of pop resp")
	pylab.ylabel("image mean")
	
	pylab.figure()
	pylab.title("Correlation between measured response mean and image mean")
	pylab.plot(response_mean,image_mean,'ro')
	pylab.xlabel("response mean")
	pylab.ylabel("image mean")
	
	pylab.figure()
	pylab.title("Correlation between measured response mean and image basic contrast")
	pylab.plot(response_mean,image_contrast,'ro')
	pylab.xlabel("response mean")
	pylab.ylabel("image basic contrast")
	
	pylab.figure()
	pylab.title("Correlation between measured response mean and contrast of low passed image t=7")
	pylab.plot(response_mean,lp7,'ro')
	pylab.xlabel("response mean")
	pylab.ylabel("low passed image contrast")
	
	
	fig = pylab.figure()
	from mpl_toolkits.mplot3d import Axes3D
	ax = Axes3D(fig)

	ax.scatter(lp7,image_mean,tf_ranks)
	ax.set_xlabel("contrast")
	ax.set_ylabel("image mean")
	ax.set_zlabel("rank")
	
	fig = pylab.figure()
	ax = Axes3D(fig)

	ax.scatter(lp7,corr_of_pop_resp,tf_ranks)
	ax.set_xlabel("contrast")
	ax.set_ylabel("corr_of_pop_resp")
	ax.set_zlabel("rank")
	
	
	(later_pred_act,later_pred_val_act) = later_interaction_prediction(training_set,pred_act_t,validation_set,pred_val_act_t)
	
	#of = run_nonlinearity_detection(numpy.mat(training_set),later_pred_act,10,False)
	ofs = fit_sigmoids_to_of(numpy.mat(training_set),numpy.mat(later_pred_act))
        later_pred_act_t = apply_sigmoid_output_function(later_pred_act,ofs)
        later_pred_val_act_t= apply_sigmoid_output_function(later_pred_val_act,ofs)
	#later_pred_act_t = later_pred_act
	#later_pred_val_act_t = later_pred_val_act
	
	(ranks,correct,pred) = performIdentification(validation_set,later_pred_val_act)
	print "After lateral identification> Correct:", correct , "Mean rank:", numpy.mean(ranks)

	(tf_ranks,tf_correct,pred) = performIdentification(validation_set,later_pred_val_act_t)
	print "After lateral identification> TFCorrect:", tf_correct , "Mean tf_rank:", numpy.mean(tf_ranks)
	
	
	lat_pve = []
	lat_corr_coef = []
        for i in xrange(0,num_neurons):
	    lat_corr_coef.append(numpy.corrcoef(later_pred_act_t.T[i], training_set.T[i])[0][1])
	    lat_pve.append(1-numpy.sum(numpy.power(later_pred_act_t.T[i]- training_set.T[i],2)) / numpy.sum(numpy.power(numpy.mean(training_set.T[i])- training_set.T[i],2)))
	    
	lat_val_pve = []
	lat_val_corr_coef = []
        for i in xrange(0,num_neurons):
	    lat_val_corr_coef.append(numpy.corrcoef(later_pred_val_act_t.T[i], validation_set.T[i])[0][1])
	    lat_val_pve.append(1-numpy.sum(numpy.power(later_pred_val_act_t.T[i]- validation_set.T[i],2)) / numpy.sum(numpy.power(numpy.mean(validation_set.T[i])- validation_set.T[i],2)))
	    
	    
	print "The mean FEV after lateral interactions: ", numpy.mean(lat_pve)
	print "The mean correlation coeficient after lateral interactions: ", numpy.mean(lat_corr_coef)

	print "The mean FEV on validation set after lateral interactions: ", numpy.mean(lat_val_pve)
	print "The mean correlation coeficient on validation set  after lateral interactions: ", numpy.mean(lat_val_corr_coef)
	return 
	g = 1
	for (x,i) in pred:
	    
	    #if x==i: continue
	    pylab.figure()
	    pylab.subplot(3,1,1)
	    pylab.imshow(validation_inputs[i],vmin=0.0,vmax=1.0,interpolation='nearest',cmap=pylab.cm.gray)
	    pylab.axis('off')
	    pylab.subplot(3,1,2)
	    pylab.imshow(validation_inputs[x],vmin=0.0,vmax=1.0,interpolation='nearest',cmap=pylab.cm.gray)
	    pylab.axis('off')
	    
	    pylab.subplot(3,1,3)
	    pylab.plot(numpy.array(pred_val_act_t)[i],'ro',label='Predicted activity')
	    pylab.plot(validation_set[i],'bo',label='Measured activity')
	    pylab.axhline(y=numpy.mean(validation_set[i]),linewidth=1, color='b')
	    pylab.axhline(y=numpy.mean(pred_val_act_t[i]),linewidth=1, color='r')
	    if x != i:
	       pylab.plot(validation_set[x],'go',label='Most similar')
	       pylab.axhline(y=numpy.mean(validation_set[x]),linewidth=1, color='g')
	    pylab.legend()
            g+=1


def performIdentification(responses,model_responses):
    correct=0
    ranks=[]
    pred=[]
    for i in xrange(0,len(responses)):
        tmp = []
        for j in xrange(0,len(responses)):
            tmp.append(numpy.sqrt(numpy.mean(numpy.power(numpy.mat(responses)[i]-model_responses[j],2))))
	    
	    #/numpy.sqrt(numpy.var(numpy.mat(responses)[i]))
        x = numpy.argmin(tmp)
	z = tmp[i]
	ranks.append(numpy.nonzero((numpy.sort(tmp)==z)*1.0)[0][0])
        if (x == i): correct+=1
	pred.append((x,i))
    return (ranks,correct,pred)


def sortOutLoading(db_node):
    params = {}
    params["density"] = __main__.__dict__.get('density', 20) 
    #params["dataset"] = "Mice/20091110_19_16_53/(20091110_19_16_53)-_retinotopy_region4_stationary_180_15fr_66cells_on_response_spikes_DELTA"
    #params["dataset"] = "Mice/2009_11_04/region3_stationary_180_15fr_103cells_on_response_spikes"
    params["dataset"] = "Mice/2009_11_04/region5_stationary_180_15fr_103cells_on_response_spikes"
    #params["dataset"] = "Mice/20090925_14_36_01/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_2700images_on_&_off_response"
    
    params["num_cells"] = 55
    params["clump_mag"] = __main__.__dict__.get('ClumpMag',0.1)
    params["normalize_inputs"] = __main__.__dict__.get('NormalizeInputs',False)
    params["normalize_activities"] = __main__.__dict__.get('NormalizeActivities',True)
    params["cut_out"] = __main__.__dict__.get('CutOut',False)
    params["validation_set_fraction"] = 40
    params["sepparate_validation_set"] = True
    
    db_node = db_node.get_child(params)
    
    density=__main__.__dict__.get('density', 20)
    
    dataset = loadSimpleDataSet(params["dataset"],1260,params["num_cells"])
    (index,data) = dataset
    index+=1
    dataset = (index,data)
    dataset = averageRangeFrames(dataset,0,1)
    dataset = averageRepetitions(dataset)


    if not params["sepparate_validation_set"]:	
	(validation_data_set,dataset) = splitDataset(dataset,params["validation_set_fraction"])
	validation_set = generateTrainingSet(validation_data_set)
	ff = numpy.arange(0,params["num_cells"],1)*0
	validation_inputs=generateInputs(validation_data_set,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",params["density"],1.8,offset=1000)
    else:
	#valdataset = loadSimpleDataSet("Mice/2009_11_04/region3_50stim_10reps_15fr_103cells_on_response_spikes",50,params["num_cells"],10)
	valdataset = loadSimpleDataSet("Mice/2009_11_04/region5_50stim_10reps_15fr_103cells_on_response_spikes",50,params["num_cells"],8)
	(valdataset,trash) = splitDataset(valdataset,params["validation_set_fraction"])
	ff  = analyse_reliability(valdataset,params)
	valdataset = averageRangeFrames(valdataset,0,1)
    	valdataset = averageRepetitions(valdataset)
        validation_set = generateTrainingSet(valdataset)
    	validation_inputs=generateInputs(valdataset,"/home/antolikjan/topographica/topographica/Mice/2009_11_04/","/20091104_50stimsequence/50stim%04d.tif",params["density"],1.8,offset=0)

    
    training_set = generateTrainingSet(dataset)
    training_inputs=generateInputs(dataset,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",params["density"],1.8,offset=1000)

    
    if params["normalize_inputs"]:
       avgRF = compute_average_input(training_inputs)
       training_inputs = normalize_image_inputs(training_inputs,avgRF)
       validation_inputs = normalize_image_inputs(validation_inputs,avgRF)
    
    if params["normalize_activities"]:
        #(a,v) = compute_average_min_max(numpy.concatenate((training_set,validation_set),axis=0))
        (a,v) = compute_average_min_max(training_set)
        training_set = normalize_data_set(training_set,a,v)
        validation_set = normalize_data_set(validation_set,a,v)
    
    if params["cut_out"]:
        (x,y)= numpy.shape(training_inputs[0])
        training_inputs = cut_out_images_set(training_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))
        validation_inputs = cut_out_images_set(validation_inputs,int(y*0.55),(int(x*0.0),int(y*0.3)))
        (sizex,sizey) = numpy.shape(training_inputs[0])
    
    (sizex,sizey) = numpy.shape(training_inputs[0])
    training_inputs = generate_raw_training_set(training_inputs)
    validation_inputs = generate_raw_training_set(validation_inputs)
    
    db_node.add_data("training_inputs",training_inputs,force=True)
    db_node.add_data("training_set",training_set,force=True)
    db_node.add_data("validation_inputs",validation_inputs,force=True)
    db_node.add_data("validation_set",validation_set,force=True)
    db_node.add_data("Fano Factors",ff,force=True)
    
    return (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node)






from pygene.organism import Organism
from pygene.gene import FloatGene
class ComplexCellOrganism(Organism):
	training_set = []
	training_inputs = []
	
	def fitness(self):
		z,t = numpy.shape(self.training_inputs) 
		x =  self[str(0)]
		y =  self[str(1)]
		sigma = self[str(2)]*0.1
		angle = self[str(3)]*numpy.pi
		p =  self[str(4)]*numpy.pi*2
		f = self[str(5)]*10
		ar = self[str(6)]*2.5
		alpha = self[str(7)]
		dx = numpy.sqrt(t)
		dy = dx
		g =  numpy.mat(Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=x-0.5,y=y-0.5,xdensity=dx,ydensity=dy,size=sigma,orientation=angle,phase=p,aspect_ratio=ar)() * alpha)
		r1 = self.training_inputs * g.flatten().T
		return numpy.mean(numpy.power(r1-self.training_set,2))  

rand = UniformRandom(seed=513)
class CCGene(FloatGene):
      randMin=0.0
      randMax=1.0
      #def mutate(self):
#	  self.value = self.value + self.value*2.0*(0.5-rand())

def GeneticAlgorithms():
    from pygene.gamete import Gamete
    from pygene.population import Population
    
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)
    training_set = dd.children[0].data["training_set"][0:1800,:]
    training_inputs = dd.children[0].data["training_inputs"][0:1800,:]
    
    #dd = contrib.dd.DB2(None)
    
    #(sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = sortOutLoading(dd)
    
    
    
    genome = {}
    for i in range(8):
    	genome[str(i)] = CCGene
    
    ComplexCellOrganism.genome = genome
    ComplexCellOrganism.training_set = numpy.mat(training_set)[:,0]
    ComplexCellOrganism.training_inputs = numpy.mat(training_inputs)
    	  
    class CPopulation(Population):
	  species = ComplexCellOrganism
	  initPopulation = 200
	  childCull = 100
	  childCount = 500
	  incest=10
	  i = 0
	  
    pop = CPopulation()
    
    pylab.ion()
    pylab.hold(False)
    pylab.figure()
    pylab.show._needmain=False
    pylab.show()
    pylab.figure()
    while True:
    	pop.gen()
	best = pop.best()
	print "fitness:" , (best.fitness())
	z,t = numpy.shape(training_inputs) 
	x =  best[str(0)]
	y =  best[str(1)]
	sigma = best[str(2)]*0.1
	angle = best[str(3)]*numpy.pi
	p =  best[str(4)]*numpy.pi*2
	f = best[str(5)]*10
	ar = best[str(6)]*2.5
	alpha = best[str(7)]
	dx = numpy.sqrt(t)
	dy = dx
	g =  numpy.mat(Gabor(bounds=BoundingBox(radius=0.5),frequency=f,x=x-0.5,y=y-0.5,xdensity=dx,ydensity=dy,size=sigma,orientation=angle,phase=p,aspect_ratio=ar)() * alpha)
	m=numpy.max(numpy.abs(numpy.min(g)),numpy.abs(numpy.max(g)))
	pylab.subplot(2,1,1)
	pylab.imshow(g,vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
	
	pylab.show._needmain=False
    	pylab.show()

def runSurrondStructureDetection():
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)
			
    ddnode = dd.children[0]
    act = ddnode.data["training_set"]
    val_act = ddnode.data["validation_set"]
    ddnode = ddnode.children[0]
    dataset = loadSimpleDataSet("Mice/2009_11_04/region3_stationary_180_15fr_103cells_on_response_spikes",1800,103)
    (index,data) = dataset
    index+=1
    dataset = (index,data)
    valdataset = loadSimpleDataSet("Mice/2009_11_04/region3_50stim_10reps_15fr_103cells_on_response_spikes",50,103,10)
    (valdataset,trash) = splitDataset(valdataset,40)
    
    training_inputs=generateInputs(dataset,"/home/antolikjan/topographica/topographica/Flogl/DataOct2009","/20090925_image_list_used/image_%04d.tif",__main__.__dict__.get('density', 20),1.8,offset=1000)
    
    validation_inputs=generateInputs(valdataset,"/home/antolikjan/topographica/topographica/Mice/2009_11_04/","/20091104_50stimsequence/50stim%04d.tif",__main__.__dict__.get('density', 20),1.8,offset=0)
    
    (sizex,sizey) = numpy.shape(training_inputs[0])
    
    
    
    pred_act = ddnode.data["ReversCorrelationPredictedActivities+TF"]
    pred_val_act = ddnode.data["ReversCorrelationPredictedValidationActivities+TF"]
    #print pred_act
    new_target_act =  numpy.divide(act+0.7,pred_act+0.7)
    new_val_target_act =  numpy.divide(val_act+0.7,pred_val_act+0.7)
    
    training_inputs = generate_raw_training_set(training_inputs)
    validation_inputs = generate_raw_training_set(validation_inputs)
    
    print "Mins"
    print numpy.min(pred_act)
    print numpy.min(pred_val_act)
    print numpy.min(act)
    print numpy.min(val_act)
    
    
    (e,te,c,tc,RFs,pa,pva,corr_coef,corr_coef_tf) = regulerized_inverse_rf(training_inputs,new_target_act,sizex,sizey,100,validation_inputs,new_val_target_act,contrib.dd.DB2(None),True)
    
    ofs = fit_sigmoids_to_of(numpy.mat(act+0.7),numpy.mat(numpy.multiply(pred_act+0.7,pa)))
    pa_t = apply_sigmoid_output_function(numpy.multiply(pred_act+0.7,pa),ofs)
    pva_t = apply_sigmoid_output_function(numpy.multiply(pred_val_act+0.7,pva),ofs)
    
    print numpy.min(pva)
    print numpy.min(pva_t)
    
    print performIdentification(val_act+0.7,pred_val_act+0.7)
    print performIdentification(val_act+0.7,numpy.multiply(pred_val_act+0.7,pva))
    print performIdentification(val_act+0.7,pva_t)


def runSTCandSTAtest():
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)
    
    
    
    STCact = dd.children[6].data["STCact"]
    STCrfs = dd.children[6].data["STCrfs"]
    predicted_activities = dd.children[0].children[0].data["ReversCorrelationPredictedActivities"]
    tf_predicted_activities = dd.children[0].children[0].data["ReversCorrelationPredictedActivities+TF"]
    predicted_validation_activities = dd.children[0].children[0].data["ReversCorrelationPredictedValidationActivities"]
    tf_validation_predicted_activities = dd.children[0].children[0].data["ReversCorrelationPredictedValidationActivities+TF"]
    target_act = dd.children[6].data["training_set"]
    target_val_act = dd.children[6].data["validation_set"]
    training_inputs = dd.children[6].data["training_inputs"]
    validation_inputs = dd.children[6].data["validation_inputs"]
    
    model_predicted_activities = numpy.mat(numpy.zeros(numpy.shape(predicted_activities)))
    model_validation_predicted_activities = numpy.mat(numpy.zeros(numpy.shape(predicted_validation_activities)))
    
    
    for (rfs,i) in zip(STCrfs,xrange(0,len(STCrfs))):
	(ei,vv,avv,em,ep) = rfs	    
	a = predicted_activities[:,i]
	a_v = predicted_validation_activities[:,i]
	for j in avv:
	    r = ei[j,:].real
	    o = run_nonlinearity_detection((training_inputs*r.T),numpy.mat(target_act)[:,i],10,display=False)
	    act = apply_output_function(training_inputs*r.T,o)
	    val_act = apply_output_function(validation_inputs*r.T,o)
	    a = numpy.concatenate((a,act),axis=1)
	    a_v = numpy.concatenate((a_v,val_act),axis=1)
	mf = ModelFit()
	mf.learning_rate = __main__.__dict__.get('lr',0.01)
	mf.epochs=__main__.__dict__.get('epochs',100)
	mf.num_of_units = 1
	mf.init()
	
	
	(err,stop,min_errors) = mf.trainModel(a,numpy.mat(target_act)[:,i],a_v,numpy.mat(target_val_act)[:,i])
	
	print numpy.shape(numpy.mat(model_predicted_activities)[:,i])
	print numpy.shape(mf.returnPredictedActivities(mat(a))[:,0]) 
	model_predicted_activities[:,i] = mf.returnPredictedActivities(mat(a))[:,0]
	model_validation_predicted_activities[:,i] = mf.returnPredictedActivities(mat(a_v))[:,0]

    #(ranks,correct,cc) = performIdentification(target_act,model_predicted_activities)
    #print "After lateral identification> TFCorrect:", tf_correct , "Mean tf_rank:", numpy.mean(tf_ranks)
    (ranks,correct,cc) = performIdentification(target_val_act,predicted_validation_activities)
    print "Simple Correct:", correct , "Mean tf_rank:", numpy.mean(ranks), "Percentage:" ,correct/(len(ranks)*1.0)*100 ,"%"
    (ranks,correct,cc) = performIdentification(target_val_act,model_validation_predicted_activities)
    print "Simple + Complex Correct:", correct , "Mean tf_rank:", numpy.mean(ranks), "Percentage:" ,correct/(len(ranks)*1.0)*100 ,"%"	
    
    ofs = run_nonlinearity_detection(numpy.mat(target_act),model_predicted_activities,10,display=True)
    pred_act_t = apply_output_function(model_predicted_activities,ofs)
    pred_val_act_t= apply_output_function(model_validation_predicted_activities,ofs)

    (ranks,correct,cc) = performIdentification(target_val_act,pred_val_act_t)
    print "Simple + Complex + TF Correct:", correct , "Mean tf_rank:", numpy.mean(ranks), "Percentage:" ,correct/(len(ranks)*1.0)*100 ,"%"	
	
	

def analyseInhFiring():
    dataset = loadSimpleDataSet("Mice/2009716_17_03_10/(20090716_17_03_10)-_orientation_classic_region9_15hz_8oris_4grey_2mov_DFOF",6138,27,transpose=True)
    
    ts = generateTrainingSet(dataset)
    
    (x,y) = numpy.shape(ts)
    
    #ts = ts[0:6000,:]
    
    inh = numpy.array([2, 20, 22,23,26])
    inh = inh - 1.0

    exc  = numpy.delete(ts,inh,axis=1)
    inh  = numpy.delete(ts,numpy.delete(numpy.arange(0,y,1),inh),axis=1)	
    
    exc_base = numpy.concatenate((exc[0:93,:] , exc[0:93,-93:]),axis=0)
    inh_base = numpy.concatenate((inh[0:93,:] , inh[0:93,-93:]),axis=0)

    exc = exc[93:-93,:]
    inh = inh[93:-93,:]
    
    print numpy.shape(exc)
    
    exc_average_trace = [numpy.mean(e.reshape(93,64),axis=0) for e in exc.T]
    inh_average_trace = [numpy.mean(i.reshape(93,64),axis=0) for i in inh.T]

    print numpy.shape(exc_average_trace)
    
    pylab.figure()
    pylab.title("Inhibitory neurons")
    for e in exc.T:
	pylab.plot(e)
    pylab.ylim((-0.07,0.2))
    
    pylab.figure()
    pylab.title("Excitatory neurons")
    for i in inh.T:
	pylab.plot(i)
    pylab.ylim((-0.07,0.2))
    
    pylab.figure()
    
    pylab.title("Trace excitatory")
    for e in exc_average_trace:
	pylab.plot(e)
    pylab.ylim((-0.0,0.05))
    
    pylab.figure()
    pylab.title("Trace inhibitory")
    for i in inh_average_trace:
	pylab.plot(i)
    pylab.ylim((-0.0,0.05))
    
    pylab.figure()
    pylab.title("baseline: Excitatory neurons")
    for e in exc_base.T:
	pylab.plot(e)
    pylab.ylim((-0.05,0.2))
  
    pylab.figure()
    pylab.title("baseline: Inhibitory neurons")
    for i in inh_base.T:
	pylab.plot(i)
    pylab.ylim((-0.05,0.2))
    
    
    pylab.figure()
    pylab.title('mean vs max of neurons')
    pylab.plot(numpy.mean(exc.T,axis=1),numpy.max(exc.T,axis=1),'ro')	
    pylab.plot(numpy.mean(inh.T,axis=1),numpy.max(inh.T,axis=1),'go')

    pylab.figure()
    pylab.title('mean vs variance of neurons')
    pylab.plot(numpy.mean(exc.T,axis=1),numpy.var(exc.T,axis=1),'ro')	
    pylab.plot(numpy.mean(inh.T,axis=1),numpy.var(inh.T,axis=1),'go')

    pylab.figure()
    pylab.title('mean triggered vs mean at base')
    pylab.plot(numpy.mean(exc.T,axis=1),numpy.mean(exc_base.T,axis=1),'ro')	
    pylab.plot(numpy.mean(inh.T,axis=1),numpy.mean(inh_base.T,axis=1),'go')


    exc_fft  = [numpy.fft.fft(e) for e in exc.T]
    inh_fft  = [numpy.fft.fft(i) for i in inh.T]

    exc_fft_power  = [numpy.abs(e) for e in exc_fft]
    inh_fft_power  = [numpy.abs(e) for e in inh_fft]

    exc_fft_phase  = [numpy.angle(e) for e in exc_fft]
    inh_fft_phase  = [numpy.angle(e) for e in inh_fft]


    
    
    exc_fft_base  = [numpy.fft.fft(e) for e in exc_base.T]
    inh_fft_base  = [numpy.fft.fft(i) for i in inh_base.T]

    exc_fft_power_base  = [numpy.abs(e) for e in exc_fft_base]
    inh_fft_power_base  = [numpy.abs(e) for e in inh_fft_base]

    exc_fft_phase_base  = [numpy.angle(e) for e in exc_fft_base]
    inh_fft_phase_base  = [numpy.angle(e) for e in inh_fft_base]




    pylab.figure()
    pylab.plot(numpy.mean(exc_fft_power,axis=0))	

    pylab.figure()
    pylab.plot(numpy.mean(inh_fft_power,axis=0))	

    pylab.figure()
    pylab.plot(numpy.mean(exc_fft_phase,axis=0))	

    pylab.figure()
    pylab.plot(numpy.mean(inh_fft_phase,axis=0))
    	
    pylab.figure()
    pylab.title('Power spectrum of baseline of excitatory neurons')
    pylab.plot(numpy.mean(exc_fft_power_base,axis=0))	

    pylab.figure()
    pylab.title('Power spectrum of baseline of inhibitory neurons')
    pylab.plot(numpy.mean(inh_fft_power_base,axis=0))	
    
    
    
    pylab.figure()
    pylab.title('high feq power of baseline vs mean of triggered')
    pylab.plot(numpy.mean(numpy.mat(exc_fft_power_base)[:,7:25],axis=1).T,numpy.mat(exc_fft_power).T[0],'ro')
    pylab.plot(numpy.mean(numpy.mat(inh_fft_power_base)[:,7:25],axis=1).T,numpy.mat(inh_fft_power).T[0],'go')
    
    
    pylab.figure()
    pylab.title('high feq power of triggered vs mean of triggered')
    pylab.plot(numpy.mean(numpy.mat(exc_fft_power)[:,7:25],axis=1).T,numpy.mat(exc_fft_power).T[0],'ro')
    pylab.plot(numpy.mean(numpy.mat(inh_fft_power)[:,7:25],axis=1).T,numpy.mat(inh_fft_power).T[0],'go')
    
    pylab.figure()
    pylab.title('high feq power of triggered vs mean of triggered')
    pylab.plot(numpy.mean(numpy.mat(exc_fft_power)[:,7:50],axis=1).T,numpy.mat(exc_fft_power).T[0],'ro')
    pylab.plot(numpy.mean(numpy.mat(inh_fft_power)[:,7:50],axis=1).T,numpy.mat(inh_fft_power).T[0],'go')

    pylab.figure()
    pylab.title('high feq power of triggered vs mean of triggered')
    pylab.plot(numpy.mean(numpy.mat(exc_fft_power)[:,7:70],axis=1).T,numpy.mat(exc_fft_power).T[0],'ro')
    pylab.plot(numpy.mean(numpy.mat(inh_fft_power)[:,7:70],axis=1).T,numpy.mat(inh_fft_power).T[0],'go')
    
    
    
    pylab.figure()
    pylab.title('fanofactor vs variance of trace')
    pylab.plot(numpy.var(exc_average_trace,axis=1)/numpy.mean(exc_average_trace,axis=1),numpy.var(exc_average_trace,axis=1),'ro')
    pylab.plot(numpy.var(inh_average_trace,axis=1)/numpy.mean(inh_average_trace,axis=1),numpy.var(inh_average_trace,axis=1),'go')
    
    pylab.figure()
    pylab.title('fanofactor vs mean of trace')
    pylab.plot(numpy.var(exc_average_trace,axis=1)/numpy.mean(exc_average_trace,axis=1),numpy.mean(exc_average_trace,axis=1),'ro')
    pylab.plot(numpy.var(inh_average_trace,axis=1)/numpy.mean(inh_average_trace,axis=1),numpy.mean(inh_average_trace,axis=1),'go')
    
    pylab.figure()
    pylab.title('variance vs mean of trace')
    pylab.plot(numpy.var(exc_average_trace,axis=1),numpy.mean(exc_average_trace,axis=1),'ro')
    pylab.plot(numpy.var(inh_average_trace,axis=1),numpy.mean(inh_average_trace,axis=1),'go')
    
    
    pylab.figure()
    pylab.title('fanofactor vs variance of base')
    pylab.plot(numpy.var(exc_base,axis=0)/numpy.mean(exc_base,axis=0),numpy.var(exc_base,axis=0),'ro')
    pylab.plot(numpy.var(inh_base,axis=0)/numpy.mean(inh_base,axis=0),numpy.var(inh_base,axis=0),'go')
    
    pylab.figure()
    pylab.title('fanofactor vs mean of base')
    pylab.plot(numpy.var(exc_base,axis=0)/numpy.mean(exc_base,axis=0),numpy.mean(exc_base,axis=0),'ro')
    pylab.plot(numpy.var(inh_base,axis=0)/numpy.mean(inh_base,axis=0),numpy.mean(inh_base,axis=0),'go')

    pylab.figure()
    pylab.title('variance vs mean of base')
    pylab.plot(numpy.var(exc_base,axis=0),numpy.mean(exc_base,axis=0),'ro')
    pylab.plot(numpy.var(inh_base,axis=0),numpy.mean(inh_base,axis=0),'go')
    
    
    
    
    
    pylab.figure()
    pylab.title('mean vs 1st harmonic of neurons')
    pylab.plot(numpy.mat(exc_fft_power).T[0],numpy.mat(exc_fft_power).T[64],'ro')
    pylab.plot(numpy.mat(inh_fft_power).T[0],numpy.mat(inh_fft_power).T[64],'go')
    
    pylab.figure()
    pylab.title('1st vs 2nd harmonic of neurons')
    pylab.plot(numpy.mat(exc_fft_power).T[64],numpy.mat(exc_fft_power).T[128],'ro')
    pylab.plot(numpy.mat(inh_fft_power).T[64],numpy.mat(inh_fft_power).T[128],'go')

    
    pylab.figure()
    pylab.title('mean/1st harmonic vs 1st/2nd harmonic of neurons')
    pylab.plot(numpy.mat(exc_fft_power).T[0] / numpy.mat(exc_fft_power).T[64], numpy.mat(exc_fft_power).T[64] / numpy.mat(exc_fft_power).T[128] ,'ro')
    pylab.plot(numpy.mat(inh_fft_power).T[0] / numpy.mat(inh_fft_power).T[64], numpy.mat(inh_fft_power).T[64] / numpy.mat(inh_fft_power).T[128] ,'go')
    
    
    
    pylab.figure()
    pylab.title('mean vs power at 1st harmonic of neurons')
    pylab.plot(numpy.mean(exc.T,axis=1),numpy.array(numpy.mat(exc_fft_power).T[64])[0],'ro')
    pylab.plot(numpy.mean(inh.T,axis=1),numpy.array(numpy.mat(inh_fft_power).T[64])[0],'go')
    
    pylab.figure()
    pylab.title('power at harmonic vs phase at harmonic of neurons')
    pylab.plot(numpy.mat(exc_fft_power).T[64],numpy.mat(exc_fft_phase).T[64],'ro')
    pylab.plot(numpy.mat(inh_fft_power).T[64],numpy.mat(inh_fft_phase).T[64],'go')
    
    print zip(numpy.mean(exc_fft_power,axis=0),numpy.arange(0,x,1))[0:200]
    
    return(numpy.mean(inh_fft_power,axis=0))


def activationPatterns():
    from scipy import linalg
    f = open("modelfitDB2.dat",'rb')
    import pickle
    dd = pickle.load(f)
    node = dd.children[0]
    activities = node.data["training_set"]
    validation_activities = node.data["validation_set"]

    
    num_act,len_act = numpy.shape(activities)
    
    CC = numpy.zeros((len_act,len_act))
   
    for a in activities:
	CC = CC + numpy.mat(a).T * numpy.mat(a)
	CC = CC / num_act
	
    v,la = linalg.eigh(CC)
    pylab.figure()	
    pylab.plot(numpy.sort(numpy.abs(v.real[-30:-1])),'ro')
    
    ind = numpy.argsort(numpy.abs(v.real))
    
    pylab.figure()
    pylab.plot(la[ind[-1],:],'ro')
    pylab.figure()
    pylab.plot(la[ind[-2],:],'ro')
    pylab.figure()
    pylab.plot(la[ind[-3],:],'ro')
    
    pylab.figure()
    pylab.plot(numpy.mat(activities)*numpy.mat(la[ind[-1],:]).T) 
    
    pylab.figure()
    pylab.hist(numpy.mat(activities)*numpy.mat(la[ind[-1],:]).T)
    
    pylab.figure()
    pylab.plot(numpy.mat(activities)*numpy.mat(la[ind[-1],:]).T,numpy.mat(activities)*numpy.mat(la[ind[-2],:]).T,'ro')
    
    node.add_data("ActivityPattern",la[ind[-1],:],force=True)
    
    f = open("modelfitDB2.dat",'wb')
    pickle.dump(dd,f,-2)
    f.close()
    
    pred_act=node.children[0].data["ReversCorrelationPredictedActivities"]
    pred_val_act=node.children[0].data["ReversCorrelationPredictedValidationActivities"]	
	
    ofs = fit_sigmoids_to_of(numpy.mat(activities),numpy.mat(pred_act))
    pred_act = apply_sigmoid_output_function(numpy.mat(pred_act),ofs)
    pred_val_act= apply_sigmoid_output_function(numpy.mat(pred_val_act),ofs)
	
	
    pylab.figure()	
    print numpy.shape(1-numpy.divide(numpy.sum(numpy.power(activities-pred_act,2),axis=1),numpy.var(activities,axis=1)))
    print numpy.shape(numpy.sum(numpy.power(activities-pred_act,2),axis=1))
    print numpy.shape(numpy.var(activities,axis=1)*len_act)
    
    pylab.plot(1-numpy.divide(numpy.sum(numpy.power(activities-pred_act,2),axis=1),numpy.mat(numpy.var(activities,axis=1)*len_act).T).T,numpy.mat(activities)*numpy.mat(la[ind[-1],:]).T,'ro')
    
    (ranks,correct,pred) =  performIdentification(validation_activities,pred_val_act)
    print correct
    
    pylab.figure()
    pylab.plot(ranks,numpy.mat(validation_activities)*numpy.mat(la[ind[-1],:]).T,'ro')
    
	
	