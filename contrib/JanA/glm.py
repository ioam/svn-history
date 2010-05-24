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
	
	def __init__(self,XX,YY,ZZ,HH=None,history_bias=0.0,afferent_bias=0.0,norm='LAPLACE',of='Exp'):
	    (self.num_pres,self.kernel_size) = numpy.shape(XX) 	
	    
	    self.Y = theano.shared(YY)
    	    self.X = theano.shared(XX)
	    self.Z = theano.shared(ZZ)
	    self.K = T.dvector('K')
	    self.k = self.K[0:self.kernel_size]
	    self.n = self.K[self.kernel_size]
	    self.a = self.K[self.kernel_size+1]
	    self.afferent_norm = norm
	    self.history_bias = history_bias
	    self.afferent_bias = afferent_bias
	    self.of = of
	    self.history = (HH != None)
	    
	    if self.history:
               (self.num_pres,self.history_size) = numpy.shape(HH)
	       self.H = theano.shared(numpy.mat(HH))		    
	       self.h = self.K[self.kernel_size+2:self.kernel_size+2+self.history_size]		    
        
	def model_output(self):
	    lin = T.dot(self.X,self.k.T) 
	    
	    if self.history:
	       lin = lin + T.dot(self.H,self.h.T)
	    
	    return self.construct_of(lin - self.n)
	
	def log_likelyhood(self):
	    mo = self.model_output()	
	    ll = T.sum(mo) - T.sum(T.dot(self.Y.T,  T.log(mo)))
	     
	    if self.afferent_norm == 'LAPLACE':
	    	ll = ll + T.sum(T.dot(self.k ,T.dot(self.Z,self.k.T)))
	    elif self.afferent_norm == 'SPARSE':
	    	ll = ll + self.afferent_bias*T.sum(abs(self.k))
	     
	    if self.history and (self.history_bias != 0):
	       ll = ll + self.history_bias*T.sum(abs(self.h))
	    return ll	
	
	def func(self):
	    return theano.function(inputs=[self.K], outputs=self.log_likelyhood()) 
			
	def der(self):
	    g_K = T.grad(self.log_likelyhood(), self.K)
	    return theano.function(inputs=[self.K], outputs=g_K)
 
 	def hess(self):
            g_K = T.grad(self.log_likelyhood(), self.K,consider_constant=[self.Y,self.X])
	    H, updates = theano.scan(lambda i,v: T.grad(g_K[i],v), sequences= T.arange(g_K.shape[0]), non_sequences=self.K)
  	    return theano.function(inputs=[self.K], outputs=H)
	
	def construct_of(self,inn):
    	    if self.of == 'Exp':
	       return T.exp(inn)
	    elif self.of == 'Sigmoid':
	       return 1 / (1 + T.exp(inn)) 

	
	def response(self,X,H,kernels):
	    self.X.value = X	
	    self.H.value = H
	    resp = theano.function(inputs=[self.K], outputs=self.model_output())
	    
	    (a,b) = numpy.shape(kernels)
	    (c,d) = numpy.shape(X)
	    
	    responses = numpy.zeros((c,a))
	    for i in xrange(0,a):
		responses[:,i] = resp(kernels[i,:]).T
	    
	    return responses
	    
def fitGLM(X,Y,H,l,hl,sp,norm,of,lateral,num_neurons_to_estimate):
    num_pres,num_neurons = numpy.shape(Y)
    num_pres,kernel_size = numpy.shape(X)
    
    if H != None:
       (trash,hist_size) = numpy.shape(H)
    else:
       hist_size = 0
       
    Ks = numpy.zeros((num_neurons,kernel_size+2+hist_size+lateral*(num_neurons-1)))
    
    laplace = laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))
    
    rpi = numpy.linalg.pinv(X.T*X + __main__.__dict__.get('RPILaplaceBias',0.0001)*laplace) * X.T * Y
    for i in xrange(0,num_neurons_to_estimate): 
	print i
	k0 = rpi[:,i].getA1().tolist()+[0,0] + numpy.zeros((1,hist_size)).flatten().tolist()  + numpy.zeros((1,lateral*(num_neurons-1))).flatten().tolist()
	if lateral and H != None:
	   HH = numpy.hstack((H,Y[:,:i],Y[:,i+1:]))
	elif lateral:
	   HH = numpy.hstack((Y[:,:i],Y[:,i+1:]))
	else:
	   HH = H
	
	glm = GLM(numpy.mat(X),numpy.mat(Y[:,i]),l*laplace,HH,hl,sp,norm,of=of)
	K = fmin_ncg(glm.func(),numpy.array(k0),glm.der(),fhess = glm.hess(),avextol=0.00001,maxiter=200)
	Ks[i,:] = K
	
    return [Ks,rpi,glm]
	    
    
