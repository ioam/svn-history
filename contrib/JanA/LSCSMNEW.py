from scipy.optimize import fmin_ncg, anneal, fmin_cg, fmin_bfgs, fmin_tnc, fmin_l_bfgs_b
import __main__
import numpy
import pylab
import sys
sys.path.append('/home/jan/Theano/')
import theano
theano.config.floatX='float32' 
#theano.config.warn.sum_sum_bug=False
from theano import tensor as T
from theano import function, config, shared #, sandbox
from param import normalize_path
from contrib.JanA.ofestimation import *
from contrib.modelfit import *
import contrib.dd
import contrib.JanA.dataimport
from contrib.JanA.regression import laplaceBias
from contrib.JanA.visualization import printCorrelationAnalysis, showRFS
from matplotlib.gridspec import GridSpec
from contrib.JanA.ofestimation import *
import scipy.stats

#pylab.show=lambda:1; 
#pylab.interactive(True)

class LSCSM(object):
        def __init__(self,XX,YY,num_lgn,num_neurons):
            (self.num_pres,self.kernel_size) = numpy.shape(XX)
            self.num_lgn = num_lgn
            self.num_neurons = num_neurons
            self.size = numpy.sqrt(self.kernel_size)

            self.xx = theano.shared(numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).T.flatten())   
            self.yy = theano.shared(numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).flatten())
            self.Y = theano.shared(YY)
            self.X = theano.shared(XX)

            
            self.v1of = __main__.__dict__.get('V1OF','Exp')
            self.lgnof = __main__.__dict__.get('LGNOF','Exp')
            
            self.K = T.dvector('K')
            
            self.x = self.K[0:self.num_lgn]
            self.y = self.K[self.num_lgn:2*self.num_lgn]
            self.sc = self.K[2*self.num_lgn:3*self.num_lgn]
            self.ss = self.K[3*self.num_lgn:4*self.num_lgn]
            
            idx = 4*self.num_lgn
            
            if not __main__.__dict__.get('BalancedLGN',True):
                    self.rc = self.K[idx:idx+self.num_lgn]
                    self.rs = self.K[idx+self.num_lgn:idx+2*self.num_lgn]
                    idx = idx  + 2*self.num_lgn
            
            if __main__.__dict__.get('LGNTreshold',False):
                self.ln = self.K[idx:idx + self.num_lgn]
                idx += self.num_lgn
            
            
            
            if __main__.__dict__.get('SecondLayer',False):
               self.a = T.reshape(self.K[idx:idx+int(num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))*self.num_lgn],(self.num_lgn,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))))
               idx +=  int(num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))*self.num_lgn                   
               self.a1 = T.reshape(self.K[idx:idx+num_neurons*int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))],(int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0)),self.num_neurons))
               idx = idx+num_neurons*int(num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))
            else:
               self.a = T.reshape(self.K[idx:idx+num_neurons*self.num_lgn],(self.num_lgn,self.num_neurons))
               idx +=  num_neurons*self.num_lgn

            
            self.n = self.K[idx:idx+self.num_neurons]
            
            if __main__.__dict__.get('SecondLayer',False):
               self.n1 = self.K[idx+self.num_neurons:idx+self.num_neurons+int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))]
            
            #if __main__.__dict__.get('BalancedLGN',True):
                #lgn_kernel = lambda i,x,y,sc,ss: T.dot(self.X,(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/sc[i]).T/ (2*sc[i]*numpy.pi)) - (T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/ss[i]).T/ (2*ss[i]*numpy.pi)))
                #lgn_output,updates = theano.scan(lgn_kernel , sequences= T.arange(self.num_lgn), non_sequences=[self.x,self.y,self.sc,self.ss])
            
            #else:
                #lgn_kernel = lambda i,x,y,sc,ss,rc,rs: T.dot(self.X,rc[i]*(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/sc[i]).T/ (2*sc[i]*numpy.pi)) - rs[i]*(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/ss[i]).T/ (2*ss[i]*numpy.pi)))
                #lgn_output,updates = theano.scan(lgn_kernel,sequences=T.arange(self.num_lgn),non_sequences=[self.x,self.y,self.sc,self.ss,self.rc,self.rs])
            
            lgn_kernel = lambda i,x,y,sc,ss,rc,rs: T.dot(self.X,rc[i]*(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/sc[i]).T/ (2*sc[i]*numpy.pi)))
            lgn_output,updates = theano.scan(lgn_kernel , sequences= T.arange(self.num_lgn), non_sequences=[self.x,self.y,self.sc,self.ss,self.rc,self.rs])
            
            lgn_output = lgn_output.T
            
            if __main__.__dict__.get('LGNTreshold',False):
               lgn_output = lgn_output - self.ln.T
 
               
            self.output = T.dot(self.construct_of(lgn_output,self.lgnof),self.a)
            if __main__.__dict__.get('SecondLayer',False):
               self.model_output = self.construct_of(self.output-self.n1,self.v1of)
               self.model_output = self.construct_of(T.dot(self.model_output , self.a1) - self.n,self.v1of)
            else:
               self.model_output = self.construct_of(self.output-self.n,self.v1of)          
            
            if __main__.__dict__.get('LL',True):
               ll = T.sum(self.model_output) - T.sum(self.Y * T.log(self.model_output+0.0000000000000000001))
               
               if __main__.__dict__.get('Sparse',False):
                  ll += __main__.__dict__.get('FLL1',1.0)*T.sum(abs(self.a)) + __main__.__dict__.get('FLL2',1.0)*T.sum(self.a**2) 
                  if __main__.__dict__.get('SecondLayer',False):
                        ll += __main__.__dict__.get('SLL1',1.0)*T.sum(abs(self.a1)) + __main__.__dict__.get('SLL2',1.0)**T.sum(self.a1**2)
               
            else:
               ll = T.sum(T.sqr(self.model_output - self.Y)) 

            self.loglikelyhood =  ll
        
        def func(self):
            return theano.function(inputs=[self.K], outputs=self.loglikelyhood,mode='FAST_RUN')
        
        def der(self):
            g_K = T.grad(self.loglikelyhood, self.K)
            return theano.function(inputs=[self.K], outputs=g_K,mode='FAST_RUN')
        
        def response(self,X,kernels):
            self.X.value = X
            
            resp = theano.function(inputs=[self.K], outputs=self.model_output,mode='FAST_RUN')
            return resp(kernels)        
        
        def construct_of(self,inn,of):
            if of == 'Linear':
               return inn
            if of == 'Exp':
               return T.exp(inn)
            elif of == 'Sigmoid':
               return 5.0 / (1.0 + T.exp(-inn))
            elif of == 'SoftSign':
               return inn / (1 + T.abs_(inn)) 
            elif of == 'Square':
               return T.sqr(inn)
            elif of == 'ExpExp':
               return T.exp(T.exp(inn))         
            elif of == 'ExpSquare':
               return T.exp(T.sqr(inn))
            elif of == 'LogisticLoss':
               return __main__.__dict__.get('LogLossCoef',1.0)*T.log(1+T.exp(__main__.__dict__.get('LogLossCoef',1.0)*inn))

        
        def returnRFs(self,K):
            x = K[0:self.num_lgn]
            y = K[self.num_lgn:2*self.num_lgn]
            sc = K[2*self.num_lgn:3*self.num_lgn]
            ss = K[3*self.num_lgn:4*self.num_lgn]
            idx = 4*self.num_lgn
            
            if not __main__.__dict__.get('BalancedLGN',True):
                    rc = K[idx:idx+self.num_lgn]
                    rs = K[idx+self.num_lgn:idx+2*self.num_lgn]
                    idx = idx  + 2*self.num_lgn
            
            if __main__.__dict__.get('LGNTreshold',False):
                ln = K[idx:idx + self.num_lgn]
                idx += self.num_lgn
                
            if __main__.__dict__.get('SecondLayer',False):
               a = numpy.reshape(K[idx:idx+int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))*self.num_lgn],(self.num_lgn,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))))
               idx +=  int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))*self.num_lgn              
               a1 = numpy.reshape(K[idx:idx+self.num_neurons*int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))],(int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0)),self.num_neurons))
               idx = idx+self.num_neurons*int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))
            else:
               a = numpy.reshape(K[idx:idx+self.num_neurons*self.num_lgn],(self.num_lgn,self.num_neurons))
               idx +=  self.num_neurons*self.num_lgn
        
            n = K[idx:idx+self.num_neurons]

            if __main__.__dict__.get('SecondLayer',False):
               n1 = K[idx+self.num_neurons:idx+self.num_neurons+int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))]

            
            
            xx = numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).T.flatten()       
            yy = numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).flatten()
                                    
            print 'X'                               
            print x
            print 'Y'
            print y
            print 'SS'
            print ss
            print 'SC'
            print sc
            print 'A'
            print a
            print 'N'
            print n
            
            if not __main__.__dict__.get('BalancedLGN',True):
                print 'RS'
                print rs
                print 'RC'
                print rc
            
            if __main__.__dict__.get('SecondLayer',False):
                print 'A1'
                print a1
            if __main__.__dict__.get('LGNTreshold',False):
               print 'LN'           
               print ln
            
            if __main__.__dict__.get('SecondLayer',False):
                num_neurons_first_layer = int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))  
            else:
                num_neurons_first_layer = self.num_neurons
            
            rfs = numpy.zeros((num_neurons_first_layer,self.kernel_size))       
            
            
            for j in xrange(num_neurons_first_layer):
                for i in xrange(0,self.num_lgn):
                    if  __main__.__dict__.get('BalancedLGN',True):                      
                        rfs[j,:] += a[i,j]*(numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/sc[i])/(2*sc[i]*numpy.pi) - numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/ss[i])/(2*ss[i]*numpy.pi)) 
                    else:
                        rfs[j,:] += a[i,j]*(rc[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/sc[i])/(2*sc[i]*numpy.pi) - rs[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/ss[i])/(2*ss[i]*numpy.pi))
                        
            
            #average_lgn = numpy.zeros((1,self.kernel_size*self.kernel_size))   
            average_lgn=0
            for i in xrange(0,1):#elf.num_lgn):
                    if  __main__.__dict__.get('BalancedLGN',True):                      
                        average_lgn += (numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/sc[i])/(2*sc[i]*numpy.pi) - numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/ss[i])/(2*ss[i]*numpy.pi)) 
                    else:
                        average_lgn += (rc[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/sc[i])/(2*sc[i]*numpy.pi) - rs[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/ss[i])/(2*ss[i]*numpy.pi))
            
            return rfs,a1,average_lgn,a
        
        def generateBounds(self):
              bounds = []
              for j in xrange(0,self.num_lgn):
                  bounds.append((6,(numpy.sqrt(self.kernel_size)-6)))
                  bounds.append((6,(numpy.sqrt(self.kernel_size)-6)))
              for j in xrange(0,self.num_lgn):  
                  bounds.append((1.0,25))
                  bounds.append((1.0,25))

              if not __main__.__dict__.get('BalancedLGN',True): 
                  for j in xrange(0,self.num_lgn):      
                          bounds.append((0.0,1.0))
                          bounds.append((0.0,1.0))

              if __main__.__dict__.get('LGNTreshold',False):
                for j in xrange(0,self.num_lgn):
                    bounds.append((0,20))
                  

              if __main__.__dict__.get('NegativeLgn',True):

                  minw = -__main__.__dict__.get('MaxW',5000)
              else:
                  minw = 0
              maxw = __main__.__dict__.get('MaxW',5000)
              print __main__.__dict__.get('MaxW',5000)
              
              if __main__.__dict__.get('SecondLayer',False):
                  for j in xrange(0,self.num_lgn):              
                          for k in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):
                                  bounds.append((minw,maxw))
                          
                  for j in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):                
                          for k in xrange(0,self.num_neurons):
                                  bounds.append((-__main__.__dict__.get('MaxWL2',4),__main__.__dict__.get('MaxWL2',4)))
              else:
                  for j in xrange(0,self.num_lgn):              
                          for k in xrange(0,self.num_neurons):
                                  bounds.append((minw,maxw))
                                  
                          
                                  
              for k in xrange(0,self.num_neurons):
                  bounds.append((0,20))
                  
              if __main__.__dict__.get('SecondLayer',False):
                  for k in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):
                          bounds.append((0,20))
              return bounds




