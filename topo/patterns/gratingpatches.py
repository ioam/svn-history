"""
Patterns based on patches of Sine Gratings as used in experiments.

$Id$
"""
__version__='$$'

### JABALERT: These classes should not be necessary, if we can provide a way
### to control the parameters of subparts of Composite objects
### more easily (e.g. in the Test Pattern window, or when
### measuring tuning curves).

import numpy

from topo.patterns.basic import SineGrating, Disk, Ring
from math import pi, sin, cos, sqrt
from numpy.oldnumeric import around,bitwise_and,sin,add,Float,bitwise_or
from numpy import alltrue

from topo.base.parameterclasses import Integer, Number, Parameter, Enumeration
from topo.base.parameterclasses import DynamicNumber, ListParameter
from topo.base.functionfamilies import OutputFnParameter
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant

from topo.misc.patternfns import gaussian,gabor,line,disk,ring
from topo.misc.utils import wrap
from topo.misc.numbergenerators import UniformRandom




class SineGratingDisk(PatternGenerator):
    """A sine grating masked by a circular disk so that only a round patch is visible."""
 
    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the disk.")

    size  = Number(default=0.5,doc="Top to bottom height of the disk")
    
    smoothing = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")

    phase  = Number(default=1.0, doc="phase of the sine grating")

    frequency  = Number(default=2.4,doc="frequency of the sine grating")


    def __init__(self,**params):
        super(SineGratingDisk,self).__init__(**params)
       
    def __call__(self,**params):
      	bounds = params.get('bounds',self.bounds)
        xdensity=params.get('xdensity',self.xdensity)
        ydensity=params.get('ydensity',self.ydensity)
        x=params.get('x',self.x)
        y=params.get('y',self.y)
        scale=params.get('scale',self.scale)
        offset=params.get('offset',self.offset)
        orientation=params.get('orientation',self.orientation)
        size=params.get('size',self.size)
        phase=params.get('phase',self.phase)
        frequency=params.get('frequency',self.frequency)
        aspect_ratio=params.get('aspect_ratio',self.aspect_ratio)
        smoothing=params.get('smoothing',self.smoothing)

      
        input_1=SineGrating(phase=phase, frequency=frequency, orientation=orientation, scale=scale, offset=offset)
        input_2=Disk(aspect_ratio=aspect_ratio,smoothing=smoothing,x=x, y=y,size=size,scale=scale, offset=offset)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.minimum.reduce(patterns)
        return image_array



class SineGratingRing(PatternGenerator):
    """A sine grating masked by a ring so that only the ring is visible."""

    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
                           "Ratio of width to height; size*aspect_ratio gives the overall width.")

    thickness = Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.60,doc="Thickness (line width) of the ring.")

    size  = Number(default=0.5,doc="Top to bottom height of the disk")
    
    smoothing = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")

    phase  = Number(default=1.0, doc="phase of the sine grating")

    frequency  = Number(default=2.4,doc="frequency of the sine grating")


    def __init__(self,**params):
        super(SineGratingRing,self).__init__(**params)
       
    def __call__(self,**params):
      	bounds = params.get('bounds',self.bounds)
        xdensity=params.get('xdensity',self.xdensity)
        ydensity=params.get('ydensity',self.ydensity)
        x=params.get('x',self.x)
        y=params.get('y',self.y)
        scale=params.get('scale',self.scale)
        offset=params.get('offset',self.offset)
        orientation=params.get('orientation',self.orientation)
        size=params.get('size',self.size)
        phase=params.get('phase',self.phase)
        frequency=params.get('frequency',self.frequency)
        aspect_ratio=params.get('aspect_ratio',self.aspect_ratio)
        smoothing=params.get('smoothing',self.smoothing)
        thickness=params.get('thickness', self.thickness)
      
        input_1=SineGrating(phase=phase, frequency=frequency, orientation=orientation, scale=scale, offset=offset)
        input_2=Ring(thickness=thickness,aspect_ratio=aspect_ratio,smoothing=smoothing,x=x, y=y,size=size,scale=scale, offset=offset)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.minimum.reduce(patterns)
        return image_array




class OrientationContrastPattern (SineGratingRing):
    """A sine grating ring and a disk with parameters (orientation and size) which can be changed independantly"""
 
    orientationcentre= Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                               precedence=0.50, doc="Frequency of the sine grating.")

    orientationsurround= Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                                   precedence=0.50, doc="Frequency of the sine grating.")

    size_centre= Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                               precedence=0.50, doc="Frequency of the sine grating.")

    size_surround= Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                                   precedence=0.50, doc="Frequency of the sine grating.")
    
    def __init__(self,**params):
        super(OrientationContrastPattern,self).__init__(**params)
       
    def __call__(self,**params):
      	bounds = params.get('bounds',self.bounds)
        xdensity=params.get('xdensity',self.xdensity)
        ydensity=params.get('ydensity',self.ydensity)
        x=params.get('x',self.x)
        y=params.get('y',self.y)
        scale=params.get('scale',self.scale)
        offset=params.get('offset',self.offset)
        phase=params.get('phase',self.phase)
        frequency=params.get('frequency',self.frequency)
        aspect_ratio=params.get('aspect_ratio',self.aspect_ratio)
        smoothing=params.get('smoothing',self.smoothing)
        thickness=params.get('thickness', self.thickness)
        orientationcentre=params.get('orientationcentre',self.orientationcentre)
        orientationsurround=params.get('orientationsurround',self.orientationsurround)
        size_centre=params.get('size_centre',self.size_centre)
        size_surround=params.get('size_surround',self.size_surround)
      
        input_1=SineGratingDisk(phase=phase, frequency=frequency,orientation=orientationcentre, scale=scale, offset=offset,
                                aspect_ratio=aspect_ratio,smoothing=0.0,x=x, y=y,size=size_centre)
        input_2=SineGratingRing(phase=phase, frequency=frequency, orientation=orientationsurround, scale=scale, offset=offset,
                                thickness=thickness,aspect_ratio=aspect_ratio,smoothing=0.0,x=x, y=y, size=size_surround)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.add.reduce(patterns)
        return image_array
