"""
sheet for randomly generating gaussian inputs

$Id$
"""

import debug
from kernelfactory import *
import random
from simulator import EventProcessor
from sheet import Sheet
from utils import NxN


from Numeric import *
from pprint import pprint,pformat
from params import setup_params

class GaussianSheet(Sheet):

    period = 1
    phase = 0

    x = (random.uniform,-1,1)

    def __init__(self,**config):
        Sheet.__init__(self,**config)
        setup_params(self,GaussianSheet,**config)

        self.kernel =  KernelFactory(kernel_bounds=self.bounds,
                                     kernel_density=self.density)


    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.db_print("Received %s input from %s." % (NxN(data.shape),src), debug.VERBOSE)

        self.db_print("Generating a new kernel...",debug.VERBOSE)

        self.activation = self.kernel.create(x=GaussianSheet.x,
                                             y=GaussianSheet.y,
                                             theta=GaussianSheet.theta,
                                             width=GaussianSheet.width,
                                             height=GaussianSheet.height)
  
        self.send_output(data=self.activation)
        self.db_print("Sending %s output." % NxN(self.activation.shape))


if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver

    GaussianSheet.density = 10000
    GaussianSheet.period = 10.0
    GaussianSheet.phase = 3.0

    GaussianSheet.x = (random.gauss,0,0.5)
    GaussianSheet.y = (random.uniform,-0.5,0.5)
    GaussianSheet.theta = (random.uniform,-3.1415926,3.1415926)
    GaussianSheet.width = (random.uniform,-1,1)
    GaussianSheet.height = (random.uniform,-1,1)

    s = Simulator()
    g = GaussianSheet()
    save = ImageSaver()

    s.connect(src=g,dest=save)
    s.run()
