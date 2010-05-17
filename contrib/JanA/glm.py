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


class GLM(object):
	
	def __init__(self,XX,YY,ZZ,HH=None,history_bias=1.0,sparse_bias=0.0,norm='LAPLACE'):
	    (self.num_pres,self.kernel_size) = numpy.shape(XX) 	
	    
	    self.Y = theano.shared(YY)
    	    self.X = theano.shared(XX)
	    self.Z = theano.shared(ZZ)
	    self.K = T.dvector('K')
	    self.k = self.K[0:self.kernel_size]
	    self.n = self.K[self.kernel_size]
	    self.a = self.K[self.kernel_size+1]
	    self.lin = T.dot(self.X,self.k.T) 
	    
	    if HH != None:
	       #we also have a history of other neurons
	       (self.num_pres,self.num_neurons) = numpy.shape(HH)
	       self.H = theano.shared(HH)		    
	       self.h = self.K[self.kernel_size+2:self.kernel_size+2+self.num_neurons]		    
	       self.lin = self.lin + T.dot(self.H,self.h.T)
	       print 'B'
	    
	    self.model = T.exp(self.lin - self.n)
	    
	    self.loglikelyhood = T.sum(self.model) - T.sum(T.dot(self.Y.T,  T.log(self.model)))
	     
	    if norm == 'LAPLACE':
		print 'LAPLACE'
	    	self.loglikelyhood = self.loglikelyhood + T.sum(T.dot(self.k ,T.dot(self.Z,self.k.T)))
	    elif norm == 'SPARSE':
		print 'SPARSE'
	    	self.loglikelyhood = self.loglikelyhood + sparse_bias*T.sum(abs(self.k))
	     
	    if (HH != None) and (history_bias != 0):
	       self.loglikelyhood = self.loglikelyhood + history_bias*T.sum(abs(self.h))
	       print 'B'

	def func(self):
	    return theano.function(inputs=[self.K], outputs=self.loglikelyhood) 
			
	def der(self):
	    g_K = T.grad(self.loglikelyhood, self.K)
	    return theano.function(inputs=[self.K], outputs=g_K)
 
 	def hess(self):
            g_K = T.grad(self.loglikelyhood, self.K,consider_constant=[self.Y,self.X])
	    H, updates = theano.scan(lambda i,v: T.grad(g_K[i],v), sequences= T.arange(g_K.shape[0]), non_sequences=self.K)
  	    return theano.function(inputs=[self.K], outputs=H)
	
	def response(self,X,H,kernels):
	    self.IN = theano.shared(X)	
	    self.HH = theano.shared(H)
	    self.lin = T.dot(self.IN,self.k.T) 
	    if H != None:
	     	self.lin + T.dot(self.HH,self.h.T)	
		
	    self.model = T.exp(self.lin -self.n)
	     	
	    resp =  theano.function(inputs=[self.K], outputs=self.model)
	    
	    (a,b) = numpy.shape(kernels)
	    (c,d) = numpy.shape(X)
	    
	    responses = numpy.zeros((c,a))
	    
	    for i in xrange(a):
		responses[:,i] = resp(kernels[i,:]).T
	    
	    return responses
	    
def fitGLM(X,Y,H,l,hl,sp,norm,num_neurons_to_estimate):
    num_pres,num_neurons = numpy.shape(Y)
    num_pres,kernel_size = numpy.shape(X)
    
    if H!= None:
       Ks = numpy.zeros((num_neurons,kernel_size+2+num_neurons))
    else:
       Ks = numpy.zeros((num_neurons,kernel_size+2))
    
    laplace = laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))
    
    rpi = numpy.linalg.pinv(X.T*X + __main__.__dict__.get('RPILaplaceBias',0.0001)*laplace) * X.T * Y
    
    print 'C'
    
    for i in xrange(0,num_neurons_to_estimate): 
	print i
	k0 = rpi[:,i].getA1().tolist()+[0,0]
	if H!= None:
	   k0 = k0 +numpy.zeros((1,num_neurons)).flatten().tolist()
	   glm = GLM(numpy.mat(X),numpy.mat(Y[:,i]),l*laplace,numpy.mat(H),hl,sp,norm)
	else:
	   glm = GLM(numpy.mat(X),numpy.mat(Y[:,i]),l*laplace,None,hl,sp,norm)
	K = fmin_ncg(glm.func(),numpy.array(k0),glm.der(),fhess = glm.hess(),avextol=0.00001,maxiter=20)
	Ks[i,:] = K
	
    return [Ks,rpi,glm]
	    
    
def runGLM():
    res = contrib.dd.loadResults("results.dat")
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.JanA.dataimport.sortOutLoading(res)
    #return
    raw_validation_set = db_node.data["raw_validation_set"]
    
    # creat history
    history_set = training_set[0:-1,:]
    history_validation_set = validation_set[0:-1,:]
    training_set = training_set[1:,:]
    validation_set = validation_set[1:,:]
    training_inputs= training_inputs[1:,:]
    validation_inputs= validation_inputs[1:,:]
    
    for i in xrange(0,len(raw_validation_set)):
	raw_validation_set[i] = raw_validation_set[i][1:,:]
    
    
    print numpy.shape(training_inputs[0])
    
    params={}
    params["LaplacaBias"] = __main__.__dict__.get('LaplaceBias',0.0004)
    params["Norm"] = __main__.__dict__.get('Norm','LAPLACE')
    params["SparseBias"] = __main__.__dict__.get('SparseBias',0.0004)
    params["History"] = __main__.__dict__.get('History',False)
    if params["History"]:
       params["HistBias"] = __main__.__dict__.get('HistBias',0)
     
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,kernel_size = numpy.shape(training_inputs)
    num_neurons_to_run=num_neurons
    
    sx,sy = numpy.shape(training_set)	
    if __main__.__dict__.get('History',False):
    	[K,rpi,glm]=  fitGLM(numpy.mat(training_inputs),numpy.mat(training_set),numpy.mat(history_set),params["LaplacaBias"],params["HistBias"],params["SparseBias"],params["Norm"],num_neurons_to_run)
    else:
	[K,rpi,glm]=  fitGLM(numpy.mat(training_inputs),numpy.mat(training_set),None,params["LaplacaBias"],0,params["SparseBias"],params["Norm"],num_neurons_to_run)
	    
	    
    analyseGLM(K,rpi,glm,validation_inputs,training_inputs,validation_set,training_set,raw_validation_set,history_set,history_validation_set,db_node,num_neurons_to_run)
    
    db_node.add_data("Kernels",K,force=True)
    db_node.add_data("GLM",glm,force=True)
    
    contrib.dd.saveResults(res,"results.dat")

    
