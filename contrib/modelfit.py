from topo.pattern.basic import Gabor, SineGrating, Gaussian
import numpy
import pylab
from numpy import array, size, mat, shape, ones, arange
from topo.misc.numbergenerator import UniformRandom, BoundedNumber, ExponentialDecay
from topo.base.functionfamily import IdentityTF
import topo
from topo.sheet import GeneratorSheet 
from topo.base.boundingregion import BoundingBox
from topo.pattern.image import Image
import contrib.jacommands

class ModelFit():
    
    filters = []
    weigths = []
    retina_diameter=1.0
    density=24
    epochs = 2000
    learning_rate = 0.0001
    inputDC = 0
    modelDC = 0
    meanModelResponses=[]
    reliable_indecies=[]
    momentum=0.0
    num_of_units=0
    
    def init(self):
        self.reliable_indecies = ones(self.num_of_units)
        for freq in [1.0,2.0,4.0,8.0]:
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
            res.append(numpy.sqrt(r1*r1+r2*r2))
            #res.append(r1)
            #res.append(r2)
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
    
    def trainModel(self,inputs,activities):
        self.calculateInputDC(inputs)
        modelResponses=[]
        delta=[]
        self.meanModelResponses=numpy.array(self.calculateModelResponse(inputs,0)).copy()*0.0
        self.modelDC=numpy.array(activities[0]).copy()*0.0
        
        # calculate the model responses and their average to the set of inputs
        for i in xrange(len(inputs)):
            modelResponses.append(numpy.array(self.calculateModelResponse(inputs,i)))
            self.meanModelResponses = self.meanModelResponses + modelResponses[len(modelResponses)-1] 
        self.meanModelResponses = self.meanModelResponses/len(inputs)
       
        # substract the mean from model responses
        for i in xrange(0,len(modelResponses)):
            modelResponses[i] = modelResponses[i] - self.meanModelResponses
                      
        #calculate the initial model DC as the mean of the target activities
        for a in activities:
            self.modelDC+=a
        
        self.modelDC = self.modelDC/len(activities)    
            
                    
        self.weigths=numpy.mat(numpy.zeros((size(activities,1),size(modelResponses[0],1))))
        
        mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
        
        old_error = 10000000 * ones(shape(activities[0]))
        for k in xrange(0,self.epochs):
            mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
            tmp_weigths=numpy.mat(numpy.zeros((size(activities,1),size(modelResponses[0],1))))
            for i in xrange(0,len(inputs)):
                error = ((activities[i].T - self.weigths*modelResponses[i].T - self.modelDC.T))
                tmp_weigths = tmp_weigths + (error * modelResponses[i])
                mean_error=mean_error+numpy.power(error,2)
            if k == 0:
               delta = tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            else:
               delta = self.momentum*delta + (1.0-self.momentum)*tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            
            delta = delta/numpy.sqrt(numpy.sum(numpy.power(delta,2)))
                   
            self.weigths = self.weigths + self.learning_rate*delta
            err = numpy.sum(mean_error)/len(inputs)/len(mean_error)    
            
            # adjust learning rates based on new errors
            print (k,err)
            #print delta[0]
            #print mean_error[0]/len(inputs)
            
            #ii =  (mean_error.T/len(inputs)) > old_error
            
            #print shape(ii)
            #learning_rates -= numpy.multiply((learning_rates/10.0), ii)
            #old_error=mean_error.T/len(inputs)
            #print (learning_rates[0][0]) 
        
#        print mean_error/len(inputs)

        # recalculate a new model DC based on what we have learned
        self.modelDC*=0.0
        for i in xrange(0,len(inputs)):
            self.modelDC+=(activities[i].T - self.weigths*modelResponses[i].T).T
        self.modelDC = self.modelDC/len(inputs)    
    
    def calculateReliabilities(self,inputs,activities,top_percentage):
        corr_coef=numpy.zeros(self.num_of_units)
        modelResponses=[]
        modelActivities=[]

        for i in xrange(0,len(inputs)):
            modelResponses.append(numpy.array(self.calculateModelResponse(inputs,i))-self.meanModelResponses)
            
        for i in xrange(0,len(inputs)):
           a = self.weigths*modelResponses[i].T + self.modelDC.T
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
            pylab.figure()            
            pylab.plot(numpy.array(activities.T[t[self.num_of_units-1-i][0]][0].T))
            pylab.plot(numpy.array(modelActivities[t[self.num_of_units-1-i][0]][0].T))
            

    def testModel(self,inputs,activities,target_inputs=None):
        modelActivities=[]
        modelResponses=[]
        error = 0
        
        if target_inputs == None:
           target_inputs = [a for a in xrange(0,len(inputs))]
        
        
        for i in xrange(0,len(inputs)):
            modelResponses.append(numpy.array(self.calculateModelResponse(inputs,i)))
       
        # substract the mean from model responses
        for i in xrange(0,len(modelResponses)):
            modelResponses[i] = modelResponses[i] - self.meanModelResponses

        for mr in modelResponses:
            modelActivities.append(self.weigths*mr.T+self.modelDC.T)
            
        #for i in xrange(0,len(modelResponses)):
        #    if self.reliable_indecies[i]==1.0:    
            
    
        tmp = []
        correct = 0
        pylab.figure()
        
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
            #print (x,i)

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
                        for speed in [6,10,30]:
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

