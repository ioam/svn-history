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
from params import * 
from pprint import pprint,pformat

from math import pi


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

class KernelFactory(base.TopoObject):

    #kernel = array([[1.0]])

    bounds   = Parameter(default=BoundingBox( points=((0,0), (1,1)) ))
    density  = Parameter(default=1.0)

    # setup some default parameters. keep in mind that these are effectively
    # meaningless
    x = Parameter(default=0.5) 
    y = Parameter(default=0.5)
   

    def create(self):
        left,bottom,right,top = self.bounds.aarect().lbrt()
        self.bound_width  = right-left
        self.bound_height = top-bottom
        self.linear_density = sqrt(self.density)

        rows,cols = bounds2shape(self.bounds,self.density)
        
        x = produce_value(self.x)
        y = produce_value(self.y) 

        # TODO: this can generate ouput that may be off by one in terms of size,
        # for example most times this generates a 100x100 image, but sometimes
        # it generates a 101x100 

        # TODO: Use sheet operations defined in sheet.py

        # TODO: fix the 90 degree rotation problem

        self.kernel_y = arange(left-x,right-x, self.bound_width/cols)
        self.kernel_x = arange(bottom-y,top-y, self.bound_height/rows)
  
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

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        new_kernel = -(new_kernel_x / width)**2 + -(new_kernel_y / height)**2

        return exp(maximum(-100,new_kernel))

"""
Sine Grating Kernel Factory
"""


class SineGratingKernelFactory(KernelFactory):
    amplitude = Parameter(default=0.5) 
    frequency = Parameter(default=0.5)
    theta     = Parameter(default=0.0)
 
    def function(self, kernel_x, kernel_y):

        amplitude = produce_value(self.amplitude)
        frequency = produce_value(self.frequency)
        theta     = produce_value(self.theta) 

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        new_kernel = amplitude*sin(frequency*new_kernel_x)

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

"""
Uniform Random Kernel Factory
"""

class UniformRandomKernelFactory(KernelFactory):
 
    def function(self, kernel_x, kernel_y):
        
        return 




if __name__ == '__main__':

    print "No tests"
    #l = KernelFactory(bounds=BoundingBox(points=((0,0), (10,10)), density=1))