def runGLM():
    res = contrib.dd.loadResults("results.dat")
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.JanA.dataimport.sortOutLoading(res)
    #return
    raw_validation_set = db_node.data["raw_validation_set"]
    
    dataset = contrib.JanA.dataimport.loadSimpleDataSet('Mice/2009_11_04/Raw/region3/spiking_13-15.dat',1800,103,num_rep=1,num_frames=1,offset=0,transpose=False)
    history_set = contrib.JanA.dataimport.generateTrainingSet(dataset)
    
    dataset = contrib.JanA.dataimport.loadSimpleDataSet('Mice/2009_11_04/Raw/region3/val/spiking_13-15.dat',50,103,num_rep=10,num_frames=1,offset=0,transpose=False)
    dataset = contrib.JanA.dataimport.averageRepetitions(dataset)
    history_validation_set = contrib.JanA.dataimport.generateTrainingSet(dataset)
    
    print numpy.shape(training_inputs[0])
    
    params={}
    params["LaplacaBias"] = __main__.__dict__.get('LaplaceBias',0.0004)
    params["Norm"] = __main__.__dict__.get('Norm','LAPLACE')
    params["SparseBias"] = __main__.__dict__.get('SparseBias',0.0004)
    params["OF"] = __main__.__dict__.get('OF','Exp')
    params["HistoryShort"] = __main__.__dict__.get('HistoryShort',False)
    params["HistoryLong"] = __main__.__dict__.get('HistoryLong',False)
    params["Lateral"] = __main__.__dict__.get('Lateral',False)
    
    if params["HistoryShort"] or params["HistoryLong"] or params["Lateral"]:
       params["HistBias"] = __main__.__dict__.get('HistBias',0)
     
    histories =  []
    val_histories = []
        
    if params["HistoryShort"]:
    	histories.append(history_set[0:-1,:])
    	val_histories.append(history_validation_set[0:-1,:])
    
    if params["HistoryLong"]:
    	histories.append(training_set[0:-1,:])
    	val_histories.append(validation_set[0:-1,:])
    
    if params["HistoryShort"] or params["HistoryLong"]:
    	history_set = numpy.mat(numpy.hstack(histories))
    	history_validation_set = numpy.mat(numpy.hstack(val_histories))
    else:
 	history_set=None
	history_validation_set=None
 
    # creat history
    training_set = training_set[1:,:]
    validation_set = validation_set[1:,:]
    training_inputs= training_inputs[1:,:]
    validation_inputs= validation_inputs[1:,:]
    
    for i in xrange(0,len(raw_validation_set)):
	raw_validation_set[i] = raw_validation_set[i][1:,:]


 
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,kernel_size = numpy.shape(training_inputs)
    num_neurons_to_run=1#num_neurons
    
    [K,rpi,glm]=  fitGLM(numpy.mat(training_inputs),numpy.mat(training_set),history_set,params["LaplacaBias"],__main__.__dict__.get('HistBias',0),params["SparseBias"],params["Norm"],params["OF"],params["Lateral"],num_neurons_to_run)
	    
    analyseGLM(K,rpi,glm,validation_inputs,training_inputs,validation_set,training_set,raw_validation_set,history_set,history_validation_set,db_node,num_neurons_to_run)
    
    db_node.add_data("Kernels",K,force=True)
    db_node.add_data("GLM",glm,force=True)
    db_node.add_data("HistorySet",history_set,force=True)
    db_node.add_data("HistoryValidationSet",history_validation_set,force=True)
    
    contrib.dd.saveResults(res,"results.dat")

    
