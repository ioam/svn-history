"""
sheet for randomly generating inputs

$Id$
"""

from kernelfactory import *
import random
from simulator import EventProcessor
from sheet import Sheet 
from utils import NxN

from Numeric import *
from pprint import pprint,pformat
from params import Parameter

class InputSheet(Sheet):

    period = Parameter(default=1)
    phase = Parameter(default=0)

    x = Parameter(default=0)

    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))

        self.verbose("Generating a new kernel...")

        self.activation = self.create( )
  
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))

class GaussianSheet(InputSheet, GaussianKernelFactory):
    pass        


#class UniformRandomSheet(InputSheet, UniformRandomSheet):
#    pass

class SineGratingSheet(InputSheet, SineGratingKernelFactory):
    pass

class GaborSheet(InputSheet, GaborKernelFactory):
    pass


if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver

    # BUG?: these give errors now:

    #GaussianSheet.density = 81 
    #GaussianSheet.density = 10000
    #GaussianSheet.period = 10.0
    #GaussianSheet.phase = 3.0

    #GaussianSheet.x = lambda:random.gauss(0,0.5)
    #GaussianSheet.y = lambda:random.uniform(-0.5,0.5)
    #GaussianSheet.theta  = lambda:random.uniform(-3.1415926,3.1415926)
    #GaussianSheet.width  = lambda:random.uniform(0,1)
    #GaussianSheet.height = lambda:random.uniform(0,1)


    s = Simulator()
    g = GaussianSheet(density=10000, 
                      period=10.0, 
                      phase=3.0,
                      x = lambda:random.gauss(0,0.5),
                      y = lambda:random.gauss(0,0.5),
                      theta  = lambda:random.uniform(-3.1415926, 3.1415926),
                      width  = lambda:random.uniform(0,1),
                      height = lambda:random.uniform(0,1))
    save = ImageSaver()

    s.connect(src=g,dest=save)
    s.run()
