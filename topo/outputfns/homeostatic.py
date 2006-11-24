"""
Homeostatic output functions, which are designed to keep an activity
value in a desired range over time.

Originally implemented by Veldri Kurniawan, 2006.
"""

import Numeric
import copy

from Numeric import exp,zeros,ones

from topo.base.arrayutils import clip_in_place
from topo.base.functionfamilies import OutputFn
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import activity_type

class HomeostaticMaxEnt(OutputFn):
    """
    Implementation of homeostatic intrinsic plasticity from Jochen Triesch,
    ICANN 2005, LNCS 3696 pp.65-70.

    A sigmoid activation function is adapted automatically to achieve
    desired average firing rate and approximately exponential
    distribution of firing rates (for the maximum possible entropy).

    Note that this OutputFn has state, so the history of calls to it
    will affect future behavior.
    """

    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta = Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    mu = Number(default=0.01,doc="Target average firing rate.")


    def __init__(self,**params):
        super(HomeostaticMaxEnt,self).__init__(**params)

	self.first_call = True

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = Numeric.ones(x.shape, x.typecode()) * self.a_init
	    self.b = Numeric.ones(x.shape, x.typecode()) * self.b_init

	# Apply sigmoid function to x, resulting in what Triesch calls y
        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))

	# Update a and b
	self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
	self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)


class HomeostaticMaxEnt_debug(OutputFn):
    """
    Intended to be the same as HomeostaticMaxEnt, but also prints useful debugging
    information.
    """

    lstep = Number(default=8,doc="How often to print debugging information.")
    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta = Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    mu = Number(default=0.01,doc="Target average firing rate.")

    def __init__(self,**params):
        super(HomeostaticMaxEnt_debug,self).__init__(**params)

	self.first_call = True

	# DEBUG only (not required for the algorithm)
	self.y_avg_count = 0 
	self.n_step = 0
	self.beta = 0.0003
	self.ncall = 0

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = Numeric.ones(x.shape, x.typecode()) * self.a_init
	    self.b = Numeric.ones(x.shape, x.typecode()) * self.b_init

            # DEBUG only (only required for computing average
            # activity of each neuron over time)
	    self.y_avg = zeros(x.shape,x.typecode())
	    self.y_hist = zeros([5,30000],activity_type)  # average firing rate
	    self.y_rate = zeros([5,30000],activity_type)  # firing rate over time
	    self.x_rate = zeros([5,30000],activity_type)  # input to postsynaptic neurons, before thresholding
	    self.ab_hist = zeros([2,5,30000],activity_type) # History of a and b

	# Apply sigmoid function to x, resulting in what Triesch calls y
        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))

        # DEBUG only (only required for computing average
        # activity of each neuron over time)
	self.n_step += 1	
	if self.n_step == self.lstep:
	    self.n_step = 0
	
	    self.ncall += 1
	    if self.ncall <= 500:
	        self.y_avg = ((self.y_avg*self.ncall) + x) / (self.ncall+1)
	    else:
	        self.y_avg = self.beta*x + (1.0-self.beta)*self.y_avg

	    # Average firing rate
	    self.y_hist[0][self.ncall] = self.y_avg[0][0]
	    self.y_hist[1][self.ncall] = self.y_avg[11][11]
	    self.y_hist[2][self.ncall] = self.y_avg[23][23]
	    self.y_hist[3][self.ncall] = self.y_avg[35][35]
	    self.y_hist[4][self.ncall] = self.y_avg[47][47]

	    # firing rate over time
	    self.y_rate[0][self.ncall] = x[0][0]
	    self.y_rate[1][self.ncall] = x[11][11]
	    self.y_rate[2][self.ncall] = x[23][23]
	    self.y_rate[3][self.ncall] = x[35][35]
	    self.y_rate[4][self.ncall] = x[47][47]

	    # input to postsynaptic neurons, before thresholding
	    self.x_rate[0][self.ncall] = x_orig[0][0]
	    self.x_rate[1][self.ncall] = x_orig[11][11]
	    self.x_rate[2][self.ncall] = x_orig[23][23]
	    self.x_rate[3][self.ncall] = x_orig[35][35]
	    self.x_rate[4][self.ncall] = x_orig[47][47]

	    # a & b
	    self.ab_hist[0][0][self.ncall] = self.a[0][0]
	    self.ab_hist[0][1][self.ncall] = self.a[11][11]
	    self.ab_hist[0][2][self.ncall] = self.a[23][23]
	    self.ab_hist[0][3][self.ncall] = self.a[35][35]
	    self.ab_hist[0][4][self.ncall] = self.a[47][47]

	    self.ab_hist[1][0][self.ncall] = self.b[0][0]
	    self.ab_hist[1][1][self.ncall] = self.b[11][11]
	    self.ab_hist[1][2][self.ncall] = self.b[23][23]
	    self.ab_hist[1][3][self.ncall] = self.b[35][35]
	    self.ab_hist[1][4][self.ncall] = self.b[47][47]
   
	    print self.y_avg[23][23], ' - ', self.y_avg[11][11], ' - ', self.y_avg[0][0], ' - ', self.y_avg[47][47]
	    print self.a[23][23], ',', self.b[23][23] , ' : ', self.a[11][11], ',', self.b[11][11]

	# Update a and b
	self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
	self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)