class LSCSMNEW(object):
        def __init__(self,XX,YY,num_lgn,num_neurons,batch_size=100):
            (self.num_pres,self.kernel_size) = numpy.shape(XX)
            self.num_lgn = num_lgn
            self.num_neurons = num_neurons
            self.size = numpy.sqrt(self.kernel_size)
            self.hls = __main__.__dict__.get('HiddenLayerSize',1.0)
            self.divisive = __main__.__dict__.get('Divisive',False)
            self.batch_size=batch_size      

            #self.xx = theano.shared(numpy.asarray(numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).T.flatten(),dtype=theano.config.floatX))        
            #self.yy = theano.shared(numpy.asarray(numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).flatten(),dtype=theano.config.floatX))
            self.xx = theano.shared(numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).T.flatten())   
            self.yy = theano.shared(numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).flatten())
            
            #self.Y = theano.shared(numpy.asarray(YY,dtype=theano.config.floatX))
            #self.X = theano.shared(numpy.asarray(XX,dtype=theano.config.floatX))
            self.Y = theano.shared(YY)
            self.X = theano.shared(XX)

            
            self.v1of = __main__.__dict__.get('V1OF','Exp')
            self.lgnof = __main__.__dict__.get('LGNOF','Exp')
            
            #self.K = T.fvector('K')
            self.K = T.dvector('K')
            #self.index = T.lscalar('I')
            
            #srng = RandomStreams(seed=234)
            #self.index = srng.random_integers((1,1),high=self.num_pres-batch_size)[0]

            
            self.x = self.K[0:self.num_lgn]
            self.y = self.K[self.num_lgn:2*self.num_lgn]
            self.sc = self.K[2*self.num_lgn:3*self.num_lgn]
            self.ss = self.K[3*self.num_lgn:4*self.num_lgn]
            
            idx = 4*self.num_lgn
            
            if not __main__.__dict__.get('BalancedLGN',True):
                    self.rc = self.K[idx:idx+self.num_lgn]
                    self.rs = self.K[idx+self.num_lgn:idx+2*self.num_lgn]
                    idx = idx  + 2*self.num_lgn

            if __main__.__dict__.get('LGNTreshold',False):
                self.ln = self.K[idx:idx + self.num_lgn]
                idx += self.num_lgn
            
            
            
            if __main__.__dict__.get('SecondLayer',False):
               self.a = T.reshape(self.K[idx:idx+int(num_neurons*self.hls)*self.num_lgn],(self.num_lgn,int(self.num_neurons*self.hls)))
               idx +=  int(num_neurons*self.hls)*self.num_lgn               
               self.a1 = T.reshape(self.K[idx:idx+num_neurons*int(self.num_neurons*self.hls)],(int(self.num_neurons*self.hls),self.num_neurons))
               idx = idx+num_neurons*int(num_neurons*self.hls)
               if self.divisive:
                       self.d = T.reshape(self.K[idx:idx+int(num_neurons*self.hls)*self.num_lgn],(self.num_lgn,int(self.num_neurons*self.hls)))
                       idx +=  int(num_neurons*self.hls)*self.num_lgn               
                       self.d1 = T.reshape(self.K[idx:idx+num_neurons*int(self.num_neurons*self.hls)],(int(self.num_neurons*self.hls),self.num_neurons))
                       idx = idx+num_neurons*int(num_neurons*self.hls)
            else:
               self.a = T.reshape(self.K[idx:idx+num_neurons*self.num_lgn],(self.num_lgn,self.num_neurons))
               idx +=  num_neurons*self.num_lgn
               if self.divisive:               
                       self.d = T.reshape(self.K[idx:idx+num_neurons*self.num_lgn],(self.num_lgn,self.num_neurons))
                       idx +=  num_neurons*self.num_lgn

            
            self.n = self.K[idx:idx+self.num_neurons]
            idx +=  num_neurons
            
            if self.divisive:
                    self.nd = self.K[idx:idx+self.num_neurons]
                    idx +=  num_neurons
            
            if __main__.__dict__.get('SecondLayer',False):
               self.n1 = self.K[idx:idx+int(self.num_neurons*self.hls)]
               idx +=  int(self.num_neurons*self.hls)
               if self.divisive:
                       self.nd1 = self.K[idx:idx+int(self.num_neurons*self.hls)]
                       idx +=  int(self.num_neurons*self.hls)
            
            if __main__.__dict__.get('BalancedLGN',True):
                lgn_kernel = lambda i,x,y,sc,ss: T.dot(self.X,(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/sc[i]).T/ (2*sc[i]*numpy.pi)) - (T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/ss[i]).T/ (2*ss[i]*numpy.pi)))
                lgn_output,updates = theano.scan(lgn_kernel , sequences= T.arange(self.num_lgn), non_sequences=[self.x,self.y,self.sc,self.ss])
            
            else:
                lgn_kernel = lambda i,x,y,sc,ss,rc,rs: T.dot(self.X,rc[i]*(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/sc[i]).T/ (2*sc[i]*numpy.pi)) - rs[i]*(T.exp(-((self.xx - x[i])**2 + (self.yy - y[i])**2)/2/ss[i]).T/ (2*ss[i]*numpy.pi)))
                lgn_output,updates = theano.scan(lgn_kernel,sequences=T.arange(self.num_lgn),non_sequences=[self.x,self.y,self.sc,self.ss,self.rc,self.rs])
            
            #lgn_output = theano.printing.Print(message='lgn output:')(lgn_output)
            
            lgn_output = lgn_output.T
            
            if __main__.__dict__.get('LGNTreshold',False):
               lgn_output = lgn_output - self.ln.T
            lgn_output = self.construct_of(lgn_output,self.lgnof)
               
            self.output = T.dot(lgn_output,self.a)
            if self.divisive:
                self.d_output = T.dot(lgn_output,self.d)
            #self.output = theano.printing.Print(message='Output1:')(self.output)
            
            #self.n = theano.printing.Print(message='N:')(self.n)
            
            #self.output = theano.printing.Print(message='Output2:')(self.output)
            
            if __main__.__dict__.get('SecondLayer',False):
               if self.divisive:
                        self.model_output = self.construct_of(self.output-self.n1,self.v1of)
                        self.d_model_output = self.construct_of(self.d_output-self.nd1,self.v1of)
                        self.model_output = self.construct_of((T.dot(self.model_output , self.a1) - self.n)/(1+self.construct_of(T.dot(self.d_model_output , self.d1) - self.nd,self.v1of)),self.v1of)
               else:
                        self.model_output = self.construct_of(self.output-self.n1,self.v1of)
                        self.model_output = self.construct_of(T.dot(self.model_output , self.a1) - self.n,self.v1of)
            else:
               if self.divisive:
                  self.model_output = self.construct_of((self.output-self.n)/(1.0+T.dot(lgn_output,self.d)-self.nd),self.v1of)
               else:
                  self.model_output = self.construct_of(self.output-self.n,self.v1of)
            
            
            if __main__.__dict__.get('LL',True):
               #self.model_output = theano.printing.Print(message='model output:')(self.model_output)
               ll = T.sum(self.model_output) - T.sum(self.Y * T.log(self.model_output+0.0000000000000000001))
               
               if __main__.__dict__.get('Sparse',False):
                  ll += __main__.__dict__.get('FLL1',1.0)*T.sum(abs(self.a)) + __main__.__dict__.get('FLL2',1.0)*T.sum(self.a**2) 
                  if __main__.__dict__.get('SecondLayer',False):
                        ll += __main__.__dict__.get('SLL1',1.0)*T.sum(abs(self.a1)) + __main__.__dict__.get('SLL2',1.0)**T.sum(self.a1**2)
               
            else:
               ll = T.sum(T.sqr(self.model_output - self.Y)) 

            #ll = theano.printing.Print(message='LL:')(ll)
            self.loglikelyhood =  ll
        
        def func(self):
            return theano.function(inputs=[self.K], outputs=self.loglikelyhood,mode='FAST_RUN')
        
        def der(self):
            g_K = T.grad(self.loglikelyhood, self.K)
            return theano.function(inputs=[self.K], outputs=g_K,mode='FAST_RUN')
        
        def response(self,X,kernels):
            self.X.value = X
            
            resp = theano.function(inputs=[self.K], outputs=self.model_output,mode='FAST_RUN')
            return resp(kernels)        
        
        def construct_of(self,inn,of):
            if of == 'Linear':
               return inn
            if of == 'Exp':
               return T.exp(inn)
            elif of == 'Sigmoid':
               return 5.0 / (1.0 + T.exp(-inn))
            elif of == 'SoftSign':
               return inn / (1 + T.abs_(inn)) 
            elif of == 'Square':
               return T.sqr(inn)
            elif of == 'ExpExp':
               return T.exp(T.exp(inn))         
            elif of == 'ExpSquare':
               return T.exp(T.sqr(inn))
            elif of == 'LogisticLoss':
               return __main__.__dict__.get('LogLossCoef',1.0)*T.log(1+T.exp(__main__.__dict__.get('LogLossCoef',1.0)*inn))

        
        def returnRFs(self,K):
            x = K[0:self.num_lgn]
            y = K[self.num_lgn:2*self.num_lgn]
            sc = K[2*self.num_lgn:3*self.num_lgn]
            ss = K[3*self.num_lgn:4*self.num_lgn]
            idx = 4*self.num_lgn
            
            if not __main__.__dict__.get('BalancedLGN',True):
                    rc = K[idx:idx+self.num_lgn]
                    rs = K[idx+self.num_lgn:idx+2*self.num_lgn]
                    idx = idx  + 2*self.num_lgn
            
            if __main__.__dict__.get('LGNTreshold',False):
                ln = K[idx:idx + self.num_lgn]
                idx += self.num_lgn
                
            if __main__.__dict__.get('SecondLayer',False):
               a = numpy.reshape(K[idx:idx+int(self.num_neurons*self.hls)*self.num_lgn],(self.num_lgn,int(self.num_neurons*self.hls)))
               idx +=  int(self.num_neurons*self.hls)*self.num_lgn                  
               a1 = numpy.reshape(K[idx:idx+self.num_neurons*int(self.num_neurons*self.hls)],(int(self.num_neurons*self.hls),self.num_neurons))
               idx = idx+self.num_neurons*int(self.num_neurons*self.hls)
               if self.divisive:
                       d = numpy.reshape(K[idx:idx+int(self.num_neurons*self.hls)*self.num_lgn],(self.num_lgn,int(self.num_neurons*self.hls)))
                       idx +=  int(self.num_neurons*self.hls)*self.num_lgn                  
                       d1 = numpy.reshape(K[idx:idx+self.num_neurons*int(self.num_neurons*self.hls)],(int(self.num_neurons*self.hls),self.num_neurons))
                       idx = idx+self.num_neurons*int(self.num_neurons*self.hls)

            else:
               a = numpy.reshape(K[idx:idx+self.num_neurons*self.num_lgn],(self.num_lgn,self.num_neurons))
               idx +=  self.num_neurons*self.num_lgn
               if self.divisive:               
                       d = numpy.reshape(K[idx:idx+self.num_neurons*self.num_lgn],(self.num_lgn,self.num_neurons))
                       idx +=  self.num_neurons*self.num_lgn

        
            n = K[idx:idx+self.num_neurons]

            if __main__.__dict__.get('SecondLayer',False):
               n1 = K[idx+self.num_neurons:idx+self.num_neurons+int(self.num_neurons*self.hls)]

            xx = numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).T.flatten()       
            yy = numpy.repeat([numpy.arange(0,self.size,1)],self.size,axis=0).flatten()
                                    
            print 'X'                               
            print x
            print 'Y'
            print y
            print 'SS'
            print ss
            print 'SC'
            print sc
            print 'A'
            print a
            print 'N'
            print n
            
            if not __main__.__dict__.get('BalancedLGN',True):
                print 'RS'
                print rs
                print 'RC'
                print rc
            
            if __main__.__dict__.get('SecondLayer',False):
                print 'A1'
                print a1
                print self.hls
            
            if __main__.__dict__.get('LGNTreshold',False):
               print 'LN'           
               print ln
            
            if __main__.__dict__.get('SecondLayer',False):
                num_neurons_first_layer = int(self.num_neurons*self.hls)  
            else:
                num_neurons_first_layer = self.num_neurons
            
            rfs = numpy.zeros((num_neurons_first_layer,self.kernel_size))               
            
            for j in xrange(num_neurons_first_layer):
                for i in xrange(0,self.num_lgn):
                    if  __main__.__dict__.get('BalancedLGN',True):                      
                        rfs[j,:] += a[i,j]*(numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/sc[i])/(2*sc[i]*numpy.pi) - numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/ss[i])/(2*ss[i]*numpy.pi)) 
                    else:
                        rfs[j,:] += a[i,j]*(rc[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/sc[i])/(2*sc[i]*numpy.pi) - rs[i]*numpy.exp(-((xx - x[i])**2 + (yy - y[i])**2)/2/ss[i])/(2*ss[i]*numpy.pi))
                        
            return rfs,a1,a

        def generateBounds(self):
              bounds = []

              for j in xrange(0,self.num_lgn):
                  bounds.append((6,(numpy.sqrt(self.kernel_size)-6)))
                  bounds.append((6,(numpy.sqrt(self.kernel_size)-6)))
                  
              for j in xrange(0,self.num_lgn):  
                  bounds.append((1.0,25))
                  bounds.append((1.0,25))
              if not __main__.__dict__.get('BalancedLGN',True): 
                  for j in xrange(0,self.num_lgn):      
                          bounds.append((0.0,1.0))
                          bounds.append((0.0,1.0))
                  
                  
              if __main__.__dict__.get('LGNTreshold',False):
                for j in xrange(0,self.num_lgn):
                    bounds.append((0,20))
                  

              if __main__.__dict__.get('NegativeLgn',True):
                  minw = -__main__.__dict__.get('MaxW',5000)
              else:
                  minw = 0
              maxw = __main__.__dict__.get('MaxW',5000)
              print __main__.__dict__.get('MaxW',5000)
              
              if __main__.__dict__.get('Divisive',False):
                  d=2
              else:
                  d=1

              
              if __main__.__dict__.get('SecondLayer',False):
                  for j in xrange(0,self.num_lgn):              
                          for k in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):
                                  bounds.append((minw,maxw))
                          
                  for j in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):                
                          for k in xrange(0,self.num_neurons):
                                  bounds.append((-__main__.__dict__.get('MaxWL2',4),__main__.__dict__.get('MaxWL2',4)))
                  if __main__.__dict__.get('Divisive',False):
                          for j in xrange(0,self.num_lgn):              
                                  for k in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):
                                          bounds.append((minw,maxw))
                                  
                          for j in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):                
                                  for k in xrange(0,self.num_neurons):
                                          bounds.append((0,2))
                                  
              else:
                  for i in xrange(0,d):    
                          for j in xrange(0,self.num_lgn):              
                                  for k in xrange(0,self.num_neurons):
                                          bounds.append((minw,maxw))
                                  
                          
                                  
              for k in xrange(0,self.num_neurons):
                  for i in xrange(0,d):
                          bounds.append((0,20))
                  
              if __main__.__dict__.get('SecondLayer',False):
                  for i in xrange(0,d):
                          for k in xrange(0,int(self.num_neurons*__main__.__dict__.get('HiddenLayerSize',1.0))):
                                  bounds.append((0,20))

              return bounds


def fitLSCSM(training_inputs,training_set,lgn_num,num_neurons,validation_inputs,validation_set):
    num_pres,num_neurons = numpy.shape(training_set) 
    
    if __main__.__dict__.get('EarlyStopping',False):
       frac=0.1
    else:
       frac=0.01
    
    early_stopping_set = training_set[-num_pres*frac:,:]
    early_stopping_inputs = training_inputs[-num_pres*frac:,:]
    training_set = training_set[:-num_pres*frac,:]
    training_inputs = training_inputs[:-num_pres*frac,:]
    
    if __main__.__dict__.get('LSCSMOLD',True):
        lscsm = LSCSM(training_inputs,training_set,lgn_num,num_neurons)
    else:
        lscsm = LSCSMNEW(training_inputs,training_set,lgn_num,num_neurons)
    func = lscsm.func() 
    der = lscsm.der()
    bounds = lscsm.generateBounds()
    
    rand =numbergen.UniformRandom(seed=__main__.__dict__.get('Seed',513))
    
    Ks = []
    terr=[]
    eserr=[]
    verr=[]
    
    pylab.figure()
    
    pylab.show()
    pylab.hold(True)

    [Ks.append(a[0]+rand()*(a[1]-a[0])/2.0)  for a in bounds]
    
    best_Ks = list(Ks)
    best_eserr = 100000000000000000000000000000000000
    time_since_best=0
    
    for i in xrange(0,__main__.__dict__.get('NumEpochs',100)):
        print i
        
        (Ks,success,c)=fmin_tnc(func,Ks,fprime=der,bounds=bounds,maxfun = __main__.__dict__.get('EpochSize',1000),messages=0)
        
        terr.append(func(numpy.array(Ks))/numpy.shape(training_set)[0])
        lscsm.X.value = early_stopping_inputs
        lscsm.Y.value = early_stopping_set
        eserr.append(func(numpy.array(Ks))/ numpy.shape(early_stopping_set)[0])
        lscsm.X.value = validation_inputs
        lscsm.Y.value = validation_set
        verr.append(func(numpy.array(Ks))/numpy.shape(validation_set)[0])
        lscsm.X.value = training_inputs
        lscsm.Y.value = training_set
        print terr[-1],verr[-1],eserr[-1]
        pylab.plot(verr,'r')
        pylab.plot(terr,'b')
        pylab.plot(eserr,'g')   
        pylab.draw()
        
        if best_eserr > eserr[-1]:    
           best_eserr = eserr[-1]
           best_Ks = list(Ks)
           time_since_best = 0
        else:
           time_since_best+=1
        
        if __main__.__dict__.get('EarlyStopping',False):
           if time_since_best > 30:
              break

    if __main__.__dict__.get('EarlyStopping',False):
       Ks = best_Ks

    print 'Final training error: ', func(numpy.array(Ks))/ numpy.shape(training_set)[0] 
    lscsm.X.value = early_stopping_inputs
    lscsm.Y.value = early_stopping_set
    print 'Final testing error: ', func(numpy.array(Ks))/ numpy.shape(early_stopping_set)[0] 

    pylab.savefig(normalize_path('Error_evolution.png'))
    rfs = lscsm.returnRFs(Ks)
    kernel_size =  numpy.shape(training_inputs)[1]
    laplace = laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))
    rpi = numpy.linalg.pinv(training_inputs.T*training_inputs + __main__.__dict__.get('RPILaplaceBias',0.0001)*laplace) * training_inputs.T * training_set
    return [Ks,rpi,lscsm,rfs]   
  

