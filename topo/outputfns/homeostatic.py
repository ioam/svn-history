"""
Homeostatic output functions, which are designed to keep an activity
value in a desired range over time.

Originally implemented by Veldri Kurniawan, 2006.

$Id$
"""
__version__='$Revision$'

import copy
import topo
from numpy import exp,zeros,ones

from topo.base.arrayutils import clip_in_place
from topo.base.functionfamilies import OutputFn, OutputFnParameter, IdentityOF
from topo.base.parameterclasses import Number, BooleanParameter, ListParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import activity_type
from topo.commands.pylabplots import vectorplot
from topo.misc.filepaths import normalize_path

class HomeostaticMaxEnt(OutputFn):
    """
    Implementation of homeostatic intrinsic plasticity from Jochen Triesch,
    ICANN 2005, LNCS 3696 pp.65-70.
    
    A sigmoid activation function is adapted automatically to achieve
    desired average firing rate and approximately exponential
    distribution of firing rates (for the maximum possible entropy).
    
    Note that this OutputFn has state, so the history of calls to it
    will affect future behavior.
    
    Also calculates average activity as useful debugging information,
    for use with OutputFnDebugger.  Average activity is calculated as
    an exponential moving average with a smoothing factor (smoothing).
    For more information see:
    NIST/SEMATECH e-Handbook of Statistical Methods, Single Exponential Smoothing
    http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc431.htm
    """

    learning = BooleanParameter(True,doc="""
        If False, disables the dynamic adjustment of threshold levels.""")
    
    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    
    eta = Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    
    mu = Number(default=0.01,doc="Target average firing rate.")
    
    smoothing = Number(default=0.0003, doc="""
        Determines the degree of weighting of current activity vs.
        previous activity when calculating the average.""")

    def __init__(self,**params):
        super(HomeostaticMaxEnt,self).__init__(**params)
	self.first_call = True

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = ones(x.shape, x.dtype.char) * self.a_init
	    self.b = ones(x.shape, x.dtype.char) * self.b_init
	    self.y_avg = zeros(x.shape, x.dtype.char) 

	# Apply sigmoid function to x, resulting in what Triesch calls y
        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))

        if self.learning:

            self.y_avg = self.smoothing*x + (1.0-self.smoothing)*self.y_avg #Calculate average for use in debugging only

            # Update a and b
            self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
            self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)



class AdaptingHomeostaticMaxEnt(OutputFn):
    """
    Similar to HomeoMaxEnt, except that the learning rate (eta) also
    changes depending on the current average activity.
    
    The average activity is calculated as an exponential moving
    average with a smoothing factor (smoothing).  For more information
    see the NIST/SEMATECH e-Handbook of Statistical Methods: Single
    Exponential Smoothing
    http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc431.htm
    """
    
    learning = BooleanParameter(True,doc="""
      If False, disables the dynamic adjustment of threshold levels.""")
    
    lstep = Number(default=8,doc="How often to update learning rate")
    
    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    
    eta_init = Number(default=0.0002,doc="Initial learning rate for homeostatic plasticity.")
    
    mu = Number(default=0.01,doc="Target average firing rate.")
    
    rate_factor = Number(default=0.1, doc="""
        Factor determining gradient of linear transformation between
        average firing rate and learning rate.""")
    
    smoothing = Number(default=0.0003, doc="""
        Determines the degree of weighting of current activity vs.
        previous activity when calculating the average.""")

    def __init__(self,**params):
        super(AdaptingHomeostaticMaxEnt,self).__init__(**params)
	self.first_call = True
	self.n_step = 0

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = ones(x.shape, x.dtype.char) * self.a_init
	    self.b = ones(x.shape, x.dtype.char) * self.b_init
            self.eta = ones(x.shape, x.dtype.char) * self.eta_init
            self.y_avg = zeros(x.shape, x.dtype.char)
	   
	# Apply sigmoid function to x, resulting in what Triesch calls y
        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))
        	        
        if self.learning:
            self.n_step += 1
            if self.n_step == self.lstep:
                self.n_step = 0
                self.y_avg = self.smoothing*x + (1.0-self.smoothing)*self.y_avg #Calculate the average
                
                # Update eta
                self.eta = self.rate_factor * self.y_avg #high avg_rate = high eta


            self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
            self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)




class OutputFnDebugger(OutputFn):
    """
    Collates information for debugging as specifed by the
    parameter_list. Should be called as eg.::
    
      HE = HomeostaticMaxEnt(a_init=14.5, b_init=-4, eta=0.0002, mu=0.01)
      ODH=OutputFnDebugger(function=HE, debug_params=['a', 'b'], avg_params=['x'], units=[(0,0),(11,11)])
      topo.sim['V1'].output_fn=Pipeline(output_fns=[HE, ODH])
    """
    
    function = OutputFnParameter(default=None, doc="""
        Output function whose parameters will be tracked.""")
    
    debug_params = ListParameter(default=[], doc="""
        List of names of the function object's parameters that should be stored.""")
    
    avg_params = ListParameter(default=['x'], doc="""
        List of names of the function object's parameters that should be averaged and stored.
        The name 'x' is a special case, referring to the values of the
        matrix supplied to the OutputFnDebugger on each call.""")
    
    units= ListParameter(default=[(0,0)], doc="""
        Matrix coordinates of the unit(s) for which parameter values will be stored.""")
    
    step=Number(default=1, doc="How often to update debugging information and calculate averages.")

    smoothing = Number(default=0.0003, doc="""
        The relative weighting of current and previous values when calculating the average.
        The average is then an exponentially smoothed version of the
        value, using this value as the time constant.""")

    
    def __init__(self,**params):
        super(OutputFnDebugger,self).__init__(**params)
        self.values={}
        self.n_step = 0
        self.first_call=True
        
        param_names=self.debug_params + [p+"_avg" for p in self.avg_params]
        for p in param_names:
            self.values[p]={}
            for u in self.units:
                self.values[p][self.units.index(u)]=[]
    
        
    def __call__(self,x):
        if self.first_call:
            self.first_call=False
            self.avg_values={}
            for p in self.avg_params:
                self.avg_values[p]=zeros(x.shape,activity_type)

        # Collect values on each appropriate step
        self.n_step += 1
        if self.n_step == self.step:
            self.n_step = 0
            
            for p in self.debug_params+self.avg_params:
                for u in self.units:
                    if p=="x":
                        value_matrix=x
                    else:
                        value_matrix=getattr(self.function,p)
                        
                    if p in self.avg_params:
                        self.avg_values[p] = self.smoothing*value_matrix + (1.0-self.smoothing)*self.avg_values[p]
                        self.values[p+"_avg"][self.units.index(u)].append((topo.sim.time(),self.avg_values[p][u]))
                    else:
                        self.values[p][self.units.index(u)].append((topo.sim.time(),value_matrix[u]))

          

