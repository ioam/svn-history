from scipy.optimize import fmin_ncg
import __main__
import numpy
import pylab
import sys
sys.path.append('/home/antolikjan/topographica/Theano/')
import theano 
from theano import tensor as T
from topo.misc.filepath import normalize_path, application_path
from contrib.modelfit import *
import contrib.dd
import contrib.JanA.dataimport

class LSCSM(object):
	
	def __init__(self,XX,YY,num_lgn):
	    (self.num_pres,self.image_size) = numpy.shape(XX)
	    self.num_lgn = num_lgn
	    self.ss = numpy.sqrt(self.image_size)

	    self.xx = theano.shared(numpy.repeat([numpy.arange(0,self.ss,1)],self.ss,axis=0).T.flatten())	
	    self.yy = theano.shared(numpy.repeat([numpy.arange(0,self.ss,1)],self.ss,axis=0).flatten())
	    self.Y = theano.shared(YY)
    	    self.X = theano.shared(XX)
	    
	    self.K = T.dvector('K')
	    self.x = self.K[0:self.num_lgn]
	    self.y = self.K[self.num_lgn:2*self.num_lgn]
	    self.a = self.K[2*self.num_lgn:3*self.num_lgn]
	    self.s = self.K[3*self.num_lgn:4*self.num_lgn]
	    self.n = self.K[4*self.num_lgn]
	    
	    self.output = T.dot(self.X,T.mul(self.a[0],T.exp(-T.div_proxy(((self.xx - self.x[0])**2 + (self.yy - self.y[0])**2),self.s[0] )).T))
	    
	    for i in xrange(1,self.num_lgn):
		self.output = self.output + T.dot(self.X,T.mul(self.a[i],T.exp(-T.div_proxy(((self.xx - self.x[i])**2 + (self.yy - self.y[i])**2),self.s[i] )).T))
	        
	    self.model = T.exp(self.output-self.n)
	    self.loglikelyhood = T.sum(self.model) - T.sum(T.dot(self.Y.T,  T.log(self.model))) 

	def func(self):
	    return theano.function(inputs=[self.K], outputs=self.loglikelyhood) 
			
	def der(self):
	    g_K = T.grad(self.loglikelyhood, self.K)
	    return theano.function(inputs=[self.K], outputs=g_K)
 
 	def hess(self):
            g_K = T.grad(self.loglikelyhood, self.K,consider_constant=[self.Y,self.X])
	    H, updates = theano.scan(lambda i,v: T.grad(g_K[i],v), sequences= T.arange(g_K.shape[0]), non_sequences=self.K)
  	    return theano.function(inputs=[self.K], outputs=H)
	
	def response(self,X,kernels):
	    self.IN = theano.shared(X)	
	    
	    self.output = T.dot(self.IN,T.mul(self.a[0],T.exp(-T.div_proxy(((self.xx - self.x[0])**2 + (self.yy - self.y[0])**2),self.s[0] )).T))
	    
	    for i in xrange(1,self.num_lgn):
		self.output = self.output + T.dot(self.IN,T.mul(self.a[i],T.exp(-T.div_proxy(((self.xx - self.x[i])**2 + (self.yy - self.y[i])**2),self.s[i] )).T))
	        
	    self.model = T.exp(self.output-self.n)
	    	
	    resp =  theano.function(inputs=[self.K], outputs=self.model)
	    
	    (a,b) = numpy.shape(kernels)
	    (c,d) = numpy.shape(X)
	    
	    responses = numpy.zeros((c,a))
	    
	    for i in xrange(a):
		responses[:,i] = resp(kernels[i,:]).T
	    
	    return responses
	    
	
	def returnRFs(self,kernels):
	    (k,l) = numpy.shape(kernels)
            rfs = numpy.zeros((k,self.image_size))
	    
	    xx = numpy.repeat([numpy.arange(0,self.ss,1)],self.ss,axis=0).T.flatten()	
	    yy = numpy.repeat([numpy.arange(0,self.ss,1)],self.ss,axis=0).flatten()
	    			    
			    
	    for j in xrange(k):
   		x = kernels[j,0:self.num_lgn]
	        y = kernels[j,self.num_lgn:2*self.num_lgn]
	        a = kernels[j,2*self.num_lgn:3*self.num_lgn]
		s = kernels[j,3*self.num_lgn:4*self.num_lgn]
		print x
		print y
		print a
		print s
	    	for i in xrange(0,self.num_lgn):
		    rfs[j,:] += a[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/s[i])
	    
	    return rfs
	
