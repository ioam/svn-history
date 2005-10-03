from math import pi
from topo.patterngenerator import PatternGenerator
from topo.parameter import Number
from topo.patternfns import *


class GaussianGenerator(PatternGenerator):
    """
    Gaussian pattern generator
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
    Sine grating pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        return sine_grating( self.pattern_x,
                             self.pattern_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 


class GaborGenerator(PatternGenerator):
    """
    Gabor pattern generator
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
    Fuzzy Line Generating Generator
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
    Fuzzy disk pattern generator
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
    Fuzzy ring pattern generator
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
    Rectangle pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        width = params.get('width',self.width)
        height= params.get('height',self.height)
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class SquareGratingGenerator(PatternGenerator):
    """
    Square grating pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        return square_grating( self.pattern_x,
                             self.pattern_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 