def analyseGLM(K,rpi,glm,validation_inputs,training_inputs,validation_set,training_set,raw_validation_set,history_set,history_validation_set,db_node,num_neurons_to_run):
    num_pres,kernel_size = numpy.shape(training_inputs)
    num_pres,num_neurons = numpy.shape(training_set)
    size = numpy.sqrt(kernel_size)
    #num_neurons=num_neurons_to_run
    
    pylab.figure()
    m = numpy.max(numpy.abs(K))
    for i in xrange(0,num_neurons_to_run):
	pylab.subplot(11,11,i+1)    
    	pylab.imshow(numpy.reshape(K[i,0:kernel_size],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('GLM_rfs.png'))	
	    
    pylab.figure()
    m = numpy.max(numpy.abs(rpi))
    for i in xrange(0,num_neurons_to_run):
	pylab.subplot(11,11,i+1)
    	pylab.imshow(numpy.reshape(rpi[:,i],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('RPI_rfs.png'))
    
    rpi_pred_act = training_inputs * rpi
    rpi_pred_val_act = validation_inputs * rpi
    
    
    if not __main__.__dict__.get('Lateral',False):
    	glm_pred_act = glm.response(training_inputs,history_set,K)
	glm_pred_val_act = glm.response(validation_inputs,history_validation_set,K)
    else:
	if history_set != None:    
		print numpy.shape(history_set)
		print numpy.shape(numpy.delete(training_set,[i],axis=1))
       		glm_pred_act =  numpy.hstack([ glm.response(training_inputs,numpy.vstack((history_set,numpy.delete(training_set,[i],axis=1))),numpy.array([K[i]])) for i in xrange(0,num_neurons)])
		glm_pred_val_act =  numpy.hstack([ glm.response(validation_inputs,numpy.vstack((history_validation_set,numpy.delete(validation_set,[i],axis=1))),numpy.array([K[i]])) for i in xrange(0,num_neurons)])
        else:
       		glm_pred_act =  numpy.hstack([ glm.response(training_inputs,numpy.delete(training_set,[i],axis=1),numpy.array([K[i]])) for i in xrange(0,num_neurons)])
		glm_pred_val_act =  numpy.hstack([ glm.response(validation_inputs,numpy.delete(validation_set,[i],axis=1),numpy.array([K[i]])) for i in xrange(0,num_neurons)])
	
    print glm_pred_act	
    print numpy.shape(glm_pred_act)
	
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpi_pred_act))
    rpi_pred_act_t = apply_output_function(numpy.mat(rpi_pred_act),ofs)
    rpi_pred_val_act_t = apply_output_function(numpy.mat(rpi_pred_val_act),ofs)
    
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(glm_pred_act))
    glm_pred_act_t = apply_output_function(numpy.mat(glm_pred_act),ofs)
    glm_pred_val_act_t = apply_output_function(numpy.mat(glm_pred_val_act),ofs)
    
    
    pylab.figure()
    pylab.title('RPI')
    for i in xrange(0,num_neurons_to_run):
	pylab.subplot(11,11,i+1)    
    	pylab.plot(rpi_pred_val_act[:,i],validation_set[:,i],'o')
    pylab.savefig(normalize_path('RPI_val_relationship.png'))	
	
    pylab.figure()
    pylab.title('GLM')
    for i in xrange(0,num_neurons_to_run):
	pylab.subplot(11,11,i+1)    
 	pylab.plot(glm_pred_val_act[:,i],validation_set[:,i],'o')   
    pylab.savefig(normalize_path('GLM_val_relationship.png'))
    
    
    pylab.figure()
    pylab.title('RPI')
    for i in xrange(0,num_neurons_to_run):
	pylab.subplot(11,11,i+1)    
    	pylab.plot(rpi_pred_val_act_t[:,i],validation_set[:,i],'o')
    pylab.savefig(normalize_path('RPI_t_val_relationship.png'))	
	
	
    pylab.figure()
    pylab.title('GLM')
    for i in xrange(0,num_neurons_to_run):
	pylab.subplot(11,11,i+1)    
 	pylab.plot(glm_pred_val_act_t[:,i],validation_set[:,i],'o')   
    pylab.savefig(normalize_path('GLM_t_val_relationship.png'))
    
    pylab.figure()
    pylab.plot(numpy.mean(numpy.power(validation_set - rpi_pred_val_act_t,2)[:,:num_neurons_to_run],0),numpy.mean(numpy.power(validation_set - glm_pred_val_act,2)[:,:num_neurons_to_run],0),'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI')
    pylab.ylabel('GLM')
    pylab.savefig(normalize_path('GLM_vs_RPI_MSE.png'))
    
    print '\n \n RPI \n'
    
    print 'Without TF'
    performance_analysis(training_set,validation_set,rpi_pred_act,rpi_pred_val_act,raw_validation_set)
    print 'With TF'
    (signal_power,noise_power,normalized_noise_power,training_prediction_power,rpi_validation_prediction_power,signal_power_variance) = performance_analysis(training_set,validation_set,rpi_pred_act_t,rpi_pred_val_act_t,raw_validation_set)
	
    print '\n \n GLM \n'
	
    print 'Without TF'
    (signal_power,noise_power,normalized_noise_power,training_prediction_power,glm_validation_prediction_power,signal_power_variance) = performance_analysis(training_set,validation_set,glm_pred_act,glm_pred_val_act,raw_validation_set)
    print 'With TF'
    performance_analysis(training_set,validation_set,glm_pred_act_t,glm_pred_val_act_t,raw_validation_set)
    
    
    pylab.figure()
    pylab.plot(rpi_validation_prediction_power[:num_neurons_to_run],glm_validation_prediction_power[:num_neurons_to_run],'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI')
    pylab.ylabel('GLM')
    pylab.savefig(normalize_path('GLM_vs_RPI_prediction_power.png'))
    
    db_node.add_data("ReversCorrelationPredictedActivities",glm_pred_act,force=True)
    db_node.add_data("ReversCorrelationPredictedActivities+TF",glm_pred_act_t,force=True)
    db_node.add_data("ReversCorrelationPredictedValidationActivities",glm_pred_val_act,force=True)
    db_node.add_data("ReversCorrelationPredictedValidationActivities+TF",glm_pred_val_act_t,force=True)


