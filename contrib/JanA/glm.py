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

class GLM(object):
	
	def __init__(self,XX,YY,ZZ):
	    (self.num_pres,self.kernel_size) = numpy.shape(XX) 	
	    (self.num_pres,self.num_neurons) = numpy.shape(YY)

	    self.Y = theano.shared(YY)
    	    self.X = theano.shared(XX)
	    self.Z = theano.shared(ZZ)
	    self.K = T.dvector('K')
	    self.k = self.K[0:self.kernel_size]
	    self.n = self.K[self.kernel_size]
	    self.a = self.K[self.kernel_size+1]
	    self.model = T.exp(T.dot(self.X,self.k.T)-self.n)
	    self.loglikelyhood = T.sum(self.model) - T.sum(T.dot(self.Y.T,  T.log(self.model))) + T.sum(T.dot(self.k ,T.dot(self.Z,self.k.T))) 
	    

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
	    self.model = T.exp(T.dot(self.IN,self.k.T)-self.n)		
	    resp =  theano.function(inputs=[self.K], outputs=self.model)
	    
	    (a,b) = numpy.shape(kernels)
	    (c,d) = numpy.shape(X)
	    
	    responses = numpy.zeros((c,a))
	    
	    for i in xrange(a):
		responses[:,i] = resp(kernels[i,:]).T
	    
	    return responses
	    
def fitGLM(X,Y,l,num_neurons):
    #num_pres,num_neurons = numpy.shape(Y)
    num_pres,kernel_size = numpy.shape(X)
    
    Ks = numpy.zeros((num_neurons,kernel_size+2))
    
    laplace = l*laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))
    
    rpi = numpy.linalg.pinv(X.T*X + laplace) * X.T * Y
    
    
    for i in xrange(0,num_neurons): 
	k0 = rpi[:,i].getA1().tolist()+[0,0]
	glm = GLM(numpy.mat(X),numpy.mat(Y[:,i]),laplace)
	K = fmin_ncg(glm.func(),numpy.array(k0),glm.der(),fhess = glm.hess(),avextol=0.00001)
	Ks[i,:] = K
	
    return [Ks,rpi,glm]
	    
    