def runLSCSM():
    import noiseEstimation
    
    import param
        
    contrib.modelfit.save_fig_directory=param.normalize_path.prefix
    
    print contrib.modelfit.save_fig_directory

    res = contrib.dd.DB(None)
    (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.JanA.dataimport.sortOutLoading(res)

    raw_validation_set = db_node.data["raw_validation_set"]
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,kernel_size = numpy.shape(training_inputs)
    size = numpy.sqrt(kernel_size)

    raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)
    
    params={}
    params["LSCSM"]=True
    db_node = db_node.get_child(params)
    
    params={}
    params["LaplacaBias"] = __main__.__dict__.get('LaplaceBias',0.0004)
    params["LGN_NUM"] = __main__.__dict__.get('LgnNum',6)
    params["num_neurons"] = __main__.__dict__.get('NumNeurons',103)
    params["sequential"] = __main__.__dict__.get('Sequential',False)
    params["ll"] =  __main__.__dict__.get('LL',True)
    params["V1OF"] = __main__.__dict__.get('V1OF','Exp')
    params["LGNOF"] = __main__.__dict__.get('LGNOF','Exp')
    params["BalancedLGN"] = __main__.__dict__.get('BalancedLGN',True)
    params["LGNTreshold"] =  __main__.__dict__.get('LGNTreshold',False)
    params["SecondLayer"] = __main__.__dict__.get('SecondLayer',False)
    params["HiddenLayerSize"] = __main__.__dict__.get('HiddenLayerSize',1.0)
    params["LogLossCoef"] = __main__.__dict__.get('LogLossCoef',1.0)
    params["NegativeLgn"] = __main__.__dict__.get('NegativeLgn',True)
    params["MaxW"] = __main__.__dict__.get('MaxW',5000)
    params["GenerationSize"] = __main__.__dict__.get('GenerationSize',100)
    params["PopulationSize"] = __main__.__dict__.get('PopulationSize',100)
    params["MutationRate"] = __main__.__dict__.get('MutationRate',0.05)
    params["CrossoverRate"] = __main__.__dict__.get('CrossoverRate',0.9)
    params["FromWhichNeuron"] = __main__.__dict__.get('FromWhichNeuron',0)
    
    db_node1 = db_node
    db_node = db_node.get_child(params)
    
    num_neurons=params["num_neurons"]

    training_set = training_set[:,params["FromWhichNeuron"]:params["FromWhichNeuron"]+num_neurons]
    validation_set = validation_set[:,params["FromWhichNeuron"]:params["FromWhichNeuron"]+num_neurons]
    for i in xrange(0,len(raw_validation_set)):
        raw_validation_set[i] = raw_validation_set[i][:,params["FromWhichNeuron"]:params["FromWhichNeuron"]+num_neurons]
        
    
    raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)
    
    [K,rpi,glm,rfs]=  fitLSCSM(numpy.mat(training_inputs),numpy.mat(training_set),params["LGN_NUM"],num_neurons,numpy.mat(validation_inputs),numpy.mat(validation_set))
    
    rpi_pred_act = training_inputs * rpi
    rpi_pred_val_act = validation_inputs * rpi
    
    if __main__.__dict__.get('Sequential',False):
        glm_pred_act = numpy.hstack([glm[i].response(training_inputs,K[i]) for i in xrange(0,num_neurons)])
        glm_pred_val_act = numpy.hstack([glm[i].response(validation_inputs,K[i]) for i in xrange(0,num_neurons)])
    else:
        glm_pred_act = glm.response(training_inputs,K)
        glm_pred_val_act = glm.response(validation_inputs,K)

    db_node.add_data("Kernels",K,force=True)
    db_node.add_data("LSCSM",glm,force=True)
    
    contrib.dd.saveResults(res,normalize_path(__main__.__dict__.get('save_name','BestLSCSM.dat')))


    runLSCSMAnalysis(rpi_pred_act,rpi_pred_val_act,glm_pred_act,glm_pred_val_act,training_set,validation_set,num_neurons,raw_validation_data_set)

    pylab.figure()
    print numpy.shape(rfs)
    print num_neurons
    print kernel_size
    m = numpy.max(numpy.abs(rfs))
    for i in xrange(0,numpy.shape(rfs)[0]):
        pylab.subplot(11,11,i+1)    
        pylab.imshow(numpy.reshape(rfs[i,0:kernel_size],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu_r,interpolation='nearest')
    pylab.savefig(normalize_path('GLM_rfs.png'))
    
    pylab.figure()
    m = numpy.max(numpy.abs(rpi))
    for i in xrange(0,num_neurons):
        pylab.subplot(11,11,i+1)
        pylab.imshow(numpy.reshape(rpi[:,i],(size,size)),vmin=-m,vmax=m,cmap=pylab.cm.RdBu_r,interpolation='nearest')
    pylab.savefig(normalize_path('RPI_rfs.png'))


    signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), glm_pred_act, glm_pred_val_act)
    to_delete = numpy.array(numpy.nonzero((numpy.array(normalized_noise_power) > 85) * 1.0))[0]
    print 'After deleting ' , len(to_delete) , 'most noisy neurons (<15% signal to noise ratio)\n\n\n'
        
    if len(to_delete) != num_neurons:
    
        training_set = numpy.delete(training_set, to_delete, axis = 1)
        validation_set = numpy.delete(validation_set, to_delete, axis = 1)
        glm_pred_act = numpy.delete(glm_pred_act, to_delete, axis = 1)
        glm_pred_val_act = numpy.delete(glm_pred_val_act, to_delete, axis = 1)
        rpi_pred_act = numpy.delete(rpi_pred_act, to_delete, axis = 1)
        rpi_pred_val_act = numpy.delete(rpi_pred_val_act, to_delete, axis = 1)
        
        for i in xrange(0,len(raw_validation_set)):
                raw_validation_set[i] = numpy.delete(raw_validation_set[i], to_delete, axis = 1)

        raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)       
        runLSCSMAnalysis(rpi_pred_act,rpi_pred_val_act,glm_pred_act,glm_pred_val_act,training_set,validation_set,num_neurons-len(to_delete),raw_validation_data_set)
        
    

def addRPI():
  
    res = contrib.dd.DB(None)
    
    #prefix = './LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/'
    prefix = './'
    
    #animals = ['2009_11_04_region3.dat','2009_11_04_region5.dat','2010_04_22.dat']
    #animal_names = ['2009_11_04_region3','2009_11_04_region5','2010_04_22']
    
    animals = ['20091110_region4.dat']
    animal_names = ['20091110']
    
    i=0
    for a in animals:
      __main__.__dict__['dataset']=animal_names[i]
      (sizex,sizey,training_inputs,training_set,validation_inputs,validation_set,ff,db_node) = contrib.JanA.dataimport.sortOutLoading(res)
      raw_validation_set = db_node.data["raw_validation_set"]
      
      res = contrib.dd.loadResults(prefix+a)
      dataset_node = res.children[0].children[0]
      dataset_node.add_data("raw_validation_set",raw_validation_set,force=True)

      #kernel_size =  numpy.shape(numpy.mat(training_inputs))[1]
      #laplace = laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))
      #rpi = numpy.linalg.pinv(numpy.mat(training_inputs).T*numpy.mat(training_inputs) + __main__.__dict__.get('RPILaplaceBias',0.0001)*laplace) * numpy.mat(training_inputs).T * numpy.mat(training_set)
      
      #params={}
      #params["STA"]=True
      #dataset_node = dataset_node.get_child(params)
      
      #params={}
      #params["RPILaplaceBias"]=__main__.__dict__.get('RPILaplaceBias',0.0001)
      #dataset_node = dataset_node.get_child(params)
      
      #dataset_node.add_data("RPI",rpi,force=True)
      
      contrib.dd.saveResults(res,normalize_path(prefix+a))
      
      i=i+1
  
def loadLSCSMandAnalyse(): 
    
    res = contrib.dd.DB(None)
    gallant_tr_names = ['region1_training_resp.txt','region2_training_resp.txt','region3_training_resp.txt']
    gallant_vr_names = ['region1_validation_resp.txt','region2_validation_resp.txt','region3_validation_resp.txt']
    
    #prefix = './LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping/'
    #prefix = './LSCSM/LSCSM/NumLgn=10_HLS=0.2_NoEarlyStopping/'
    prefix = './LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/'
    #prefix = './LSCSM/LSCSM/NumLgn=12_HLS=0.2_NoEarlyStopping_DOG/'
    #prefix = './LSCSM/LSCSM/'
    
    animals = ['2009_11_04_region3.dat','2009_11_04_region5.dat','2010_04_22.dat']
    animal_names = ['2009_11_04_region3','2009_11_04_region5','2010_04_22']
    region_sizes = [103,55,102]
    
    pred_act = []
    pred_val_act = []
    ts = []
    rvs = []
    vs = []
    ti = []
    vi = []
    
    
    
    gallant_pred_val_act = []
    gallant_pred_act = []
    for i in xrange(0,len(animals)):
        gallant_pred_val_act.append(numpy.loadtxt('./LSCSM/Gallant/'+gallant_vr_names[i]))
        gallant_pred_act.append(numpy.loadtxt('./LSCSM/Gallant/'+gallant_tr_names[i]))
    
    
    
    i=0
    for a in animals:
      res = contrib.dd.loadResults(prefix+a)
      
      dataset_node = res.children[0].children[0]
      
      training_set = dataset_node.data["training_set"]

      validation_set = dataset_node.data["validation_set"]
      raw_validation_set = dataset_node.data["raw_validation_set"]
      training_inputs= dataset_node.data["training_inputs"]
      validation_inputs= dataset_node.data["validation_inputs"]
      
      ts.append(numpy.mat(training_set))
      vs.append(numpy.mat(validation_set))
      rvs.append(raw_validation_set)
      ti.append(numpy.mat(training_inputs))
      vi.append(numpy.mat(validation_inputs))
      
      K = res.children[0].children[0].children[0].children[0].data["Kernels"]
      lscsm = res.children[0].children[0].children[0].children[0].data["LSCSM"]
      #rfs  = lscsm_new.returnRFs(K)
          
      pred_act.append(lscsm.response(training_inputs,K))
      pred_val_act.append(lscsm.response(validation_inputs,K))
      i=i+1
    
    
    # load rpi
    rpi = []
    for i in xrange(0,len(animals)):
        rpi.append(numpy.loadtxt(animal_names[i]+'STA.txt'))
    
    
    
     
    corrs = [] 
    gallant_corrs = []
    for i in xrange(0,len(animals)):
      #ofs = run_nonlinearity_detection(numpy.mat(ts[i]),numpy.mat(gallant_pred_act[i]),num_bins=10,display=False)
      #gallant_pred_act[i] = apply_output_function(numpy.mat(gallant_pred_act[i]),ofs)
      #gallant_pred_val_act[i] = apply_output_function(numpy.mat(gallant_pred_val_act[i]),ofs)

      print 'Correlations for' , animals[i]
      train_c,val_c = printCorrelationAnalysis(ts[i],vs[i],pred_act[i],pred_val_act[i])
      corrs.append(numpy.array(val_c))
      
      train_c,val_c = printCorrelationAnalysis(ts[i],vs[i],gallant_pred_act[i],gallant_pred_val_act[i])
      print val_c
      
      gallant_corrs.append(numpy.array(val_c))

    #check out STA
    corrs_rpi = []
    rpi_pred_act = []
    rpi_pred_val_act = []
    for i in xrange(0,len(animals)):
      rpa = numpy.mat(ti[i] * rpi[i])
      rpva = numpy.mat(vi[i] * rpi[i])
      ofs = run_nonlinearity_detection(numpy.mat(ts[i]),numpy.mat(rpa),num_bins=20,display=False)
      rpi_pred_act_t = apply_output_function(numpy.mat(rpa),ofs)
      rpi_pred_val_act_t = apply_output_function(numpy.mat(rpva),ofs)
      
      rpi_pred_act.append(rpi_pred_act_t)
      rpi_pred_val_act.append(rpi_pred_val_act_t)

      train_c,val_c = printCorrelationAnalysis(ts[i],vs[i],rpi_pred_act[-1],rpi_pred_val_act[-1])
      corrs_rpi.append(numpy.array(val_c))

    # generate signal/noise data
    snr=[]
    for i in xrange(0,len(animals)):
       raw_validation_data_set=numpy.rollaxis(numpy.array(rvs[i]),2)
       
       print numpy.shape(numpy.array(ts[i]))
       print numpy.shape(numpy.array(vs[i]))
       print numpy.shape(pred_act[i])
       print numpy.shape(pred_val_act[i])
       
       signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(ts[i]), numpy.array(vs[i]), pred_act[i], pred_val_act[i])
       snr.append(normalized_noise_power)
    
    best = numpy.argmax(corrs[0])
    median = numpy.argmin(abs(corrs[0]-numpy.median(corrs[0])))
    
    f = pylab.figure(dpi=100,facecolor='w',figsize=(14,12))
    f.text(0.5,0.96,'Best neuron. R='+("%.2f" % (corrs[0][best])),horizontalalignment='center',fontsize=16)
    f.text(0.5,0.685,'Median neuron. R='+("%.2f" % (corrs[0][median])),horizontalalignment='center',fontsize=16)

    gs = GridSpec(7,6)
    gs.update(wspace=1.0,hspace=2.0,left=0.05,right=0.95,bottom=0.05,top=0.95)

    pylab.subplot(gs[:2,:4])
    #pylab.title('Best neuron. R='+str(corrs[0][best]))
    pylab.plot(vs[0][:,best],'k')
    pylab.plot(vs[0][:,best],'ko',label='experiment')
    pylab.plot(pred_val_act[0][:,best],'k--')
    pylab.plot(pred_val_act[0][:,best],'wo',label='model')
    pylab.ylabel('Response',fontsize=14)
    pylab.legend(loc='upper left')
    
    pylab.subplot(gs[:2,4:])
    pylab.plot(vs[0][:,best],pred_val_act[0][:,best],'wo')
    pylab.xlabel("Measured response",fontsize=14)
    pylab.ylabel('Predicted response',fontsize=14)
    

    pylab.subplot(gs[2:4,:4])
    #pylab.title('Median neuron. R='+str(corrs[0][median]))
    pylab.plot(vs[0][:,median],'k',label='experiment')
    pylab.plot(vs[0][:,median],'ko',label='experiment')
    pylab.plot(pred_val_act[0][:,median],'k--',label='model')
    pylab.plot(pred_val_act[0][:,median],'wo',label='model')
    pylab.ylabel('Response',fontsize=14)
    pylab.xlabel("Image #",fontsize=14)

    pylab.subplot(gs[2:4,4:])
    pylab.plot(vs[0][:,median],pred_val_act[0][:,median],'wo')
    pylab.xlabel("Measured response",fontsize=14)
    pylab.ylabel('Predicted response',fontsize=14)
    

    pylab.subplot(gs[4:,:3])
    bins = numpy.arange(0,1.0,0.1)
    n, bins, patches = pylab.hist(corrs, bins,histtype='bar',label = ['Region1','Region2','Region3'])
    pylab.legend(loc='upper left')
    pylab.xlabel('Correlation coefficient',fontsize=14)
    pylab.ylabel('# neurons',fontsize=14)
    pylab.ylim(0,27)

    ax = pylab.subplot(gs[4:,3:])
    pylab.plot(1/(1/(1-numpy.array(snr[0])/100)-1),corrs[0],'ro',label='region1')
    pylab.plot(1/(1/(1-numpy.array(snr[1])/100)-1),corrs[1],'go',label='region2')
    pylab.plot(1/(1/(1-numpy.array(snr[2])/100)-1),corrs[2],'bo',label='region3')
    #pylab.legend()
    pylab.xlabel('NNP',fontsize=14)
    pylab.ylabel('R',fontsize=14)
    pylab.xlim(-0.05,3.0)  
    pylab.savefig('/home/jan/Doc/Papers/LSCSMPaper/fig/lscsm_predictions.png')

    K = res.children[0].children[0].children[0].children[0].data["Kernels"]
    f = pylab.figure(dpi=100,facecolor='w',figsize=(14,12))
    gs = GridSpec(2,2)
    gs.update(wspace=0.2,hspace=0.2,left=0.1,right=0.95,bottom=0.1,top=0.95)

    from numpy import mean
    #raw correlations
    ax = pylab.subplot(gs[0,0])
    width = 0.25
    
    remaining_neurons = (len(corrs_rpi[0])+len(corrs_rpi[1])+len(corrs_rpi[2]))
    means = [numpy.sum([numpy.sum(z) for z in corrs_rpi])/remaining_neurons,numpy.sum([numpy.sum(z) for z in gallant_corrs])/remaining_neurons,numpy.sum([numpy.sum(z) for z in corrs])/remaining_neurons,(0.355+0.322+0.22)/3]
    region3 = [mean(corrs_rpi[0]),mean(gallant_corrs[0]),mean(corrs[0]),0.355]
    region5 = [mean(corrs_rpi[1]),mean(gallant_corrs[1]),mean(corrs[1]),0.322]
    region2010 = [mean(corrs_rpi[2]),mean(gallant_corrs[2]),mean(corrs[2]),0.22]
    
    print "CC Means:" , means
    print "CC Medians:", numpy.median(corrs[0]),numpy.median(corrs[1]),numpy.median(corrs[2])
    import scipy
    import scipy.stats
    print "SNR to R correlation:", scipy.stats.pearsonr(snr[0],corrs[0])[0] , scipy.stats.pearsonr(snr[1],corrs[1])[0], scipy.stats.pearsonr(snr[2],corrs[2])[0]
    
    loc = numpy.array([1-width,1,1+width, 1+2*width] )
    b1= pylab.bar(loc-(width-0.05)/2, means, width-0.05, color='gray')
    pylab.plot(loc,region3,'o',color='r')
    pylab.plot(loc,region5,'o',color='g')
    pylab.plot(loc,region2010,'o',color='b')
    p1=pylab.plot(loc,region3,'-',color='r')
    p2=pylab.plot(loc,region5,'-',color='g')
    p3=pylab.plot(loc,region2010,'-',color='b')
    pylab.ylim(-0.1,0.6)
    pylab.xlim(1-width-width,1+2*width+width)
    ax.legend( (p1[0], p2[0],p3[0]), ('Region 1','Region 2','Region 3'),loc='upper left' )
    pylab.ylabel('Correlation coefficient',fontsize=14)
    ticks=loc
    ax.set_xticks(ticks)
    ax.set_xticklabels(('STA','BWT','LSCSM','LSCSM(SN)'),fontsize=14)
    
    #correlations of good neurons
    for i in xrange(0,len(animals)):
        #to_delete = numpy.array(numpy.nonzero((numpy.array(1/(1/(1-numpy.array(snr[i])/100)-1)) < 0.4) * 1.0))[0]
        to_delete = numpy.array(numpy.nonzero((numpy.array(snr[i]) > 70) * 1.0))[0]
        print 'After deleting ' , len(to_delete) , 'most noisy neurons (<30% signal to noise ratio)\n\n\n'
        
        corrs[i] =  numpy.delete(corrs[i], to_delete)
        corrs_rpi[i] =  numpy.delete(corrs_rpi[i], to_delete)
        gallant_corrs[i] =  numpy.delete(gallant_corrs[i], to_delete)
        
        ts[i] = numpy.delete(ts[i], to_delete, axis = 1)
        vs[i] = numpy.delete(vs[i], to_delete, axis = 1)
        pred_act[i] = numpy.delete(pred_act[i], to_delete, axis = 1)
        pred_val_act[i] = numpy.delete(pred_val_act[i], to_delete, axis = 1)
        rpi_pred_act[i] = numpy.delete(rpi_pred_act[i], to_delete, axis = 1)
        rpi_pred_val_act[i] = numpy.delete(rpi_pred_val_act[i], to_delete, axis = 1)
        gallant_pred_val_act[i] = numpy.delete(gallant_pred_val_act[i], to_delete, axis = 1)
        for j in xrange(0,len(rvs[i])):
                rvs[i][j] = numpy.delete(rvs[i][j], to_delete, axis = 1)


    remaining_neurons = (len(corrs_rpi[0])+len(corrs_rpi[1])+len(corrs_rpi[2]))
    means = [numpy.sum([numpy.sum(z) for z in corrs_rpi])/remaining_neurons,numpy.sum([numpy.sum(z) for z in gallant_corrs])/remaining_neurons,numpy.sum([numpy.sum(z) for z in corrs])/remaining_neurons]
    region3 = [mean(corrs_rpi[0]),mean(gallant_corrs[0]),mean(corrs[0])]
    region5 = [mean(corrs_rpi[1]),mean(gallant_corrs[1]),mean(corrs[1])]
    region2010 = [mean(corrs_rpi[2]),mean(gallant_corrs[2]),mean(corrs[2])]
    
    print "CC Means:" , means
    
    #loc = numpy.array([2-width,2,2+width] )
    #b1= pylab.bar(loc-(width-0.05)/2, means, width-0.05, color='gray')
    #pylab.plot(loc,region3,'o',color='r')
    #pylab.plot(loc,region5,'o',color='g')
    #pylab.plot(loc,region2010,'o',color='b')
    #p1=pylab.plot(loc,region3,'-',color='r')
    #p2=pylab.plot(loc,region5,'-',color='g')
    #p3=pylab.plot(loc,region2010,'-',color='b')
    #pylab.ylabel('Correlation coefficient')
    #ticks = numpy.concatenate((ticks,loc))

    efv=[]
    rpi_efv=[]
    gallant_efv=[]
    for i in xrange(0,len(animals)):
       raw_validation_data_set=numpy.rollaxis(numpy.array(rvs[i]),2)
       
       print numpy.shape(pred_act[i])
       print numpy.shape(pred_val_act[i])
       print numpy.shape(rpi_pred_act[i])
       print numpy.shape(rpi_pred_val_act[i])
       
       signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(ts[i]), numpy.array(vs[i]), pred_act[i], pred_val_act[i])
       efv.append(validation_prediction_power)
       signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(ts[i]), numpy.array(vs[i]), numpy.array(rpi_pred_act[i]), numpy.array(rpi_pred_val_act[i]))
       rpi_efv.append(validation_prediction_power)
       signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(vs[i]), numpy.array(vs[i]), numpy.array(gallant_pred_val_act[i]), numpy.array(gallant_pred_val_act[i]))
       gallant_efv.append(validation_prediction_power)

    means = [numpy.sum([numpy.sum(z) for z in rpi_efv])/remaining_neurons,numpy.sum([numpy.sum(z) for z in gallant_efv])/remaining_neurons,numpy.sum([numpy.sum(z) for z in efv])/remaining_neurons]
    region3 = [mean(rpi_efv[0]),mean(gallant_efv[0]),mean(efv[0])]
    region5 = [mean(rpi_efv[1]),mean(gallant_efv[1]),mean(efv[1])]
    region2010 = [mean(rpi_efv[2]),mean(gallant_efv[2]),mean(efv[2])]

    print "FEV Means:" , means

    ax = pylab.subplot(gs[0,1])
    
    loc = numpy.array([1-width,1,1+width] )
    b1= pylab.bar(loc-(width-0.05)/2, means, width-0.05, color='gray')
    pylab.plot(loc,region3,'o',color='r')
    pylab.plot(loc,region5,'o',color='g')
    pylab.plot(loc,region2010,'o',color='b')
    p1=pylab.plot(loc,region3,'-',color='r')
    p2=pylab.plot(loc,region5,'-',color='g')
    p3=pylab.plot(loc,region2010,'-',color='b')
    pylab.ylim(-0.1,0.6)
    pylab.xlim(1-width-width,1+width+width)
    pylab.ylabel('FEV',fontsize=14)
    ticks = numpy.concatenate((ticks,loc))
    ax.set_xticks(ticks)
    ax.set_xticklabels(('STA','BWT','LSCSM'),fontsize=14)
    
    

    ax = pylab.subplot(gs[1,0])
    pylab.plot(rpi_efv[0],efv[0],'ro',label='region1')
    pylab.plot(rpi_efv[1],efv[1],'go',label='region2')
    pylab.plot(rpi_efv[2],efv[2],'bo',label='region3')
    pylab.plot([-1.0,1.0],[-1.0,1.0],'k')
    #pylab.xlim(-12,1.0)
    #pylab.ylim(-1.0,1.0)
    pylab.xlabel('FEV STA',fontsize=14)
    pylab.ylabel('FEV LSCSM',fontsize=14)
    #pylab.legend(loc='upper left')

    ax = pylab.subplot(gs[1,1])
    pylab.plot(gallant_efv[0],efv[0],'ro',label='region1')
    pylab.plot(gallant_efv[1],efv[1],'go',label='region2')
    pylab.plot(gallant_efv[2],efv[2],'bo',label='region3')
    pylab.plot([-0.5,1.0],[-0.5,1.0],'k')
    pylab.xlim(-0.5,1.0)
    pylab.ylim(-0.5,1.0)
    pylab.xlabel('FEV BWT',fontsize=14)

    pylab.savefig('/home/jan/Doc/Papers/LSCSMPaper/fig/lscsm_comparison.png')


