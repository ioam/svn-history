"""
Simple two-dimensional mathematical or geometrical pattern generators.

$Id$
"""

from math import pi
from Numeric import around,bitwise_and,sqrt,sin,Float

from topo.base.parameter import Number
from topo.base.patternfns import gaussian,gabor,fuzzy_line,fuzzy_disk,fuzzy_ring
from topo.base.patterngenerator import PatternGenerator

# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import ConstantGenerator


class GaussianGenerator(PatternGenerator):
    """
    Gaussian pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gaussian( self.pattern_x, 
                         self.pattern_y, 
                         params.get('width',self.width), 
                         params.get('height',self.height)) 


class SineGratingGenerator(PatternGenerator):
    """
    Sine grating pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    ### JABHACKALERT!  Need to fold these two functions together.
    def sine_grating(self,x, y, frequency, phase):
        """
        Sine grating pattern (two-dimensional sine wave).
        """
        return 0.5 + 0.5*sin(frequency*2*pi*x + phase)

    def function(self,**params):
        return self.sine_grating( self.pattern_x,
                                  self.pattern_y,
                                  params.get('frequency',self.frequency), 
                                  params.get('phase',self.phase)) 


class GaborGenerator(PatternGenerator):
    """
    Gabor pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gabor( self.pattern_x,
                      self.pattern_y,
                      params.get('width',self.width),
                      params.get('height',self.height),
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  


class FuzzyLineGenerator(PatternGenerator):

    """
    Fuzzy line pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return fuzzy_line( self.pattern_x, 
                           self.pattern_y,
                           params.get('width',self.width),
                           params.get('gaussian_width',self.gaussian_width))


class FuzzyDiskGenerator(PatternGenerator):

    """
    Fuzzy disk pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    disk_radius  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return fuzzy_disk( self.pattern_x, 
                           self.pattern_y, 
                           params.get('disk_radius',self.disk_radius), 
                           params.get('gaussian_width',self.gaussian_width))  


class FuzzyRingGenerator(PatternGenerator):
    """
    Fuzzy ring pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    disk_radius  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return fuzzy_ring(self.pattern_x, 
                          self.pattern_y,
                          params.get('disk_radius',self.disk_radius),
                          params.get('width',self.width),
                          params.get('gaussian_width',self.gaussian_width))  


class RectangleGenerator(PatternGenerator):
    """
    Rectangle pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    # We will probably want to add Fuzzy-style anti-aliasing to this,
    # and there might be an easier way to do it than by cropping a
    # sine grating.

    def function(self,**params):
        width = params.get('width',self.width)
        height= params.get('height',self.height)
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class SquareGratingGenerator(PatternGenerator):
    """
    Squarewave grating pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    # We will probably want to add anti-aliasing to this,
    # and there might be an easier way to do it than by
    # cropping a sine grating.

    ### JABHACKALERT!  Need to fold these two functions together.
    def square_grating(self,x, y, frequency, phase):
        """
        Square-wave grating (alternating black and white bars).
        """
        return around(0.5 + 0.5*sin(frequency*2*pi*x + phase))

    def function(self,**params):
        return self.square_grating( self.pattern_x,
                                    self.pattern_y,
                                    params.get('frequency',self.frequency), 
                                    params.get('phase',self.phase)) 