def analyseStoredGLM():
    res = contrib.dd.loadResults("results.dat")
    node = res.children[0].children[3]
    	
    dataset = contrib.JanA.dataimport.loadSimpleDataSet('Mice/2009_11_04/Raw/region3/spiking_13-15.dat',1800,103,num_rep=1,num_frames=1,offset=0,transpose=False)
    history_set = contrib.JanA.dataimport.generateTrainingSet(dataset)
    
    dataset = contrib.JanA.dataimport.loadSimpleDataSet('Mice/2009_11_04/Raw/region3/val/spiking_13-15.dat',50,103,num_rep=10,num_frames=1,offset=0,transpose=False)
    dataset = contrib.JanA.dataimport.averageRepetitions(dataset)
    history_validation_set = contrib.JanA.dataimport.generateTrainingSet(dataset)
	
	
    history_set = history_set[0:-1,:]
    history_validation_set = history_validation_set[0:-1,:]
    training_set = node.data["training_set"][1:,:]
    validation_set = node.data["validation_set"][1:,:]
    training_inputs = node.data["training_inputs"][1:,:]
    validation_inputs = node.data["validation_inputs"][1:,:]
    raw_validation_set = node.data["raw_validation_set"]
    
    K = node.children[7].data["Kernels"]
    glm = node.children[7].data["GLM"]
    
	
    rpi = numpy.linalg.pinv(numpy.mat(training_inputs).T*numpy.mat(training_inputs) + __main__.__dict__.get('RPILaplaceBias',0.0001)*laplaceBias(numpy.sqrt(numpy.shape(training_inputs)[1]),numpy.sqrt(numpy.shape(training_inputs)[1]))) * numpy.mat(training_inputs).T * numpy.mat(training_set)	
    
    analyseGLM(K,rpi,glm,validation_inputs,training_inputs,validation_set,training_set,raw_validation_set,history_set,history_validation_set,contrib.dd.DB(None),numpy.shape(training_set)[1])	
	

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

def performIdentification(K,inputs,measured_activities):
    (num_image,num_neurons) = numpy.shape(measured_activities)
    	
    for i in xrange(0,num_neurons):
	GLM(numpy.mat(X),numpy.mat(Y[:,i]),l*laplace,numpy.mat(H),hl,sp,norm,of=of)    
	    
	
	
	