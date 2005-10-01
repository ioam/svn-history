from math import pi
from topo.kernelfactory import KernelFactory
from topo.parameter import Number
from topo.patternfns import *


class GaussianFactory(KernelFactory):
    """
    Gaussian pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))

    def function(self,**params):
        return gaussian( self.kernel_x, 
                         self.kernel_y, 
                         params.get('width',self.width), 
                         params.get('height',self.height)) 


class SineGratingFactory(KernelFactory):
    """
    Sine grating pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        return sine_grating( self.kernel_x,
                             self.kernel_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 


class GaborFactory(KernelFactory):
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
        return gabor( self.kernel_x,
                      self.kernel_y,
                      params.get('width',self.width),
                      params.get('height',self.height),
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  


class FuzzyLineFactory(KernelFactory):

    """
    Fuzzy Line Generating Factory
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    width   = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,1.0))
    height  = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    gaussian_width = Number(default=0.2,bounds=(0.0,None),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return fuzzy_line( self.kernel_x, 
                           self.kernel_y,
                           params.get('width',self.width),
                           params.get('gaussian_width',self.gaussian_width))  


class FuzzyDiskFactory(KernelFactory):

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
        return fuzzy_disk( self.kernel_x, 
                           self.kernel_y, 
                           params.get('disk_radius',self.disk_radius), 
                           params.get('gaussian_width',self.gaussian_width))  


class FuzzyRingFactory(KernelFactory):
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
        return fuzzy_ring(self.kernel_x, 
                          self.kernel_y,
                          params.get('disk_radius',self.disk_radius),
                          params.get('width',self.width),
                          params.get('gaussian_width',self.gaussian_width))  


class RectangleFactory(KernelFactory):
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
        return bitwise_and(abs(self.kernel_x)<=width/2.0,
                           abs(self.kernel_y)<=height/2.0)


class SquareGratingFactory(KernelFactory):
    """
    Square grating pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    theta   = Number(default=0.0,softbounds=(0.0,2*pi))
    frequency = Number(default=5.0,bounds=(0.0,None),softbounds=(0.0,10.0))
    phase     = Number(default=pi/2,bounds=(0.0,None),softbounds=(0.0,2*pi))

    def function(self,**params):
        return square_grating( self.kernel_x,
                             self.kernel_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 