def runLISSOMModelFit():
    
    
    train_image_filenames=["images/mymix/%d.pgm" %(i) for i in xrange(99)]
    train_inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       #x=UniformRandom(lbound=-0.75,ubound=0.75,seed=511),
                       #y=UniformRandom(lbound=-0.75,ubound=0.75,seed=1023),
                       x=0,
                       y=0)
                       #orientation=UniformRandom(lbound=-3.14,ubound=3.14,seed=511))
    for f in train_image_filenames]
    
    train_combined_inputs =contrib.jacommands.SequenceSelector(generators=train_inputs)

    test_image_filenames=["images/mymix/%d.pgm" %(i+100) for i in xrange(90)]
    test_inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       #x=UniformRandom(lbound=-0.75,ubound=0.75,seed=511),
                       #y=UniformRandom(lbound=-0.75,ubound=0.75,seed=1023),
                       x=0,
                       y=0)
                       #orientation=UniformRandom(lbound=-3.14,ubound=3.14,seed=511))
    for f in test_image_filenames]
    test_combined_inputs =contrib.jacommands.SequenceSelector(generators=test_inputs)
    
    mf = ModelFit()
    
    mf.retina_diameter = (0.5+0.25+0.375)*2
    mf.density = topo.sim["Retina"].nominal_density
    mf.init()
    topo.sim["V1"].plastic = False

    topo.sim['Retina'].set_input_generator(train_combined_inputs)
    
    inputs = []
    activities = []
    topo.sim["V1"].output_fn=IdentityTF()    
    for i in xrange(0,99):
        topo.sim.run(0.15)
        inputs.append(topo.sim["Retina"].activity.copy())
        activities.append(topo.sim["V1"].activity.copy().flatten())
        topo.sim.run(0.85)
    print float(topo.sim.time())
    
    mf.trainModel(inputs,numpy.mat(activities))    
    
    mf.testModel(inputs,numpy.mat(activities))

    topo.sim['Retina'].set_input_generator(test_combined_inputs)

    inputs = []
    activities = []
        
    for i in xrange(0,90):
        topo.sim.run(0.15)
        inputs.append(topo.sim["Retina"].activity.copy())
        activities.append(topo.sim["V1"].activity.copy().flatten())
        topo.sim.run(0.85)        
    
    mf.testModel(inputs,numpy.mat(activities))
    return mf

def runSineGratingsModelFit():
    f = file("Flogl/gratings.txt", "r")
    data = [line.split() for line in f]
    f.close()
    pylab.figure(1)
    pylab.plot(numpy.array(numpy.matrix(data).T[29].T))
      
    # transform data into floats
    (sizex,sizey) = shape(data)
    print sizex,sizey
    # getting rid of last 3 cells!
    sizey=sizey-4
    activities = numpy.zeros((sizex/10,sizey))
    for i in xrange(0,sizex):
        for j in xrange(0,sizey):
            activities[i/10,j] += float(data[i][j]) 
                                
    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = ModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density
    mf.num_of_units = sizey
    mf.init()

    
    inputs = []
    for z in xrange(0,5):
        for i in xrange(0,8):
            input = SineGrating(frequency=2.4,orientation=2*numpy.pi/8*i)
            topo.sim['Retina'].set_input_generator(input)
            topo.sim.run(1.0)
            inputs.append(topo.sim["Retina"].activity.copy())

    print shape(numpy.mat(activities[0:35]))
    print shape(inputs[0:35])
    mf.trainModel(inputs[0:35],numpy.mat(activities[0:35]))
    
    mf.calculateReliabilities(inputs[0:35],numpy.mat(activities[0:35]),10)                        
    
    print shape(numpy.mat(activities[32:40]))
    print shape(inputs[36:40])
    mf.testModel(inputs[36:40],numpy.mat(activities[36:40]))
    pylab.show()
    return mf

        