def fitLSCSM(X,Y,num_lgn,num_neurons_to_estimate):
    num_pres,num_neurons = numpy.shape(Y)
    num_pres,kernel_size = numpy.shape(X)
    
    Ks = numpy.zeros((num_neurons,num_lgn*4+1))
    laplace = 0.0001*laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))
    
    rpi = numpy.linalg.pinv(X.T*X + 10*laplace) * X.T * Y
    
    
    for i in xrange(0,num_neurons_to_estimate): 
	print i
	k0 = numpy.zeros((num_lgn*4+1,1)).flatten()
	z = numpy.reshape(k0[:-1],(4,num_lgn))
	z[0,:] = numpy.random.rand(num_lgn)*numpy.sqrt(kernel_size)
	z[1,:] = numpy.random.rand(num_lgn)*numpy.sqrt(kernel_size)
	z[2,:] = (numpy.random.rand(num_lgn)-0.5)
	z[3,:] = numpy.random.rand(num_lgn)*5
	k0[:-1] = z.flatten()
	k0=k0.tolist()
	lscsm = LSCSM(numpy.mat(X),numpy.mat(Y[:,i]),num_lgn)
	rf = lscsm.returnRFs(numpy.array([k0]))
	pylab.figure()
	m = numpy.max(numpy.abs(rf[0,0:kernel_size]))
	pylab.imshow(numpy.reshape(rf[0],(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
	
	K = fmin_ncg(lscsm.func(),numpy.array(k0),lscsm.der(),fhess = lscsm.hess(),avextol=0.00001,maxiter=10000)
	Ks[i,:] = K
	
    return [Ks,rpi,lscsm]
	    
    
def runLSCSM():
    #f = open("modelfitDatabase1.dat",'rb')
    #import pickle
    #dd = pickle.load(f)
    #f.close()
    
    #node = dd.children[0]
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.JanA.dataimport.sortOutLoading(contrib.dd.DB(None))
    raw_validation_set = db_node.data["raw_validation_set"]
    
    # creat history
    history_set = training_set[0:-1,:]
    history_validation_set = validation_set[0:-1,:]
    training_set = training_set[1:,:]
    validation_set = validation_set[1:,:]
    training_inputs= training_inputs[1:,:]
    validation_inputs= validation_inputs[1:,:]
    
    print numpy.shape(training_inputs[0])
    
    params={}
    params["LGN_NUM"] = __main__.__dict__.get('LgnNum',10)
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,kernel_size = numpy.shape(training_inputs)
    size = numpy.sqrt(kernel_size)
    num_neurons=1

    sx,sy = numpy.shape(training_set)	
    [K,rpi,glm]=  fitLSCSM(numpy.mat(training_inputs),numpy.mat(training_set),params["LGN_NUM"],num_neurons)
    
    rfs = glm.returnRFs(K[:num_neurons,:])
    
    pylab.figure()
    m = numpy.max(numpy.abs(rfs))
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
    	pylab.imshow(numpy.reshape(rfs[i,0:kernel_size],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('GLM_rfs.png'))	
	    
    pylab.figure()
    m = numpy.max(numpy.abs(rpi))
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)
    	pylab.imshow(numpy.reshape(rpi[:,i],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('RPI_rfs.png'))
    
    rpi_pred_act = training_inputs * rpi
    rpi_pred_val_act = validation_inputs * rpi
    
    glm_pred_act = glm.response(training_inputs,K)
    glm_pred_val_act = glm.response(validation_inputs,K)
        
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpi_pred_act))
    rpi_pred_act_t = apply_output_function(numpy.mat(rpi_pred_act),ofs)
    rpi_pred_val_act_t = apply_output_function(numpy.mat(rpi_pred_val_act),ofs)
    
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(glm_pred_act))
    glm_pred_act_t = apply_output_function(numpy.mat(glm_pred_act),ofs)
    glm_pred_val_act_t = apply_output_function(numpy.mat(glm_pred_val_act),ofs)
    
    
    pylab.figure()
    pylab.title('RPI')
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
    	pylab.plot(rpi_pred_val_act[:,i],validation_set[:,i],'o')
    pylab.savefig(normalize_path('RPI_val_relationship.png'))	
	
    pylab.figure()
    pylab.title('GLM')
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
 	pylab.plot(glm_pred_val_act[:,i],validation_set[:,i],'o')   
    pylab.savefig(normalize_path('GLM_val_relationship.png'))
    
    
    pylab.figure()
    pylab.title('RPI')
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
    	pylab.plot(rpi_pred_val_act_t[:,i],validation_set[:,i],'o')
    pylab.savefig(normalize_path('RPI_t_val_relationship.png'))	
	
	
    pylab.figure()
    pylab.title('GLM')
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
 	pylab.plot(glm_pred_val_act_t[:,i],validation_set[:,i],'o')   
    pylab.savefig(normalize_path('GLM_t_val_relationship.png'))
    
    raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)
    
    print 'RPI \n'
	
    (ranks,correct,pred) = performIdentification(validation_set,rpi_pred_val_act)
    print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - rpi_pred_val_act,2))
	
    (ranks,correct,pred) = performIdentification(validation_set,rpi_pred_val_act_t)
    print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - rpi_pred_val_act_t,2))
		
    signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(rpi_pred_act), numpy.array(rpi_pred_val_act))
    signal_power,noise_power,normalized_noise_power,training_prediction_power_t,validation_prediction_power_t = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(rpi_pred_act_t), numpy.array(rpi_pred_val_act_t))
	
    print "Prediction power on training set / validation set: ", numpy.mean(training_prediction_power) , " / " , numpy.mean(validation_prediction_power)
    print "Prediction power after TF on training set / validation set: ", numpy.mean(training_prediction_power_t) , " / " , numpy.mean(validation_prediction_power_t)

	
    print '\n \n GLM \n'
	
    (ranks,correct,pred) = performIdentification(validation_set,glm_pred_val_act)
    print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - glm_pred_val_act,2))
	
    (ranks,correct,pred) = performIdentification(validation_set,glm_pred_val_act_t)
    print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - glm_pred_val_act_t,2))
		
    signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(glm_pred_act), numpy.array(glm_pred_val_act))
    signal_power,noise_power,normalized_noise_power,training_prediction_power_t,validation_prediction_power_t = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(glm_pred_act_t), numpy.array(glm_pred_val_act_t))
	
    print "Prediction power on training set / validation set: ", numpy.mean(training_prediction_power) , " / " , numpy.mean(validation_prediction_power)
    print "Prediction power after TF on training set / validation set: ", numpy.mean(training_prediction_power_t) , " / " , numpy.mean(validation_prediction_power_t)
    
    db_node.add_data("Kernels",K,force=True)
    db_node.add_data("GLM",glm,force=True)
    db_node.add_data("ReversCorrelationPredictedActivities",glm_pred_act,force=True)
    db_node.add_data("ReversCorrelationPredictedActivities+TF",glm_pred_act_t,force=True)
    db_node.add_data("ReversCorrelationPredictedValidationActivities",glm_pred_val_act,force=True)
    db_node.add_data("ReversCorrelationPredictedValidationActivities+TF",glm_pred_val_act_t,force=True)
    
    f = open("modelfitDatabase1.dat",'wb')
    pickle.dump(dd,f,-2)
    f.close()
    
    return [K,validation_inputs, validation_set]
	
	
def laplaceBias(sizex,sizey):
	S = numpy.zeros((sizex*sizey,sizex*sizey))
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
			S[x*sizex+y,:] = norm.flatten()
	S=numpy.mat(S)
        return S*S.T
	
	
	
	
	
def h(a,b):
    a(b)
	
def testLSCSM():
    X = numpy.mat(numpy.zeros((25,25)))
    glm = LSCSM(X,numpy.mat(X[:,1]),3)	
    l_h =  glm.hess()
    f = glm.func()
    h(l_h,numpy.mat(numpy.zeros((1,10))).getA1())
