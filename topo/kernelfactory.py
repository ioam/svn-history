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

Sets up two arrays for the x and y values based on a bounds and density
"""      

def produce_kernel_matrices(bounds, density, x, y):
    bounds  = produce_value(bounds)
    density = produce_value(density)
        
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

    # TODO: Use sheet operations defined in sheet.py? I think we already
    # do...

    kernel_y = arange(left-x,right-x, bound_width/cols)
    kernel_x = arange(bottom-y,top-y, bound_height/rows)
 
    return kernel_x, kernel_y

"""
Get Rotated matrices

Takes in two Numeric /arrays/ that specify the x and y coordinates separately
and a theta value, returns two Numeric matrices that have their coordinates
rotated by that theta
"""


def produce_rotated_matrices(kernel_x, kernel_y, theta):
    theta  = produce_value(theta)
    
    new_kernel_x = subtract.outer(cos(theta)*kernel_x, sin(theta)*kernel_y)
    new_kernel_y = add.outer(sin(theta)*kernel_x, cos(theta)*kernel_y)
    
    return new_kernel_x, new_kernel_y

"""
Gaussian Kernel Factory
"""

def gaussian(bounds, density, x, y, theta, width, height):
        
    kernel_x, kernel_y = produce_kernel_matrices(bounds, density, x, y)
    kernel_x, kernel_y = produce_rotated_matrices(kernel_x, kernel_y, theta)
    
    width  = produce_value(width)
    height = produce_value(height) 
    
    new_kernel = -(kernel_x / width)**2 + -(kernel_y / height)**2

    return exp(maximum(-100,new_kernel))

"""
Sine Grating Kernel Factory
"""


def sine_grating(bounds, density, x, y, theta, frequency, phase):
        
    kernel_x, kernel_y = produce_kernel_matrices(bounds, density, x, y)
    kernel_x, kernel_y = produce_rotated_matrices(kernel_x, kernel_y, theta)
        
    phase     = produce_value(phase)
    frequency = produce_value(frequency)

    new_kernel = sin(frequency*2*pi*kernel_x + phase)

    return new_kernel

"""
Gabor Kernel Factory
"""

def gabor(bounds, density, x, y, theta, width, height, frequency, phase):
 
    kernel_x, kernel_y = produce_kernel_matrices(bounds, density, x, y)
    kernel_x, kernel_y = produce_rotated_matrices(kernel_x, kernel_y, theta)
        
    phase     = produce_value(phase)
    frequency = produce_value(frequency)
    width  = produce_value(width)
    height = produce_value(height) 

    # TODO: this doesn't seem to be working correctly.

    return exp( maximum(-100, -(kernel_x/width)**2-(kernel_y/height)**2)) *\
    (0.5 + 0.5*cos(2*pi*frequency*kernel_x + phase ))

"""
Uniform Random Kernel Factory
"""

def uniform_random(bounds, density):
    bounds  = produce_value(bounds)
    density = produce_value(density)
        
    rows,cols = bounds2shape(bounds,density)
                                                                                                                 
    return random((rows,cols)) 

"""
Rectangle Kernel Factory
"""

def rectangle(bounds, density, x, y, width, height, theta):
    # TODO: This is also kind of a hack: produce x, y early to use them later
    x = produce_value(x)
    y = produce_value(y)
    
    kernel_x, kernel_y = produce_kernel_matrices(bounds, density, x, y)
    kernel_x, kernel_y = produce_rotated_matrices(kernel_x, kernel_y, theta)
   
    width  = produce_value(width)
    height = produce_value(height) 
    
    kernel_x = bitwise_and( less_equal( kernel_x, x+width/2 ), 
                            greater_equal( kernel_x, x-width/2 ) )
    kernel_y = bitwise_and( less_equal( kernel_y, y+height/2 ), 
                            greater_equal( kernel_y, y-height/2 ) )
    
    return bitwise_and( kernel_x, kernel_y )

"""
Fuzzy Line Kernel Factory
"""

def fuzzy_line(bounds, density, x, y, theta, width):
    #TODO: This is a hack: the height should be specified in terms of bounds
    return gaussian(bounds, density, x, y, theta, width, 100)


"""
Fuzzy Disk Kernel Factory
"""

def fuzzy_disk(bounds, density, x, y, disk_radius, gaussian_width):
    kernel_x, kernel_y = produce_kernel_matrices(bounds, density, x, y)
    # TODO: Needs Optimization: pass 0 for theta to simulate a rotation
    kernel_x, kernel_y = produce_rotated_matrices(kernel_x, kernel_y, 0.0)

    disk_radius    = produce_value(disk_radius)
    gaussian_width = produce_value(gaussian_width)

    distance_from_line = sqrt((kernel_x**2)+(kernel_y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 


    #return less_equal(gaussian_x_coord, 0) * \
    #       exp(maximum(-100, -(gaussian_x_coord/gaussian_width)**2 ))#- (kernel_y/gaussian_width)**2))
    return less_equal(gaussian_x_coord, 0) * \
           exp(maximum(-100, -(kernel_x/gaussian_width)**2 - (kernel_y/gaussian_width)**2))
"""
Fuzzy Ring Kernel Factory
"""

def fuzzy_ring(bounds, density, x, y, inner_radius, outer_radius, gaussian_width):
    kernel_x, kernel_y = produce_kernel_matrices(bounds, density, x, y)
    kernel_x, kernel_y = produce_rotated_matrices(kernel_x, kernel_y, theta)
    
    distance_from_line = abs(outer_radius - sqrt(kernel_x**2)+(kernel_y**2))
    gaussian_x_coord   = distance_from_line - disk_radius/2

    return less_equal(gaussian_x_coord, 0) * \
           exp(maximum(-100, -(gaussian_x_coord/gaussian_width)**2))


if __name__ == '__main__':

    print "No tests here. Run inputsheet.py instead."
