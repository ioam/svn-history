"""

Kernel Factory

Defines a class to return Kernels

"""

import types
import random

import base
from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet, bounds2shape

from Numeric import *
from RandomArray import *
from params import * 
from pprint import pprint,pformat

from math import pi

"""
Get Kernel Matrices

Sets up two vectors for the x and y values based on a bounds and density.
The x and y vectors are lists of indexes at which to sample the kernel
function.
"""       

def produce_kernel_matrices(bounds, density):
    left,bottom,right,top = bounds.aarect().lbrt()
    bound_width  = right-left
    bound_height = top-bottom
    linear_density = sqrt(density)
    
    rows,cols = bounds2shape(bounds,density)
    
    # TODO: this can generate ouput that may be off by one in terms of size,
    # for example most times this generates a 100x100 image, but sometimes
    # it generates a 101x100 
    
    # TODO: Use sheet operations defined in sheet.py? I think we already
    # do...
    
    
    #kernel_y = arange(left,right, bound_width/cols)
    #kernel_x = arange(bottom,top, bound_height/rows)
    
    kernel_x = array([matrix2sheet(r,0,bounds,density) for r in range(rows)])
    kernel_y = array([matrix2sheet(0,c,bounds,density) for c in range(cols)])


    # NOTE: This is correct,
    #  kernels use x for rows and y for columns, not sure why. --jp
    assert len(kernel_x) == rows
    assert len(kernel_y) == cols
    
    return kernel_x[:,1], kernel_y[:,0]

"""
Get Rotated matrices

Takes in two Numeric /arrays/ that specify the x and y coordinates separately
and a theta value, returns two Numeric matrices that have their coordinates
rotated by that theta
"""


def produce_rotated_matrices(kernel_x, kernel_y, theta):
    
    new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
    new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)
    
    return new_kernel_x, new_kernel_y


"""
Gaussian Kernel Factory
"""

def gaussian(kernel_x, kernel_y, width, height):
  
    new_kernel = -(kernel_x / width)**2 + -(kernel_y / height)**2

    # maximum( ) is needed to avoid overflow in some situations
    return exp(maximum(-100,new_kernel))


"""
Sine Grating Kernel Factory
"""


def sine_grating(kernel_x, kernel_y, frequency, phase):
    return 0.5 + 0.5*sin(frequency*2*pi*kernel_x + phase)

"""
Gabor Kernel Factory
"""

def gabor(kernel_x, kernel_y, width, height, frequency, phase):
 
    return exp( maximum(-100, -(kernel_x/width)**2-(kernel_y/height)**2)) *\
    (0.5 + 0.5*cos(2*pi*frequency*kernel_x + phase ))

"""
Uniform Random Kernel Factory
"""

def uniform_random(kernel_x, kernel_y):
    return random(kernel_x.shape) 


"""
Rectangle Kernel Factory
"""

def rectangle(kernel_x, kernel_y, x, y, width, height):
    kernel_x = bitwise_and( less_equal( kernel_x, x+width/2 ), 
                            greater_equal( kernel_x, x-width/2 ) )
    kernel_y = bitwise_and( less_equal( kernel_y, y+height/2 ), 
                            greater_equal( kernel_y, y-height/2 ) )
    
    return bitwise_and( kernel_x, kernel_y )

"""
Fuzzy Line Kernel Factory
"""

def fuzzy_line(kernel_x, kernel_y, width):
    #TODO: This is a hack: the height should be specified in terms of bounds
    return gaussian(kernel_x, kernel_y, width, 100)


"""
Fuzzy Disk Kernel Factory
"""

