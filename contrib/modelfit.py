from topo.pattern.basic import Gabor
from topo.command.pylabplots import matrixplot
import numpy
import pylab
from numpy import array, size, mat, shape
from topo.misc.numbergenerators import UniformRandom, BoundedNumber, ExponentialDecay
from topo.base.functionfamily import IdentityOF
import topo
from topo.base.boundingregion import BoundingBox
from topo.pattern.image import Image


class ModelFit():
    
    filters = []
    weigths = []
    retina_diameter=1.0
    density=48
    epochs = 1000
    learning_rate = 0.1
    inputDC = 0
    modelDC = 0
    meanModelResponses=[]
    
    def init(self):
        for freq in [8.0]:
            for xpos in xrange(0,int(freq)):
                for ypos in xrange(0,int(freq)):
                    x=xpos*(self.retina_diameter/freq)-self.retina_diameter/2 + self.retina_diameter/freq/2 
                    y=ypos*(self.retina_diameter/freq)-self.retina_diameter/2 + self.retina_diameter/freq/2
                    for orient in xrange(0,8):
                        g1 = Gabor(bounds=BoundingBox(radius=self.retina_diameter/2),frequency=freq,x=x,y=y,xdensity=self.density,ydensity=self.density,size=1/freq,orientation=numpy.pi/8*orient,phase=0.0)
                        g2 = Gabor(bounds=BoundingBox(radius=self.retina_diameter/2),frequency=freq,x=x,y=y,xdensity=self.density,ydensity=self.density,size=1/freq,orientation=numpy.pi/8*orient,phase=numpy.pi)
                        self.filters.append((g1(),g2()))  

    def calculateModelResponse(self,input):
        res = []
        inn = input - self.inputDC
        for (gabor1,gabor2) in self.filters:
            r1 = numpy.sum(numpy.multiply(gabor1,inn))
            r2 = numpy.sum(numpy.multiply(gabor2,inn))
            res.append(numpy.sqrt(r1*r1+r2*r2))
        # the constant luminance wavelet
        #res.append(numpy.sum(inn))
        # allow DC substractions (eg threshold in NN) 
        res.append(1.0)
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
        momentum=0.0
        self.meanModelResponses=numpy.array(self.calculateModelResponse(inputs[0])).copy()*0.0
        self.modelDC=numpy.array(activities[0]).copy()*0.0
        
        # calculate the model responses and their average to the set of inputs
        for input in inputs:
            modelResponses.append(numpy.array(self.calculateModelResponse(input)))
            self.meanModelResponses = self.meanModelResponses + modelResponses[len(modelResponses)-1] 
        self.meanModelResponses = self.meanModelResponses/len(inputs)
       
        # substract the mean from model responses
        for i in xrange(0,len(modelResponses)):
            modelResponses[i] = modelResponses[i] - self.meanModelResponses
                      
        #calculate the initial model DC as the mean of the target activities
        for a in activities:
            self.modelDC+=a
        print "BVV" + str(len(activities))
        self.modelDC = self.modelDC/len(activities)    
            
                    
        self.weigths=numpy.mat(numpy.zeros((size(activities,1),size(modelResponses[0],1))))
        
        mean_error=numpy.mat(numpy.zeros(shape(activities[0].T)))
        
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
               delta = momentum*delta + (1.0-momentum)*tmp_weigths/numpy.sqrt(numpy.sum(numpy.power(tmp_weigths,2)))
            
            delta = delta/numpy.sqrt(numpy.sum(numpy.power(delta,2)))
                  
            self.weigths = self.weigths + self.learning_rate*delta        
            print (k,numpy.sum(mean_error)/len(inputs)/len(mean_error))
#        print mean_error/len(inputs)

        # recalculate a new model DC based on what we have learned
        self.modelDC*=0.0
        for i in xrange(0,len(inputs)):
            self.modelDC+=(activities[i].T - self.weigths*modelResponses[i].T).T
        self.modelDC = self.modelDC/len(inputs)    
         
            
    def testModel(self,inputs,activities):
        modelActivities=[]
        modelResponses=[]
        error = 0
        
        for input in inputs:
            modelResponses.append(numpy.array(self.calculateModelResponse(input)))
       
        # substract the mean from model responses
        for i in xrange(0,len(modelResponses)):
            modelResponses[i] = modelResponses[i] - self.meanModelResponses

        for mr in modelResponses:
            modelActivities.append(self.weigths*mr.T+self.modelDC.T)

        tmp = []
        correct = 0
        pylab.figure()
        for i in xrange(0,len(inputs)):
            tmp = []
            for j in xrange(0,len(inputs)):
                tmp.append(numpy.sum(numpy.power(activities[i].T - modelActivities[j],2)))
                
            x = numpy.argmin(array(tmp))
            print (i, x)#, array(tmp))
            
            print numpy.sum(numpy.power(activities[i].T - modelActivities[i],2))/len(activities[0])
            print numpy.sum(numpy.power(activities[i].T - modelActivities[x],2))/len(activities[0])
            
            if x == i:
                 correct+=1.0
            if i%200 == 0:
                print "figure"                
                pylab.subplot(5,5,i/200+1)
                pylab.imshow(toMatrix(activities[i].T.A,48,48),vmin=0,vmax=0.15)
                pylab.subplot(5,5,5+i/200+1)
                pylab.imshow(toMatrix(modelActivities[i].A,48,48),vmin=0,vmax=0.15)
                pylab.subplot(5,5,10+i/200+1)
                pylab.imshow(toMatrix(modelActivities[x].A,48,48),vmin=0,vmax=0.15)
                pylab.subplot(5,5,15+i/200+1)
                pylab.imshow(inputs[i],vmin=0,vmax=0.6)
                pylab.subplot(5,5,20+i/200+1)
                pylab.imshow(inputs[x],vmin=0,vmax=0.6)
                
                 
        print correct/len(inputs)*100, "%"
              
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

def runModelFit():
    
    
    image_filenames=["images/mymix/%03d.pgm" %(i+1) for i in xrange(128)]
    print image_filenames
    Image 
    inputs=[Image(filename=f,
                       size=10.0,  #size_normalization='original',(size=10.0)
                       x=UniformRandom(lbound=-0.75,ubound=0.75,seed=511),
                       y=UniformRandom(lbound=-0.75,ubound=0.75,seed=1023),
                       orientation=UniformRandom(lbound=-3.14,ubound=3.14,seed=511))
    for f in image_filenames]

    combined_inputs =topo.pattern.basic.Selector(generators=inputs)
    topo.sim['Retina'].set_input_generator(combined_corners)

    
    mf = ModelFit()
    
    mf.retina_diameter = (0.5+0.25+0.375)*2
    mf.density = topo.sim["Retina"].nominal_density
    mf.init()
    topo.sim["V1"].plastic = False
    
    inputs = []
    activities = []
    topo.sim["V1"].output_fn=IdentityOF()    
    for i in xrange(0,1000):
        topo.sim.run(0.15)
        inputs.append(topo.sim["Retina"].activity.copy())
        activities.append(topo.sim["V1"].activity.copy().flatten())
        topo.sim.run(0.85)
    print float(topo.sim.time())
    mf.trainModel(inputs,numpy.mat(activities))    
    
    mf.testModel(inputs,numpy.mat(activities))

    inputs = []
    activities = []
        
    for i in xrange(0,100):
        topo.sim.run(0.15)
        inputs.append(topo.sim["Retina"].activity.copy())
        activities.append(topo.sim["V1"].activity.copy().flatten())
        topo.sim.run(0.85)        
    
    mf.testModel(inputs,numpy.mat(activities))
    return mf
                    