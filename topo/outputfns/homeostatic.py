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
    for use with ValueTrackingOutoutFn  Average activity is calculated as
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




class ValueTrackingOutputFn(OutputFn):
    """
    Output function which keeps track of individual parameters (debug_params) over time
    for specified units. If no function is specified will just keep track of activity over time.
    Values are stored in the values dictionary as (time, value) pairs indexed by the parameter name
    and the unit index in a given list of units. 
    """
    
    function = OutputFnParameter(default=None, doc="""
        Output function whose parameters will be tracked.""")
    
    debug_params = ListParameter(default=[], doc="""
        List of names of the function object's parameters that should be stored.""")
    
    units= ListParameter(default=[(0,0)], doc="""
        Matrix coordinates of the unit(s) for which parameter values will be stored.""")
    
    step=Number(default=1, doc="How often to update parameter information")

    
    def __init__(self,**params):
        super(ValueTrackingOutputFn,self).__init__(**params)
        self.values={}
        self.n_step = 0
        for dp in self.debug_params:
            self.values[dp]={}
            for u in self.units:
                self.values[dp][self.units.index(u)]=[]
         
        
    def __call__(self,x):

        #collect values on each appropriate step
        self.n_step += 1
        
        if self.n_step == self.step:
            self.n_step = 0
            for p in self.debug_params:
                for u in self.units:
                    if p=="x":
                        value_matrix=x
                    else:
                        value_matrix= getattr(self.function, p)

                    self.values[p][self.units.index(u)].append((topo.sim.time(),value_matrix[u]))

          

class AvgScalingOutputFn(OutputFn):
    """
    Calculates average activity and a scaling factor based on this average activity which
    can be used to scale activity in order to bring it closer to the target value. 
    """
    step=Number(default=1, doc="How often to calculate average activity")
    
    smoothing = Number(default=0.0003, doc="""
    The relative weighting of current and previous values when calculating the average.
    The average is then an exponentially smoothed version of the
    value, using this value as the time constant.""")

    target = Number(default=0.1, doc="""
    The target value for the average activity , used to calculate the scaling_factor """)

    
    def __init__(self,**params):
        super(AvgScalingOutputFn,self).__init__(**params)
        self.n_step = 0
        self.first_call = True
           
        
    def __call__(self,x):
        if self.first_call:
	    self.first_call = False
            self.x_avg=zeros(x.shape, activity_type)         

        # Collect values on each appropriate step
        self.n_step += 1
        if self.n_step == self.step:
            self.n_step = 0
            self.x_avg = self.smoothing*x + (1.0-self.smoothing)*self.x_avg


    def get_scaling_factor(self):
        """
        Method for calculating the scaling factor, in this case the average activity is
        used to calculate a factor which is greater than 1 if the average activity is less
        than the target and less than 1 if the average activity is greater than the target.
        Can be overwritten by subclasses to calculate a different scaling factor.
        """
          
        self.scaling_factor = self.target/self.x_avg
        return self.scaling_factor
        
