import __main__
import numpy
import param 
import copy
import topo

from topo.base.patterngenerator import PatternGenerator, Constant 
from topo import numbergen
from topo.transferfn import TransferFnWithState 
from topo.pattern import Selector, Null
from topo.base.cf import CFPLearningFn,CFPLF_Plugin
from topo.base.arrayutil import clip_lower

class Jitterer(PatternGenerator):
    """
    PatternGenerator that moves another PatternGenerator over time.
    
    It will reset pattern every reset_period + 1. The pattern
    is prestend for reset_perdiod number of times always with a random
    offset from its original location. During the period (reset_period,reset_period + 1)
    a blank stimulus is presented.
    
    To create a pattern at a new location, asks the underlying
    PatternGenerator to create a new pattern at a location translated
    by an amount based on the global time.
    """

    generator = param.ClassSelector(default=Constant(scale=0.0),
        class_=PatternGenerator, doc="""Pattern to be translated.""")
        
    jitter_magnitude = param.Number(default=0.02, bounds=(0.0, None), doc="""
        The speed with which the pattern should move,
        in sheet coordinates per simulation time unit.""")
    
    reset_period = param.Number(default=1, bounds=(0.0, None), doc="""
        When pattern position should be reset, usually to the value of a dynamic parameter.

        The pattern is reset whenever fmod(simulation_time,reset_time)==0.""")
    
    last_time = 0.0


    def __init__(self, **params):
        super(Jitterer, self).__init__(**params)
        self.orientation = params.get('orientation', self.orientation)
        self.r =numbergen.UniformRandom(seed=1023)
        self.index = 0
        
    def __call__(self, **params):
        """Construct new pattern out of the underlying one."""
        generator = params.get('generator', self.generator)
        xdensity = params.get('xdensity', self.xdensity)
        ydensity = params.get('ydensity', self.ydensity)
        bounds = params.get('bounds', self.bounds)

        if((float(topo.sim.time()) >= self.last_time + self.reset_period) or (float(topo.sim.time()) <= 0.05)):
            if ((float(topo.sim.time()) <= (self.last_time + self.reset_period + 1.0)) and (float(topo.sim.time()) >= 0.05))    :
                return Null()(xdensity=xdensity, ydensity=ydensity, bounds=bounds)
        
            self.last_time += self.reset_period
            # time to reset the parameter
            (self.x, self.y, self.scale) = (generator.x, generator.y, generator.scale)
            if isinstance(generator, Selector):
                self.index = generator.index
            generator.force_new_dynamic_value('x')
            generator.force_new_dynamic_value('y')
            generator.force_new_dynamic_value('scale')
            discards = self.orientation
            
        (a, b, c) = (generator.x, generator.y, generator.scale)   
        return generator(xdensity=xdensity, ydensity=ydensity, bounds=bounds, x=self.x + self.jitter_magnitude * self.r(), y=self.y + self.jitter_magnitude * self.r(), orientation=self.inspect_value("orientation"), index=self.inspect_value("index"))


def randomize_V1Simple_relative_LGN_strength(sheet_name="V1Simple", prob=0.5):
    lgn_on_proj = topo.sim[sheet_name].in_connections[0]
    lgn_off_proj = topo.sim[sheet_name].in_connections[1]
    
    rand =numbergen.UniformRandom(seed=513)
    
    rows, cols = lgn_on_proj.cfs.shape
    for r in xrange(rows):
        for c in xrange(cols):
            cf_on = lgn_on_proj.cfs[r, c]
            cf_off = lgn_off_proj.cfs[r, c]
            
            #cf_on._has_norm_total = False
            #cf_off._has_norm_total = False
            del cf_on.norm_total
            del cf_off.norm_total

            ra = rand()
            
            ra = (ra-0.5)*2.0 * prob
            
            cf_on.weights *= 1-ra 
            cf_off.weights *= (1 + ra)
            
