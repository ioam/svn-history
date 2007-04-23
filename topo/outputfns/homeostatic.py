"""
Homeostatic output functions, which are designed to keep an activity
value in a desired range over time.

Originally implemented by Veldri Kurniawan, 2006.
"""

import numpy.oldnumeric as Numeric
import copy
import topo

from numpy.oldnumeric import exp,zeros,ones

from topo.base.arrayutils import clip_in_place
from topo.base.functionfamilies import OutputFn, OutputFnParameter, IdentityOF
from topo.base.parameterclasses import Number, BooleanParameter, ListParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import activity_type
from topo.commands.pylabplots import vectorplot
import matplotlib
import pylab

class HomeostaticMaxEnt(OutputFn):
    """
    Implementation of homeostatic intrinsic plasticity from Jochen Triesch,
    ICANN 2005, LNCS 3696 pp.65-70.
    
    A sigmoid activation function is adapted automatically to achieve
    desired average firing rate and approximately exponential
    distribution of firing rates (for the maximum possible entropy).
    
    Note that this OutputFn has state, so the history of calls to it
    will affect future behavior.
    Also calculates average activity as useful debugging information.
    (For use with OutputFnDebugger).Average activity is calculated as
    an exponential moving average with a smoothing factor (smoothing) which
    is calculated from the number of time periods (ie. the total duration
    of the simulation)
    NIST/SEMATECH e-Handbook of Statistical Methods:
    Single Exponential Smoothing at the National Institute of Standards and Technology
    http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc431.htm
    """

    learning = BooleanParameter(True,doc="""
      If False, disables the dynamic adjustment of threshold levels.""")
    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta = Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    mu = Number(default=0.01,doc="Target average firing rate.")
    duration=Number(default=10000, doc="Total duration of the simulation")
    smoothing = Number(default=0.0003, doc="Determines the degree of weighting of current activity vs previous activity when calculating average")

    def __init__(self,**params):
        super(HomeostaticMaxEnt,self).__init__(**params)

	self.first_call = True

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = Numeric.ones(x.shape, x.dtype.char) * self.a_init
	    self.b = Numeric.ones(x.shape, x.dtype.char) * self.b_init
	    self.y_avg =Numeric.zeros(x.shape, x.dtype.char) 

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
    Similar to HomeoMaxEnt except the learning rate (eta) also changes depending on the current
    average activity.
    Average activity is calculated as an exponential moving average with a smoothing factor (smoothing) which
    is calculated from the number of time periods (ie. the total duration
    of the simulation)
    See NIST/SEMATECH e-Handbook of Statistical Methods:
    Single Exponential Smoothing at the National Institute of Standards and Technology
    http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc431.htm
    """
    learning = BooleanParameter(True,doc="""
      If False, disables the dynamic adjustment of threshold levels.""")
    lstep = Number(default=8,doc="How often to update learning rate")
    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.") 
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta_init = Number(default=0.0002,doc="Initial learning rate for homeostatic plasticity.")
    mu = Number(default=0.01,doc="Target average firing rate.")
    rate_factor = Number(default=0.1, doc="Factor determining gradient of linear transformation between average firing rate and learning rate")
    smoothing = Number(default=0.0003, doc="Determines the degree of weighting of current activity vs previous activity when calculating average")

    def __init__(self,**params):
        super(AdaptingHomeostaticMaxEnt,self).__init__(**params)

	self.first_call = True

	self.n_step = 0

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = Numeric.ones(x.shape, x.dtype.char) * self.a_init
	    self.b = Numeric.ones(x.shape, x.dtype.char) * self.b_init
            self.eta = Numeric.ones(x.shape, x.dtype.char) * self.eta_init
            self.y_avg =Numeric.zeros(x.shape, x.dtype.char)
	   
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


class PiecewiseLinear_debug(OutputFn):
    """
    Same as PiecewiseLinear, but computes average activities for use
    in validating homeostatic plasticity mechanisms.
    Also calculates average activity as useful debugging information.
    (For use with OutputFnDebugger)
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    smoothing = Number(default=0.0003, doc="Determines the degree of weighting of current activity vs previous activity when calculating average")

    def __init__(self,**params):
        super(PiecewiseLinear_debug,self).__init__(**params)

	self.first_call = True
	self.n_step = 0

    def __call__(self,x):

        x_orig = copy.copy(x)
        fact = 1.0/(self.upper_bound-self.lower_bound)
        x -= self.lower_bound
        x *= fact
        clip_in_place(x,0.0,1.0)

	if self.first_call:
	    self.first_call = False
	    self.y_avg = zeros(x.shape,x.dtype.char)

	self.n_step += 1
	if self.n_step == self.lstep:

	    self.n_step = 0
	    	
            self.y_avg = self.smoothing*x + (1.0-self.smoothing)*self.y_avg


class OutputFnDebugger(OutputFn):
    """
    Collates information for debugging as specifed by parameter_list. Should be called as eg.:
    HE = HomeostaticMaxEnt(a_init=14.5, b_init=-4, eta=0.0002, mu=0.01)
    ODH=OutputFnDebugger(function=HE, debug_params=['a', 'b'], units=[(0,0),(11,11)])
    topo.sim['V1'].output_fn=Pipeline(output_fns=[HE, ODH])
    """
    function = OutputFnParameter(default=IdentityOF(), doc="Output function whose parameters are stored")
    debug_params = ListParameter(default=[], doc="List of parameters which should be stored",  )
    units= ListParameter(default=[], doc="Units for which parameters are stored")
    step=Number(default=8, doc="When to update debugging information") 
       
    def __init__(self,**params):
        super(OutputFnDebugger,self).__init__(**params)
        self.debug_dict={}
        self.n_step = 0
        for dp in self.debug_params:
            self.debug_dict[dp]= zeros([len(self.units),30000],activity_type)
        
    def __call__(self,x):
        self.n_step += 1
        if self.n_step == self.step:
            self.n_step = 0
            for dp in self.debug_params:
                for u in self.units:
                    value_matrix= getattr(self.function, dp)
                    value=value_matrix[u]
                    self.debug_dict[dp][self.units.index(u)][topo.sim.time()]=value
                   
     
    def plot_debug_graphs(self,debug_params, unit_list, init_time, final_time):
        """
        Plots all parameters as stored over time by the OutputFnDebugger
        called as e.g.:
        OutputFnDebugger.plot_debug_graphs(Function,['a', 'b', 'y_avg', 'eta'],[(0,0),(11,11)],1,10000)
        or
        OutputFnDebugger.plot_debug_graphs(Function,Function.debug_params,Function.units,1,10000) if you want to plot
        graphs of all the stored values for all the units.
        Where Function is the instance of the OutputFnDebugger as specified in the script
        """
   
        for db in debug_params:
            pylab.figure()
            isint=pylab.isinteractive()
            pylab.ioff()
            manager = pylab.get_current_fig_manager()
            pylab.ylabel(db)
            pylab.xlabel('Time')
            manager.window.title(topo.sim.name+': '+db)
            for unit in unit_list:
                index=self.units.index(unit)
                plot_data=self.debug_dict[db][index][init_time:final_time]
                vectorplot(plot_data, label='Unit'+str(unit))
            if isint: pylab.ion()
            pylab.legend(loc=0)
            pylab.show._needmain = False 
            pylab.show()
                       


