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
Gaussian Kernel Factory
"""      

def gaussian(bounds, density, x, y, theta, width, height):
        left,bottom,right,top = bounds.aarect().lbrt()
        bound_width  = right-left
        bound_height = top-bottom
        linear_density = sqrt(density)

        rows,cols = bounds2shape(bounds,density)
        
        x = produce_value(x)
        y = produce_value(y) 

        # TODO: this can generate ouput that may be off by one in terms of size,
        # for example most times this generates a 100x100 image, but sometimes
        # it generates a 101x100 

        # TODO: Use sheet operations defined in sheet.py

        kernel_y = arange(left-x,right-x, bound_width/cols)
        kernel_x = arange(bottom-y,top-y, bound_height/rows)
 
        theta  = produce_value(theta)
        width  = produce_value(width)
        height = produce_value(height) 

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        new_kernel = -(new_kernel_x / width)**2 + -(new_kernel_y / height)**2

        return exp(maximum(-100,new_kernel))

"""
Sine Grating Kernel Factory
"""


def sine_grating(bounds, density, x, y, theta, amplitude, frequency):
        left,bottom,right,top = bounds.aarect().lbrt()
        bound_width  = right-left
        bound_height = top-bottom
        linear_density = sqrt(density)

        rows,cols = bounds2shape(bounds,density)
        
        x = produce_value(x)
        y = produce_value(y) 

        kernel_y = arange(left-x,right-x, bound_width/cols)
        kernel_x = arange(bottom-y,top-y, bound_height/rows)
 
        amplitude = produce_value(amplitude)
        frequency = produce_value(frequency)
        theta     = produce_value(theta) 

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        new_kernel = amplitude*sin(frequency*2*pi*new_kernel_x)

        return new_kernel

"""
Gabor Kernel Factory
"""

def gabor(bounds, density, x, y, theta, width, height):
        left,bottom,right,top = bounds.aarect().lbrt()
        bound_width  = right-left
        bound_height = top-bottom
        linear_density = sqrt(density)

        rows,cols = bounds2shape(bounds,density)
        
        x = produce_value(x)
        y = produce_value(y) 

        kernel_y = arange(left-x,right-x, bound_width/cols)
        kernel_x = arange(bottom-y,top-y, bound_height/rows)
 
        theta  = produce_value(theta)
        width  = produce_value(width)
        height = produce_value(height) 

        new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)

        # TODO: this doesn't seem to be working correctly.

        return exp( maximum(-100, -(new_kernel_x/width)**2 - (new_kernel_y/height)**2 )) * cos( 2*pi*new_kernel_x )

"""
Uniform Random Kernel Factory
"""

def uniform_random(bounds, density):
        rows,cols = bounds2shape(bounds,density)
                                                                                                                   
        return random((rows,cols)) 

"""
Uniform Random Kernel Factory
"""

def rectangle(bounds, density, x, y, width, height, theta):
    return kernel_x

"""
Uniform Random Kernel Factory
"""

def fuzzy_line(bounds, density, x, y, width, theta):
    #TODO: This is a hack: the height should be specified in terms of bounds
    return gaussian(bounds, density, x, y, width, 100, theta)


"""
Uniform Random Kernel Factory
"""

def fuzzy_disc(bounds, density, x, y, radius):

    left,bottom,right,top = bounds.aarect().lbrt()
    bound_width  = right-left
    bound_height = top-bottom
    linear_density = sqrt(density)

    rows,cols = bounds2shape(bounds,density)
        
    x = produce_value(x)
    y = produce_value(y) 

    kernel_y = arange(left-x,right-x, bound_width/cols)
    kernel_x = arange(bottom-y,top-y, bound_height/rows)
 
    theta  = produce_value(theta)
    radius = produce_value(radius)

    new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
    new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)


    return tanh(radius*new_kernel_x*new_kernel_y)




if __name__ == '__main__':

    print "No tests"
    #l = KernelFactory(bounds=BoundingBox(points=((0,0), (10,10)), density=1))