class SimpleHomeoLinear(TransferFnWithState):
    mu = param.Number(default=0.01, doc="Target average activity.")
    t_init = param.Number(default=0.0, doc="Threshold parameter")
    alpha = param.Number(default=1.0, doc="Linear slope parameter")
    eta = param.Number(default=0.0002, doc="Learning rate for homeostatic plasticity.")
    smoothing = param.Number(default=0.9997, doc="Weighting of previous activity vs. current activity when calculating the average.")
    randomized_init = param.Boolean(False, doc="Whether to randomize the initial t parameter")
    noise_magnitude = param.Number(default=0.1, doc="The magnitude of the additive noise to apply to the B parameter at initialization")

    def __init__(self, **params):
        super(SimpleHomeoLinear, self).__init__(**params)
        self.first_call = True
        self.__current_state_stack=[]
        
    def __call__(self, x):
       
        if self.first_call:
            self.first_call = False
            if self.randomized_init:
                self.t = numpy.ones(x.shape, x.dtype.char) * self.t_init + (topo.pattern.random.UniformRandom(seed=123)(xdensity=x.shape[0], ydensity=x.shape[1]) - 0.5) * self.noise_magnitude * 2
            else:
                self.t = numpy.ones(x.shape, x.dtype.char) * self.t_init
            
            self.y_avg = numpy.ones(x.shape, x.dtype.char) * self.mu

        x_orig = copy.copy(x)
        x -= self.t
        clip_lower(x, 0)
        x *= self.alpha

        if self.plastic & (float(topo.sim.time()) % 1.0 >= 0.54):
            self.y_avg = (1.0 - self.smoothing) * x + self.smoothing * self.y_avg 
            self.t += self.eta * (self.y_avg - self.mu)
        
    def state_push(self):
        """
        Save the current state of the output function to an internal stack.
        """
       
        self.__current_state_stack.append((copy.copy(self.t), copy.copy(self.y_avg), copy.copy(self.first_call)))
        super(SimpleHomeoLinear, self).state_push()

        
    def state_pop(self):
        """
        Pop the most recently saved state off the stack.
        
        See state_push() for more details.
        """
       
        self.t, self.y_avg, self.first_call = self.__current_state_stack.pop()
        super(SimpleHomeoLinear, self).state_pop()
            
class Expander(PatternGenerator):
    """
    PatternGenerator that expands another PatternGenerator over time.
    
    To create a pattern at a new location, asks the underlying
    PatternGenerator to create a new pattern at a location expanded
    by an amount based on the global time.
    """

    generator = param.ClassSelector(default=Constant(scale=0.0),
        class_=PatternGenerator, doc="""Pattern to be translated.""")
    
    speed = param.Number(default=1, bounds=(0.0, None), doc="""
        The speed with which the pattern should move,
        in sheet coordinates per simulation time unit.""")
    
    reset_period = param.Number(default=1, bounds=(0.0, None), doc="""
        When pattern position should be reset, usually to the value of a dynamic parameter.

        The pattern is reset whenever fmod(simulation_time,reset_time)==0.""")
    
    last_time = 0.0


    def __init__(self, **params):
        super(Expander, self).__init__(**params)
        self.size = params.get('size', self.size)
        self.index = 0
        self.last_time=0.0
        
    def __call__(self, **params):
        """Construct new pattern out of the underlying one."""
        generator = params.get('generator', self.generator)
        xdensity = params.get('xdensity', self.xdensity)
        ydensity = params.get('ydensity', self.ydensity)
        bounds = params.get('bounds', self.bounds)

        # CB: are the float() calls required because the comparisons
        # involving FixedPoint fail otherwise? Or for some other
        # reason?
        if((float(topo.sim.time()) >= self.last_time + self.reset_period) or (float(topo.sim.time()) <= 0.05)):
            if ((float(topo.sim.time()) <= (self.last_time + self.reset_period + 1.0)) and (float(topo.sim.time()) >= 0.05))    :
                return Null()(xdensity=xdensity, ydensity=ydensity, bounds=bounds)
            if (float(topo.sim.time()) >= 0.05):
                self.last_time += self.reset_period
            # time to reset the parameter
            (self.x, self.y) = (generator.x, generator.y)
            if isinstance(generator, Selector):
                self.index = generator.index
            generator.force_new_dynamic_value('x')
            generator.force_new_dynamic_value('y')

        (a, b) = (generator.x, generator.y)   
        # compute how much time elapsed from the last reset
        t = float(topo.sim.time()) - self.last_time

        ## CEBALERT: mask gets applied twice, both for the underlying
        ## generator and for this one.  (leads to redundant
        ## calculations in current lissom_oo_or usage, but will lead
        ## to problems/limitations in the future).
        return generator(xdensity=xdensity, ydensity=ydensity, bounds=bounds, x=self.x, y=self.y,
             size=self.size + t * self.speed,index=self.index)


