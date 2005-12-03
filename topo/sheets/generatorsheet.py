"""
GeneratorSheet class.

$Id$
"""
__version__='$Revision$'

from topo.base.sheet import Sheet 
from topo.base.sheet import BoundingBox

from topo.base.utils import NxN

from topo.base.parameter import Parameter, Dynamic

from topo.base.patterngenerator import ConstantGenerator

from topo.patterns.basic import PatternGeneratorParameter


class GeneratorSheet(Sheet):
    """
    Sheet for generating a series of 2D patterns.

    Typically generates the patterns by choosing parameters from a
    random distribution, but can use any mechanism.
    """
    period = Parameter(default=1)
    phase  = Parameter(default=0)

    input_generator = PatternGeneratorParameter(default=ConstantGenerator())
    
    def __init__(self,**params):
        super(GeneratorSheet,self).__init__(**params)
        self.input_generator_stack = []
        self.set_input_generator(self.input_generator)


    def set_input_generator(self,new_ig,push_existing=False):
        """
        Set the input_generator, overwriting the existing one by default.

        If push_existing is false, the existing input_generator is
        discarded permanently.  Otherwise, the existing one is put
        onto a stack, and can later be restored by calling
        pop_input_generator.
        """

        if push_existing:
            push_input_generator(self.input_generator)

        self.input_generator = new_ig
        self.input_generator.bounds = self.bounds
        self.input_generator.density = self.density
        

    def push_input_generator(self):
        """Push the current input_generator onto a stack for future retrieval."""
        self.input_generator_stack.append(self.input_generator)

               
    def pop_input_generator(self):
        """
        Discard the current input_generator, and retrieve the previous one from the stack.

        Warns if no input_generator is available on the stack.
        """
        if len(self.input_generator_stack) >= 1:
            self.set_input_generator(self.input_generator_stack.pop())
        else:
            TopoObject().warning('There is no previous input generator to restore.')

               
    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activity)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))
        self.verbose("Generating a new pattern...")

        self.activity = self.input_generator()
        
        self.send_output(data=self.activity)
        self.verbose("Sending %s output at time %d." % (NxN(self.activity.shape),self.simulator.time()))
