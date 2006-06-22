"""
GeneratorSheet class.

$Id$
"""
__version__='$Revision$'

from topo.base.simulation import EPConnectionEvent
from topo.base.sheet import Sheet 
from topo.base.sheet import BoundingBox

from topo.misc.utils import NxN

from topo.base.parameterclasses import Number, Dynamic

import topo.base.patterngenerator


class GeneratorSheet(Sheet):
    """
    Sheet for generating a series of 2D patterns.

    Typically generates the patterns by choosing parameters from a
    random distribution, but can use any mechanism.
    """
    
    dest_ports=['Trigger']

    period = Number(default=1,doc=
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

               
    def pop_input_generator(self):
        """
        Discard the current input_generator, and retrieve the previous one from the stack.

        Warns if no input_generator is available on the stack.
        """
        if len(self.input_generator_stack) >= 1:
            self.set_input_generator(self.input_generator_stack.pop())
        else:
            ParameterizedObject().warning('There is no previous input generator to restore.')

               
    def start(self):
        assert self.simulation

        # connect self<->self (for repeating)
        conn=self.simulation.connect(self.name,self.name,delay=self.period,dest_port='Trigger',name='Trigger')

        # first event is special
        e=EPConnectionEvent(self.phase+topo.sim.time(),conn)
        self.simulation.enqueue_event(e)

    def input_event(self,conn,data):
        self.verbose("Time " + str(self.simulation.time()) + ":" +
                     " Receiving input from " + str(conn.src.name) +
                     " on dest_port " + str(conn.dest_port) +
                     " via connection " + conn.name + ".")
        self.verbose("Time %0.4f: Generating a new pattern" % (self.simulation.time()))
        self.activity = self.input_generator()
        self.send_output(data=self.activity)