def runSineGratingsMotionModelFit():
    f = file("Flogl/gratings.txt", "r")
    data = [line.split() for line in f]
    f.close()
    
    # transform data into floats
    (sizex,sizey) = shape(data)
    # getting rid of last 3 cells!
    sizey=sizey-4
    activities = numpy.zeros((sizex,sizey))
    for i in xrange(0,sizex):
        for j in xrange(0,sizey):
            activities[i,j] += float(data[i][j]) 
 
    #pylab.figure(2)
    #pylab.plot(numpy.array(numpy.matrix(activities).T[29].T))

    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = MotionModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density
    mf.num_of_units = sizey
    mf.init()

    
    inputs = []
    for z in xrange(0,5):
        for i in xrange(0,8):
            for x in xrange(0,10):
                input = SineGrating(frequency=1.0,orientation=2*numpy.pi/8*i,phase=numpy.pi/10*x)
                topo.sim['Retina'].set_input_generator(input)
                topo.sim.run(1.0)
                inputs.append(topo.sim["Retina"].activity.copy())
    if False:
        pylab.figure()
        #f1 = fig.add_subplot(112, autoscale_on=True)
        f1 = pylab.subplot(121)
        f2 = pylab.subplot(122,autoscale_on=False,ylim=(-800, 800))
        pylab.ylim(-800,800)
        pylab.hold(False)
        import time
        #f2 = fig.add_subplot(112, autoscale_on=True)
        for i in xrange(0,80):
            act = mf.calculateModelResponse(inputs,i)
            f1.imshow(inputs[i])
            f2.plot(numpy.array(act[0].T),'ro',scaley=False)
            pylab.show._needmain=False
            pylab.show()
            time.sleep(2)

    
    print shape(inputs[0:320])
    mf.trainModel(inputs[0:320],numpy.mat(activities[0:320]))                        
    
    #mf.calculateReliabilities(inputs[0:320],numpy.mat(activities[0:320]),100)
    
    
    #print shape(inputs[320:400])
    #mf.testModel(inputs[240:320],numpy.mat(activities[240:320]),[9,19,29,39,49,59,69,79])
    mf.calculateReliabilities(inputs[0:320],numpy.mat(activities[0:320]),10)
    mf.testModel(inputs[320:400],numpy.mat(activities[320:400]),[8,18,28,38,48,58,68,78])
    mf.testModel(inputs[240:320],numpy.mat(activities[240:320]),[8,18,28,38,48,58,68,78])
    mf.testModel(inputs[160:240],numpy.mat(activities[160:240]),[8,18,28,38,48,58,68,78])
    mf.testModel(inputs[80:160],numpy.mat(activities[80:160]),[8,18,28,38,48,58,68,78])
    mf.testModel(inputs[0:80],numpy.mat(activities[0:80]),[8,18,28,38,48,58,68,78])

    pylab.show()
    return mf


def runSineGratingsEpisodicMotionModelFit():
    f = file("Flogl/gratings.txt", "r")
    data = [line.split() for line in f]
    f.close()
    
    # transform data into floats
    (sizex,sizey) = shape(data)
    # getting rid of last 3 cells!
    sizey=sizey-4
    activities = numpy.zeros((sizex/10,sizey))
     
    for i in xrange(0,sizex/10):
        for j in xrange(0,sizey):
            for r in xrange(0,10):
                activities[i,j] += float(data[i*10+r][j]) 

    for i in xrange(0,sizex/10):
        for j in xrange(0,sizey):
            activities[i,j] /=10    
    
    #pylab.figure(2)
    #pylab.plot(numpy.array(numpy.matrix(activities).T[29].T))

    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = MotionModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density
    mf.num_of_units = sizey
    mf.real_time=False
    mf.init()
    
    
    inputs = []
    for z in xrange(0,5):
        for i in xrange(0,8):
            inn = []
            for x in xrange(0,9):
                input = SineGrating(frequency=1.0,orientation=2*numpy.pi/8*i,phase=numpy.pi/9*x)
                topo.sim['Retina'].set_input_generator(input)
                topo.sim.run(1.0)
                inn.append(topo.sim["Retina"].activity.copy())
            inputs.append(inn)    

    
    print shape(inputs[0:32])
    mf.trainModel(inputs[0:32],numpy.mat(activities[0:32]))                        
    mf.calculateReliabilities(inputs[0:32],numpy.mat(activities[0:32]),20)
    mf.testModel(inputs[0:8],numpy.mat(activities[32:40]))
    mf.testModel(inputs[0:8],numpy.mat(activities[32:40]))
    mf.testModel(inputs[0:8],numpy.mat(activities[32:40]))
    mf.testModel(inputs[0:8],numpy.mat(activities[32:40]))
    mf.testModel(inputs[0:8],numpy.mat(activities[32:40]))
    
    

    pylab.show()
    return mf