def AnalyzeRF():
    from mpl_toolkits.axes_grid1 import make_axes_locatable
 
    res = contrib.dd.DB(None)
    prefix = './LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/'
    animals = ['2009_11_04_region3.dat','2009_11_04_region5.dat','2010_04_22.dat']
    animal_names = ['2009_11_04_region3','2009_11_04_region5','2010_04_22']
    
    f = pylab.figure(dpi=100,facecolor='w',figsize=(14,5))
    gs = GridSpec(6,20)
    gs.update(wspace=0.1,hspace=0.1,left=0.05,right=0.95,bottom=0.1,top=0.9)
    
    pylab.figtext(0.2, 0.94, 'Weight matrix',fontsize=14)
    pylab.figtext(0.62, 0.94, 'Hidden layer receptive fields',fontsize=14)          
    
    i=0
    
    for a in animals:
      res = contrib.dd.loadResults(prefix+a)
      
      dataset_node = res.children[0].children[0]
      
      training_set = dataset_node.data["training_set"]
      training_inputs= dataset_node.data["training_inputs"]
      
      num_pres,num_neurons = numpy.shape(training_set)
      num_pres,size = numpy.shape(training_inputs)
      size = numpy.sqrt(size)
      
      if __main__.__dict__.get('LSCSMOLD',True):
              lscsm_new = contrib.JanA.LSCSMNEW.LSCSM(numpy.mat(training_inputs),numpy.mat(training_set),9,num_neurons)
      else:
              lscsm_new = contrib.JanA.LSCSMNEW.LSCSMNEW(numpy.mat(training_inputs),numpy.mat(training_set),9,num_neurons)
      
      lscsm = res.children[0].children[0].children[0].children[0].data["LSCSM"]
      K = res.children[0].children[0].children[0].children[0].data["Kernels"]
      
      (rfs,hlw,lgn_w)  = lscsm_new.returnRFs(K)
      (hls,a) =  numpy.shape(rfs)
      rfs = numpy.reshape(rfs,(hls,size,size))
      ax = pylab.subplot(gs[i*2:i*2+2,0:9])
      im = pylab.imshow(hlw,interpolation='nearest',cmap=pylab.cm.RdBu_r)
      #pylab.ylabel('Region '+str(i+1))
      
      if i == 1:
                        pylab.ylabel('Hidden Layer Unit ID',fontsize=14)
      if i == 2:
                        pylab.xlabel('Output Layer Unit ID',fontsize=14)
      
      divider = make_axes_locatable(ax)
      cax = divider.append_axes("right", size="2%", pad=0.03)
      pylab.colorbar(im, cax=cax,ticks=[-4,4])
      
      m = numpy.max([numpy.abs(numpy.min(rfs)),numpy.abs(numpy.max(rfs))])
      
      print hls
      print len(rfs)
      for j in xrange(0,len(rfs)):
              ax = pylab.subplot(gs[i*2+int(j/10),10+j%10])
              w = numpy.array(rfs[j])
              m = numpy.max([numpy.abs(numpy.min(w)),numpy.abs(numpy.max(w))])
              pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
              pylab.axis('off')
      
      #ax = pylab.subplot(gs[i*2+int(j/10)-1:i*2+int(j/10)+1,20:24])
      #w = numpy.array(numpy.reshape(average_lgn,(size,size)))
      #m = numpy.max([numpy.abs(numpy.min(w)),numpy.abs(numpy.max(w))])
      #pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
      #pylab.axis('off')
      
      i=i+1
      
      pylab.savefig('/home/jan/Doc/Papers/LSCSMPaper/fig/lscsm_rfs.png')