class CFPLF_KeyserRule(CFPLearningFn):
    """
    CF-aware Anti-Hebbian like learning rule rule.

    Based on: 
    
    Andrew S. Kayser and Kenneth D. Miller,
    Opponent Inhibition: A Developmental Model of Layer 4 of the Neocortical Circuit    
    Neuron, Vol. 33, 131-142, January 3, 2002
    
    JAHACK:
    This is going to work correctly only if all inhibitory projections are subtractive,
    but technically all already defined learning rules have that problem!!!
    """
    
    def __init__(self,sheet,inhibitory_projection_list):
        self.sheet = sheet
        self.inhibitory_projection_list = inhibitory_projection_list
    
    def __call__(self, iterator, input_activity, output_activity, learning_rate, **params):
        
        single_connection_learning_rate = self.constant_sum_connection_rate(iterator.proj_n_units,learning_rate)
        if single_connection_learning_rate==0:
            return
	

        #calculate overall incomming inhibition
        inhibition = 0
        for s in self.inhibitory_projection_list:
            p = topo.sim[self.sheet].projections()[s]
            inhibition += abs(p.activity)

        
        for cf,i in iterator():
            
            # Anti-hebbian part
            if output_activity.flat[i] != 0:
                cf.weights -= single_connection_learning_rate * output_activity.flat[i] * cf.get_input_matrix(input_activity)
            
            # inhibition part
            if inhibition.flat[i] != 0:
                cf.weights += single_connection_learning_rate * inhibition.flat[i] * cf.get_input_matrix(input_activity)
            
            cf.weights *= numpy.multiply((cf.weights>0),cf.mask)


def circular_dist(a,b,period):
    """
    The distance between a and b (scalars) in the periodic. 
    a,b have to be in (0,period)
    """
    return  numpy.minimum(abs(a-b), period - abs(a-b))

def rad_to_complex(vector):
    """
    Converts a vector/matrix of angles (0,2*pi) to vector/matrix of complex numbers (that will lie on the unit circle)
    """
    return numpy.cos(vector)+1j*numpy.sin(vector)
    

def angle_two_pi(array):
    """
    returns angles of complex numbers in array but in (0,2*pi) interval unlike numpy.angle the returns it in (-pi,pi)
    """
    return (numpy.angle(array)+ 4*numpy.pi) % (numpy.pi*2)
    

def circ_mean(matrix,weights=None,axis=None,low=0,high=numpy.pi*2,normalize=False):
    """
    Circular mean of matrix. Weighted if weights are not none.
    
    matrix   - 2d ndarray of data. Mean will be computed for each column.
    weights  - if not none, a vector of the same length as number of matrix rows.
    low,high - the min and max values that will be mapped onto the periodic interval of (0,2pi)
    axis     - axis along which to compute the circular mean. default = 1
    normalize - if True weights will be normalized along axis. If any weights that are to be jointly normalized are all zero they will be kept zero!
    
    return (angle,length)  - where angle is the circular mean, and len is the length of the resulting mean vector
    """
    
    # check whether matrix and weights are ndarrays
    if not isinstance(matrix,numpy.ndarray):
       logger.error("circ_mean: array not type ndarray ") 
       raise TypeError("circ_mean: array not type ndarray ") 

    if weights!= None and not isinstance(weights,numpy.ndarray):
       logger.error("circ_mean: weights not type ndarray ") 
       raise TypeError("circ_mean: weights not type ndarray ") 
    
    # convert the periodic matrix to corresponding complex numbers
    
    m = rad_to_complex((matrix - low)/(high-low) * numpy.pi*2)
    
    if axis == None:
       axis == 1
    
    # normalize weights
    if normalize:
       row_sums = numpy.sum(numpy.abs(weights),axis=axis)
       row_sums[numpy.where(row_sums == 0)] = 1.0
       weights = weights / row_sums[:, numpy.newaxis]
       
           
    if weights == None:
       m  = numpy.mean(m,axis=axis) 
    else:
       z = m*weights
       m = numpy.mean(z,axis=axis) 
        
    return ((angle_two_pi(m) / (numpy.pi*2))*(high-low) + low, abs(m))
    

