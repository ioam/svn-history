"""
Neural sheet objects.

$Id$
"""
__version__='$Revision: 8986 $'

# Imported here so that all Sheets will be in the same package
from topo.base.sheet import Sheet
from topo.base.projection import ProjectionSheet
from topo.base.cf import CFSheet

import copy
import numpy

import topo

import param

from topo.base.cf import CFSheet, CFPOutputFn
from topo.base.functionfamily import TransferFn
from topo.base.patterngenerator import PatternGenerator, Constant
from topo.base.projection import Projection
from topo.base.sheet import activity_type, BoundingBox
from topo.base.simulation import EPConnectionEvent
from topo.base.simulation import FunctionEvent, PeriodicEventSequence
from topo.misc.keyedlist import KeyedList
from topo.misc.util import NxN
from topo.transferfn.basic import PiecewiseLinear



class ActivityCopy(Sheet):
    """
    Copies incoming Activity patterns to its activity matrix and output port.

    Trivial Sheet class that is useful primarily as a placeholder for
    data that is computed elsewhere but that you want to appear as a
    Sheet, e.g. when wrapping an external simulation.
    """

    dest_ports=['Activity']
    src_ports=['Activity']
    
    def input_event(self,conn,data):
        self.input_data=data

    def process_current_time(self):
        if hasattr(self, 'input_data'):
            self.activity*=0
            self.activity+=self.input_data
            self.send_output(src_port='Activity',data=self.activity)
            del self.input_data



# JLALERT: This sheet should have override_plasticity_state/restore_plasticity_state
# functions that call override_plasticity_state/restore_plasticty_state on the
# sheet output_fn and input_generator output_fn.
class GeneratorSheet(Sheet):
    """
    Sheet for generating a series of 2D patterns.

    Typically generates the patterns by choosing parameters from a
    random distribution, but can use any mechanism.
    """

    src_ports=['Activity']
    
    period = param.Number(default=1,bounds=(0,None),doc=
        "Delay (in Simulation time) between generating new input patterns.")
    
    phase  = param.Number(default=0.05,doc=
        """
        Delay after the start of the Simulation (at time zero) before
        generating an input pattern.  For a clocked, feedforward simulation, 
        one would typically want to use a small nonzero phase and use delays less
        than the user-visible step size (typically 1.0), so that inputs are
        generated and processed before this step is complete.
        """)
    
    input_generator = param.ClassSelector(PatternGenerator,default=Constant(),
        doc="""Specifies a particular PatternGenerator type to use when creating patterns.""")

    
    def __init__(self,**params):
        super(GeneratorSheet,self).__init__(**params)
        self.input_generator_stack = []
        self.set_input_generator(self.input_generator)

        # JABALERT: Should make period have an exclusive lower bound instead
        assert self.period!=0, "Period must be greater than zero."

    def set_input_generator(self,new_ig,push_existing=False):
        """
        Set the input_generator, overwriting the existing one by default.

        If push_existing is false, the existing input_generator is
        discarded permanently.  Otherwise, the existing one is put
        onto a stack, and can later be restored by calling
        pop_input_generator.
        """

        if push_existing:
            self.push_input_generator()

        self.input_generator = new_ig

        # CEBALERT: replaces any bounds specified for the
        # PatternGenerator with this sheet's own bounds. When
        # PatternGenerators can draw patterns into supplied
        # boundingboxes, should remove this.
        self.input_generator.bounds = self.bounds
        
        self.input_generator.xdensity = self.xdensity
        self.input_generator.ydensity = self.ydensity
        

    def push_input_generator(self):
        """Push the current input_generator onto a stack for future retrieval."""
        self.input_generator_stack.append(self.input_generator)

        # CEBALERT: would be better to reorganize code so that
        # push_input_generator must be supplied with a new generator.
        from topo.base.patterngenerator import Constant
        self.set_input_generator(Constant()) 

               
    def pop_input_generator(self):
        """
        Discard the current input_generator, and retrieve the previous one from the stack.

        Warns if no input_generator is available on the stack.
        """
        if len(self.input_generator_stack) >= 1:
            self.set_input_generator(self.input_generator_stack.pop())
        else:
            self.warning('There is no previous input generator to restore.')

    def generate(self):
        """
        Generate the output and send it out the Activity port.
        """
        self.verbose("Generating a new pattern")

        # JABALERT: What does the [:] achieve here?  Copying the
        # values, instead of the pointer to the array?  Is that
        # guaranteed?
        self.activity[:] = self.input_generator()

        if self.apply_output_fns:
            for of in self.output_fns:
                of(self.activity)
        self.send_output(src_port='Activity',data=self.activity)
                                                        
              
    def start(self):
        assert self.simulation

        if self.period > 0:
            # if it has a positive period, then schedule a repeating event to trigger it
            e=FunctionEvent(0,self.generate)
            now = self.simulation.time()
            self.simulation.enqueue_event(PeriodicEventSequence(now+self.phase,self.period,[e]))

    def input_event(self,conn,data):
        raise NotImplementedError

        