def AnalyzeSTARF():
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import scipy.stats
    animal = 0
    lambdas = []    
    
    lambdas.append([3.27680000e-06 ,  1.31072000e-05 ,  1.60000000e-09  , 6.55360000e-06,
                6.40000000e-09 ,  1.04857600e-04 ,  6.55360000e-06  , 1.63840000e-06,
                4.19430400e-04 ,  8.00000000e-10 ,  5.12000000e-08 ,  5.12000000e-08,
                5.24288000e-05 ,  4.09600000e-07 ,  3.20000000e-09  , 1.31072000e-05,
                3.27680000e-06 ,  1.63840000e-06 ,  8.19200000e-07 ,  1.31072000e-05,
                5.24288000e-05 ,  2.00000000e-10 ,  8.38860800e-04 ,  3.27680000e-06,
                6.55360000e-06 ,  6.55360000e-06 ,  1.67772160e-03 ,  5.24288000e-05,
                4.09600000e-07 ,  4.09600000e-07 ,  2.62144000e-05 ,  1.34217728e-02,
                1.67772160e-03 ,  1.04857600e-04 ,  4.09600000e-07 ,  1.63840000e-06,
                1.60000000e-09 ,  1.00000000e-10 ,  8.00000000e-10 ,  4.09600000e-07,
                2.04800000e-07 ,  8.00000000e-10,   1.31072000e-05 ,  4.09600000e-07,
                3.27680000e-06 ,  2.09715200e-04 ,  2.62144000e-05 ,  1.63840000e-06,
                1.63840000e-06 ,  2.56000000e-08 ,  8.38860800e-04 ,  2.04800000e-07,
                3.20000000e-09 ,  3.27680000e-06 ,  1.63840000e-06 ,  2.62144000e-05,
                2.56000000e-08 ,  5.36870912e-02 ,  1.67772160e-03 ,  5.49755814e+01,
                1.34217728e-02 ,  2.68435456e-02 ,  2.09715200e-04 ,  1.31072000e-05,
                1.31072000e-05 ,  3.20000000e-09 ,  6.71088640e-03 ,  3.27680000e-06,
                2.56000000e-08 ,  1.02400000e-07 ,  2.09715200e-04,   8.19200000e-07,
                2.56000000e-08 ,  3.35544320e-03 ,  5.12000000e-08 ,  1.04857600e-04,
                1.28000000e-08 ,  5.49755814e+01 ,  1.63840000e-06 ,  1.63840000e-06,
                1.34217728e-02 ,  1.60000000e-09 ,  6.55360000e-06 ,  2.62144000e-05,
                3.27680000e-06 ,  6.55360000e-06 ,  4.09600000e-07 ,  2.62144000e-05,
                8.00000000e-10 ,  5.24288000e-05 ,  1.67772160e-03 ,  1.28000000e-08,
                1.31072000e-05 ,  1.60000000e-09 ,  1.00000000e-10 ,  2.04800000e-07,
                8.19200000e-07 ,  3.35544320e-03 ,  5.49755814e+01 ,  2.00000000e-10,
                6.55360000e-06 , 1.60000000e-09  , 6.55360000e-06])
                
    lambdas.append([  5.12000000e-08  , 3.27680000e-06 ,  1.31072000e-05 ,  5.24288000e-05,
                1.31072000e-05  , 1.63840000e-06  , 6.55360000e-06  , 1.60000000e-09,
                5.24288000e-05  , 2.09715200e-04  , 5.24288000e-05 ,  4.19430400e-04,
                1.67772160e-03  , 6.55360000e-06  , 2.09715200e-04 ,  2.62144000e-05,
                1.00000000e-10  , 1.71798692e+00  , 1.34217728e-02 ,  4.09600000e-07,
                2.09715200e-04  , 4.19430400e-04  , 6.55360000e-06 ,  1.31072000e-05,
                1.00000000e-10  , 1.02400000e-07  , 3.27680000e-06 ,  2.09715200e-04,
                8.38860800e-04  , 2.09715200e-04  , 2.62144000e-05 ,  3.27680000e-06,
                1.63840000e-06  , 2.04800000e-07  , 5.24288000e-05 ,  1.02400000e-07,
                5.24288000e-05  , 5.24288000e-05  , 1.31072000e-05 ,  2.62144000e-05,
                8.19200000e-07  , 2.04800000e-07  , 1.31072000e-05 ,  5.24288000e-05,
                1.00000000e-10  , 4.09600000e-07 ,  1.00000000e-10 ,  3.27680000e-06,
                1.02400000e-07  , 2.62144000e-05 ,  1.63840000e-06 ,  1.31072000e-05,
                1.63840000e-06  , 3.27680000e-06 ,  1.00000000e-10])
                        
    lambdas.append([  1.04857600e-04  , 2.62144000e-05 ,  5.24288000e-05 ,  1.63840000e-06,
                    5.24288000e-05  , 5.24288000e-05  , 2.09715200e-04  , 2.09715200e-04,
                    4.09600000e-07  , 2.09715200e-04  , 1.04857600e-04  , 3.27680000e-06,
                    2.62144000e-05  , 1.31072000e-05 ,  5.49755814e+01  , 6.55360000e-06,
                    5.24288000e-05  , 1.31072000e-05  , 2.09715200e-04  , 1.04857600e-04,
                    3.20000000e-09  , 5.24288000e-05  , 8.58993459e-01  , 2.62144000e-05,
                    6.71088640e-03  , 4.29496730e-01  , 1.04857600e-04  , 6.55360000e-06,
                    2.62144000e-05  , 1.63840000e-06  , 1.67772160e-03  , 1.31072000e-05,
                    1.04857600e-04  , 3.27680000e-06  , 1.31072000e-05  , 5.24288000e-05,
                    6.55360000e-06  , 4.09600000e-07  , 1.67772160e-03  , 1.31072000e-05,
                    4.19430400e-04  , 1.04857600e-04  , 1.60000000e-09  , 1.31072000e-05,
                    2.09715200e-04  , 1.60000000e-09  , 1.31072000e-05  , 5.24288000e-05,
                    2.62144000e-05  , 1.04857600e-04 ,  8.38860800e-04  , 8.38860800e-04,
                    2.09715200e-04  , 5.49755814e+01 ,  1.63840000e-06  , 5.49755814e+01,
                    1.31072000e-05 ,  6.40000000e-09  , 1.31072000e-05  , 1.04857600e-04,
                    2.62144000e-05 ,  4.09600000e-07  , 8.38860800e-04  , 2.62144000e-05,
                    1.07374182e-01 ,  4.19430400e-04  , 8.38860800e-04 ,  5.12000000e-08,
                    6.55360000e-06 ,  2.62144000e-05  , 2.62144000e-05  , 5.36870912e-02,
                    5.24288000e-05 ,  8.38860800e-04  , 8.38860800e-04 ,  1.31072000e-05,
                    5.24288000e-05 ,  1.04857600e-04  , 2.62144000e-05 ,  5.24288000e-05,
                    2.09715200e-04 ,  1.04857600e-04  , 1.04857600e-04 ,  4.09600000e-07,
                    4.19430400e-04  , 3.27680000e-06  , 1.04857600e-04 ,  8.38860800e-04,
                    1.31072000e-05 ,  1.04857600e-04  , 5.49755814e+01 ,  1.04857600e-04,
                    5.24288000e-05 ,  1.04857600e-04  , 1.00000000e-10 ,  5.49755814e+01,
                    5.24288000e-05 ,  1.00000000e-10  , 3.27680000e-06 ,  6.71088640e-03,
                    1.00000000e-10  , 1.07374182e-01])
                        
    res = contrib.dd.DB(None)
    
    
    animal_data = ['./LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/2009_11_04_region3.dat','./LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/2009_11_04_region5.dat','./LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/2010_04_22.dat']
    animal_name = ['2009_11_04_region3', '2009_11_04_region5', '2010_04_22']
    
    res = contrib.dd.loadResults(animal_data[animal])
    
    dataset_node = res.children[0].children[0]
    
    training_set = numpy.mat(dataset_node.data["training_set"])
    training_inputs= numpy.mat(dataset_node.data["training_inputs"])
    validation_set = numpy.mat(dataset_node.data["validation_set"])
    validation_inputs= numpy.mat(dataset_node.data["validation_inputs"])
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,size = numpy.shape(training_inputs)
    size = numpy.sqrt(size)
    
    kernel_size =  numpy.shape(numpy.mat(training_inputs))[1]
    laplace = laplaceBias(int(numpy.sqrt(kernel_size)),int(numpy.sqrt(kernel_size)))

    if __main__.__dict__.get('LSCSMOLD',True):
            lscsm_new = contrib.JanA.LSCSMNEW.LSCSM(numpy.mat(training_inputs),numpy.mat(training_set),9,num_neurons)
    else:
            lscsm_new = contrib.JanA.LSCSMNEW.LSCSMNEW(numpy.mat(training_inputs),numpy.mat(training_set),9,num_neurons)
    
    lscsm = res.children[0].children[0].children[0].children[0].data["LSCSM"]
    K = res.children[0].children[0].children[0].children[0].data["Kernels"]
    pred_act = lscsm.response(training_inputs,K)
    pred_val_act = lscsm.response(validation_inputs,K)
    
    
    rpi = numpy.loadtxt(animal_name[animal]+'STA.txt')

    rpa = numpy.mat(training_inputs * rpi)
    rpva = numpy.mat(validation_inputs * rpi)
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpa),num_bins=20,display=False)
    rpi_pred_val_act_t = apply_output_function(numpy.mat(rpva),ofs)
    
    
    f = pylab.figure(dpi=200,facecolor='w',figsize=(21.0,16.0))
    
    # GOOD f = pylab.figure(dpi=100,facecolor='w',figsize=(10.5,8.0))
    gs = GridSpec(13,18)
    gs.update(wspace=0.25,hspace=0.05,left=0.05,right=0.98,bottom=0.02,top=0.93)
    
    pylab.figtext(0.03,0.300, 'Linear RFs from data',fontsize=18,rotation='vertical')
    pylab.figtext(0.03,0.825, 'Linear RFs from fitted LSCSM',fontsize=18,rotation='vertical')          
    
    
    ma = numpy.mat(training_inputs).T*numpy.mat(training_inputs)
    ma1 =  numpy.mat(training_inputs).T * numpy.mat(pred_act)
    lc = []
    llc = []
    
    lscsm_rpis = []
    
    # lets sort STA correlations, we will use the idx for sorting the order in which we plot things
    c = []
    for i in xrange(0,num_neurons):
        c.append(scipy.stats.pearsonr(rpi_pred_val_act_t[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0])
    idx = numpy.argsort(c).tolist()
    idx.reverse()
    
    for i in xrange(0,num_neurons):
        print i
        lscsm_rpi = numpy.linalg.pinv(ma + lambdas[animal][i]*laplace) * ma1
        lscsm_rpis.append(lscsm_rpi[:,i])
        
        rpa = numpy.mat(training_inputs * lscsm_rpi)
        rpva = numpy.mat(validation_inputs * lscsm_rpi)
        ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpa),num_bins=20,display=False)
        lscsm_rpi_pred_val_act_t = apply_output_function(numpy.mat(rpva),ofs)
        
        corr_lscsm = scipy.stats.pearsonr(pred_val_act[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0]
        corr_rpi = scipy.stats.pearsonr(rpi_pred_val_act_t[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0]
        corr_lscsm_rpi = scipy.stats.pearsonr(lscsm_rpi_pred_val_act_t[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0]
        
        lc.append(corr_lscsm)
        llc.append(corr_lscsm_rpi)
        
        w = numpy.reshape(rpi[:,i],(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size)))
        m = numpy.max([numpy.abs(numpy.min(w)),numpy.abs(numpy.max(w))])
        ax = pylab.subplot(gs[idx.index(i)/18,idx.index(i)%18])
        pylab.title('%.2f' % corr_rpi,fontsize=12)
        im = pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
        ax.title.set_y(0.9)
        pylab.axis('off')
        
        w = numpy.reshape(numpy.array(lscsm_rpi[:,i]),(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size)))
        m = numpy.max([numpy.abs(numpy.min(w)),numpy.abs(numpy.max(w))])
        ax = pylab.subplot(gs[7+idx.index(i)/18,idx.index(i)%18])
        pylab.title('%.2f/%.2f' % (corr_lscsm_rpi, corr_lscsm),fontsize=12)
        im = pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
        ax.title.set_y(0.9)
        pylab.axis('off')

    print "LSCSM Correlations:" , lc
    print "LSCSM Linear Correlations:" , llc
    
    f = open(animal_name[animal] + '_LSCSM_STA.pickle','wb')
    import pickle
    pickle.dump(lscsm_rpis,f)
    pylab.savefig('/home/jan/Doc/Papers/LSCSMPaper/fig/STA_comparison_rfs.png')
    


def FreeParameters():
    LgnSizes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,16,18,20]
   
    LgnSizesRG1TSCC = [0.14978643170799999, 0.23026758047699999, 0.28340199495500001, 0.31949204251800001, 0.33565319846899999, 0.34419813618, 0.35345091545000001, 0.35742253389899997, 0.36384012409299998, 0.36755197511100002, 0.370053883418, 0.37173809721899997, 0.37311075709199998, 0.37666755651200001, 0.377759459573, 0.38028678579199998, 0.382736179748]
    LgnSizesRG2TSCC = [0.173985598809, 0.25471114856799998, 0.29326244117900002, 0.323573124253, 0.33851024304100003, 0.34766435031300003, 0.35485908595400001, 0.36052709580300002, 0.364791608203, 0.36826158802100001, 0.37213132785199998, 0.372739448556, 0.375527557437, 0.37887738439200003, 0.38126912656599998, 0.38614697989899999, 0.38918618849999997]
    LgnSizesRG3TSCC = [0.13887973440199999, 0.21184742115499999, 0.26499995276299998, 0.29276656123400002, 0.30748182213199998, 0.32052071344499999, 0.3295203149, 0.33719566349000002, 0.34196917737100002, 0.34567251025000001, 0.34794915309199997, 0.35151374232100002, 0.35261215789799999, 0.35205353520600002, 0.356525770593, 0.35762810600400002, 0.35876559034200001]
                      
    LgnSizesRG1VSCC = [0.25263042124000001, 0.32737470056099999, 0.429555534179, 0.46417129203000002, 0.48173675796999998, 0.49331554741, 0.52453319074399996, 0.52409206793700003, 0.51458534369999998, 0.53349227894700002, 0.51990962724900003, 0.522774171638, 0.50824487550200004, 0.49346024545799999, 0.51076363444100004, 0.51168441972800005, 0.47168634561900002]
    LgnSizesRG2VSCC = [0.19255105961999999, 0.251315338763, 0.30390508105000003, 0.40053637697900002, 0.37798328655699998, 0.42823657700500001, 0.44132258109099998, 0.39344926215100001, 0.439020418483, 0.41193363394400001, 0.37259620009200001, 0.39108459487699998, 0.42251965633299998, 0.39727933885700001, 0.40541028968999998, 0.40216781950399999, 0.41478643185699998]
    LgnSizesRG3VSCC = [0.182601116131, 0.29581987602699999, 0.34661114435099999, 0.38502772054599999, 0.43771521053599999, 0.43099546073299999, 0.438349878867, 0.43551835038100001, 0.45052674522800001, 0.456054292684, 0.44898840319799999, 0.46937641785700002, 0.45088535443400002, 0.44528672434700001, 0.431691934434, 0.41213186315200001, 0.44850036857600001]
    
    
    HLS = [0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.6,0.7,0.9,1.0]

    HLSRG1TSCC = [0.26401744575800001, 0.31817680085299999, 0.34428508959800003, 0.36384012409299998, 0.37917938021399999, 0.38936563435299998, 0.41257827266000002, 0.42942943247900001, 0.43432492047999999, 0.43523145503299998, 0.44494317333900002, 0.43489255922600001]
    HLSRG2TSCC = [0.19979235900600001, 0.29304553137099998, 0.33801216717900001, 0.364791608203, 0.37768247784600001, 0.393772925675, 0.417239354635, 0.43455928021899998, 0.44903022447699997, 0.46115427723199998, 0.48396247146999999, 0.49356995856800001]
    HLSRG3TSCC = [0.23764761808900001, 0.29826910829800002, 0.325039453049, 0.34196917737100002, 0.35437453867599999, 0.36444761208699999, 0.38176753107599998, 0.39362426314299997, 0.398463876173, 0.40274338103200003, 0.40396687225599998, 0.40567870127299999]
    
    
    HLSRG1VSCC = [0.39186233072299997, 0.48183931072399999, 0.51160575230100003, 0.51458534369999998, 0.55050937267800004, 0.52215723225900001, 0.51769871173100002, 0.47997004025500001, 0.49850435549799998, 0.44596866461500001, 0.49672758300100001, 0.497293816331]
    HLSRG2VSCC = [0.221180857797, 0.40637152746999999, 0.423779729233, 0.439020418483, 0.42681274608199998, 0.46272534759099998, 0.39694241208100001, 0.398135916624, 0.37114608293200002, 0.37817705734700002, 0.32945173246199999, 0.30257254899500002]
    HLSRG3VSCC = [0.35202372469100002, 0.41105375514600001, 0.44745074832100001, 0.45052674522800001, 0.44551291462199999, 0.44371204219499999, 0.431830846386, 0.41317334237199999, 0.42428369980500003, 0.42222987985100002, 0.405085063021, 0.43164526995000002]
    
    
    f = pylab.figure(dpi=100,facecolor='w',figsize=(12,5))
    pylab.subplot(1,2,1)
    pylab.plot(LgnSizes,LgnSizesRG1TSCC,'r',label='Region1')
    pylab.plot(LgnSizes,LgnSizesRG2TSCC,'g',label='Region2')
    pylab.plot(LgnSizes,LgnSizesRG3TSCC,'b',label='Region3')

    pylab.plot(LgnSizes,LgnSizesRG1VSCC,'r--',label='Region1')
    pylab.plot(LgnSizes,LgnSizesRG2VSCC,'g--',label='Region2')
    pylab.plot(LgnSizes,LgnSizesRG3VSCC,'b--',label='Region3')
    
    p1 = pylab.plot([-10,-11],[-10,-11],'k')
    p2 = pylab.plot([-10,-11],[-10,-11],'k--')
    p3 = pylab.plot([-10,-11],[-10,-11],'r',lw=10)
    p4 = pylab.plot([-10,-11],[-10,-11],'g',lw=10)
    p5 = pylab.plot([-10,-11],[-10,-11],'b',lw=10)
    
    pylab.ylim(0.0,0.6)
    pylab.xlim(0,20)
    pylab.xlabel('# of LGN units',fontsize=16)
    pylab.ylabel('Correlation coefficient',fontsize=16)
    pylab.legend( (p1[0], p2[0],p3[0],p4[0],p5[0]), ('Training set','Validation set','Region 1','Region 2','Region 3'),loc='best' )
    
    
    pylab.subplot(1,2,2)
    pylab.plot(HLS,HLSRG1TSCC,'r',label='Region1')
    pylab.plot(HLS,HLSRG2TSCC,'g',label='Region2')
    pylab.plot(HLS,HLSRG3TSCC,'b',label='Region3')
    
    pylab.plot(HLS,HLSRG1VSCC,'r--',label='Region1')
    pylab.plot(HLS,HLSRG2VSCC,'g--',label='Region2')
    pylab.plot(HLS,HLSRG3VSCC,'b--',label='Region3')
    pylab.ylim(0.0,0.6)
    pylab.xlabel('# of hidden units',fontsize=16)
    
    pylab.savefig('/home/jan/Doc/Papers/LSCSMPaper/fig/FreeParameters.png')    
    
    
    