def runMoviesModelRepeatabilityFit():
    f = file("Flogl/newdata.txt", "r")
    data = [line.split() for line in f]
    f.close()
 
    num_trials = 20
    num_frames = 30
    num_test = 1
     
    # transform data into floats
    (trash,num_cells) = shape(data)
    # getting rid of last 3 cells!
    num_cells=num_cells-10
    train_activities = numpy.zeros((num_frames,num_cells))
    test_activities = numpy.zeros((num_frames,num_cells))
    for t in xrange(0,num_trials-num_test):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                train_activities[i][j] += float(data[t*30+i][j])

    for t in xrange(num_trials-num_test,num_trials):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                test_activities[i][j] += float(data[t*30+i][j])
                
    train_activities/=(num_trials-num_test)
    test_activities/=num_test
         
    range = arange(1,31,1) 
    ######################################################################################
    image_filenames=["Flogl/first-avi/frame%03d.png" %(i) for i in range]
    inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       x=0,
                       y=0)
    for f in image_filenames]
    
    combined_inputs =contrib.jacommands.SequenceSelector(generators=inputs)
    
    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = ModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density#
    mf.num_of_units = num_cells
    mf.init()


    topo.sim['Retina'].set_input_generator(combined_inputs)    
    inputs = []
    for i in xrange(0,num_frames):
        topo.sim.run(1.0)
        inputs.append(topo.sim["Retina"].activity.copy())




    mf.trainModel(inputs,numpy.mat(train_activities))

    mf.testModel(inputs,numpy.mat(train_activities))
    mf.testModel(inputs,numpy.mat(test_activities))
    
    mf.calculateReliabilities(inputs,numpy.mat(train_activities),50)
    mf.testModel(inputs,numpy.mat(test_activities))

    mf.calculateReliabilities(inputs,numpy.mat(train_activities),20)
    mf.testModel(inputs,numpy.mat(test_activities))

    mf.calculateReliabilities(inputs,numpy.mat(train_activities),10)
    mf.testModel(inputs,numpy.mat(test_activities))

    #mf.calculateReliabilities(inputs,numpy.mat(train_activities),1)
    #mf.testModel(inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(inputs,numpy.mat(train_activities),2)
    #mf.testModel(inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(inputs,numpy.mat(train_activities),5)
    #mf.testModel(inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(inputs,numpy.mat(train_activities),10)
    #mf.testModel(inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(inputs,numpy.mat(train_activities),15)
    #mf.testModel(inputs,numpy.mat(test_activities))


    
    #for i in xrange(0,100):
    #    mf.testModel(inputs,numpy.mat(train_activities))
    

    return mf


def runMoviesMotionModelRepeatabilityFit():
    f = file("Flogl/newdata.txt", "r")
    data = [line.split() for line in f]
    f.close()
 
    num_trials = 20
    num_frames = 30
    num_test = 1
     
    # transform data into floats
    (trash,num_cells) = shape(data)
    # getting rid of last 3 cells!
    num_cells=num_cells-10
    train_activities = numpy.zeros((num_frames,num_cells))
    test_activities = numpy.zeros((num_frames,num_cells))
    for t in xrange(0,num_trials-num_test):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                train_activities[i][j] += float(data[t*30+i][j])

    for t in xrange(num_trials-num_test,num_trials):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                test_activities[i][j] += float(data[t*30+i][j])
                
    train_activities/=(num_trials-num_test)
    test_activities/=num_test
         
    range = arange(1,900,1) 
    ######################################################################################
    image_filenames=["Flogl/hf-avi/frame%03d.png" %(i) for i in range]
    inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       x=0,
                       y=0)
    for f in image_filenames]
    
    combined_inputs =contrib.jacommands.SequenceSelector(generators=inputs)
    
    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = MotionModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density#
    mf.num_of_units = num_cells
    mf.real_time=False
    mf.init()


    topo.sim['Retina'].set_input_generator(combined_inputs)    
    inputs = []
    for i in xrange(0,num_frames):
        inn = []
        for j in xrange(0,30):
            topo.sim.run(1.0)
            inn.append(topo.sim["Retina"].activity.copy())
        inputs.append(inn)    



    mf.trainModel(inputs,numpy.mat(train_activities))

    mf.testModel(inputs,numpy.mat(train_activities))
    mf.testModel(inputs,numpy.mat(test_activities))

    mf.calculateReliabilities(inputs,numpy.mat(train_activities),5)
    mf.testModel(inputs,numpy.mat(test_activities))

    mf.calculateReliabilities(inputs,numpy.mat(train_activities),10)
    mf.testModel(inputs,numpy.mat(test_activities))
    
    mf.calculateReliabilities(inputs,numpy.mat(train_activities),20)
    mf.testModel(inputs,numpy.mat(test_activities))

    mf.calculateReliabilities(inputs,numpy.mat(train_activities),50)
    mf.testModel(inputs,numpy.mat(test_activities))


    return mf
    
    
