"""
LISSOM and related sheet classes.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric as Numeric
import numpy
from numpy import abs,zeros,ones
import topo
import copy

from topo.base.functionfamilies import OutputFn
from topo.base.cf import CFSheet, CFPOutputFn
from topo.base.parameterclasses import Parameter,BooleanParameter, Number, Integer,\
     ListParameter,ClassSelectorParameter
from topo.base.projection import Projection
from ..param import Parameterized
from topo.base.sheet import activity_type
from topo.misc.inlinec import optimized
from topo.misc.keyedlist import KeyedList
from topo.outputfns.basic import PiecewiseLinear
from topo.base.simulation import EPConnectionEvent

class JointNormalizingCFSheet(CFSheet):
    """
    A type of CFSheet extended to support joint sum-based normalization.

    For L1 normalization, joint normalization means normalizing the
    sum of (the absolute values of) all weights in a set of
    corresponding CFs in different Projections, rather than only
    considering weights in the same CF.

    This class makes it possible for a model to use joint
    normalization, by providing a mechanism for grouping Projections
    (see _port_match), plus a learn() function that computes the joint
    sums.  Joint normalization also requires having ConnectionField
    store and return a norm_total for each neuron, and having an
    OutputFn that will respect this norm_total rather than the strict
    total of the ConnectionField's weights.  At present,
    CFPOF_DivisiveNormalizeL1 and CFPOF_DivisiveNormalizeL1_opt do use
    norm_total; others can be extended to do something similar if
    necessary.

    To enable joint normalization, you can declare that all the
    incoming connections that should be normalized together each
    have a dest_port of:

    dest_port=('Activity','JointNormalize', 'AfferentGroup1'),

    Then all those that have this dest_port will be normalized
    together, as long as an appropriate OutputFn is being used.
    """

    # JABALERT: Should check that whenever a connection is added to a
    # group, it has the same no of cfs as the existing connections.
    def start(self):
        self._normalize_weights()        

                       
    def compute_joint_norm_totals(self,projlist,mask):
        """
        Compute norm_total for each CF in each projection from a group to be normalized jointly.
        """

        # Assumes that all Projections in the list have the same r,c size
        assert len(projlist)>=1
        proj  = projlist[0]
        rows,cols = proj.cfs.shape

        for r in range(rows):
            for c in range(cols):
                if(mask[r,c] != 0):
                    sums = [p.cfs[r,c].norm_total for p in projlist]
                    joint_sum = Numeric.add.reduce(sums)
                    for p in projlist:
                        p.cfs[r,c].norm_total=joint_sum


    def _normalize_weights(self,mask = None):
        """
        Apply the weights_output_fn for every group of Projections.
        
        The mask is telling which neurons need to be normalized.
        """
        
        if(mask == None):
            mask = Numeric.ones(self.shape,activity_type)
        
        for key,projlist in self._grouped_in_projections('JointNormalize'):
            if key == None:
                normtype='Independent'
            else:
                normtype='Joint'
                self.compute_joint_norm_totals(projlist,mask)

            self.debug(normtype + "ly normalizing:")

            for p in projlist:
                p.apply_learn_output_fn(mask)
                self.debug('  ',p.name)


    def learn(self):
        """
        Call the learn() method on every Projection to the Sheet, and
        call the output functions (jointly if necessary).
        """
        # Ask all projections to learn independently
        for proj in self.in_connections:
            if not isinstance(proj,Projection):
                self.debug("Skipping non-Projection "+proj.name)
            else:
                proj.learn()

        # Apply output function in groups determined by dest_port
        self._normalize_weights(self.activity)

        

class LISSOM(JointNormalizingCFSheet):
    """
    A Sheet class implementing the LISSOM algorithm
    (Sirosh and Miikkulainen, Biological Cybernetics 71:66-78, 1994).

    A LISSOM sheet is a JointNormalizingCFSheet slightly modified to
    enforce a fixed number of settling steps.  Settling is controlled
    by the tsettle parameter; once that number of settling steps has
    been reached, an external input is required before the sheet will
    activate again.
    """
    
    strict_tsettle = Parameter(default = None,
        doc='This parameter when defined tells the LISSOM sheet not to send afferent output until the strict_tsettle time')    
    
    mask_init_time=param.Integer(default=5,bounds=(0,None),doc=""" 
       Determines when a new mask is initialized in each new iteration.

       The mask is reset whenever new input comes in.  Once the
       activation_count (see tsettle) reaches mask_init_time, the mask
       is initialized to reflect the current activity profile.""")

    tsettle=param.Integer(default=8,bounds=(0,None),doc="""
       Number of times to activate the LISSOM sheet for each external input event.
       
       A counter is incremented each time an input is received from any
       source, and once the counter reaches tsettle, the last activation
       step is skipped so that there will not be any further recurrent
       activation.  The next external (i.e., afferent or feedback)
       event will then start the counter over again.""")

    continuous_learning = param.Boolean(default=False, doc="""
       Whether to modify the weights after every settling step.
       If false, waits until settling is completed before doing learning.""")

    output_fn = param.ClassSelector(OutputFn,default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    
    precedence = param.Number(0.6)
    
    post_initialization_weights_output_fn = param.ClassSelector(
        CFPOutputFn,default=None,doc="""
        Weights output_fn which can be set after an initial normalization step""")

    
    def __init__(self,**params):
        super(LISSOM,self).__init__(**params)
        self.__counter_stack=[]
        self.activation_count = 0
        self.new_iteration = True


    def start(self):
        self._normalize_weights()
        if self.post_initialization_weights_output_fn is not None:
            for proj in self.in_connections:
                if not isinstance(proj,Projection):
                    self.debug("Skipping non-Projection ")
                else:
                    proj.weights_output_fn=self.post_initialization_weights_output_fn 


    def input_event(self,conn,data):
        # On a new afferent input, clear the activity
        if self.new_iteration:
            self.new_iteration = False
            self.activity *= 0.0
            for proj in self.in_connections:
                proj.activity *= 0.0
            self.mask.reset()        
        super(LISSOM,self).input_event(conn,data)


    ### JABALERT!  There should be some sort of warning when
    ### tsettle times the input delay is larger than the input period.
    ### Right now it seems to do strange things in that case (does it
    ### settle at all after the first iteration?), but of course that
    ### is arguably an error condition anyway (and should thus be
    ### flagged).
    def process_current_time(self):
        """
        Pass the accumulated stimulation through self.output_fn and
        send it out on the default output port.
        """
        if self.new_input:
            self.new_input = False
            
            if self.activation_count == self.mask_init_time:
                self.mask.calculate()
            
            if self.tsettle == 0:
                # Special case: behave just like a CFSheet
                self.activate()
                self.learn()
                
   	    elif self.activation_count == self.tsettle:
                # Once we have been activated the required number of times
                # (determined by tsettle), reset various counters, learn
                # if appropriate, and avoid further activation until an
                # external event arrives.
                self.activation_count = 0
                self.new_iteration = True # used by input_event when it is called
                if (self.plastic and not self.continuous_learning):
                    self.learn()
            else:
                self.activate()
                self.activation_count += 1
                if (self.plastic and self.continuous_learning):
                   self.learn()
                   

    # print the weights of a unit
    def printwts(self,x,y):
        for proj in self.in_connections:
            print proj.name, x, y
            print proj.cfs[x,y].weights


    def state_push(self,**args):
        super(LISSOM,self).state_push(**args)
        self.__counter_stack.append((self.activation_count,self.new_iteration))


    def state_pop(self,**args):
        super(LISSOM,self).state_pop(**args)
        self.activation_count,self.new_iteration=self.__counter_stack.pop()

    def send_output(self,src_port=None,data=None):
        """Send some data out to all connections on the given src_port."""
        out_conns_on_src_port = [conn for conn in self.out_connections
                                 if self._port_match(conn.src_port,[src_port])]

        for conn in out_conns_on_src_port:
            if self.strict_tsettle != None:
               if self.activation_count < self.strict_tsettle:
                   if len(conn.dest_port)>2 and conn.dest_port[2] == 'Afferent':
                    continue
            self.verbose("Sending output on src_port %s via connection %s to %s" % (str(src_port), conn.name, conn.dest.name))
            e=EPConnectionEvent(conn.delay+self.simulation.time(),conn,data)
            self.simulation.enqueue_event(e)


class JointNormalizingCFSheet_Continuous(JointNormalizingCFSheet):
    """
    CFSheet that runs continuously, with no 'resting' periods between pattern presentations.
    
    Note that learning occurs only when the time is a whole number.
    """
    def process_current_time(self):
        if(float(topo.sim.time()) % 1.0 == 0.0):
            #self.activate()
            if (self.plastic):
                 self.learn()
        else:
             self.activate()



class JointScaling(LISSOM):
    """
    LISSOM sheet extended to allow joint auto-scaling of Afferent input projections.
    
    An exponentially weighted average is used to calculate the average
    joint activity across all jointly-normalized afferent projections.
    This average is then used to calculate a scaling factor for the
    current afferent activity and for the afferent learning rate.

    The target average activity for the afferent projections depends
    on the statistics of the input; if units are activated more often
    (e.g. the number of Gaussian patterns on the retina during each
    iteration is increased) the target average activity should be
    larger in order to maintain a constant average response to similar
    inputs in V1. The target activity for learning rate scaling does
    not need to change, because the learning rate should be scaled
    regardless of what causes the change in average activity.
    """
    # ALERT: Should probably be extended to jointly scale different
    # groups of projections. Currently only works for the joint
    # scaling of projections named "Afferent", grouped together by
    # JointNormalize in dest_port.
    
    target = param.Number(default=0.045, doc="""
        Target average activity for jointly scaled projections.""")

    # JABALERT: I cannot parse the docstring; is it an activity or a learning rate?
    target_lr = param.Number(default=0.045, doc="""
        Target average activity for jointly scaled projections.

        Used for calculating a learning rate scaling factor.""")
    
    smoothing = param.Number(default=0.999, doc="""
        Influence of previous activity, relative to current, for computing the average.""")


    def __init__(self,**params):
        super(JointScaling,self).__init__(**params)
        self.x_avg=None
        self.sf=None
        self.lr_sf=None
        self.scaled_x_avg=None
        self.__current_state_stack=[]

    def calculate_joint_sf(self, joint_total):
        """
        Calculate current scaling factors based on the target and previous average joint activities.

        Keeps track of the scaled average for debugging. Could be
        overridden by a subclass to calculate the factors differently.
        """
      
        if self.plastic:
            self.sf *=0.0
            self.lr_sf *=0.0
            self.sf += self.target/self.x_avg
            self.lr_sf += self.target_lr/self.x_avg
            self.x_avg = (1.0-self.smoothing)*joint_total + self.smoothing*self.x_avg
            self.scaled_x_avg = (1.0-self.smoothing)*joint_total*self.sf + self.smoothing*self.scaled_x_avg


    def do_joint_scaling(self):
        """
        Scale jointly normalized projections together.

        Assumes that the projections to be jointly scaled are those
        that are being jointly normalized.  Calculates the joint total
        of the grouped projections, and uses this to calculate the
        scaling factor.
        """
        joint_total = zeros(self.shape, activity_type)
        
        for key,projlist in self._grouped_in_projections('JointNormalize'):
            if key is not None:
                if key =='Afferent':
                    for proj in projlist:
                        joint_total += proj.activity
                    self.calculate_joint_sf(joint_total)
                    for proj in projlist:
                        proj.activity *= self.sf
                        if hasattr(proj.learning_fn,'learning_rate_scaling_factor'):
                            proj.learning_fn.update_scaling_factor(self.lr_sf)
                        else:
                            raise ValueError("Projections to be joint scaled must have a learning_fn that supports scaling e.g. CFPLF_PluginScaled")
                   
                else:
                    raise ValueError("Only Afferent scaling currently supported")                  


    def activate(self):
        """
        Compute appropriate scaling factors, apply them, and collect resulting activity.

        Scaling factors are first computed for each set of jointly
        normalized projections, and the resulting activity patterns
        are then scaled.  Then the activity is collected from each
        projection, combined to calculate the activity for this sheet,
        and the result is sent out.
        """
        self.activity *= 0.0

        if self.x_avg is None:
            self.x_avg=self.target*ones(self.shape, activity_type)
        if self.scaled_x_avg is None:
            self.scaled_x_avg=self.target*ones(self.shape, activity_type) 
        if self.sf is None:
            self.sf=ones(self.shape, activity_type)
        if self.lr_sf is None:
            self.lr_sf=ones(self.shape, activity_type)

        #Afferent projections are only activated once at the beginning of each iteration
        #therefore we only scale the projection activity and learning rate once.
        if self.activation_count == 0: 
            self.do_joint_scaling()   

        for proj in self.in_connections:
            self.activity += proj.activity
        
        if self.apply_output_fn:
            self.output_fn(self.activity)
          
        self.send_output(src_port='Activity',data=self.activity)


    def state_push(self,**args):
        super(JointScaling,self).state_push(**args)
        self.__current_state_stack.append((copy.copy(self.x_avg),copy.copy(self.scaled_x_avg),
                                           copy.copy(self.sf), copy.copy(self.lr_sf)))
        
        

    def state_pop(self,**args):
        super(JointScaling,self).state_pop(**args)
        self.x_avg,self.scaled_x_avg, self.sf, self.lr_sf=self.__current_state_stack.pop()