def runLSCSMAnalysis(rpi_pred_act,rpi_pred_val_act,glm_pred_act,glm_pred_val_act,training_set,validation_set,num_neurons,raw_validation_data_set):
    
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpi_pred_act),display=True)
    rpi_pred_act_t = apply_output_function(numpy.mat(rpi_pred_act),ofs)
    rpi_pred_val_act_t = apply_output_function(numpy.mat(rpi_pred_val_act),ofs)
    
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(glm_pred_act),display=True)
    glm_pred_act_t = apply_output_function(numpy.mat(glm_pred_act),ofs)
    glm_pred_val_act_t = apply_output_function(numpy.mat(glm_pred_val_act),ofs)
    
    
    pylab.figure()
    
    for i in xrange(0,num_neurons):
        pylab.subplot(11,11,i+1)    
        pylab.plot(rpi_pred_val_act[:,i],validation_set[:,i],'o')
    pylab.savefig(normalize_path('RPI_val_relationship.png'))
        
    pylab.figure()
    for i in xrange(0,num_neurons):
        pylab.subplot(11,11,i+1)    
        pylab.plot(glm_pred_val_act[:,i],validation_set[:,i],'o')   
    pylab.savefig(normalize_path('GLM_val_relationship.png'))
    
    
    pylab.figure()
    for i in xrange(0,num_neurons):
        pylab.subplot(11,11,i+1)    
        pylab.plot(rpi_pred_val_act_t[:,i],validation_set[:,i],'o')
    pylab.savefig(normalize_path('RPI_t_val_relationship.png'))
        
        
    pylab.figure()
    for i in xrange(0,num_neurons):
        pylab.subplot(11,11,i+1)    
        pylab.plot(glm_pred_val_act_t[:,i],validation_set[:,i],'o')
        pylab.title('RPI')   
    pylab.savefig(normalize_path('GLM_t_val_relationship.png'))
    
    
    print numpy.shape(validation_set)
    print numpy.shape(rpi_pred_val_act_t)
    print numpy.shape(glm_pred_val_act)
    
    pylab.figure()
    pylab.plot(numpy.mean(numpy.power(validation_set - rpi_pred_val_act_t,2),0),numpy.mean(numpy.power(validation_set - glm_pred_val_act,2),0),'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI')
    pylab.ylabel('GLM')
    pylab.savefig(normalize_path('GLM_vs_RPI_MSE.png'))

    print 'RPI'
    print 'WithoutTF'
    printCorrelationAnalysis(training_set,validation_set,rpi_pred_act,rpi_pred_val_act)
    print 'WithTF'
    printCorrelationAnalysis(training_set,validation_set,rpi_pred_act_t,rpi_pred_val_act_t)
    
    print 'LSCSM'    
    print 'WithoutTF'
    printCorrelationAnalysis(training_set,validation_set,glm_pred_act,glm_pred_val_act)
    print 'WithTF'
    printCorrelationAnalysis(training_set,validation_set,glm_pred_act_t,glm_pred_val_act_t)
    
    
    print 'RPI \n'
        
    (ranks,correct,pred) = performIdentification(validation_set,rpi_pred_val_act)
    print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - rpi_pred_val_act,2))
        
    (ranks,correct,pred) = performIdentification(validation_set,rpi_pred_val_act_t)
    print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - rpi_pred_val_act_t,2))
                
    signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(rpi_pred_act), numpy.array(rpi_pred_val_act))
    signal_power,noise_power,normalized_noise_power,training_prediction_power_t,rpi_validation_prediction_power_t,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(rpi_pred_act_t), numpy.array(rpi_pred_val_act_t))
        
    print "Prediction power on training set / validation set: ", numpy.mean(training_prediction_power) , " / " , numpy.mean(validation_prediction_power)
    print "Prediction power after TF on training set / validation set: ", numpy.mean(training_prediction_power_t) , " / " , numpy.mean(rpi_validation_prediction_power_t)

        
    print '\n \n GLM \n'
        
    (ranks,correct,pred) = performIdentification(validation_set,glm_pred_val_act)
    print "Natural:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - glm_pred_val_act,2))
        
    (ranks,correct,pred) = performIdentification(validation_set,glm_pred_val_act_t)
    print "Natural+TF:", correct , "Mean rank:", numpy.mean(ranks) , "MSE", numpy.mean(numpy.power(validation_set - glm_pred_val_act_t,2))
                
    glm_signal_power,glm_noise_power,glm_normalized_noise_power,glm_training_prediction_power,glm_validation_prediction_power,glm_signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(glm_pred_act), numpy.array(glm_pred_val_act))
    glm_signal_power_t,glm_noise_power_t,glm_normalized_noise_power_t,glm_training_prediction_power_t,glm_validation_prediction_power_t,glm_signal_power_variances_t = signal_power_test(raw_validation_data_set, numpy.array(training_set), numpy.array(validation_set), numpy.array(glm_pred_act_t), numpy.array(glm_pred_val_act_t))
        
    print "Prediction power on training set / validation set: ", numpy.mean(glm_training_prediction_power) , " / " , numpy.mean(glm_validation_prediction_power)
    print "Prediction power after TF on training set / validation set: ", numpy.mean(glm_training_prediction_power_t) , " / " , numpy.mean(glm_validation_prediction_power_t)
    
    pylab.figure()
    pylab.plot(rpi_validation_prediction_power_t[:num_neurons],glm_validation_prediction_power[:num_neurons],'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI_t')
    pylab.ylabel('GLM')
    pylab.savefig(normalize_path('GLM_vs_RPI_prediction_power.png'))

    
    pylab.figure()
    pylab.plot(rpi_validation_prediction_power_t[:num_neurons],glm_validation_prediction_power_t[:num_neurons],'o')
    pylab.hold(True)
    pylab.plot([0.0,1.0],[0.0,1.0])
    pylab.xlabel('RPI_t')
    pylab.ylabel('GLM_t')
    pylab.savefig('GLMt_vs_RPIt_prediction_power.png')

    #db_node.add_data("Kernels",K,force=True)
    #db_node.add_data("GLM",glm,force=True)
    #db_node.add_data("ReversCorrelationPredictedActivities",glm_pred_act,force=True)
    #db_node.add_data("ReversCorrelationPredictedActivities+TF",glm_pred_act_t,force=True)
    #db_node.add_data("ReversCorrelationPredictedValidationActivities",glm_pred_val_act,force=True)
    #db_node.add_data("ReversCorrelationPredictedValidationActivities+TF",glm_pred_val_act_t,force=True)
    #return [K,validation_inputs, validation_set]
        
        