def analyseGLM(K,rpi,glm,validation_inputs,training_inputs,validation_set,training_set,raw_validation_set,history_set,history_validation_set,db_node,num_neurons_to_run):
    num_pres,kernel_size = numpy.shape(training_inputs)
    size = numpy.sqrt(kernel_size)
    num_neurons=num_neurons_to_run
    
    pylab.figure()
    m = numpy.max(numpy.abs(K))
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
    	pylab.imshow(numpy.reshape(K[i,0:kernel_size],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('GLM_rfs.png'))	
	    
    pylab.figure()
    m = numpy.max(numpy.abs(rpi))
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)
    	pylab.imshow(numpy.reshape(rpi[:,i],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('RPI_rfs.png'))
    
    rpi_pred_act = training_inputs * rpi
    rpi_pred_val_act = validation_inputs * rpi
    
    if __main__.__dict__.get('History',False):
    	glm_pred_act = glm.response(training_inputs,history_set,K)
    	glm_pred_val_act = glm.response(validation_inputs,history_validation_set,K)
    else:
	glm_pred_act = glm.response(training_inputs,None,K)
    	glm_pred_val_act = glm.response(validation_inputs,None,K)	
	
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
    
    pylab.figure()
    pylab.plot(numpy.mean(numpy.power(validation_set - rpi_pred_val_act_t,2)[:,:num_neurons],0),numpy.mean(numpy.power(validation_set - glm_pred_val_act,2)[:,:num_neurons],0),'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI')
    pylab.ylabel('GLM')
    pylab.savefig(normalize_path('GLM_vs_RPI_MSE.png'))
    
    raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)
    
    print 'RPI \n'
	
    (ranks,correct,pred) = performIdentification(validation_set,rpi_pred_val_act)
    print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - rpi_pred_val_act,2))
	
    (ranks,correct,pred) = performIdentification(validation_set,rpi_pred_val_act_t)
    print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - rpi_pred_val_act_t,2))
		
    signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(rpi_pred_act), numpy.array(rpi_pred_val_act))
    
    signal_power,noise_power,normalized_noise_power,training_prediction_power_t,validation_prediction_power_t = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(rpi_pred_act_t), numpy.array(rpi_pred_val_act_t))
    rpi_validation_prediction_power = validation_prediction_power_t	
    print "Prediction power on training set / validation set: ", numpy.mean(training_prediction_power) , " / " , numpy.mean(validation_prediction_power)
    print "Prediction power after TF on training set / validation set: ", numpy.mean(training_prediction_power_t) , " / " , numpy.mean(validation_prediction_power_t)
    
	
    print '\n \n GLM \n'
	
    (ranks,correct,pred) = performIdentification(validation_set,glm_pred_val_act)
    print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - glm_pred_val_act,2))
	
    (ranks,correct,pred) = performIdentification(validation_set,glm_pred_val_act_t)
    print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - glm_pred_val_act_t,2))
		
    signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(glm_pred_act), numpy.array(glm_pred_val_act))
    
    glm_validation_prediction_power = validation_prediction_power
    
    signal_power,noise_power,normalized_noise_power,training_prediction_power_t,validation_prediction_power_t = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(glm_pred_act_t), numpy.array(glm_pred_val_act_t))
    	
    print "Prediction power on training set / validation set: ", numpy.mean(training_prediction_power) , " / " , numpy.mean(validation_prediction_power)
    print "Prediction power after TF on training set / validation set: ", numpy.mean(training_prediction_power_t) , " / " , numpy.mean(validation_prediction_power_t)
    
    
    pylab.figure()
    pylab.plot(rpi_validation_prediction_power[:num_neurons],glm_validation_prediction_power[:num_neurons],'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI')
    pylab.ylabel('GLM')
    pylab.savefig(normalize_path('GLM_vs_RPI_prediction_power.png'))
    
    db_node.add_data("ReversCorrelationPredictedActivities",glm_pred_act,force=True)
    db_node.add_data("ReversCorrelationPredictedActivities+TF",glm_pred_act_t,force=True)
    db_node.add_data("ReversCorrelationPredictedValidationActivities",glm_pred_val_act,force=True)
    db_node.add_data("ReversCorrelationPredictedValidationActivities+TF",glm_pred_val_act_t,force=True)


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

def testGLM():
    X = numpy.mat(numpy.zeros((1000,1000)))
    glm = GLM(X,numpy.mat(X[:,1]),numpy.eye(1000))	
    l_h =  glm.hess()
    f = glm.func()
    glmLL_hess(numpy.mat(numpy.zeros((1,1000))).getA1(),X,numpy.mat(X[:,1]),1.0)
    h(l_h,numpy.mat(numpy.zeros((1,1002))).getA1())
