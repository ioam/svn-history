"""
Homeostatic output functions, which are designed to keep an activity
value in a desired range over time.

Originally implemented by Veldri Kurniawan, 2006.

$Id$
"""
__version__='$Revision$'

import copy

from numpy import exp,zeros,ones

from topo.base.arrayutils import clip_in_place
from topo.base.functionfamilies import OutputFn, OutputFnParameter, IdentityOF
from topo.base.parameterclasses import Number, BooleanParameter, ListParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import activity_type
from topo.commands.pylabplots import vectorplot
from topo.misc.filepaths import normalize_path

import matplotlib
import topo
import pylab
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from pylab import save

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
    
    function = OutputFnParameter(default=IdentityOF(), doc="""
        Output function whose parameters will be tracked.""")
    
    debug_params = ListParameter(default=['a', 'b'], doc="""
        List of the function object's parameters that should be stored.""")
    
    avg_params = ListParameter(default=['x'], doc="""
        List of the function object's parameters that should be averaged and stored.""")
    
    units= ListParameter(default=[(0,0)], doc="""
        Units for which parameter values are stored.""")
    
    step=Number(default=8, doc="How often to update debugging information and calculate averages.")

    smoothing = Number(default=0.0003, doc="""
        Determines the relative weighting of current and previous values when calculating the average.
        The average is then an exponentially smoothed version of the
        value, using this value as the time constant.""")

    
    def __init__(self,**params):
        super(OutputFnDebugger,self).__init__(**params)
        self.debug_dict={}
        self.avg_dict={}
        self.n_step = 0
        self.first_call = True
        for dp in self.debug_params:
            self.debug_dict[dp]= zeros([len(self.units),30000],activity_type)
        for ap in self.avg_params:
            self.avg_dict[ap]=zeros([len(self.units),30000],activity_type)
    
        
    def __call__(self,x):
      
        x_copy=x
        
        if self.first_call:
	    self.first_call = False
            self.avg_values={}
            for ap in self.avg_params:
                self.avg_values[ap]=zeros(x_copy.shape, x_copy.dtype.char)
                
        self.n_step += 1
        
        if self.n_step == self.step:
            
            self.n_step = 0

            for dp in self.debug_params:
                for u in self.units:
                    if dp=="x":
                        self.debug_dict[dp][self.units.index(u)][topo.sim.time()]=x_copy[u]
                    else:
                        value_matrix= getattr(self.function, dp)
                        value=value_matrix[u]
                        self.debug_dict[dp][self.units.index(u)][topo.sim.time()]=value

            for ap in self.avg_params:
                for u in self.units:
                    if ap=="x":
                        self.avg_values[ap] = self.smoothing*x_copy + (1.0-self.smoothing)*self.avg_values[ap]
                        self.avg_dict[ap][self.units.index(u)][topo.sim.time()]=self.avg_values[ap][u]
                    else:
                        value_matrix= getattr(self.function, ap)
                        self.avg_values[ap] = self.smoothing*value_matrix + (1.0-self.smoothing)*self.avg_values[ap]
                        self.avg_dict[ap][self.units.index(u)][topo.sim.time()]=self.avg_values[ap][u]
            
                         
    # JABALERT: This function should be merged with save_debug_graphs, if possible
    def plot_debug_graphs(self,init_time, final_time, **params):
        """
        Plots parameter values accumulated by the OutputFnDebugger.
        Example call::
        ODH.plot_debug_graphs(1,10000,debug_params=['a', 'b','eta'],avg_params=[x],units=[(0,0),(11,11)])
        """
              
        # JABALERT: This for loop should be merged with the one below

        for p in params.get('debug_params',self.debug_params):
            pylab.figure()
            isint=pylab.isinteractive()
            pylab.ioff()
            manager = pylab.get_current_fig_manager()
            pylab.ylabel(p)
            pylab.xlabel('Iteration Number')
            manager.window.title(topo.sim.name+': '+p)

            for unit in params.get('units',self.units):
                index=self.units.index(unit)
                plot_data=self.debug_dict[p][index][init_time:final_time]
                vectorplot(plot_data, label='Unit'+str(unit))
                
            if isint: pylab.ion()
            pylab.legend(loc=0)
            pylab.show._needmain = False 
            pylab.show()
	    

        for p in params.get('avg_params',self.avg_params):
            pylab.figure()
            isint=pylab.isinteractive()
            pylab.ioff()
            manager = pylab.get_current_fig_manager()
            pylab.ylabel("Average "+p)
            pylab.xlabel('Iteration Number')
            manager.window.title(topo.sim.name+': '+p)
            
            for unit in params.get('units',self.units):
                index=self.units.index(unit)
                plot_data=self.avg_dict[p][index][init_time:final_time]
                vectorplot(plot_data, label='Unit'+str(unit))

            if isint: pylab.ion()
            pylab.legend(loc=0)
            pylab.show._needmain = False 
            pylab.show()
                       
                              

    # JABALERT: This function should be merged with plot_debug_graphs, if possible
    def save_debug_graphs(self,filename,init_time,final_time,**params):
        """
        Saves plots of parameter values accumulated by the OutputFnDebugger.
        
        Example call::
        
          ODH.save_debug_graphs("V1_graphs",1,10000)

        Can adjust this function to produce different plots, as
        described in the comments.
        """
              
        # JABALERT: This for loop should be merged with the one below
        for p in params.get('debug_params',self.debug_params):
            fig = matplotlib.figure.Figure(figsize=(6,4)) # can change this to change the figure size and shape
            ax = fig.add_subplot(111)
            ax.set_xlabel("Iteration Number")
            ax.set_ylabel(p)
            #ax.set_ylim( 0, 0.03 ) #specify axis limits
            #ax.set_xlim( 0, 10000)
            
            for unit in params.get('units',self.units):
                index=self.units.index(unit)
                plot_data=self.debug_dict[p][index][init_time:final_time]
                #save(normalize_path("Debug"+filename+p+str(unit[0])+"_"+str(unit[1]),plot_data,fmt='%.6f', delimiter=',')) # uncomment if you also want to save the raw data
                ax.plot(plot_data, label='Unit'+str(unit))
            ax.legend(loc=0)
            # Make the PNG
            canvas = FigureCanvasAgg(fig)
            # The size * the dpi gives the final image size
            #   a4"x4" image * 80 dpi ==> 320x320 pixel image
            canvas.print_figure(normalize_path(filename+p+str(topo.sim.time())+".png"), dpi=100)
                     
        for p in params.get('avg_params',self.avg_params):
            fig = matplotlib.figure.Figure(figsize=(6,4))
            ax = fig.add_subplot(111)
            ax.set_xlabel("Iteration Number")
            ax.set_ylabel("Average "+p)
            #ax.set_ylim( 0, 0.03 )
            #ax.set_xlim( 0, 10000)
            
            for unit in params.get('units',self.units):
                index=self.units.index(unit)
                plot_data=self.avg_dict[p][index][init_time:final_time]
                #save(normalize_path("Average"+filename+p+str(unit[0])+"_"+str(unit[1]),plot_data,fmt='%.6f', delimiter=',')) # uncomment if you also want to save the raw data
                ax.plot(plot_data, label='Unit'+str(unit))
            ax.legend(loc=0)
            # Make the PNG
            canvas = FigureCanvasAgg(fig)
            # The size * the dpi gives the final image size
            #   a4"x4" image * 80 dpi ==> 320x320 pixel image
            canvas.print_figure(normalize_path(filename+p+str(topo.sim.time())+".png"), dpi=100)


                       
                              
                       


