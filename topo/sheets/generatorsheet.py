"""
GeneratorSheet class.

$Id$
"""
__version__='$Revision$'

import copy

from topo.base.simulation import FunctionEvent, PeriodicEventSequence
from topo.base.functionfamilies import OutputFnParameter,IdentityOF
from topo.base.sheet import Sheet 
from topo.base.sheet import BoundingBox
from topo.misc.utils import NxN

from topo.base.parameterclasses import Number, ListParameter, BooleanParameter

import topo.base.patterngenerator
import topo.patterns.basic


class GeneratorSheet(Sheet):
    """
    Sheet for generating a series of 2D patterns.

    Typically generates the patterns by choosing parameters from a
    random distribution, but can use any mechanism.
    """
    
    src_ports=['Activity']
    
    period = Number(default=1,bounds=(0,None),doc=
        "Delay (in Simulation time) between generating new input patterns.")
    
    phase  = Number(default=0.05,doc=
        """
        Delay after the start of the Simulation (at time zero) before
        generating an input pattern.  For a clocked, feedforward simulation, 
        one would typically want to use a small nonzero phase and use delays less
        than the user-visible step size (typically 1.0), so that inputs are
        generated and processed before this step is complete.
        """)
    
    input_generator = topo.base.patterngenerator.PatternGeneratorParameter(doc=
        "Specifies a particular PatternGenerator type to use when creating patterns.")

    output_fn = OutputFnParameter(doc="""
        Output function to apply (if apply_output_fn is true) to this Sheet's activity.""")
    
    apply_output_fn=BooleanParameter(default=True,doc="""
        Whether to apply the output_fn after computing an Activity matrix.""")
    
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

        # CEBHACKALERT: should the bounds really be taken from the
        # GeneratorSheet itself? What if someone wants to specify that
        # a pattern should only be drawn in some smaller bounds?
        # So this line should be removed, and examples files should
        # set the bounds on the input_generators if they don't
        # already, right?
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

        ### JABALERT: Would it be more efficient to re-use the same
        ### bit of memory each time?  This way allocates a new block
        ### of memory each time a pattern is drawn...
        self.activity = self.input_generator()
        assert self.shape==self.activity.shape, \
               "Generated pattern shape %s does not match sheet shape %s." % \
               (self.shape,self.activity.shape)

        if self.apply_output_fn:
            self.output_fn(self.activity)
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
    
    input_sequence = ListParameter(default=[(1,topo.patterns.basic.Gaussian())],
          doc="""The sequence of patterns to generate. 
          Must be a list of (onset,generator) tuples.""")


    def start(self):
        assert self.simulation

        event_seq = []
        for delay,gen in self.input_sequence:
            event_seq.append(FunctionEvent(delay,self.set_input_generator,gen))
            event_seq.append(FunctionEvent(0,self.generate))
        now = self.simulation.time()
        seq = PeriodicEventSequence(now+self.phase,self.period,event_seq)
        self.simulation.enqueue_event(seq)
