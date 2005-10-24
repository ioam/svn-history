"""
Sheet for generating a series of patterns, e.g. by choosing
parameters from a random distribution.

$Id$
"""

from topo.base.sheet import Sheet 
from topo.base.sheet import BoundingBox

from topo.base.utils import NxN
import copy

from topo.base.parameter import Parameter, Dynamic

from topo.base.patterngenerator import ConstantGenerator

class GeneratorSheet(Sheet):

    period = Parameter(default=1)
    phase  = Parameter(default=0)

    theta = Parameter(default=0)

    input_generator = Parameter(default=ConstantGenerator())
    
    def __init__(self,**params):
        super(GeneratorSheet,self).__init__(**params)

        self.input_generator_stack = []  # maybe this should be a class
                                         # variable like input_generator?
        self.set_input_generator(self.input_generator)


    def set_input_generator(self,new_ig):
        """
        Allow assignment of a new pattern generator to this
        GeneratorSheet.  Only one generator is linked at a time, so if
        more than one is going to be used, the code driving the sheet
        needs to keep tabs on which one is being used.
        """

        # add current generator to stack
        #self.input_generator_stack.append(self.input_generator)
        # set generator to be the one one
        self.input_generator = new_ig
        
        self.input_generator.bounds = self.bounds
        ### JABHACKALERT!
        ###
        ### Why is this hack necessary?  How can we eliminate it?
        ###
        # PATTERNGENERATOR HACK PATCH TO GET THE X/Y RIGHT OUTSIDE OF KFS.
        (l,b,r,t) = self.bounds.aarect().lbrt()
        self.input_generator.bounds = BoundingBox(points=((b,l),(t,r)))
        self.input_generator.density = self.density


    def save_current_input_generator(self):
        """
        There's a stack of input_generators; you can add the current
        input_generator to this stack for later retrieval with
        restore_previous_input_generator().
        """
        self.input_generator_stack.append(self.input_generator)


    def restore_previous_input_generator(self):
        """
        Get an input_generator off the top of the stack of input_generators
        and set it to be the current input_generator (if there were any -
        otherwise do nothing).
        """
        if len(self.input_generator_stack) >= 1:
            self.set_input_generator(self.input_generator_stack.pop())
        else:
            TopoObject().warning('There was no previous input generator.')

               
    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activity)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))
        self.verbose("Generating a new pattern...")

        ### JABHACKALERT!
        ###
        ### What does this comment mean?  Either remove it or clarify it.
        ###
        # TODO: Pass a dictionary to this function to avoid having all of the
        # subclasses below
        self.activity = self.input_generator()
        
        self.send_output(data=self.activity)
        self.verbose("Sending %s output at time %d." % (NxN(self.activity.shape),self.simulator.time()))
