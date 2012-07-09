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
	
	z = numpy.argmax(output_activity)


        #calculate overall incomming inhibition
        inhibition = 0
        for s in self.inhibitory_projection_list:
            p = topo.sim[self.sheet].projections()[s]
            inhibition += p.activity * abs(p.strength)

        
        for cf,i in iterator():
            
            # Anti-hebbian part
            if output_activity.flat[i] != 0:
                cf.weights -= single_connection_learning_rate * output_activity.flat[i] * cf.get_input_matrix(input_activity)
            
            # inhibition part
            if inhibition.flat[i] != 0:
                cf.weights += single_connection_learning_rate * inhibition.flat[i] * cf.get_input_matrix(input_activity)
	    cf.weights *= cf.mask                
    	    
    	    if True and (i == z):
    	        print 'Z ' + str(z) 
    	        print single_connection_learning_rate
    	        print output_activity.flat[i] 
    		print single_connection_learning_rate * output_activity.flat[i] 
    		print numpy.max(cf.get_input_matrix(input_activity))
    		print numpy.max(inhibition.flat[i])
    		print numpy.max(cf.weights)
    	        print numpy.max(single_connection_learning_rate * output_activity.flat[i] * cf.get_input_matrix(input_activity))
    	        print numpy.max(single_connection_learning_rate * inhibition.flat[i] * cf.get_input_matrix(input_activity))
