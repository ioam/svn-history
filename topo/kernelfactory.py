"""

Kernel Factory

Defines a class to return Kernels

"""

import types
import random

from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet

from Numeric import *
from params import * 
from pprint import pprint,pformat

from math import pi

"""
produce -- takes in an argument, if its a generator, it calls it 
           otherwise it treats it as a literal
"""

def produce(func):
    #print "Called produce on: ", func
    if(type(func) != types.GeneratorType): 
        return func
    else:
        return func.next( ) 


# Each of these functions should be a class, and inherit from kernel_factory,
# then we could create mixins for the sheet versions easily, with a minimal
# amount of parameter passing.



"""
Function for constructing a gassian pattern out of a properly set up Numeric
matrix
"""

def uniform_random(kernel_x, kernel_y, width, height, theta):
    # not finished, needs some more information about the kernel size that isn't
    # passed through this interface
    return random(2,2)

def rectangle(kernel_x, kernel_y, width, height, theta):
    # need to specify the bounds somehow 
    return kernel_x

def fuzzy_line(kernel_x, kernel_y, width, height, theta):
    return kernel_x

def fuzzy_disc(kernel_x, kernel_y, width, height, theta):
    return kernel_x

"""
Abstract base class for the different kinds of kernels
"""

class KernelFactory:

    #kernel = array([[1.0]])

    bounds   = Parameter(default=BoundingBox( points=((0,0), (1,1)) ))
    density  = Parameter(default=1.0)

    # setup some default parameters. keep in mind that these are effectively
    # meaningless
    x = Parameter(default=0.5) 
    y = Parameter(default=0.5)
   

    def create(self):
        self.bound_width  = self.bounds.aarect().right()-self.bounds.aarect().left()
        self.bound_height = self.bounds.aarect().top()-self.bounds.aarect().bottom()
        self.linear_density = sqrt(self.density)

        x = produce( self.x )
        y = produce( self.y )

        self.kernel_x = arange(self.bounds.aarect().left()-x,
                          self.bounds.aarect().right()-x, self.bound_width /
                          self.linear_density);
        self.kernel_y = arange(self.bounds.aarect().bottom()-y,
                          self.bounds.aarect().top()-y, self.bound_height /
                          self.linear_density);
  
        return self.function(self.kernel_x, self.kernel_y)

"""
Gaussian Kernel Factory
"""      

class GaussianKernelFactory(KernelFactory):
    width = Parameter(default=0.5) 
    height = Parameter(default=0.5)
    theta = Parameter(default=0.0)
 
    def function(self, kernel_x, kernel_y):

        theta  = produce_value(self.theta)
        width  = produce_value(self.width)
        height = produce_value(self.height) 

        # TODO: this can generate ouput that may be off by one in terms of size,
        # for example most times this generates a 100x100 image, but sometimes
        # it generates a 101x100 of something like that.

        # TODO: This uses 5 numeric arrays. We can probably simplify this. It is
        # faster than the previous implementation though.


        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        new_kernel = -(new_kernel_x / width)**2 + -(new_kernel_y / height)**2

        return exp(maximum(-100,new_kernel))

"""
Sine Grating Kernel Factory
"""


class SineGratingKernelFactory(KernelFactory):
    amplitude = Parameter(default=0.5) 
    period    = Parameter(default=0.5)
    theta     = Parameter(default=0.0)
 
    def function(self, kernel_x, kernel_y):

        amplitude = produce_value(self.amplitude)
        period    = produce_value(self.period)
        theta     = produce_value(self.theta) 

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        # HACK: just for testing the sine_grating function, width and height are
        # meaningless in this context
        new_kernel = amplitude*sin(period*new_kernel_x)

        return new_kernel

"""
Gabor Kernel Factory
"""

class GaborKernelFactory(KernelFactory):
    width  = Parameter(default=0.5) 
    height = Parameter(default=0.5)
    theta  = Parameter(default=0.0)
 
    def function(self, kernel_x, kernel_y):
        
        theta  = produce_value(self.theta)
        width  = produce_value(self.width)
        height = produce_value(self.height) 

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        return exp( -(new_kernel_x/width)**2 - (new_kernel_y/height)**2 ) * cos( 2*pi*new_kernel_x )


if __name__ == '__main__':

    print "No tests"
    #l = KernelFactory(bounds=BoundingBox(points=((0,0), (10,10)), density=1))
