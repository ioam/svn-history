"""
sheet for randomly generating inputs

$Id$
"""


from sheet import Sheet 
from utils import NxN

from sheet import BoundingBox
from params import *
from kernelfactory import UniformRandomFactory

class InputSheet(Sheet):

    period = Parameter(default=1)
    phase  = Parameter(default=0)

    theta = Parameter(default=0)

    input_generator = Parameter(default=UniformRandomFactory)
    
    def __init__(self,**params):
        super(InputSheet,self).__init__(**params)
        self.init_input_generator(self.input_generator)


    def init_input_generator(self,new_ig):
        """
        Allow assignment of a new input generator to this InputSheet.
        Only one generator is linked at a time, so if more than one is
        going to be used, the code driving the sheet needs to keep
        tabs on which one is being used.
        """
        self.input_generator = new_ig
        self.input_generator.bounds = self.bounds
        self.input_generator.density = self.density
        

    def get_input_generator(self):
        """
        Return the existing input_generator Parameter.  If a temporary
        input generator is going to be used, then this function will
        be needed so that the old generator can be replaced when done.
        """
        return input_generator
    
        
    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))
        self.verbose("Generating a new kernel...")

    
        # TODO: Pass a dictionary to this function to avoid having all of the
        # subclasses below
        self.activation = self.input_generator()
        
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))
