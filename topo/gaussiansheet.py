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

        # TODO: we need to recieve the size of the kernel from somewhere
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
        self.activation = self.kernel.get_kernel(x=apply(self.x[0],self.x[1:]),
                                                 y=random.uniform(-1,1),
                                                 theta=random.uniform(-3.14159,3.14159)) 
  
        self.send_output(data=self.activation)
        self.db_print("Sending %s output." % NxN(self.activation.shape))


if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver

    GaussianSheet.density = 10000
    GaussianSheet.period = 10.0
    GaussianSheet.phase = 3.0
    GaussianSheet.x = (random.gauss,0,0.5)

    s = Simulator()
    g = GaussianSheet()
    save = ImageSaver()

    s.connect(src=g,dest=save)
    s.run()