class PiecewiseLinear_debug(OutputFn):
    """
    Same as PiecewiseLinear, but computes average activities for use
    in validating homeostatic plasticity mechanisms.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    lstep = Number(default=8,doc="How often to print debugging information.")

    def __init__(self,**params):
        super(PiecewiseLinear_debug,self).__init__(**params)

	self.first_call = True
	self.n_step = 0
	self.beta = 0.0003
	self.ncall = 0

    def __call__(self,x):

        x_orig = copy.copy(x)
        fact = 1.0/(self.upper_bound-self.lower_bound)
        x -= self.lower_bound
        x *= fact
        clip_in_place(x,0.0,1.0)

	if self.first_call:
	    self.first_call = False
	    self.y_avg = zeros(x.shape,x.typecode())
	    self.y_hist = zeros([5,30000],activity_type)  # average firing rate
	    self.y_rate = zeros([5,30000],activity_type)  # firing rate over time
	    self.y_rate = zeros([5,30000],activity_type)  # firing rate over time
	    self.x_rate = zeros([5,30000],activity_type)  # input to postsynaptic neurons, before thresholding

	self.n_step += 1
	if self.n_step == self.lstep:

	    self.n_step = 0
	    	
	    self.ncall += 1
	    if self.ncall <= 500:
	    	self.y_avg = ((self.y_avg*self.ncall) + x) / (self.ncall+1)
	    else:	    
	    	self.y_avg = self.beta*x + (1.0-self.beta)*self.y_avg

	    # Average firing rate
	    self.y_hist[0][self.ncall] = self.y_avg[0][0]
	    self.y_hist[1][self.ncall] = self.y_avg[11][11]
	    self.y_hist[2][self.ncall] = self.y_avg[23][23]
	    self.y_hist[3][self.ncall] = self.y_avg[35][35]
	    self.y_hist[4][self.ncall] = self.y_avg[47][47]

	    # firing rate over time
	    self.y_rate[0][self.ncall] = x[0][0]
	    self.y_rate[1][self.ncall] = x[11][11]
	    self.y_rate[2][self.ncall] = x[23][23]
	    self.y_rate[3][self.ncall] = x[35][35]
	    self.y_rate[4][self.ncall] = x[47][47]

	    # input to postsynaptic neurons, before thresholding
	    self.x_rate[0][self.ncall] = x_orig[0][0]
	    self.x_rate[1][self.ncall] = x_orig[11][11]
	    self.x_rate[2][self.ncall] = x_orig[23][23]
	    self.x_rate[3][self.ncall] = x_orig[35][35]
	    self.x_rate[4][self.ncall] = x_orig[47][47]

	    print self.y_avg[23][23], ' ', self.y_avg[11][11], ' ', self.y_avg[0][0], ' ', self.y_avg[47][47]
	


class PiecewiseLinear_debug2(OutputFn):
    """
    Same as PiecewiseLinear, but computes average activities for use
    in validating homeostatic plasticity mechanisms.    
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    learn_step = Number(default=8,doc="Number of step before learning take place")

    def __init__(self,**params):
        super(PiecewiseLinear_debug2,self).__init__(**params)

	self.first_call = True
	self.n_step = 0
	self.beta = 0.0003
	self.ncall = 0

    def __call__(self,x):
        fact = 1.0/(self.upper_bound-self.lower_bound)        
        x -= self.lower_bound
        x *= fact
        clip_in_place(x,0.0,1.0)

	if self.first_call:
	    self.first_call = False
	    self.x_avg = zeros(x.shape,x.typecode())
	    self.x_hist = []
	else:
	    if self.ncall <= 1000:
	    	self.x_avg = ((self.x_avg*self.ncall) + x) / (self.ncall+1)
	    	self.ncall += 1
	    else:	    
	    	self.x_avg = self.beta*x + (1.0-self.beta)*self.x_avg
	self.n_step += 1
	if self.n_step == self.learn_step:
	    self.n_step = 0
	
	
	
# Plot graphs from the _debug functions above
def plot_debug_graphs(which, ix, rng1=0, rng2=0, nbins=100, norm=0):
    import topo
    from topo.commands.pylabplots import vectorplot
    from matplotlib.pylab import figure
    if which == 'y_hist':
        figure(1)
        vectorplot (topo.sim['V1'].output_fn.y_hist[ix][rng1:rng2])
    elif which == 'y_rate':
        figure(2)
        vectorplot (topo.sim['V1'].output_fn.y_rate[ix][rng1:rng2])
    elif which == 'x_rate':
        figure(3)
        vectorplot (topo.sim['V1'].output_fn.x_rate[ix][rng1:rng2])
    elif which == 'y_bins':
        figure(4)
        print hist(topo.sim['V1'].output_fn.y_rate[ix][rng1:rng2],nbins,norm)
        #vectorplot (topo.sim['V1'].output_fn.y_bins[time][ix][rng1:rng2])
    elif which == 'x_bins':
        figure(5)
        print hist(topo.sim['V1'].output_fn.x_rate[ix][rng1:rng2],nbins,norm)
        #vectorplot (topo.sim['V1'].output_fn.x_bins[time][ix][rng1:rng2])
    elif which == 'a':
        figure(6)
        vectorplot (topo.sim['V1'].output_fn.ab_hist[0][ix][rng1:rng2])
    elif which == 'b':
        figure(7)
        vectorplot (topo.sim['V1'].output_fn.ab_hist[1][ix][rng1:rng2])
    