def runGLM():
    f = open("modelfitDatabase1.dat",'rb')
    import pickle
    dd = pickle.load(f)
    f.close()
    
    node = dd.children[0]
    raw_validation_set = node.data["raw_validation_set"]
    
    
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.modelfit.sortOutLoading(contrib.dd.DB2(None))
    
    training_set = (training_set)/0.028;
    validation_set = (validation_set)/0.028;
    
    training_inputs=training_inputs/1000000.0
    validation_inputs=validation_inputs/1000000.0
    
    
    print numpy.shape(training_inputs[0])
    
    params={}
    params["GLMlambda"] = __main__.__dict__.get('Alpha',50)
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,kernel_size = numpy.shape(training_inputs)
    size = numpy.sqrt(kernel_size)
    #num_neurons=2
    
    sx,sy = numpy.shape(training_set)	
    [K,rpi,glm]=  fitGLM(numpy.mat(training_inputs),numpy.mat(training_set),params["GLMlambda"],num_neurons)

    
    pylab.figure()
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)    
    	m = numpy.max(numpy.abs(K[i,0:kernel_size]))
    	pylab.imshow(numpy.reshape(K[i,0:kernel_size],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('GLM_rfs.png'))	
	    
    pylab.figure()
    for i in xrange(0,num_neurons):
	pylab.subplot(11,11,i+1)
    	m = numpy.max(numpy.abs(rpi[:,i]))
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

def testGLM():
    X = numpy.mat(numpy.zeros((1000,1000)))
    glm = GLM(X,numpy.mat(X[:,1]),numpy.eye(1000))	
    l_h =  glm.hess()
    f = glm.func()
    glmLL_hess(numpy.mat(numpy.zeros((1,1000))).getA1(),X,numpy.mat(X[:,1]),1.0)
    h(l_h,numpy.mat(numpy.zeros((1,1002))).getA1())
    
    
    
     




































#def merge(*args):
   ## Reduce all inputs to vector
   #join_args = []
   #for i,arg in enumerate(args):
      ##arg = numpy.array(arg)
      ##join_args.append(arg.flatten())
      #if arg.type.ndim: # it is not a scalar
           #join_args.append(arg.flatten())
      #else:
           #join_args.append( T.shape_padleft(arg))
   ## join them into a vector
   #return T.join(0, *join_args)

#def dist_arg(f,vec,kernel_size):
    #return f(vec[0:kernel_size],vec[kernel_size]) 	


#class GLM(object):
	
	#def __init__(self,XX,YY,ll):
	    #(self.num_pres,self.kernel_size) = numpy.shape(XX) 	
	    #(self.num_pres,self.num_neurons) = numpy.shape(YY)
		
	    #self.l = theano.shared(ll)
	    #self.Y = theano.shared(YY)
    	    #self.X = theano.shared(XX)
	    #self.K = T.dvector('K')
	    #self.a = T.dscalar('a')
	    #self.loglikelyhood = T.sum(T.exp(self.a*T.dot(self.X,self.K.T))) - T.sum(T.dot(self.Y.T,self.a*T.dot(self.X,self.K.T))) + self.l*T.sum(self.K**2)

	#def func(self):
	    #return lambda x: dist_arg(theano.function(inputs=[self.K,self.a], outputs=self.loglikelyhood,mode='DEBUG_MODE'),x,self.kernel_size) 
			
	#def der(self):
	    #g_K = T.grad(self.loglikelyhood, self.K)
	    #g_a = T.grad(self.loglikelyhood, self.a)
	    #return lambda x: dist_arg(theano.function(inputs=[self.K,self.a], outputs=merge(g_K,g_a),mode='DEBUG_MODE'),x,self.kernel_size)
 
 	#def hess(self):
            #g_K = T.grad(self.loglikelyhood, self.K,consider_constant=[self.Y,self.X,self.l])
	    #g_a = T.grad(self.loglikelyhood, self.a,consider_constant=[self.Y,self.X,self.l])
	    ##H, updates = theano.scan(lambda i,v: T.grad(g_K[i],v), sequences= T.arange(g_K.shape[0]), non_sequences=self.K)
	    #g_all  = merge(g_K,g_a)
	    #H,updates = theano.scan(lambda i,g,m,v: merge(T.grad(g[i],m), T.grad(g[i],v)), sequences = T.arange(g_all.shape[0]), non_sequences= [g_all, g_K, g_a])
	    #return lambda x: dist_arg(theano.function(inputs=[self.K,self.a], outputs=H,mode='DEBUG_MODE'),x,self.kernel_size)

def glmLL(K,X,Y,l):
    # do not include the bias term in ridge regression
    K = numpy.mat(K)	
    k = K.T
    numpy.size(k)
    k[22*22:-1,:]=0
    resp = sum(numpy.exp(X*K.T)) - Y.T*(X*K.T) + l*numpy.sum(numpy.power(k,2))
    return resp.getA1()

def glmLL_der(K,X,Y,l):
    # do not include the bias term in ridge regression
    K = numpy.mat(K)	
    k = K.T
    k[22*22:-1,:]=0
    der = -X.T*Y+X.T*numpy.exp(X*K.T) + 2*k*l
    return der.getA1() 
        
def glmLL_hess(K,X,Y,l):
    # do not include the bias term in ridge regression
    K = numpy.mat(K)	
    k = K.T
    k[22*22:-1,:]=0
    c=k>=0
    hess = X.T*numpy.diag(numpy.exp(X*K.T).getA1())*X + 2*l*numpy.diag(c.getA1())	
    return hess.getA() 
    