def runMoviesModelAveragedFit():
    f = file("Flogl/newdata.txt", "r")
    data = [line.split() for line in f]
    f.close()
 
    num_trials = 20
    num_frames = 30
     
    # transform data into floats
    (trash,num_cells) = shape(data)
    # getting rid of last 3 cells!
    num_cells=num_cells-10
    train_activities = numpy.zeros((num_frames/2,num_cells))
    test_activities = numpy.zeros((num_frames/2,num_cells))
    for t in xrange(0,num_trials):
        for i in xrange(0,num_frames/2):
            for j in xrange(0,num_cells):
                train_activities[i][j] += float(data[t*30+2*i][j])
                test_activities[i][j] += float(data[t*30+2*i+1][j])
    train_activities/=num_trials/2
    test_activities/=num_trials/2
         
    train_range = arange(1,16,1) * 2 
    test_range = arange(1,16,1) * 2 +1
    ######################################################################################
    train_image_filenames=["Flogl/first-avi/frame%03d.png" %(i) for i in train_range]
    train_inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       x=0,
                       y=0)
    for f in train_image_filenames]
    
    train_combined_inputs =contrib.jacommands.SequenceSelector(generators=train_inputs)
    ######################################################################################
    test_image_filenames=["Flogl/first-avi/frame%03d.png" %(i) for i in test_range]
    test_inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       x=0,
                       y=0)
    for f in test_image_filenames]
    
    test_combined_inputs =contrib.jacommands.SequenceSelector(generators=test_inputs)
    ######################################################################################
 
    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = ModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density#
    mf.num_of_units = num_cells
    mf.init()


    topo.sim['Retina'].set_input_generator(train_combined_inputs)    
    train_inputs = []
    for i in xrange(0,num_frames/2):
        topo.sim.run(1.0)
        train_inputs.append(topo.sim["Retina"].activity.copy())


    topo.sim['Retina'].set_input_generator(test_combined_inputs)    
    test_inputs = []
    for i in xrange(0,num_frames/2):
        topo.sim.run(1.0)
        test_inputs.append(topo.sim["Retina"].activity.copy())
    



    mf.trainModel(train_inputs,numpy.mat(train_activities))
    mf.testModel(train_inputs,numpy.mat(train_activities))
    
    
    mf.testModel(test_inputs,numpy.mat(test_activities))

    mf.reliability_trehsold=10.0
    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),10)
    mf.testModel(test_inputs,numpy.mat(test_activities))
    
    mf.reliability_trehsold=8
    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),15)
    mf.testModel(test_inputs,numpy.mat(test_activities))
    
    mf.reliability_trehsold=3
    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),20)
    mf.testModel(test_inputs,numpy.mat(test_activities))
    
    mf.reliability_trehsold=1.0
    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),25)
    mf.testModel(test_inputs,numpy.mat(test_activities))
    
    mf.reliability_trehsold=0.8
    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),30)
    mf.testModel(test_inputs,numpy.mat(test_activities))
    
    
    
    