class SequenceGeneratorSheet(GeneratorSheet):
    """
    Sheet that generates a timed sequence of patterns.

    This sheet will repeatedly generate the input_sequence, with the
    given onsets.  The sequence is repeated every self.period time
    units.  If the total length of the sequence is longer than
    self.period, a warning is issued and the sequence repeats
    immediately after completion.
    """
    
    input_sequence = param.List(default=[],
          doc="""The sequence of patterns to generate.  Must be a list of
          (onset,generator) tuples. An empty list defaults to the
          single tuple: (0,self.input_generator), resulting in
          identical behavior to an ordinary GeneratorSheet.""")


    def __init__(self,**params):
        super(SequenceGeneratorSheet,self).__init__(**params)
        if not self.input_sequence:
            self.input_sequence = [(0,self.input_generator)]
            
    def start(self):
        assert self.simulation

        event_seq = []
        for delay,gen in self.input_sequence:
            event_seq.append(FunctionEvent(delay,self.set_input_generator,gen))
            event_seq.append(FunctionEvent(0,self.generate))
        now = self.simulation.time()
        self.event = PeriodicEventSequence(now+self.phase,self.period,event_seq)
        self.simulation.enqueue_event(self.event)


# CEBALERT: ignores sheet mask
def compute_joint_norm_totals(projlist,active_units_mask):
    """
    Compute norm_total for each CF in each projection from a group to
    be normalized jointly.

    Only active units specified by active_units_mask!=0 are processed.
    """
    # Assumes that all Projections in the list have the same r,c size
    assert len(projlist)>=1
    proj  = projlist[0]
    rows,cols = proj.cfs.shape

    for r in range(rows):
        for c in range(cols):
            if active_units_mask[r,c] != 0:
                sums = [p.cfs[r,c].norm_total for p in projlist]
                joint_sum = numpy.add.reduce(sums)
                for p in projlist:
                    p.cfs[r,c].norm_total=joint_sum


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
    TransferFn that will respect this norm_total rather than the strict
    total of the ConnectionField's weights.  At present,
    CFPOF_DivisiveNormalizeL1 and CFPOF_DivisiveNormalizeL1_opt do use
    norm_total; others can be extended to do something similar if
    necessary.

    To enable joint normalization, you can declare that all the
    incoming connections that should be normalized together each
    have a dest_port of:

    dest_port=('Activity','JointNormalize', 'AfferentGroup1'),

    Then all those that have this dest_port will be normalized
    together, as long as an appropriate TransferFn is being used.
    """

    joint_norm_fn = param.Callable(default=compute_joint_norm_totals,doc="""
    Function to use to compute the norm_total for each CF in each
    projection from a group to be normalized jointly.""")

    # JABALERT: Should check that whenever a connection is added to a
    # group, it has the same no of cfs as the existing connections.
    def start(self):
        self._normalize_weights()        

    # CEBALERT: ignores sheet mask
    def _normalize_weights(self,active_units_mask=None):
        """
        Apply the weights_output_fns for every group of Projections.
        
        Only active units as specified by active_units_mask!=0 will
        have their weights normalized (unless active_units_mask is
        None, in which case all units will be processed).
        """
        
        if active_units_mask is None:
            active_units_mask = numpy.ones(self.shape,activity_type)
        
        for key,projlist in self._grouped_in_projections('JointNormalize'):
            if key == None:
                normtype='Individually'
            else:
                normtype='Jointly'
                self.joint_norm_fn(projlist,active_units_mask)

            self.debug(normtype + " normalizing:")

            for p in projlist:
                p.apply_learn_output_fns(active_units_mask)
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

        

class JointNormalizingCFSheet_Continuous(JointNormalizingCFSheet):
    """
    CFSheet that runs continuously, with no 'resting' periods between pattern presentations.
    
    Note that learning occurs only when the time is a whole number.
    """
    def process_current_time(self):
        if self.new_input:
           self.new_input = False
           if(float(topo.sim.time()) % 1.0 == 0.0):
               #self.activate()
               if (self.plastic):
                   self.learn()
           #else:
           self.activate()



__all__ = list(set([k for k,v in locals().items() if isinstance(v,type) and issubclass(v,Sheet)]))
