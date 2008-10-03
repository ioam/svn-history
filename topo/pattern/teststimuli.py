"""
Composite patterns such as patches of sine gratings as used in
psychophysical or physiological experiments.

$Id$
"""
__version__='$Revision$'

### JABALERT: These classes should not be necessary, if we can provide a way
### to control the parameters of subparts of Composite objects
### more easily (e.g. in the Test Pattern window, or when
### measuring tuning curves).

from math import pi, sin, cos, sqrt
import numpy
from numpy.oldnumeric import around,bitwise_and,sin,add,Float,bitwise_or
from numpy import alltrue

from .. import param
from ..param.parameterized import ParamOverrides

from topo.base.patterngenerator import PatternGenerator
# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant
from topo.pattern.basic import SineGrating, Disk, Ring, Rectangle
from topo.misc.patternfn import gaussian,gabor,line,disk,ring
from topo.misc.numbergenerator import UniformRandom

# Simpler versions using the mask instead:
#class SineGratingDisk_m(SineGrating):
#    """2D sine grating pattern generator with a circular mask."""
#    mask_shape = param.Parameter(default=Disk(smoothing=0))
#
#class SineGratingRectangle_m(SineGrating):
#    """2D sine grating pattern generator with a rectangular mask."""
#    mask_shape = param.Parameter(default=Rectangle())
#
#class SineGratingRing_m(SineGrating):
#    """2D sine grating pattern generator with a ring-shaped mask."""
#    mask_shape = param.Parameter(default=Ring(smoothing=0))


class SineGratingDisk(PatternGenerator):
    """A sine grating masked by a circular disk so that only a round patch is visible."""
 
    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
        "Ratio of width to height; size*aspect_ratio gives the width of the disk.")

    size  = param.Number(default=0.5,doc="Top to bottom height of the disk")
    
    smoothing = param.Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")

    phase  = param.Number(default=1.0, doc="phase of the sine grating")

    frequency  = param.Number(default=2.4,doc="frequency of the sine grating")

       
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


class SineGratingRectangle(PatternGenerator):
    """A sine grating masked by a rectangle so that only a rectangular patch is visible"""
 
    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc="""Ratio of width to height
        size*aspect_ratio gives the width of the rectangle.""")

    size  = param.Number(default=0.5,doc="Top to bottom height of the rectangle")
    
    phase  = param.Number(default=1.0, doc="Phase of the sine grating")

    frequency  = param.Number(default=2.4,doc="Frequency of the sine grating")

       
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
              
        input_1=SineGrating(phase=phase, frequency=frequency, orientation=orientation, scale=scale, offset=offset)
        input_2=Rectangle(aspect_ratio=aspect_ratio,x=x, y=y,size=size,scale=scale, offset=offset)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.minimum.reduce(patterns)
        return image_array



class SineGratingRing(PatternGenerator):
    """A sine grating masked by a ring so that only the ring is visible."""

    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc=
                           "Ratio of width to height; size*aspect_ratio gives the overall width.")

    thickness = param.Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.60,doc="Thickness (line width) of the ring.")

    size  = param.Number(default=0.5,doc="Top to bottom height of the disk")
    
    smoothing = param.Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,doc="Width of the Gaussian fall-off")

    phase  = param.Number(default=1.0, doc="phase of the sine grating")

    frequency  = param.Number(default=2.4,doc="frequency of the sine grating")


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




class OrientationContrastPattern(SineGratingRing):
    """A sine grating ring and a disk with parameters (orientation, size, scale and offset) which can be changed independantly"""
 
    orientationcentre= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                               precedence=0.50, doc="Frequency of the sine grating.")

    orientationsurround= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                                   precedence=0.50, doc="Frequency of the sine grating.")

    size_centre= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                               precedence=0.50, doc="Frequency of the sine grating.")

    size_surround= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                                   precedence=0.50, doc="Frequency of the sine grating.")

    scalecentre= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                               precedence=0.50, doc="Frequency of the sine grating.")

    scalesurround= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                                   precedence=0.50, doc="Frequency of the sine grating.")


    offsetcentre= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                               precedence=0.50, doc="Frequency of the sine grating.")

    offsetsurround= param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,10.0),
                                   precedence=0.50, doc="Frequency of the sine grating.")
       
    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)
      	bounds = params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        scalesurround=params['scalesurround']
        offsetsurround=params['offsetsurround']
        scalecentre=params['scalecentre']
        offsetcentre=params['offsetcentre']
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
      
        input_1=SineGratingDisk(phase=phase, frequency=frequency,orientation=orientationcentre, scale=scalecentre, offset=offsetcentre,
                                aspect_ratio=aspect_ratio,smoothing=0.0,x=x, y=y,size=size_centre)
        input_2=SineGratingRing(phase=phase, frequency=frequency, orientation=orientationsurround, scale=scalesurround, offset=offsetsurround,
                                thickness=thickness,aspect_ratio=aspect_ratio,smoothing=0.0,x=x, y=y, size=size_surround)
        
        patterns = [input_1(xdensity=xdensity,ydensity=ydensity,bounds=bounds),
                            input_2(xdensity=xdensity,ydensity=ydensity,bounds=bounds)]
                      
        image_array = numpy.add.reduce(patterns)
        return image_array
