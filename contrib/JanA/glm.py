from scipy.optimize import fmin_ncg
import __main__
import numpy
import pylab
import sys
sys.path.append('/home/antolikjan/topographica/Theano/')
import theano 
from theano import tensor as T
from topo.misc.filepath import normalize_path, application_path

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
	    self.loglikelyhood = T.sum(T.exp(self.a*T.dot(self.X,self.k.T)-self.n)) - T.sum(T.dot(self.Y.T,self.a*T.dot(self.X,self.k.T)-self.n)) + T.sum(T.dot(self.k ,T.dot(self.Z,self.k.T))) 
	    #self.l*T.sum(self.k**2)

	def func(self):
	    return theano.function(inputs=[self.K], outputs=self.loglikelyhood,mode='DEBUG_MODE') 
			
	def der(self):
	    g_K = T.grad(self.loglikelyhood, self.K)
	    return theano.function(inputs=[self.K], outputs=g_K,mode='DEBUG_MODE')
 
 	def hess(self):
            g_K = T.grad(self.loglikelyhood, self.K,consider_constant=[self.Y,self.X])
	    H, updates = theano.scan(lambda i,v: T.grad(g_K[i],v), sequences= T.arange(g_K.shape[0]), non_sequences=self.K)
  	    return theano.function(inputs=[self.K], outputs=H,mode='DEBUG_MODE')
	    

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


def fitGLM(X,Y,l):
    s=0	
    sta = X.T*Y[:,s]
    k0 =numpy.vstack([numpy.mat(sta),[[0],[0]]])
    #augmented_inputs = numpy.hstack([X,numpy.zeros((numpy.shape(X)[0],1))])
    
    glm = GLM(numpy.mat(X),numpy.mat(Y[:,s]),l*laplaceBias(22,22))

    K = fmin_ncg(glm.func(),k0.getA1(),glm.der(),fhess = glm.hess(),avextol=0.00001)
    return K
    
def h(z):
    print 'A'    
    
def fitGLM1(X,Y,l):
    num_pres,num_neurons = numpy.shape(Y)
    num_pres,kernel_size = numpy.shape(X)
    
    Ks = numpy.zeros((num_neurons,kernel_size))
    
    for i in xrange(0,num_neurons): 
	sta = X.T*Y[:,i]
	k0 =numpy.vstack([numpy.mat(sta),[[0],[0]]])
	#k0 = sta
	augmented_inputs = numpy.hstack([X,numpy.ones((numpy.shape(X)[0],1))])
	
	glm = GLM(numpy.mat(augmented_inputs),numpy.mat(Y[:,i]),l)
	K = fmin_ncg(glm.func(),k0.getA1(),glm.der(),fhess = glm.hess(),avextol=0.000001,callback=h,maxiter=10)
        #Ks = K[)]
    return Ks
    
    
    
def runGLM():
    import contrib.modelfit
    f = open("modelfitDatabase1.dat",'rb')
    import pickle
    d = pickle.load(f)
    f.close()
    
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.modelfit.sortOutLoading(d)
    
    training_set = (training_set)/0.028;
    validation_set = (validation_set)/0.028;
    
    training_inputs=training_inputs/1000000.0
    validation_inputs=validation_inputs/1000000.0
    
    
    print numpy.shape(training_inputs[0])
    
    params={}
    params["GLMlambda"] = __main__.__dict__.get('Alpha',50)
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    sx,sy = numpy.shape(training_set)	
    K=  fitGLM(numpy.mat(training_inputs),numpy.mat(training_set),params["GLMlambda"])
    
    pylab.figure()
    m = numpy.max(numpy.abs(K[0:22*22]))
    pylab.imshow(numpy.reshape(K[0:22*22],(22,22)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.savefig(normalize_path('RFs.png'))

    
    return [K,validation_inputs, validation_set]
    
    #f = open("modelfitDatabase1.dat",'wb')
    #pickle.dump(d,f,-2)
    #f.close()
    

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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def drawkernel(k):
    m = numpy.max(numpy.abs(k))
    pylab.imshow(numpy.reshape(k,(22,22)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu,interpolation='nearest')
    pylab.show._needmain=False
    pylab.show()

def h(a,b):
    a(b)
	

def testGLM():
    X = numpy.mat(numpy.zeros((1000,1000)))
    glm = GLM(X,numpy.mat(X[:,1]),1.0)	
    l_h =  glm.hess()
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
