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

    sheet_period = Parameter(default=1)
    sheet_phase  = Parameter(default=0)

    bounds  = Parameter(default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))))
    density = Parameter(default=10000)
    
    def start(self):
        assert self.simulator

        # connect self<->self (for repeating)
        self.simulator.connect(src=self,dest=self,delay=self.sheet_period)

        # first event is special
        self.simulator.enqueue_event_rel(self.sheet_phase,self,self,data=self.activation)

    def input_event(self,src,src_port,dest_port,data):
        self.verbose("Received %s input from %s." % (NxN(data.shape),src))
        self.verbose("Generating a new kernel...")

        self.activation = produce_value(self.function)
        
        self.send_output(data=self.activation)
        self.message("Sending %s output." % NxN(self.activation.shape))


"""
Gassian Kernel Generating Sheet
"""

class GaussianSheet(InputSheet):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)
    height  = Parameter(default=1)

    # Pass set up a function to run using lambdas. We need to specify self as a
    # parameter. Should not be a parameter because we don't want the user to
    # change it.

    function = lambda self:gaussian( self.bounds,
                                     self.density,
                                     self.x, 
                                     self.y, 
                                     self.theta, 
                                     self.width, 
                                     self.height )

"""
Sine Grating Kernel Generating Sheet
"""

class SineGratingSheet(InputSheet):

    x         = Parameter(default=0)
    y         = Parameter(default=0)
    theta     = Parameter(default=0)
    frequency = Parameter(default=1)
    phase     = Parameter(default=0)

    function = lambda self:sine_grating( self.bounds,
                                         self.density,
                                         self.x,
                                         self.y,
                                         self.theta,
                                         self.frequency, 
                                         self.phase )


"""
Gabor Kernel Generating Sheet
"""

class GaborSheet(InputSheet):

    x        = Parameter(default=0)
    y        = Parameter(default=0)
    theta    = Parameter(default=0)
    width    = Parameter(default=2)
    height   = Parameter(default=1)
    frequency = Parameter(default=1)
    phase     = Parameter(default=0)

    function  = lambda self:sine_grating( self.bounds,
                                          self.density,
                                          self.x,
                                          self.y,
                                          self.theta,
                                          self.width,
                                          self.height,
                                          self.frequency,
                                          self.phase ) 

"""
Uniform Random Generating Sheet
"""
  
class UniformRandomSheet(InputSheet):

    function = lambda self:uniform_random( self.bounds,
                                           self.density ) 

"""
Fuzzy Line Generating Sheet
"""

class FuzzyLineSheet(InputSheet):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)

    function = lambda self:fuzzy_line( self.bounds,
                                       self.density,
                                       self.x, 
                                       self.y, 
                                       self.theta, 
                                       self.width ) 


if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver

    GaussianSheet.period = 1.0
    GaussianSheet.x = lambda:random.uniform(-0.5,0.5)
    GaussianSheet.y = lambda:random.uniform(-0.5,0.5)
    GaussianSheet.theta = 3.1415926/4
    GaussianSheet.width = 20
    GaussianSheet.height = 0.2 

    SineGratingSheet.period = 1.0
    SineGratingSheet.x = lambda:random.uniform(-0.5,0.5)
    SineGratingSheet.y = lambda:random.uniform(-0.5,0.5)
    SineGratingSheet.theta = 3.1415926/4
    SineGratingSheet.amplitude = 20
    SineGratingSheet.freguency = 2 

    GaborSheet.period = 1.0
    GaborSheet.x = lambda:random.uniform(-0.5,0.5)
    GaborSheet.y = lambda:random.uniform(-0.5,0.5)
    GaborSheet.theta = 0
    GaborSheet.width =  0.5 
    GaborSheet.height = 0.5 
    
    s  = Simulator()

    g  = GaussianSheet()
    sg = SineGratingSheet()
    ga = GaborSheet() 
    ur = UniformRandomSheet()

    save = ImageSaver()

    s.connect(src=ur,dest=save,dest_port='random')
    s.connect(src=ga,dest=save,dest_port='gabor')
    s.connect(src=sg,dest=save,dest_port='sine_grating')
    s.connect(src=g,dest=save,dest_port='gassian')
    
    s.run(duration=10)
