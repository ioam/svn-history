"""

Kernel Factory

Defines a class to return Kernels

"""

import debug

import random

from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet

from Numeric import *
from pprint import pprint,pformat
from params import setup_params

"""
The width and height of the gaussian are specified in terms of the matrix size, i.e. a gaussian with
with 2 has a width of two squares on the matrix. 
"""

def gaussian(self, x, y, width, height, theta):
    st = sin(theta)
    ct = cos(theta)
    nx = ct*x - st*y
    ny = st*x + ct*y
    return (exp(-(nx**2)/(width**2)), exp(-(ny**2)/(height**2)))

def random_field(x, y, width, height, theta):
    return random.uniform(0,1)

class KernelFactory:

    #kernel = array([[1.0]])

    kernel_bounds = BoundingBox( points=((0,0), (1,1)) )
    kernel_density  = 1.0

    x = 0.5 
    y = 0.5
    width = 0.5 
    height = 0.5
    theta = 0.0
    
    function = gaussian

    def __init__(self,**config):
        setup_params(self,KernelFactory,**config)
        #self.kernel = zeros((1,1), Float)


    # there is mostly likely an easier way to do this
    def save_params(self):
        self.tkernel_density = self.kernel_density
        self.tkernel_bounds = self.kernel_bounds

        self.tx = self.x
        self.ty = self.y
        self.twidth = self.width
        self.theight = self.height
        self.ttheta = self.theta
                                                                                                                                                            
        self.tfunction = self.function

    def restore_params(self):  
        self.kernel_density = self.tkernel_density
        self.kernel_bounds = self.tkernel_bounds

        self.x = self.tx
        self.y = self.ty
        self.width = self.twidth
        self.height = self.theight
        self.theta = self.ttheta
                                                                                                                                                            
        self.function = self.tfunction


    def get_kernel(self, **config):
        self.save_params()
        setup_params(self, KernelFactory,**config)

        (x_min,y_min) = sheet2matrix( self.kernel_bounds.aarect().left(),
                                      self.kernel_bounds.aarect().top(),
                                      self.kernel_bounds, 
                                      self.kernel_density )

        (x_max,y_max) = sheet2matrix( self.kernel_bounds.aarect().right(),
                                      self.kernel_bounds.aarect().bottom(),
                                      self.kernel_bounds, 
                                      self.kernel_density )
        
        new_kernel = array([[1.0]])
        new_kernel = zeros((x_max-x_min+1,y_max-y_min+1), Float)

# Ok, lets dissect this transform:
# We have a generic function, function, that returns the x and y heights 
# of a kernel centered at 0,0 with width and height and theta

# first, we need to get the bounds of the sheet in matrix coords,
# then we need to iterate over those bounds in matrix coordinates 
# (the step is calculated by the transform function) and get the 
# sheet coordinates to feed into the function.  

        for x in range(x_min, x_max+1): # need to ensure we get the boundary points 
            for y in range(y_min, y_max+1):
                (sheet_x, sheet_y) = matrix2sheet(x, y, self.kernel_bounds, self.kernel_density)
        #        print sheet_x, sheet_y
                (a, b)=self.function(sheet_x-self.x,sheet_y-self.y, self.width, self.height, self.theta)
                new_kernel[x][y] = a*b

        self.kernel = new_kernel

        self.restore_params()
        return self.kernel



if __name__ == '__main__':

    l = KernelFactory(kernel_bounds=BoundingBox(points=((0,0), (10,10)), kernel_density=1))

    print l.get_kernel(x=1.0, y=1.0, theta=3.14159/2.0)
    print l.get_kernel(x=2.0, y=2.0)
    print l.get_kernel(x=2.0, y=2.0, width=3, kernel_bounds=BoundingBox(points=((0,0), (1,1))), kernel_density=100)
