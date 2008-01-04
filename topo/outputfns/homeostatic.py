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
from topo.base.parameterclasses import Number, BooleanParameter, ListParameter, StringParameter
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

    updating = BooleanParameter(True,doc="""
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
        self._updating_state = []

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

        if self.updating:

            self.y_avg = self.smoothing*x + (1.0-self.smoothing)*self.y_avg #Calculate average for use in debugging only

            # Update a and b
            self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
            self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)

    def stop_updating(self):
        """
        Save the current state of the adapting parameter to an internal stack. 
        Turn updating off for the output_fn.
        """

        self._updating_state.append(self.updating)
        self.updating=False


    def restore_updating(self):
        """Pop the most recently saved adapting parameter off the stack"""

        self.updating = self._updating_state.pop()                        
          


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
    
    updating = BooleanParameter(True,doc="""
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
        self._updating_state = []

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
        	        
        if self.updating:
            self.n_step += 1
            if self.n_step == self.lstep:
                self.n_step = 0
                self.y_avg = self.smoothing*x + (1.0-self.smoothing)*self.y_avg #Calculate the average
                
                # Update eta
                self.eta = self.rate_factor * self.y_avg #high avg_rate = high eta


            self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
            self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)

    def stop_updating(self):
        """
        Save the current state of the updating parameter to an internal stack. 
        Turn updating off for the output_fn.
        """

        self._updating_state.append(self.updating)
        self.updating=False


    def restore_updating(self):
        """Pop the most recently saved updating parameter off the stack"""

        self.updating = self._updating_state.pop()                        
          


class ScalingOF(OutputFn):
    """
    Scales input activity based on the current average activity (x_avg).
    The scaling is calculated to bring x_avg for each unit closer to a
    specified target average.  Calculates a scaling factor that is
    greater than 1 if x_avg is less than the target and less than 1 if
    x_avg is greater than the target, and multiplies the input
    activity by this scaling factor.
    """
    
    target = Number(default=0.01, doc="""
        Target average activity for each unit.""")

    step=Number(default=1, doc="""
        How often to calculate the average activity and scaling factor.""")
    
    smoothing = Number(default=0.0003, doc="""
        The degree of weighting decrease for older values when calculating the average.""")

    updating = BooleanParameter(default=True, doc="""
        Whether or not to update the average.
        Allows averaging to be turned off, e.g. during map measurement.""")

    
    def __init__(self,**params):
        super(ScalingOF,self).__init__(**params)
        self.n_step = 0
        self.x_avg=None
        self.sf=None
        self._updating_state = []

    def __call__(self,x):
    
        if self.x_avg is None:
            self.x_avg=self.target*ones(x.shape, activity_type)         
        if self.sf is None:
            self.sf=ones(x.shape, activity_type)

        # Collect values on each appropriate step
        self.n_step += 1
        if self.n_step == self.step:
            self.n_step = 0
            if self.updating:
                self.sf *= 0.0
                self.sf += self.target/self.x_avg # Calculate scaling factor based on old average
                self.x_avg = self.smoothing*x + (1.0-self.smoothing)*self.x_avg
               

        x *= self.sf
              

    def stop_updating(self):
        """
        Save the current state of the updating parameter to an internal stack. 
        Turns updating off for the output_fn.
        """
        self._updating_state.append(self.updating)
        self.updating=False


    def restore_updating(self):
        """Pop the most recently saved updating parameter off the stack."""
        self.updating = self._updating_state.pop() 

        

class JointScalingOF(OutputFn):
    """
    Scales input activity of two or more projections based on the current average total activity.

    Total input activity is scaled based on the current average
    activity of all specified projections (x_avg) in order to bring
    x_avg for each unit closer to a specified target average.
    Calculates a scaling factor that is greater than 1 if x_avg is
    less than the target and less than 1 if x_avg is greater than the
    target, and multiplies the input activity by this scaling
    factor. The new scaled total activity is then divided equally
    amongst the jointly scaled projections.
    """
    
    target = Number(default=0.01, doc="""
        Target average activity for each unit.""")

    step=Number(default=1, doc="""
        How often to calculate average activity and scale the input activity.""")
    
    smoothing = Number(default=0.0003, doc="""
        The degree of weighting decrease for older values when calculating the average.""")

    updating = BooleanParameter(default=True, doc="""
        Whether or not to update average.
        Allows averaging to be turned off, e.g. during map measurement.""")

    joint_projections = ListParameter(default=[], doc="""
        Names of the projections to be jointly scaled with the current projection.""")

    sheet = StringParameter(default=None)
    
    def __init__(self,**params):
        super(JointScalingOF,self).__init__(**params)
        self.n_step = 0
        self.x_avg=None
        self.sf=None
        self.scaled_x_avg=None
        self._updating_state = []
        
    def __call__(self,x):
    
        if self.x_avg is None:
            self.x_avg=self.target*ones(x.shape, activity_type)         
        if self.sf is None:
            self.sf=ones(x.shape, activity_type)

        total_x = copy.copy(x)
      
        for each in self.joint_projections:
            proj = topo.sim[self.sheet].projections()[each]
            total_x += proj.activity 

       
        # Collect values on each appropriate step
        self.n_step += 1
        if self.n_step == self.step:
            self.n_step = 0
            if self.updating:
                self.sf *= 0.0
                self.sf += self.target/self.x_avg #Calculate scaling factor based on old average
                self.x_avg = self.smoothing*total_x + (1.0-self.smoothing)*self.x_avg

        x *= self.sf
        
    def stop_updating(self):
        """
        Save the current state of the updating parameter to an internal stack. 
        Turns updating off for the output_fn.
        """
        self._updating_state.append(self.updating)
        self.updating=False


    def restore_updating(self):
        """Pop the most recently saved updating parameter off the stack."""
        self.updating = self._updating_state.pop() 


__all__ = list(set([k for k,v in locals().items() if isinstance(v,type) and issubclass(v,OutputFn)]))

