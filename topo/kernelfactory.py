"""

Kernel Factory

Defines a class to return Kernels

"""

import debug
import types
import random

from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet

from Numeric import *
from pprint import pprint,pformat
from params import setup_params


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

    bounds = BoundingBox( points=((0,0), (1,1)) )
    density  = 1.0

    # setup some default parameters. keep in mind that these are effectively
    # meaningless
    x = 0.5 
    y = 0.5
    width = 0.5 
    height = 0.5
    theta = 0.0
   
    # the default, we can set this by passing a new value to the init 
    function = gaussian

    def __init__(self,**config):
        setup_params(self,KernelFactory,**config)
        #self.kernel = zeros((1,1), Float)

    def create(self):
        x = produce( self.x )
        y = produce( self.y )
        theta = produce( self.theta )
        width = produce( self.width )
        height = produce( self.height )

        # TODO: This is all embedded in matrix2sheet...
        bound_width  = self.bounds.aarect().right()-self.bounds.aarect().left()
        bound_height = self.bounds.aarect().top()-self.bounds.aarect().bottom()
        linear_density = sqrt(self.density)

        # TODO: this can generate ouput that may be off by one in terms of size,
        # for example most times this generates a 100x100 image, but sometimes
        # it generates a 101x100 of something like that.

        # TODO: This uses 5 numeric arrays. We can probably simplify this. It is
        # faster than the previous implementation though.

        kernel_x = arange(self.bounds.aarect().left()-x,
                          self.bounds.aarect().right()-x, bound_width / linear_density);
        kernel_y = arange(self.bounds.aarect().bottom()-y,
                          self.bounds.aarect().top()-y, bound_height / linear_density);
        
        new_kernel_x = subtract.outer(cos(theta)*kernel_x,
                                      sin(theta)*kernel_y)
        new_kernel_y = add.outer(sin(theta)*kernel_x,
                                 cos(theta)*kernel_y)

        new_kernel = -(new_kernel_x / width)**2 + -(new_kernel_y / height)**2
        new_kernel = maximum(-100, new_kernel)

        new_kernel = exp(new_kernel)

        return new_kernel


if __name__ == '__main__':

    l = KernelFactory(bounds=BoundingBox(points=((0,0), (10,10)), density=1))

    


#    print l.create(x=1.0, y=1.0, theta=3.14159/2.0)
#    print l.create(x=2.0, y=2.0)
#    print l.create(x=2.0, y=2.0, width=3, bounds=BoundingBox(points=((0,0), (1,1))), density=100)