def analyse_push_pull_connectivity():
    _analyse_push_pull_connectivity('V1Simple','V1SimpleExcToExc')
    _analyse_push_pull_connectivity('V1Simple','V1SimpleInhToExc')
    _analyse_push_pull_connectivity('V1Complex','LateralExcitatory')

def _analyse_push_pull_connectivity(sheet_name,proj_name):
    """
    It assumes orientation preference was already measured.
    """
    projection = topo.sim[sheet_name].projections()[proj_name]
    or_pref = topo.sim[sheet_name].sheet_views['OrientationPreference'].view()[0]*numpy.pi
    phase_pref = topo.sim[sheet_name].sheet_views['PhasePreference'].view()[0]*numpy.pi*2
    
    app  = []
    av1 = []
    av2 = []
    for (i,cf) in enumerate(projection.cfs.flatten()):
        this_or = or_pref.flatten()[i]
        this_phase = phase_pref.flatten()[i]
        ors = cf.input_sheet_slice.submatrix(or_pref).flatten()
        phases = cf.input_sheet_slice.submatrix(phase_pref).flatten()
        weights = numpy.multiply(cf.weights,cf.mask)
        
        #First lets compute the average phase of neurons which are within 30 degrees of the given neuron
        within_30_degrees = numpy.nonzero((circular_dist(ors,this_or,numpy.pi) < (numpy.pi/6.0))*1.0)[0]
        if len(within_30_degrees) != 0:
            z = circ_mean(numpy.array([phases[within_30_degrees]]),weights=numpy.array([weights.flatten()[within_30_degrees]]),axis=1,low=0.0,high=numpy.pi*2,normalize=False)
            app.append(z[0])
        else:
            app.append(0.0)
            
        #Now lets compare the average connection strength to neurons oriented within 30 degrees and having the same phase (within 60 degrees), with the average connections strength to neurons more than 30 degrees off in orientation
        outside_30_degrees = numpy.nonzero(circular_dist(ors,this_or,numpy.pi) > numpy.pi/6.0)[0]
        within_30_degrees_and_same_phase = numpy.nonzero(numpy.multiply(circular_dist(ors,this_or,numpy.pi) < numpy.pi/6.0,circular_dist(phases,this_phase,2*numpy.pi) < numpy.pi/3.0))[0]
        
        if len(outside_30_degrees) != 0:
            av1.append(numpy.mean(weights.flatten()[outside_30_degrees])/max(len(outside_30_degrees),1.0))
        else:
            av1.append(0.0)
        if len(within_30_degrees_and_same_phase) != 0:
            av2.append(numpy.mean(weights.flatten()[within_30_degrees_and_same_phase])/max(len(within_30_degrees_and_same_phase),1.0))
        else:
            av2.append(0.0)
        
        

    import pylab
    pylab.figure()
    pylab.subplot(3,1,1)
    pylab.plot(numpy.array(app),phase_pref.flatten()*numpy.pi*2,'ro')
    pylab.subplot(3,1,2)
    pylab.hist(phase_pref.flatten()*numpy.pi*2)
    pylab.subplot(3,1,3)
    pylab.bar(numpy.arange(2), (numpy.mean(av1),numpy.mean(av2)),   0.35, color='b')
    
    from param import normalize_path
    pylab.savefig(normalize_path('PPconnectivity: ' + sheet_name + '|' + proj_name));


import matplotlib.gridspec as gridspec
import pylab

def plot_domains_stability(gs,mr):
      gs = gridspec.GridSpecFromSubplotSpec(2, len(mr.records.keys()), subplot_spec=gs)  
      for i,s in enumerate(mr.records.keys()):
          
          ax = pylab.subplot(gs[0,i])
          ax.imshow(mr.records[s]['activity'][7],cmap='gray') 

          ax = pylab.subplot(gs[1,i])
          ax.imshow(sum(mr.records[s]['activity']),cmap='gray') 
    
def domains_stability_test(parameters,parameter_values,sheets,sheets_to_record,retina,reset_homeo,directory):
    from modelparametrization import ModelRecording,ModelParametrization
    mr = ModelRecording(sheets, retina, sheets_to_record = sheets_to_record, reset_homeo = reset_homeo)
    f = lambda : mr.present_stimulus_sequence(1.0,[None,None,None,None,None,None,None,None])
    
    
    mp = ModelParametrization(parameters,parameter_values,f,plot_domains_stability,{'mr' : mr},directory)
    mp.go(initial_run=True)

    
    
    
