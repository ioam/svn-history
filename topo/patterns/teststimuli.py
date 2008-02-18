"""
Patterns based on patches of Sine Gratings as used in experiments.

$Id$
"""
__version__='$Revision$'

### JABALERT: These classes should not be necessary, if we can provide a way
### to control the parameters of subparts of Composite objects
### more easily (e.g. in the Test Pattern window, or when
### measuring tuning curves).

import numpy

from topo.patterns.basic import SineGrating, Disk, Ring
from math import pi, sin, cos, sqrt
from numpy.oldnumeric import around,bitwise_and,sin,add,Float,bitwise_or
from numpy import alltrue

from topo.base.parameterizedobject import ParamOverrides
from topo.base.parameterclasses import Integer, Number, Parameter, Enumeration
from topo.base.parameterclasses import ListParameter
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant

from topo.misc.patternfns import gaussian,gabor,line,disk,ring
from topo.misc.numbergenerators import UniformRandom
from topo.base.parameterclasses import BooleanParameter



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

       
    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)
      	bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        orientation=params['orientation']
        size=params['size']
        phase=params['phase']
        frequency=params['frequency']
        aspect_ratio=params['aspect_ratio']
        smoothing=params['smoothing']
      
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


    def __call__(self,**params_to_override):
        # CEBALERT: missing check_params (should upgrade/remove/decide what to do with check_params anyway)
        params = ParamOverrides(self,params_to_override)

      	bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        orientation=params['orientation']
        size=params['size']
        phase=params['phase']
        frequency=params['frequency']
        aspect_ratio=params['aspect_ratio']
        smoothing=params['smoothing']
        thickness=params['thickness']
      
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
    
       
    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)
      	bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scale=params['scale']
        offset=params['offset']
        size=params['size']
        phase=params['phase']
        frequency=params['frequency']
        aspect_ratio=params['aspect_ratio']
        smoothing=params['smoothing']
        thickness=params['thickness']
        orientationcentre=params['orientationcentre']
        orientationsurround=params['orientationsurround']
        size_centre=params['size_centre']
        size_surround=params['size_surround']
      
        input_1=SineGratingDisk(phase=phase, frequency=frequency,orientation=orientationcentre, scale=scale, offset=offset,
                                aspect_ratio=aspect_ratio,smoothing=0.0,x=x, y=y,size=size_centre)
        input_2=SineGratingRing(phase=phase, frequency=frequency, orientation=orientationsurround, scale=scale, offset=offset,
                                thickness=thickness,aspect_ratio=aspect_ratio,smoothing=0.0,x=x, y=y, size=size_surround)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.add.reduce(patterns)
        return image_array
