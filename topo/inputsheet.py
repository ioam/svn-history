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

    period = 1
    phase = 0

    x = (random.uniform,-1,1)

    def __init__(self,**config):
        Sheet.__init__(self,**config)

        self.kernel =  KernelFactory(bounds=self.bounds,
                                     density=self.density,
                                     x=self.x,
                                     y=self.y,
                                     theta=self.theta,
                                     width=self.width,
                                     height=self.height)

    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.period)

        # first event is special
        self.simulator.enqueue_event_rel(self.phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))

        self.verbose("Generating a new kernel...")

        self.activation = self.kernel.create( )
  
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))

# TODO: these should all be mix-ins

class GaussianSheet(InputSheet):

    def __init__(self, **config):
        InputSheet.__init__(self,**config)
        self.kernel.function = gaussian


class UniformRandomSheet(InputSheet):

    def __init__(self, **config):
        InputSheet.__init__(self,**config)
        self.kernel.function = uniform_random

class SineGratingSheet(InputSheet):

    def __init__(self, **config):
        InputSheet.__init__(self,**config)
        self.kernel.function = sine_grating

if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver

    def random_gaussian(mean, std):
        while( 1 ):
            yield random.gauss(mean, std)

    def random_uniform(lower, upper):
        while( 1 ):        
            yield random.uniform(lower, upper)

    #GaussianSheet.density = 81 
    GaussianSheet.density = 10000
    GaussianSheet.period = 10.0
    GaussianSheet.phase = 3.0

    GaussianSheet.x = random_gaussian(0,0.5)
    GaussianSheet.y = random_uniform(-0.5,0.5)
    GaussianSheet.theta = random_uniform(-3.1415926,3.1415926)
    GaussianSheet.width = random_uniform(0,1)
    GaussianSheet.height = random_uniform(0,1)


    s = Simulator()
    g = GaussianSheet()
    save = ImageSaver()

    s.connect(src=g,dest=save)
    s.run()
