"""
Simple two-dimensional mathematical or geometrical pattern generators.

$Id$
"""
__version__='$Revision$'

from math import pi
from Numeric import around,bitwise_and,sin,Float

from topo.base.parameter import Number
from topo.base.patternfns import gaussian,gabor,line,disk,ring
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import ConstantGenerator


# CEB:
# I don't understand why params.get() is used as it is here and
# elsewhere.
# E.g. how would "self.pattern_x" alone be any different from
# "params.get('pattern_x', self.pattern_x)"?


class GaussianGenerator(PatternGenerator):
    """2D Gaussian pattern generator."""
    
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gaussian( params.get('pattern_x',self.pattern_x), 
                         params.get('pattern_y',self.pattern_y), 
                         params.get('width',self.width), 
                         params.get('height',self.height)) 


class SineGratingGenerator(PatternGenerator):
    """2D sine grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        """
        Return a sine grating pattern (two-dimensional sine wave).
        """
        y          = params.get('pattern_y',self.pattern_y)
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return 0.5 + 0.5*sin(frequency*2*pi*y + phase)        



class GaborGenerator(PatternGenerator):
    """2D Gabor pattern generator."""
    
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gabor( params.get('pattern_x',self.pattern_x),
                      params.get('pattern_y',self.pattern_y),
                      params.get('width',self.width),
                      params.get('height',self.height),
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  


class LineGenerator(PatternGenerator):
    """2D line pattern generator."""

    # CEBHACKALERT:
    # Set smoothing to zero for the cfsom_example and you can
    # see a problem with lines. The problem is either in
    # the line() function, the generation of the matrices
    # used to draw it, or just in the display; I have to look to
    # see which.

    thickness   = Number(default=0.006,bounds=(0.0,None),softbounds=(0.0,0.075))
    smoothing = Number(default=0.05,bounds=(0.0,None),softbounds=(0.0,0.075))

    # CEBHACKALERT:
    # scale does not need to be here. For the tutorial, having this scale
    # allows users to see patchy responses to a line without needing to
    # adjust it themselves.
    scale = Number(default=0.7,softbounds=(0.0,2.0))
    
    def function(self,**params):
        return line( params.get('pattern_y',self.pattern_y), 
                           params.get('thickness',self.thickness),
                           params.get('smoothing',self.smoothing))


class DiskGenerator(PatternGenerator):
    """2D disk pattern generator."""

    width  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    smoothing = Number(default=0.07,bounds=(0.0,None),softbounds=(0.0,0.5))
    
    def function(self,**params):
        return disk( params.get('pattern_x',self.pattern_x), 
                           params.get('pattern_y',self.pattern_y), 
                           params.get('width',self.width),
                           params.get('height',self.height),
                           params.get('smoothing',self.smoothing))  


class RingGenerator(PatternGenerator):
    """2D ring pattern generator."""

    # CEBALERT:
    # defaults make it look like a disk
    
    thickness   = Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5))
    width  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    smoothing = Number(default=0.07,bounds=(0.0,None),softbounds=(0.0,0.5))

    def function(self,**params):
        return ring(params.get('pattern_x',self.pattern_x), 
                          params.get('pattern_y',self.pattern_y),
                          params.get('width',self.width),
                          params.get('height',self.height),
                          params.get('thickness',self.thickness),
                          params.get('smoothing',self.smoothing))  


class RectangleGenerator(PatternGenerator):
    """2D rectangle pattern generator."""
    
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.4,bounds=(0.0,None),softbounds=(0.0,1.0))

    # We will probably want to add Fuzzy-style anti-aliasing to this,

    def function(self,**params):
        width = params.get('width',self.width)
        height= params.get('height',self.height)
        return bitwise_and(abs(params.get('pattern_x',self.pattern_x))<=width/2.0,
                           abs(params.get('pattern_y',self.pattern_y))<=height/2.0)


class SquareGratingGenerator(PatternGenerator):
    """2D squarewave grating pattern generator."""
    
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi))

    # We will probably want to add anti-aliasing to this,
    # and there might be an easier way to do it than by
    # cropping a sine grating.

    def function(self,**params):
        """
        Return a square-wave grating (alternating black and white bars).
        """
        y          = params.get('pattern_y',self.pattern_y)
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return around(0.5 + 0.5*sin(frequency*2*pi*y + phase))