def AnalyzeSTARFforYoungAnimal():
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import scipy.stats
    
    lambdas = [  1.31072000e-05  , 2.62144000e-05  , 1.04857600e-04  , 8.19200000e-07,
    1.04857600e-04 ,  1.31072000e-05 ,  6.40000000e-09 ,  1.67772160e-03,
    2.62144000e-05 ,  1.00000000e-10 ,  5.12000000e-08 ,  3.27680000e-06,
    3.35544320e-03 ,  6.40000000e-09 ,  8.38860800e-04 ,  1.00000000e-10,
    5.24288000e-05 ,  2.09715200e-04 ,  2.68435456e-02 ,  2.62144000e-05,
    3.27680000e-06 ,  1.02400000e-07 ,  1.67772160e-03 ,  1.63840000e-06,
    3.35544320e-03 ,  3.27680000e-06 ,  1.00000000e-10 ,  8.19200000e-07,
    2.68435456e-02 ,  6.40000000e-09 ,  1.28000000e-08 ,  1.00000000e-10,
    2.09715200e-04 ,  8.38860800e-04 ,  5.49755814e+01 ,  6.55360000e-06,
    6.55360000e-06 ,  3.35544320e-03 ,  8.19200000e-07 ,  8.38860800e-04,
    1.00000000e-10 ,  1.60000000e-09 ,  2.09715200e-04 ,  1.67772160e-03,
    6.71088640e-03 ,  5.49755814e+01 ,  2.62144000e-05 ,  4.19430400e-04,
    4.19430400e-04 ,  1.31072000e-05 ,  3.27680000e-06 ,  2.09715200e-04,
    2.04800000e-07 ,  5.12000000e-08 ,  1.67772160e-03 ,  2.09715200e-04,
    5.49755814e+01 ,  5.49755814e+01 ,  1.04857600e-04 ,  2.62144000e-05,
    8.38860800e-04 ,  4.19430400e-04 ,  5.49755814e+01 ,  3.27680000e-06,
    1.67772160e-03 ,  1.00000000e-10 ,  1.63840000e-06 ,  5.49755814e+01]
                
    res = contrib.dd.DB(None)
    animal = './20091110_region4.dat'
    animal_name = '2009_11_10_region4'
    
    res = contrib.dd.loadResults(animal)
    
    dataset_node = res.children[0].children[0]
    
    training_set = numpy.mat(dataset_node.data["training_set"])
    training_inputs= numpy.mat(dataset_node.data["training_inputs"])
    validation_set = numpy.mat(dataset_node.data["validation_set"])
    validation_inputs= numpy.mat(dataset_node.data["validation_inputs"])
    
    num_pres,num_neurons = numpy.shape(training_set)
    num_pres,size = numpy.shape(training_inputs)
    size = numpy.sqrt(size)
    
    kernel_size =  numpy.shape(numpy.mat(training_inputs))[1]
    laplace = laplaceBias(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size))

    if __main__.__dict__.get('LSCSMOLD',True):
            lscsm_new = contrib.JanA.LSCSMNEW.LSCSM(numpy.mat(training_inputs),numpy.mat(training_set),9,num_neurons)
    else:
            lscsm_new = contrib.JanA.LSCSMNEW.LSCSMNEW(numpy.mat(training_inputs),numpy.mat(training_set),9,num_neurons)
    
    lscsm = res.children[0].children[0].children[0].children[0].data["LSCSM"]
    K = res.children[0].children[0].children[0].children[0].data["Kernels"]
    
    pred_act = lscsm.response(training_inputs,K)
    pred_val_act = lscsm.response(validation_inputs,K)
    
    
    rpi = numpy.loadtxt('20091110_region4STA_20091011.txt')
    
    rpa = numpy.mat(training_inputs * rpi)
    rpva = numpy.mat(validation_inputs * rpi)
    ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpa),num_bins=20,display=False)
    rpi_pred_val_act_t = apply_output_function(numpy.mat(rpva),ofs)
    
    f = pylab.figure(dpi=100,facecolor='w',figsize=(10,10))
    gs = GridSpec(13,17)
    gs.update(wspace=0.1,hspace=0.1,left=0.02,right=0.98,bottom=0.02,top=0.93)
    
    pylab.figtext(0.155, 0.97, 'Linear RFs from data',fontsize=14)
    pylab.figtext(0.605, 0.97, 'Linear RFs from fitted LSCSM',fontsize=14)          
    
    
    ma = numpy.mat(training_inputs).T*numpy.mat(training_inputs)
    ma1 =  numpy.mat(training_inputs).T * numpy.mat(pred_act)
    
    for i in xrange(0,num_neurons):
        print i
        lscsm_rpi = numpy.linalg.pinv(ma + lambdas[i]*laplace) * ma1
        
        rpa = numpy.mat(training_inputs * lscsm_rpi)
        rpva = numpy.mat(validation_inputs * lscsm_rpi)
        
        ofs = run_nonlinearity_detection(numpy.mat(training_set),numpy.mat(rpa),num_bins=20,display=False)
        lscsm_rpi_pred_val_act_t = apply_output_function(numpy.mat(rpva),ofs)
        
        corr_lscsm = scipy.stats.pearsonr(pred_val_act[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0]
        corr_rpi = scipy.stats.pearsonr(rpi_pred_val_act_t[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0]
        corr_lscsm_rpi = scipy.stats.pearsonr(lscsm_rpi_pred_val_act_t[:,i].flatten(),numpy.array(validation_set)[:,i].flatten())[0]
        
        w = numpy.reshape(rpi[:,i],(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size)))
        m = numpy.max([numpy.abs(numpy.min(w)),numpy.abs(numpy.max(w))])
        ax = pylab.subplot(gs[i/8,i%8])
        pylab.title('%.2f' % corr_rpi,fontsize=7)
        im = pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
        ax.title.set_y(0.9)
        pylab.axis('off')
        
        w = numpy.reshape(numpy.array(lscsm_rpi[:,i]),(numpy.sqrt(kernel_size),numpy.sqrt(kernel_size)))
        m = numpy.max([numpy.abs(numpy.min(w)),numpy.abs(numpy.max(w))])
        ax = pylab.subplot(gs[i/8,9+i%8])
        pylab.title('%.2f/%.2f' % (corr_lscsm_rpi, corr_lscsm),fontsize=7)
        im = pylab.imshow(w,vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
        ax.title.set_y(0.9)
        pylab.axis('off')
                
    pylab.savefig('./STA_comparison_rfs_for_young_animal.png')


def loadBestResults():
    res = contrib.dd.DB(None)
    prefix = './LSCSM/LSCSM/NumLgn=9_HLS=0.2_NoEarlyStopping_DOG_Seeds50/'
    
    animals = ['2009_11_04_region3.dat','2009_11_04_region5.dat','2010_04_22.dat']
    animal_names = ['2009_11_04_region3','2009_11_04_region5','2010_04_22']
    region_sizes = [103,55,102]
    lc = []
    llc = []
    
    lc.append(numpy.array([0.75430004841710951, 0.71047154705444038, 0.083850494769766998, 0.5117166453377554, 0.15034188538084073, 0.53853320271005878, 0.48203561612048695, 0.28971515412984633, 0.83135861020007074, 0.33255309258986238, 0.2245499890277726, 0.086755521611549383, 0.23307304927119868, 0.60100753277116736, 0.14443778876306157, 0.2650806421817945, 0.52188935698174621, 0.69958792739051712, 0.66690681340991931, 0.8083910367456375, 0.75873889710116271, 0.59456938973432816, 0.75869323758903717, 0.67824262800899471, 0.42315492152418138, 0.89313733089871661, 0.62803684151694505, 0.72564310205425442, 0.71192328556005224, 0.36314564583376263, 0.55936601963794585, 0.7874549706815146, 0.57630729740531239, 0.84117254052853219, 0.49271098879162317, 0.18304541974532876, 0.30971882931449896, 0.2238498201649409, 0.55999383423355731, 0.71369771091143541, 0.37303677871312108, 0.64447692810310941, 0.90290439700943725, 0.35308582832783281, 0.35385753488344085, 0.60585605386945118, 0.87226663638028612, 0.52854989663440333, 0.58392838044989948, 0.5203953550446021, 0.42149435564390603, 0.21373730569354971, 0.35471039505053042, 0.6849548054257929, 0.34321503242839763, 0.59501321823261577, 0.44123191909521536, 0.49312875800217043, 0.76513584066740348, 0.80951855733162648, 0.25159815128036217, 0.37823459167684081, 0.82737438470953983, 0.20699878479925976, 0.62654014241545453, 0.53035157004805433, 0.53498118618845125, 0.1398686375035755, 0.15989676823661678, 0.80820865127273978, 0.31528734374181122, 0.11144453222658771, 0.59604534715630186, 0.13262833512698072, 0.38850987575552232, 0.89026321281329091, 0.29847999565921302, 0.48402815180701009, 0.48806583960081767, 0.73062921042842965, 0.75493895519141829, 0.11996095217530764, 0.32821903432769245, 0.74473138897942659, 0.16761638130466164, 0.77648110068710274, 0.31674730176312088, 0.38555034168462243, 0.39384690023163965, 0.80463599615689019, 0.0074951728459309872, 0.17023129499390408, 0.8150775943119456, 0.58924093415755407, 0.67680414454223448, 0.70794520473741429, 0.56879412117805761, 0.29639923670848983, 0.57441680953258789, 0.097726448322283083, 0.66296060828945713, 0.56135424787275756, 0.78508228262813839]))
    llc.append(numpy.array([0.74378786707772482, 0.46371016248650493, 0.0069139758004957913, 0.042125737214889762, -0.079850020772496019, 0.25866794019714084, 0.21710740187649183, 0.0094866653976834695, 0.74260526680279781, 0.25043813365315964, 0.10127397939916637, -0.041114384103443383, 0.19596249261531878, 0.28359362812820355, 0.10342508326528869, -0.066755845258872987, 0.43781648716335564, 0.72091107538957522, 0.2510845277460334, 0.69332264803442401, 0.3519669364657505, 0.38316825811821331, 0.12652276385306507, 0.3712184356501903, 0.46614789028702247, 0.84907161723580327, 0.31865146386379101, 0.53130200914289227, 0.12043375548430249, 0.24605767481515314, 0.35660949739197922, 0.69363358919473872, 0.45424723399767031, 0.59731117657839339, 0.083882581130556105, -0.0045154618886228725, 0.22672505912020166, 0.11705380041801781, 0.047390697202335838, 0.59469284204297124, 0.017143766053190564, 0.4411757249782296, 0.83754110883464716, 0.046704395343869734, 0.045310902891549806, 0.18394627562128829, 0.8464654162628219, 0.37358282331696796, 0.57681274577647679, 0.012864710892395645, 0.31368448675467181, -0.044225459451442829, 0.021639576236575839, 0.60245370216573557, 0.47031446334643839, 0.66130683194467066, 0.5141677911974889, 0.36035547464546419, 0.31466146721295218, 0.19029012174242696, 0.44588980651089871, -0.071176408244165518, 0.70380931246641143, -0.051352384515376867, 0.17050115346035349, 0.11330216119188148, -0.059723940369613822, -0.1376716102565094, -0.13833725374047209, 0.83111518302588694, 0.24734911164631718, 0.089391886254633166, 0.0093391936218827579, 0.20024866271455621, -0.066347702572402814, 0.85092401583079835, -0.17630786433654236, 0.15874662889884886, 0.7168162959903237, 0.50983680796338227, 0.72690569330202248, -0.027144368760635234, -0.32050051841482236, 0.15863864864525615, 0.30571533204810453, 0.8624924083221498, -0.10501211512156608, -0.27099467129362559, 0.10456824568165435, 0.82475652559827184, 0.050067688046741096, 0.11811252095343526, 0.7450939576592861, 0.073314487236825099, 0.065098428226316049, 0.36478220003266837, 0.15783378804899292, 0.16076955923797684, 0.33034417127689325, -0.065438730331975142, 0.48544951500656192, 0.36586072907423156, 0.36415432683947563]))
    lc.append(numpy.array([0.43966480330738184, 0.53634238083692998, 0.12772581056004781, 0.046291739609058385, 0.64993959610645313, 0.56557317811755103, 0.10069786991358033, 0.5089988971231505, 0.48929392816115758, 0.5098961856250942, 0.45776107022625684, 0.51691397205070122, 0.35900990019595769, 0.52570122247164608, 0.29668825400562565, 0.55644808425419146, 0.13048756655634994, 0.34906108282985993, 0.072991018931633386, 0.47271255231870196, 0.40284054043507328, 0.56842629077060636, 0.63471378063700379, 0.75606172697333252, 0.27338144020475358, 0.42546083188202105, 0.44394682450425249, 0.14280422524940053, 0.75330427980486225, 0.53161530187568018, 0.55648423482277465, 0.18924239289434955, 0.27122659880711991, 0.6486964668835048, 0.66620435243542053, 0.46883246199231454, 0.59890255392637071, 0.16028631374091584, 0.78557488793605834, 0.15882786714542252, 0.34401873181732745, 0.14246919794675147, 0.25258146498312678, 0.19890202487633007, 0.051487465208805469, 0.45152509820454362, 0.92942378336624887, 0.28780063930010441, 0.80816879952440746, 0.52593188255618128, 0.65233988100173024, 0.27695615844982913, 0.44635824903017934, 0.57127244266865274, 0.48003045400476346]))
    llc.append(numpy.array([-0.057800997573891802, 0.58755425782364012, -0.023189344606317157, 0.23580669742749399, 0.65369684217481083, 0.28001317275787779, -0.075596976398303067, 0.23943337270584564, 0.36452326030871435, 0.57512362556107977, 0.44563503134085081, 0.0676125262566903, 0.15500895058335198, 0.44271961141412325, 0.27677418473220133, 0.43055884126067256, -0.16522084508000145, 0.14452960941793322, 0.20192797737590956, 0.56338499650081997, 0.40716593743765683, 0.017049404879762243, 0.53171723855868624, 0.26939895636597028, 0.1508776445573223, -0.060487128144253333, 0.50177179089004975, 0.063685482334628465, 0.1864585325269445, 0.20010949246304985, 0.41348322632832835, -0.058922884217796768, 0.088747268140187768, 0.65417333335231198, 0.44173857100043529, 0.2458294938287052, 0.45043625548198257, 0.17801622778512557, 0.51525812260470683, 0.26489779246463868, 0.20103099280407455, -0.26402106091752908, 0.17237555219558431, 0.38586731921861495, 0.072113482309280247, 0.079065566959181349, 0.25356793536470618, 0.299913860342917, 0.62897213641296468, 0.14990686223586522, 0.54180397590852725, 0.033883405759072512, 0.20182622297060931, 0.54765782896700188, 0.31346690807436367]))
    lc.append(numpy.array([0.44060620555260005, 0.76734787956646944, 0.85399828206216977, 0.17643943254950517, 0.51690299800511885, 0.648381761794105, 0.78503848725631165, 0.75448772338939618, 0.27419061289738506, 0.28916903315186837, 0.32185510540937179, 0.082050948073730368, 0.49477234426226496, 0.59402976865903834, -0.1490320136170826, 0.32927211957070546, 0.80850029369938292, 0.74039203988899716, 0.54110142548162976, 0.70046310523782873, 0.56642105407253418, 0.82883644822391489, 0.31578040382751066, 0.61697544125163684, 0.35177102978891434, 0.3883975465745077, 0.5260369941603843, 0.1919954966811952, 0.8240026929231361, -0.032827727755101933, 0.32549977700293553, 0.59030383920807694, 0.57478963457627308, 0.66703794020162621, 0.65074819972079812, 0.28618699969307054, 0.3790797455355665, 0.60775985911777664, 0.70004029311390348, 0.46189179811820358, 0.65829070317105631, 0.7394142533254322, 0.32684725028575912, -0.061947539432541443, 0.045301773709000681, 0.25510873355309727, 0.39856574302644265, 0.50221192784190682, 0.70499220144528552, 0.44891822385577251, 0.73504496150296994, 0.54330491499923916, 0.37484280759454985, 0.41665169831791388, 0.63783176209116177, 0.31226416762339843, 0.74400254533541355, 0.47536391181622534, 0.77177774221679718, 0.39963456999686836, 0.69193295714678982, 0.31821404154892158, 0.47401995520731594, 0.8237005871058537, 0.13196344002644173, -0.01589480814828137, 0.12178407238490487, 0.48213553175421436, 0.58051565760864332, 0.63069042112996054, 0.54000841842299396, -0.010086170774215373, 0.78817908499803158, 0.55254582869790292, 0.58649028786755852, 0.64884609896474132, 0.19513229175411934, 0.62669376834754931, 0.34332744985172703, 0.61045072986533422, 0.53715167275280651, 0.43536889381099164, 0.3827931780556269, 0.22941062179157667, 0.40301321829729786, 0.22853966225040442, 0.60270896328444867, 0.4403334067335648, 0.4480197790733445, 0.64405766000211773, 0.6319537075632925, 0.35068670837044691, 0.56808770338433745, 0.49761752085559846, 0.15742159924976154, 0.067140938770380923, 0.4319173285037271, 0.3332323835716241, -0.10194926276626423, 0.59624671872149393, 0.1309571214981502, 0.17357188638913065]))
    llc.append(numpy.array([0.33390793096377314, 0.74401782142395023, 0.86298593454582462, 0.13686168267451185, 0.37955895456272071, 0.54693458634553527, 0.60206630781611292, 0.71984767484308665, 0.024474117686420518, 0.19876826453977026, 0.27607317810411902, 0.089195113027309619, 0.13393975701518848, 0.49528345874878865, -0.33251358623515997, 0.33714017092759618, 0.72822997643006482, 0.70502239380466714, 0.42699675046615104, 0.44042310072999169, 0.35992351666578204, 0.75324938215503823, 0.25306842932316004, 0.63212803022323527, 0.33487366490586606, 0.12452340198736267, 0.63610739046672526, -0.017727974777358338, 0.77391431989689985, 0.18408786608141575, 0.24536782457712336, 0.53603574730077641, 0.30707839913543494, 0.51277920164978974, 0.5883468880281002, 0.5371445069280858, 0.30635549479493634, 0.42581718754403258, 0.26808225382919948, 0.50859345330360961, 0.42380125784883521, 0.71140104492485468, -0.25309408320418653, -0.042048052091668064, 0.14206740813392824, 0.25055167295697339, 0.46462462050668507, 0.42215400397686575, 0.73595724993447886, 0.38605539176164577, 0.73699118488502813, 0.47467222111702834, 0.23881170099224397, 0.030733991182398557, 0.34790768685436618, -0.16846500581178322, 0.62698450489755442, -0.43988921703381378, 0.74874934544232452, 0.43359384312678823, 0.53845535528424526, 0.032383321660254857, 0.41303091990169116, 0.65072937352293581, -0.17973215497974179, 0.47016811812002468, 0.065956705521277595, 0.27665663551234981, 0.38631877814243265, 0.5268161537841225, 0.60526575674404526, 0.014866503463840063, 0.59410152463324128, 0.49800908840700692, 0.58997348069768862, 0.52893091699493489, 0.48265413997221313, 0.6216356893543924, 0.37826691790770822, 0.41674130308559942, 0.72009036955454797, 0.43354054481354526, 0.37063021350647196, 0.017400683653330893, 0.44480095594610525, 0.28439813942885706, 0.56888146653678062, 0.2233289773889168, 0.19517780922124364, 0.62885715197108749, 0.010217076503262547, 0.42887892881395362, 0.39331539441468644, 0.37849011904534341, -0.00071241262180596386, 0.14093398701623458, 0.14593500922896491, 0.17656014742438902, 0.36491122522134595, 0.52390647678845292, -0.28011877107196748, -0.13474442373541173]))
    
    
    pred_act = []
    pred_val_act = []
    ts = []
    rvs = []
    vs = []
    ti = []
    vi = []
    sp = []
    rpi = []
    corrs = [] 
    snr=[]
    fev = []
    ps = []
    srm = []
    lscsm_rfs = []
    lscsm_hw = []
    lscsm_lgnw  = []
    
    # load locations
    loc = []
    f = file("./Mice/2009_11_04/region3_cell_locations", "r")
    loc.append([line.split() for line in f])
    for (i,s) in enumerate(loc[-1]):
        loc[-1][i][0] = float(s[0])
        loc[-1][i][1] = float(s[1])
    f.close()
		
    f = file("./Mice/2009_11_04/region5_cell_locations", "r")
    loc.append([line.split() for line in f])
    for (i,s) in enumerate(loc[-1]):
        loc[-1][i][0] = float(s[0])
        loc[-1][i][1] = float(s[1])
    f.close()

    f = file("./Mice/2010_04_22/cell_locations", "r")
    loc.append([line.split() for line in f])
    for (i,s) in enumerate(loc[-1]):
        loc[-1][i][0] = float(s[0])
        loc[-1][i][1] = float(s[1])
    f.close()
			
    #f = file("./Mice/20090925_14_36_01/(20090925_14_36_01)-_retinotopy_region2_sequence_50cells_cell_locations.txt", "r")
    #loc.append([line.split() for line in f])
    #f.close()
    
   
    i=0
    for a in animals:
      res = contrib.dd.loadResults(prefix+a)
      rpi.append(numpy.loadtxt(animal_names[i]+'STA.txt'))
      
      dataset_node = res.children[0].children[0]
      
      training_set = dataset_node.data["training_set"]

      validation_set = dataset_node.data["validation_set"]
      raw_validation_set = dataset_node.data["raw_validation_set"]
      training_inputs= dataset_node.data["training_inputs"]
      validation_inputs= dataset_node.data["validation_inputs"]
      
      num_trials = numpy.shape(raw_validation_set)[0]
      (num_trials,num_pres,num_neurons) = numpy.shape(numpy.array(raw_validation_set))
      raw_validation_set_flattened = numpy.reshape(raw_validation_set,(num_trials*num_pres,num_neurons))
      
      ts.append(numpy.mat(training_set))
      vs.append(numpy.mat(validation_set))
      rvs.append(raw_validation_set)
      ti.append(numpy.mat(training_inputs))
      vi.append(numpy.mat(validation_inputs))
      sp.append(TrevesRollsSparsness(numpy.mat(raw_validation_set_flattened)))
      #sp.append(TrevesRollsSparsness(numpy.mat(training_set)))
      
      srm.append(SejnowskiReliabilityMeasure(numpy.array(raw_validation_set)))
      
      K = res.children[0].children[0].children[0].children[0].data["Kernels"]
      lscsm = res.children[0].children[0].children[0].children[0].data["LSCSM"]
      lscsm_rfs.append(lscsm.returnRFs(K)[0])
      lscsm_hw.append(lscsm.returnRFs(K)[1])
      lscsm_lgnw.append(lscsm.returnRFs(K)[2])
          
      # predictions
      pred_act.append(lscsm.response(training_inputs,K))
      pred_val_act.append(lscsm.response(validation_inputs,K))
      
      # correlations
      train_c,val_c = printCorrelationAnalysis(ts[i],vs[i],pred_act[i],pred_val_act[i])
      corrs.append(numpy.array(val_c))

      #snr
      raw_validation_data_set=numpy.rollaxis(numpy.array(raw_validation_set),2)
      signal_power,noise_power,normalized_noise_power,training_prediction_power,validation_prediction_power,signal_power_variance = signal_power_test(raw_validation_data_set, numpy.array(ts[i]), numpy.array(vs[i]), pred_act[i], pred_val_act[i])
      snr.append(normalized_noise_power)
      
      fev.append(validation_prediction_power)
      
      a = scipy.stats.pearsonr(corrs[i],sp[i])
      b = scipy.stats.pearsonr(corrs[i],numpy.mean(numpy.array(ts[i]),axis=0))
      c = scipy.stats.pearsonr(corrs[i],srm[i])
      
      
      ps.append((a,b,c))
      i=i+1
    return locals()
    
    


def ReliabilityAnalysis(): 
    import pylab
    l = loadBestResults()
    globals().update(l)
    
    fstr = '%.2f(p=%.2f) : %.2f(p=%.2f) : %.2f(p=%.2f)'
    
    pylab.figure()
    pylab.subplot(1,3,1)
    pylab.title(fstr % (ps[0][0][0],ps[0][0][1],ps[1][0][0],ps[1][0][1],ps[2][0][0],ps[2][0][1]),fontsize=10)
    pylab.plot(corrs[0],sp[0],'ro')
    pylab.plot(corrs[1],sp[1],'go')
    pylab.plot(corrs[2],sp[2],'bo')
    pylab.xlabel('Prediction power (as Correlation coefficient)')
    pylab.ylabel('Treves-Rolls Sparsness')
    
    pylab.subplot(1,3,2)
    pylab.title(fstr % (ps[0][1][0],ps[0][1][1],ps[1][1][0],ps[1][1][1],ps[2][1][0],ps[2][1][1]),fontsize=10)
    pylab.plot(corrs[0],numpy.mean(numpy.array(ts[0]),axis=0),'ro')
    pylab.plot(corrs[1],numpy.mean(numpy.array(ts[1]),axis=0),'go')
    pylab.plot(corrs[2],numpy.mean(numpy.array(ts[2]),axis=0),'bo')
    pylab.xlabel('Prediction power (as Correlation coefficient)')
    pylab.ylabel('Mean firing rate')
    
    pylab.subplot(1,3,3)
    pylab.title(fstr % (ps[0][2][0],ps[0][2][1],ps[1][2][0],ps[1][2][1],ps[2][2][0],ps[2][2][1]),fontsize=10)
    pylab.plot(corrs[0],srm[0],'ro')
    pylab.plot(corrs[1],srm[1],'go')
    pylab.plot(corrs[2],srm[2],'bo')
    pylab.xlabel('Prediction power (as Correlation coefficient)')
    pylab.ylabel('Reliability')
    
    pylab.figure()
    pylab.subplot(1,3,1)
    pylab.plot(sp[0],numpy.mean(numpy.array(ts[0]),axis=0),'ro')
    pylab.plot(sp[1],numpy.mean(numpy.array(ts[1]),axis=0),'go')
    pylab.plot(sp[2],numpy.mean(numpy.array(ts[2]),axis=0),'bo')
    pylab.xlabel('Sparsness')
    pylab.ylabel('Mean firing rate')


    pylab.subplot(1,3,2)
    pylab.plot(srm[0],numpy.mean(numpy.array(ts[0]),axis=0),'ro')
    pylab.plot(srm[1],numpy.mean(numpy.array(ts[1]),axis=0),'go')
    pylab.plot(srm[2],numpy.mean(numpy.array(ts[2]),axis=0),'bo')
    pylab.xlabel('Reliability')
    pylab.ylabel('Mean firing rate')


    pylab.subplot(1,3,3)
    pylab.plot(sp[0],srm[0],'ro')
    pylab.plot(sp[1],srm[1],'go')
    pylab.plot(sp[2],srm[2],'bo')
    pylab.xlabel('Sparsness')
    pylab.ylabel('Reliability')
    
    from mpl_toolkits.mplot3d import Axes3D
    
    ax = Axes3D(pylab.figure())
    ax.scatter(sp[0],numpy.mean(numpy.array(ts[0]),axis=0),corrs[0],c='r')
    ax.scatter(sp[1],numpy.mean(numpy.array(ts[1]),axis=0),corrs[1],c='g')
    ax.scatter(sp[2],numpy.mean(numpy.array(ts[2]),axis=0),corrs[2],c='b')
    ax.set_xlabel('Sparsness')
    ax.set_ylabel('Mean firing rate')
    ax.set_zlabel('Prediction power (as Correlation coefficient)')



def CorticalGeometry():
    l = loadBestResults()
    globals().update(l)
    
    animal_num = 0
    nli = [[],[],[]]
    print 'NLI:'
    for i in [0,1,2]:
        llc[i][numpy.nonzero(llc[i]<0.0)]=0
        nli[i] = (lc[i]-llc[i])/lc[i]
        #nli[i][numpy.where(lc[i]<0.05)]=-10
        #nli[i][numpy.where((lc[i]<0.05) * (llc[i]>0.1))]=1.0
        nli[i][numpy.where((lc[i]<llc[i]))]=0.0
        print numpy.shape(numpy.where((lc[i]<llc[i])))
        


    locx = [x[0] for x in loc[animal_num]]
    locy = [x[1] for x in loc[animal_num]]

    # lets first normalize each lscsm_hw individually for each neuron
    for hw in lscsm_hw:
        for i in xrange(0,numpy.shape(hw)[1]):
            hw[:,i] = hw[:,i]/numpy.sqrt(numpy.sum(numpy.power(hw[:,i],2)))
    
    
    #lets calculate LGN contributions
    m = max([-numpy.min(lscsm_lgnw[animal_num]),numpy.max(lscsm_lgnw[animal_num])])
    # plot it as is
    pylab.figure()
    pylab.imshow(lscsm_lgnw[animal_num],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
    pylab.title('lgn weights')
    
    lgn_contr = numpy.zeros((numpy.shape(lscsm_lgnw[animal_num])[0],numpy.shape(lscsm_hw[animal_num])[1]))
    pylab.figure()
    for i in xrange(0,numpy.shape(lscsm_lgnw[animal_num])[0]):
        for j in xrange(0,numpy.shape(lscsm_hw[animal_num])[1]):
            ww = 0
            for k in xrange(0,numpy.shape(lscsm_hw[animal_num])[0]):
                ww = ww + numpy.abs(lscsm_lgnw[animal_num][i][k] * lscsm_hw[animal_num][k][j])
            lgn_contr[i][j] = ww
        pylab.subplot(3,3,i+1)                    
        pylab.scatter(locx,locy,c=numpy.array(lgn_contr[i,:]))
        pylab.colorbar()
    
    
    # Correlation between neuron models and activity
    pylab.figure(figsize=(18,7),dpi=200)
    colors = ['red','blue','green']
    labels = ['region 1','region 2' , 'region 3']
    for animal in [0,1,2]:
        lscsm_corr = []
        sta_corr = []
        activity_corr = []
        for i in xrange(0,numpy.shape(lscsm_hw[animal])[1]):
            for j in xrange(0,numpy.shape(lscsm_hw[animal])[1]):
                if i != j:
                    lscsm_corr.append(scipy.stats.pearsonr(lscsm_hw[animal][:,i].flatten(),lscsm_hw[animal][:,j].flatten())[0])
                    sta_corr.append(scipy.stats.pearsonr(rpi[animal][:,i].flatten(),rpi[animal][:,j].flatten())[0])
                    activity_corr.append(scipy.stats.pearsonr(numpy.array(vs[animal])[:,i].flatten(),numpy.array(vs[animal])[:,j].flatten())[0])
                    
        print scipy.stats.pearsonr(lscsm_corr,activity_corr)
        print scipy.stats.pearsonr(sta_corr,activity_corr)
        
        pylab.subplot(1,2,1)           
        pylab.scatter(lscsm_corr,activity_corr, s=2, facecolor = colors[animal],lw = 0)
        pylab.xlabel('LSCSM weight correlation')
        pylab.xlim(-0.5,1.0)
        pylab.ylabel('Activity correlation')
        pylab.hold('on')
         
        pylab.subplot(1,2,2)           
        pylab.scatter(sta_corr,activity_corr, s=2, facecolor = colors[animal], lw = 0,label=labels[animal])
        pylab.xlabel('STA RF correlation')
        pylab.xlim(-0.5,1.0)
        pylab.hold('on')
    
    pylab.savefig('../Doc/Latex/LSCSMFigs/ActivityWeightCorrelations.png')     
    
    # lets plot lscsm_hw
    m = max([-numpy.min(lscsm_hw[animal_num]),numpy.max(lscsm_hw[animal_num])])
    # plot it as is
    pylab.figure()
    pylab.imshow(lscsm_hw[animal_num],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
    pylab.xlabel('no ordering')
    # plot it with neurons sorted by performance (corr)
    idx = numpy.argsort(corrs[animal_num])
    pylab.figure()
    pylab.imshow(lscsm_hw[animal_num][:,idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
    pylab.xlabel('corr ordering')
    # plot it with neurons sorted by performance (fev)
    idx = numpy.argsort(fev[animal_num])
    pylab.figure()
    pylab.imshow(lscsm_hw[animal_num][:,idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
    pylab.xlabel('fev')
    # plot it with neurons sorted by performance (NLI)
    idx = numpy.argsort(nli[animal_num])
    pylab.figure()
    pylab.imshow(lscsm_hw[animal_num][:,idx],vmin=-m,vmax=m,interpolation='nearest',cmap=pylab.cm.RdBu_r)
    pylab.xlabel('nli')
    
    #compute sparseness of inter-layer connections 
    trs = scipy.stats.kurtosis(lscsm_hw[animal_num],axis=0)
    
    # hidden neurons are either excitatory or inhibitory    
    b = lscsm_hw[animal_num].copy()
    for i,z in enumerate(lscsm_hw[animal_num]):
        if numpy.mean(z)<0:
            b[i,:] = -z
        else:
            b[i,:] = z

    pylab.figure()
    pylab.hist(b.ravel(),bins=30)
    pylab.xlabel('mean sign corrected weight distribution')

    
    if True:
        import pickle
        f = open('2009_11_04_region3_LSCSM_STA.pickle','rb')
        rfs = pickle.load(f)
        
        import visualization
        n,size,i = numpy.shape(rfs)
        rfs = numpy.reshape(numpy.array(rfs),(-1,numpy.sqrt(size),numpy.sqrt(size)))
        visualization.showRFSinCorticalSpace(rfs,loc[animal_num],joinnormalize=False,scatter_value=nli[animal_num],scatter_value_cmap=pylab.cm.winter,colorbar=True)
        pylab.savefig('../Doc/Latex/LSCSMFigs/RFdistribution.png')
    
    # compute distances
    dist = [[],[],[]]
    hlw_corr = [[],[],[]]
    nli_diff = [[],[],[]]
    lscsm_pp = [[],[],[]]
    
    for an in [0,1,2]:
        for i in xrange(0,len(loc[an])):
            for j in xrange(0,len(loc[an])):
                  if i!=j and nli[animal_num][i]!=-10 and nli[animal_num][j]!=-10:
                    x = loc[an][i][0] - loc[an][j][0]
                    y = loc[an][i][1] - loc[an][j][1]
                    dist[an].append(numpy.sqrt(x*x+y*y))
                    hlw_corr[an].append(scipy.stats.pearsonr(lscsm_hw[an][:,i].ravel(),lscsm_hw[an][:,j].ravel())[0])
                    nli_diff[an].append(numpy.abs(nli[an][i]-nli[an][j]))
                    lscsm_pp[an].append(numpy.abs(lc[an][i]-lc[an][j]))
    
    
    print numpy.shape(dist[0])
    print numpy.shape(hlw_corr[0])
    print scipy.stats.pearsonr(dist[0],hlw_corr[0])
    print scipy.stats.pearsonr(dist[0],nli_diff[0])
    print scipy.stats.pearsonr(dist[1],hlw_corr[1])
    print scipy.stats.pearsonr(dist[1],nli_diff[1])
    print scipy.stats.pearsonr(dist[2],hlw_corr[2])
    print scipy.stats.pearsonr(dist[2],nli_diff[2])
    
    
    pylab.figure()
    pylab.hist(hlw_corr)
    pylab.xlabel('Hidden weight layer correlations')
    
    import matplotlib.gridspec as gridspec
    f = pylab.figure(dpi=100,facecolor='w',figsize=(11,10))
    gs = gridspec.GridSpec(2, 24)
    gs.update(left=0.1, right=0.9, top=0.9, bottom=0.1)
    

    pylab.subplot(gs[0,0:10])
    pylab.scatter(locx,locy,c=nli[animal_num],vmax=1, s=40, cmap=pylab.cm.gray_r)
    pylab.xticks([])
    pylab.yticks([])
    pylab.xlim(0,250)
    pylab.ylim(0,250)
    pylab.title('Non-linearity index')
    
    pylab.subplot(gs[0,12:22])
    z = pylab.scatter(locx,locy,c=lc[animal_num], vmax=1, s=40, cmap=pylab.cm.gray_r)
    pylab.xlim(0,250)
    pylab.ylim(0,250)
    pylab.xticks([])
    pylab.yticks([])
    pylab.title('LSCSM prediction power')
    
    ax = pylab.subplot(gs[0,22])
    pylab.colorbar(z,cax=ax)
    
    pylab.subplot(gs[1,0:10])
    pylab.scatter(dist[0],nli_diff[0], s=2, facecolor = colors[0],lw = 0)
    pylab.hold('on')
    pylab.scatter(dist[1],nli_diff[1], s=2, facecolor = colors[1],lw = 0)
    pylab.hold('on')
    pylab.scatter(dist[2],nli_diff[2], s=2, facecolor = colors[2],lw = 0)
    pylab.xlabel('Cortical distance')
    pylab.ylabel('NLI index difference')
    pylab.xlim(0,300)
    pylab.ylim(0,1.0)
    pylab.hold('on')
    

    pylab.subplot(gs[1,12:22])
    pylab.scatter(dist[0],lscsm_pp[0], s=2, facecolor = colors[0],lw = 0)
    pylab.hold('on')
    pylab.scatter(dist[1],lscsm_pp[1], s=2, facecolor = colors[1],lw = 0)
    pylab.hold('on')
    pylab.scatter(dist[2],lscsm_pp[2], s=2, facecolor = colors[2],lw = 0)
    pylab.xlabel('Cortical distance')
    pylab.ylabel('LSCSM prediction power difference')
    pylab.xlim(0,300)
    pylab.ylim(0,1.0)
    pylab.savefig('../Doc/Latex/LSCSMFigs/cortical-distributions.png')
    

    
    pylab.figure()
    pylab.plot(dist[animal_num],hlw_corr[animal_num],'ro')
    pylab.xlabel('Cortical distance')
    pylab.ylabel('Hidden layer correlation')
    
    
    pylab.figure()
    pylab.plot(dist[animal_num],nli_diff[animal_num],'ro')
    pylab.xlabel('Cortical distance')
    pylab.ylabel('NLI difference')
    

    pylab.figure()
    pylab.scatter(locx,locy,c=nli[animal_num],vmax=1)
    pylab.colorbar()
    pylab.title('NLI')
    
    pylab.figure()
    pylab.scatter(locx,locy,c=lc[animal_num])
    pylab.colorbar()
    pylab.title('LC')
    
    pylab.figure()
    pylab.scatter(locx,locy,c=llc[animal_num])
    pylab.colorbar()
    pylab.title('LLC')


    pylab.figure()
    pylab.hist(nli[animal_num],bins=20)
    pylab.xlabel('NLI')

    pylab.figure()
    pylab.plot(llc[animal_num],nli[animal_num],'ro')
    pylab.xlabel('Linear corr')
    pylab.ylabel('NLI')
    
    pylab.figure()
    pylab.subplot(1,2,1)           
    pylab.plot(numpy.mean(numpy.array(ts[animal_num]),axis=0),nli[animal_num],'bo')
    pylab.xlabel('Mean firing rate')
    pylab.ylabel('NLI')
    pylab.subplot(1,2,2)           
    pylab.plot(numpy.mean(numpy.array(ts[animal_num]),axis=0),lc[animal_num],'bo')
    pylab.xlabel('Mean firing rate')
    pylab.ylabel('LSCSM prediction power')

    

    pylab.figure()
    pylab.plot(nli[animal_num],trs,'bo')
    pylab.xlabel('NLI')
    pylab.ylabel('sparsness')
    

    


def TrevesRollsSparsness(mat):
    # Computes Trevers Rolls Sparsness of data along columns
    x,y  = numpy.shape(mat)
    trs = numpy.array(1-(numpy.power(numpy.mean(mat,axis=0),2))/(numpy.mean(numpy.power(mat,2),axis=0)+0.0000000000000000000001))[0]/(1.0 - 1.0/x)
    return trs * (trs<=1.0)

def L2norm(a):
    return numpy.sqrt(numpy.vdot(a,a))

def normalize_L2(a):
    return a / L2norm(a)

def _SejnowskiReliabilityMeasure(mat):
    (num_trials,num_pres) = numpy.shape(mat)
    count = 0
    s = 0
    for i in xrange(0,num_trials):
        for j in xrange(i+1,num_trials):
            if numpy.mean(mat[i,:]) != 0 and numpy.mean(mat[j,:]) != 0:
                s =  s + (numpy.vdot(mat[i,:],mat[j,:])/ ( L2norm(mat[i,:]) + L2norm(mat[j,:]))) 
                count = count + 1
                
    return s/count
    
def SejnowskiReliabilityMeasure(mat):
    (num_trials,num_pres,num_neurons) = numpy.shape(mat)
    a = []
    for i in xrange(0,num_neurons):
        a.append(_SejnowskiReliabilityMeasure(mat[:,:,i]))
    
    return numpy.array(a)
    
    
    
    
    
    
    
