"""
sheet for randomly generating inputs

$Id$
"""

import kernelfactory
import random
from simulator import EventProcessor
from sheet import Sheet 
from utils import NxN

from Numeric import *
from pprint import pprint,pformat
from sheet import BoundingBox
from params import *

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

    function = lambda self:kernelfactory.gaussian( self.bounds,
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

    function = lambda self:kernelfactory.sine_grating( self.bounds,
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

    function  = lambda self:kernelfactory.gabor( self.bounds,
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

    function = lambda self:kernelfactory.uniform_random( self.bounds,
                                                         self.density ) 

"""
Rectangle Generating Sheet
"""

class RectangleSheet(InputSheet):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)
    heigh   = Parameter(default=1)

    function = lambda self:kernelfactory.rectangle( self.bounds,
                                                    self.density,
                                                    self.x, 
                                                    self.y, 
                                                    self.theta, 
                                                    self.width,
                                                    self.height ) 
"""
Fuzzy Line Generating Sheet
"""

class FuzzyLineSheet(InputSheet):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)

    function = lambda self:kernelfactory.fuzzy_line( self.bounds,
                                                     self.density,
                                                     self.x, 
                                                     self.y, 
                                                     self.theta, 
                                                     self.width ) 

"""
Fuzzy Disk Generating Sheet
"""

class FuzzyDiskSheet(InputSheet):

    x              = Parameter(default=0)
    y              = Parameter(default=0)
    disk_radius    = Parameter(default=0.8)
    gaussian_width = Parameter(default=1)

    function = lambda self:kernelfactory.fuzzy_disk( self.bounds,
                                                     self.density,
                                                     self.x, 
                                                     self.y, 
                                                     self.disk_radius, 
                                                     self.gaussian_width ) 


"""
Fuzzy Ring Generating Sheet
"""

class FuzzyRingSheet(InputSheet):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)

    function = lambda self:kernelfactory.fuzzy_ring( self.bounds,
                                                     self.density,
                                                     self.x, 
                                                     self.y, 
                                                     self.theta, 
                                                     self.width ) 


if __name__ == '__main__':
    from simulator import Simulator
    from image import ImageSaver

    GaussianSheet.x = lambda:random.uniform(-0.5,0.5)
    GaussianSheet.y = lambda:random.uniform(-0.5,0.5)
    GaussianSheet.theta = 3.1415926/4
    GaussianSheet.width = 0.2
    GaussianSheet.height = 0.2 

    SineGratingSheet.x = lambda:random.uniform(-0.5,0.5)
    SineGratingSheet.y = lambda:random.uniform(-0.5,0.5)
    SineGratingSheet.theta = 3.1415926/4
    SineGratingSheet.amplitude = 20
    SineGratingSheet.freguency = 2 

    GaborSheet.x = lambda:random.uniform(-0.5,0.5)
    GaborSheet.y = lambda:random.uniform(-0.5,0.5)
    GaborSheet.theta = 0
    GaborSheet.width =  0.5 
    GaborSheet.height = 0.5 

    FuzzyLineSheet.x = lambda:random.uniform(-0.5,0.5)
    FuzzyLineSheet.x = lambda:random.uniform(-0.5,0.5)
    FuzzyLineSheet.theta = 3.1415926/4
    FuzzyLineSheet.width = 0.2 

    FuzzyDiskSheet.x = 0
    #FuzzyDiskSheet.x = lambda:random.uniform(-0.5,0.5)
    FuzzyDiskSheet.y = 0 
    #FuzzyDiskSheet.y = lambda:random.uniform(-0.5,0.5)
    FuzzyDiskSheet.disk_radius    = 0.3
    FuzzyDiskSheet.gaussian_width = 0.2 

    RectangleSheet.x = lambda:random.uniform(-0.5,0.5)
    RectangleSheet.y = lambda:random.uniform(-0.5,0.5)
    RectangleSheet.theta = 3.1415926/4
    RectangleSheet.width = 0.2 
    RectangleSheet.height = 0.2 

    s  = Simulator()

    gaussian       = GaussianSheet()
    sine_grating   = SineGratingSheet()
    gabor          = GaborSheet() 
    uniform_random = UniformRandomSheet()
    fuzzy_line     = FuzzyLineSheet()
    fuzzy_disk     = FuzzyDiskSheet()
    rectangle      = RectangleSheet()

    save = ImageSaver()

    s.connect(src=rectangle,dest=save,dest_port='rectangle')
    s.connect(src=fuzzy_disk,dest=save,dest_port='fuzzy_disk')
    s.connect(src=fuzzy_line,dest=save,dest_port='fuzzy_line')
    s.connect(src=uniform_random,dest=save,dest_port='random')
    s.connect(src=gabor,dest=save,dest_port='gabor')
    s.connect(src=sine_grating,dest=save,dest_port='sine_grating')
    s.connect(src=gaussian,dest=save,dest_port='gassian')
    
    s.run(duration=10)
