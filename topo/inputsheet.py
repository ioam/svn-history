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

    sheet_period = Parameter(default=1)
    sheet_phase  = Parameter(default=0)

    theta = Parameter(default=0)

    input_generator = Parameter(default=UniformRandomFactory)
    
    def __init__(self,**params):
        super(InputSheet,self).__init__(**params)
        self.input_generator.bounds = self.bounds
        self.input_generator.density = self.density
        
    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.sheet_period)

        # first event is special
        self.simulator.enqueue_event_rel(self.sheet_phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))
        self.verbose("Generating a new kernel...")

    
        # TODO: Pass a dictionary to this function to avoid having all of the
        # subclasses below
        self.activation = self.input_generator()
        
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))
