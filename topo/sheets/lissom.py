"""
The LISSOM and JointNormalizingCFSheet classes.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric as Numeric
import numpy
from numpy import abs,zeros,ones
import topo

from topo.base.cf import CFSheet, CFPOutputFnParameter
from topo.base.parameterclasses import BooleanParameter, Number, Integer, ListParameter
from topo.base.projection import OutputFnParameter, Projection
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import activity_type
from topo.misc.inlinec import optimized
from topo.misc.keyedlist import KeyedList
from topo.outputfns.basic import PiecewiseLinear


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

    def _port_match(self,key,portlist):
        """
        Returns True if the given key matches any port on the given list.

        A port is considered a match if the port is == to the key,
        or if the port is a tuple whose first element is == to the key,
        or if both the key and the port are tuples whose first elements are ==.

        This approach allows connections to be grouped using tuples.
        """
        port=portlist[0]
        return [port for port in portlist
                if (port == key or
                    (isinstance(key,tuple)  and key[0] == port) or
                    (isinstance(port,tuple) and port[0] == key) or
                    (isinstance(key,tuple)  and isinstance(port,tuple) and port[0] == key[0]))]

                        
    def compute_joint_norm_totals(self,projlist,mask):
        """
        Compute norm_total for each CF in each projection from a group to be normalized jointly.
        """

        # Assumes that all Projections in the list have the same r,c size
        assert len(projlist)>=1
        proj  = projlist[0]
        rows,cols = proj.cfs_shape

        for r in range(rows):
            for c in range(cols):
                if(mask[r,c] != 0):
                    sums = [p.cf(r,c).norm_total for p in projlist]
                    joint_sum = Numeric.add.reduce(sums)
                    for p in projlist:
                        p.cf(r,c).norm_total=joint_sum


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
    
    mask_init_time=Integer(default=5,bounds=(0,None),doc=""" 
       Determines when a new mask is initialized in each new iteration.

       The mask is reset whenever new input comes in.  Once the
       activation_count (see tsettle) reaches mask_init_time, the mask
       is initialized to reflect the current activity profile.""")

    tsettle=Integer(default=8,bounds=(0,None),doc="""
       Number of times to activate the LISSOM sheet for each external input event.
       
       A counter is incremented each time an input is received from any
       source, and once the counter reaches tsettle, the last activation
       step is skipped so that there will not be any further recurrent
       activation.  The next external (i.e., afferent or feedback)
       event will then start the counter over again.""")

    continuous_learning = BooleanParameter(default=False, doc="""
       Whether to modify the weights after every settling step.
       If false, waits until settling is completed before doing learning.""")

    output_fn = OutputFnParameter(default=PiecewiseLinear(lower_bound=0.1,upper_bound=0.65))
    precedence = Number(0.6)
    
    post_initialization_weights_output_fn = CFPOutputFnParameter(default=None,
       doc="""Weights output_fn which can be set after an initial normalization step""")
    
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
    ### Right now it seems to do strange things in that case (settle
    ### at all after the first iteration?), but of course that is
    ### arguably an error condition anyway (and should thus be
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
                self.activate()
                self.learn()
   	    elif self.activation_count == self.tsettle:
                # Once we have been activated the required number of times
                # (determined by tsettle), reset various counters, learn
                # if appropriate, and avoid further activation until an
                # external event arrives.
                self.activation_count = 0
                self.new_iteration = True # used by input_event when it is called
                if (self.learning and not self.continuous_learning):
                    self.learn()
            else:
                self.activate()
                self.activation_count += 1
                if (self.learning and self.continuous_learning):
                   self.learn()

                   

    # print the weights of a unit
    def printwts(self,x,y):
        for proj in self.in_connections:
            print proj.name, x, y
            print proj.cf(x,y).weights


    def state_push(self,**args):
        super(LISSOM,self).state_push(**args)
        self.__counter_stack.append((self.activation_count,self.new_iteration))


    def state_pop(self,**args):
        super(LISSOM,self).state_pop(**args)
        self.activation_count,self.new_iteration=self.__counter_stack.pop()
  
class JointNormalizingCFSheet_Continouse(JointNormalizingCFSheet):
    """
    This is a version of CFSheet that runs continousely - eg. there are no 'resting' periods between pattern presentations. 
    However learning occurs only always when the time is an integer number.
    """
    def process_current_time(self):
        if(float(topo.sim.time()) % 1.0 == 0.0):
            #self.activate()
            if (self.learning):
                 self.learn()
        else:
             self.activate()

class JointScaling(LISSOM):
    """
    A LISSOM sheet extended to allow joint scaling of Afferent input projections
    based on a specified target average activity.
    An exponentially weighted average is used to calculate the average joint afferent activity.
    This average is then used to calculate a scaling factor for the current afferent activity
    in order to bring the average activity closer to the target.
    Learning rates are also scaled in order to ensure that the afferent projections
    learn at the same rate regardless of the average input activity from the LGN.
    The target average activity for the afferent projections depends on the statistics of the input,
    if units are activated more often (e.g. the number of Gaussian patterns on the retina during each
    iteration is increased)the target should be larger in order to maintain a constant average
    response to similar inputs in V1. 
    """
    #ALERT Could also be extended to jointly scale different groups of projections.Currently only works for
    #the joint scaling of the Afferent projections as grouped together by JointNormalize in dest_port.
    
    target = Number(default=0.04, doc="""Target average activity for jointly scaled projections""")

    updating = BooleanParameter(default=True, doc="""
        Whether or not to update average.
        Allows averaging to be turned off, e.g. during map measurement.""")

    smoothing = Number(default=0.9997, doc="""
        Determines the degree of weighting of previous activity vs.
        current activity when calculating the average.""")
    
    def __init__(self,**params):
        super(JointScaling,self).__init__(**params)
        self.x_avg=None
        self.sf=None
        self._updating_state = []
        self.scaled_x_avg=None


    def calculate_joint_sf(self, joint_total):
        """
        If updating is True, calculate the scaling factor based on the target average activity and the previous
        average joint activity. Keep track of the scaled average for debugging. Could be overwritten if a different
        scaling factor is required.
        """
       
        if self.updating:
            self.sf *=0.0
            self.sf += self.target/self.x_avg
            self.x_avg = (1.0-self.smoothing)*joint_total + self.smoothing*self.x_avg
            self.scaled_x_avg = (1.0-self.smoothing)*joint_total*self.sf + self.smoothing*self.scaled_x_avg


    def do_joint_scaling(self):
        """
        Assume that the projections to be jointly scaled are those which are being jointly normalized.
        Calculate the joint total of the grouped projections and use this to calculate the scaling factor.
        Scale the projection activity and learning rate for these projections.
        """
        joint_total = zeros(self.shape, activity_type)
        
        for key,projlist in self._grouped_in_projections():
            if key is not None:
                if key =='Afferent':
                    for proj in projlist:
                        joint_total += proj.activity
                    self.calculate_joint_sf(joint_total)
                    for proj in projlist:
                        if hasattr(proj.learning_fn,'learning_rate_scaling_factor'):
                            proj.activity *= self.sf
                            proj.learning_fn.update_scaling_factor(self.sf)
                        else:
                            raise ValueError("Projections to be joint scaled must have learning function which supports scaling e.g. CFPLF_PluginScaled")
                   
                else:
                    raise ValueError("Only Afferent scaling currently supported")                  

    def activate(self):
        """
        Calculate the scaling factor and scale the afferent projection activity.
        Collect activity from each projection, combine it to calculate
        the activity for this sheet, and send the result out.  Subclasses
        may override this method to whatever it means to calculate activity
        in that subclass.
        """
        self.activity *= 0.0

        
        if self.x_avg is None:
            self.x_avg=self.target*ones(self.shape, activity_type)
        if self.scaled_x_avg is None:
            self.scaled_x_avg=self.target*ones(self.shape, activity_type) 
        if self.sf is None:
            self.sf=ones(self.shape, activity_type)

        #Afferent projections are only activated once at the beginning of each iteration
        #therefore we only scale the projection activity and learning rate once.
        if self.activation_count == 1: 
            self.do_joint_scaling()   

       
        for proj in self.in_connections:
            self.activity += proj.activity

        if self.apply_output_fn:
            self.output_fn(self.activity)
          
        self.send_output(src_port='Activity',data=self.activity)


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

                    

 