def fuzzy_disk(kernel_x, kernel_y, disk_radius, gaussian_width):

    distance_from_line = sqrt((kernel_x**2)+(kernel_y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 


    #return less_equal(gaussian_x_coord, 0) * \
    #       exp(maximum(-100, -(gaussian_x_coord/gaussian_width)**2 ))#- (kernel_y/gaussian_width)**2))
    return less_equal(gaussian_x_coord, 0) * \
           exp(maximum(-100, -(kernel_x/gaussian_width)**2 - (kernel_y/gaussian_width)**2))
"""
Fuzzy Ring Kernel Factory
"""

def fuzzy_ring(kernel_x, kernel_y, inner_radius, outer_radius, gaussian_width):
    
    distance_from_line = abs(outer_radius - sqrt(kernel_x**2)+(kernel_y**2))
    gaussian_x_coord   = distance_from_line - disk_radius/2

    return less_equal(gaussian_x_coord, 0) * \
           exp(maximum(-100, -(gaussian_x_coord/gaussian_width)**2))




#########################################################
# Kernel Factory Objects
#
#

class KernelFactory(base.TopoObject):

    bounds  = Parameter(default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))))
    density = Parameter(default=10000)

    theta = Parameter(default=0)
    
    def __call__(self,**params):
        self.verbose("params = ",params)
        self.setup_xy(params.get('bounds',self.bounds),
                      params.get('density',self.density),
                      params.get('x', self.x),
                      params.get('y',self.y),
                      params.get('theta',self.theta))
        return self.function(**params)

    def setup_xy(self,bounds,density,x,y,theta):
        self.verbose("bounds = ",bounds,"density =",density,"x =",x,"y=",y)
        x,y = produce_kernel_matrices(bounds,density)
        self.kernel_x, self.kernel_y = produce_rotated_matrices(x-self.x,y-self.y,self.theta)

"""
Gassian Kernel Generating Generator
"""

class GaussianFactory(KernelFactory):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)
    height  = Parameter(default=1)

    # Pass set up a function to run using lambdas. We need to specify self as a
    # parameter. Should not be a parameter because we don't want the user to
    # change it.

    def function(self,**params):
        return gaussian( self.kernel_x, 
                         self.kernel_y, 
                         params.get('width',self.width), 
                         params.get('height',self.height)) 

"""
Sine Grating Kernel Generating Factory
"""

class SineGratingFactory(KernelFactory):

    x         = Parameter(default=0)
    y         = Parameter(default=0)
    theta     = Parameter(default=0)
    frequency = Parameter(default=1)
    phase     = Parameter(default=0)

    def function(self,**params):
        return sine_grating( self.kernel_x,
                             self.kernel_y,
                             params.get('frequency',self.frequency), 
                             params.get('phase',self.phase)) 
    

"""
Gabor Kernel Generating Factory
"""

class GaborFactory(KernelFactory):

    x        = Parameter(default=0)
    y        = Parameter(default=0)
    theta    = Parameter(default=0)
    width    = Parameter(default=2)
    height   = Parameter(default=1)
    frequency = Parameter(default=1)
    phase     = Parameter(default=0)

    def function(self,**params):
        return gabor( self.kernel_x,
                      self.kernel_y,
                      params.get('width',self.width),
                      params.get('height',self.height),
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  

"""
Uniform Random Generating Factory
"""
  
class UniformRandomFactory(KernelFactory):
    x = Parameter(default=0)
    y = Parameter(default=0)
    def function(self,**params):
        return uniform_random( self.kernel_x, self.kernel_y) 

"""
Rectangle Generating Factory
"""

class RectangleFactory(KernelFactory):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)
    height  = Parameter(default=1)

    def function(self,**params):
        return rectangle( self.kernel_x, 
                          self.kernel_y, 
                          self.produced_x,
                          self.produced_y,
                          params.get('width',self.width),
                          params.get('height',self.height))  
"""
Fuzzy Line Generating Factory
"""

class FuzzyLineFactory(KernelFactory):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)

    def function(self,**params):
        return fuzzy_line( self.kernel_x, 
                           self.kernel_y, 
                           params.get('width',self.width))  
    
"""
Fuzzy Disk Generating Factory
"""

class FuzzyDiskFactory(KernelFactory):

    x              = Parameter(default=0)
    y              = Parameter(default=0)
    # TODO: This is a hack, we need a theta in order to appease the rotation
    # function
    theta          = Parameter(default=0)
    disk_radius    = Parameter(default=0.8)
    gaussian_width = Parameter(default=1)

    def function(self,**params):
        return fuzzy_disk( self.kernel_x, 
                           self.kernel_y, 
                           params.get('disk_radius',self.disk_radius), 
                           params.get('gaussian_width',self.gaussian_width))  
    

"""
Fuzzy Ring Generating Factory
"""

class FuzzyRingFactory(KernelFactory):

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)

    def function(self,**params):
        return fuzzy_ring( self.kernel_x, 
                           self.kernel_y, 
                           params.get('width',self.width))  
    