def runMoviesModelFit():
    f = file("Flogl/newdata.txt", "r")
    data = [line.split() for line in f]
    f.close()
 
    num_trials = 20
    num_frames = 30
     
    # transform data into floats
    (trash,num_cells) = shape(data)
    # getting rid of last 3 cells!
    num_cells=num_cells-10
    train_activities = numpy.zeros((num_frames*(num_trials-1),num_cells))
    test_activities = numpy.zeros((num_frames,num_cells))
    for t in xrange(0,num_trials-1):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                train_activities[t*num_frames+i][j] = float(data[t*num_frames+i][j])

    for t in xrange(num_trials-1,num_trials):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                test_activities[i][j] = float(data[t*30+i][j])
         
    range = arange(1,31,1) 
    ######################################################################################
    image_filenames=["Flogl/first-avi/frame%03d.png" %(i) for i in range]
    inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       x=0,
                       y=0)
    for f in image_filenames]
    
    combined_inputs =contrib.jacommands.SequenceSelector(generators=inputs)
    
    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = ModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density#
    mf.num_of_units = num_cells
    mf.init()


    topo.sim['Retina'].set_input_generator(combined_inputs)    
    train_inputs = []
    test_inputs = []
    for j in xrange(0,num_trials-1):
        topo.sim["Retina"].input_generator.index=0
        for i in xrange(0,num_frames):
            topo.sim.run(1.0)
            train_inputs.append(topo.sim["Retina"].activity.copy())

    topo.sim["Retina"].input_generator.index=0
    for i in xrange(0,num_frames):
        topo.sim.run(1.0)
        test_inputs.append(topo.sim["Retina"].activity.copy())

    mf.trainModel(train_inputs,numpy.mat(train_activities))
    mf.testModel(test_inputs,numpy.mat(test_activities))
    

    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),20)
    mf.testModel(test_inputs,numpy.mat(test_activities))

    #mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),2)
    #mf.testModel(test_inputs,numpy.mat(test_activities))

    
    #mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),2)
    #mf.testModel(test_inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),5)
    #mf.testModel(test_inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),10)
    #mf.testModel(test_inputs,numpy.mat(test_activities))
    
    #mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),15)
    #mf.testModel(test_inputs,numpy.mat(test_activities))
    
    #for i in xrange(0,100):
    #    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),i)
    #    mf.testModel(test_inputs,numpy.mat(test_activities))
    

    return mf

def runMoviesMotionModelFit():
    f = file("Flogl/newdata.txt", "r")
    data = [line.split() for line in f]
    f.close()
 
    num_trials = 20
    num_frames = 30
     
    # transform data into floats
    (trash,num_cells) = shape(data)
    # getting rid of last 3 cells!
    num_cells=num_cells-10
    train_activities = numpy.zeros((num_frames*(num_trials-1),num_cells))
    test_activities = numpy.zeros((num_frames,num_cells))
    for t in xrange(0,num_trials-1):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                train_activities[t*num_frames+i][j] = float(data[t*num_frames+i][j])

    for t in xrange(num_trials-1,num_trials):
        for i in xrange(0,num_frames):
            for j in xrange(0,num_cells):
                test_activities[i][j] = float(data[t*30+i][j])
         
    range = arange(1,900,1) 
    ######################################################################################
    image_filenames=["Flogl/hf-avi/frame%03d.png" %(i) for i in range]
    inputs=[Image(filename=f,
                       size=2.0,  size_normalization='stretch_to_fit',
                       x=0,
                       y=0)
    for f in image_filenames]
    
    combined_inputs =contrib.jacommands.SequenceSelector(generators=inputs)
    
    topo.sim['Retina']=GeneratorSheet(nominal_density=48.0,
                                  input_generator=SineGrating(),
                                  period=1.0, phase=0.01,
                                  nominal_bounds=BoundingBox(radius=0.5))

    mf = MotionModelFit()
    mf.retina_diameter = 1.0
    mf.density = topo.sim["Retina"].nominal_density#
    mf.num_of_units = num_cells
    mf.real_time=True
    mf.init()


    topo.sim['Retina'].set_input_generator(combined_inputs)    
    train_inputs = []
    test_inputs = []
    for j in xrange(0,num_trials-1):
        topo.sim["Retina"].input_generator.index=0
        for i in xrange(0,num_frames):
            inn = []
            for k in xrange(0,30):
                topo.sim.run(1.0)
                inn.append(topo.sim["Retina"].activity.copy())
            train_inputs.append(inn)

    topo.sim["Retina"].input_generator.index=0
    for i in xrange(0,num_frames):
        topo.sim.run(1.0)
        test_inputs.append(topo.sim["Retina"].activity.copy())

    mf.trainModel(train_inputs,numpy.mat(train_activities))
    mf.testModel(test_inputs,numpy.mat(test_activities))
    

    mf.calculateReliabilities(train_inputs,numpy.mat(train_activities),20)
    mf.testModel(test_inputs,numpy.mat(test_activities))
    

    return mf

