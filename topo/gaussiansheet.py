"""
sheet for randomly generating gaussian inputs

$Id$
"""

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
        super(GaussianSheet,self).__init__(**config)
        self.kernel =  KernelFactory(kernel_bounds=self.bounds,
                                     kernel_density=self.density)


    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))

        self.verbose("Generating a new kernel...")

        self.activation = self.kernel.create(x=GaussianSheet.x,
                                             y=GaussianSheet.y,
                                             theta=GaussianSheet.theta,
                                             width=GaussianSheet.width,
                                             height=GaussianSheet.height)
  
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))


if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver
    import base

    base.print_level = base.VERBOSE

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
