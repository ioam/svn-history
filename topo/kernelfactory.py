"""

Kernel Factory

Defines a class to return Kernels

There is a registry dictionary called
topo.kernelfactory.kernel_factories that stores the class name as key,
and a reference to the class definition as the value.  This dictionary
is used in the GUI Input Parameter Panel to dynamically generate the
list of valid KernelFactories that can be presented.  A user can
define a new subclass of KernelFactory anywhere, and then add an entry
to this dictionary, and the GUI will then add it to the list of
presentation types.

$Id$
"""
import types
import base
from boundingregion import BoundingBox
from sheet import sheet2matrix, matrix2sheet, bounds2shape
import RandomArray
from Numeric import *
from MLab import *
from params import * 
from pprint import pprint,pformat
from math import pi

# Registry for subclasses of KernelFactory.  Users can add to this
# list, and the GUI will automatically add them to the list of
# KernelFactory inputs possible.  Additional work may be necessary if
# other than default Parameter names are used in the definition of the
# KernelFactory
# Format:   {'NewKernelFactoryClassName':<NewKernelFactoryClass>,....}
global kernel_factories
kernel_factories = {}

# Some kernels use math.exp() to generate a falling off of activation.
# But exp will overflow if too small a value is given, so this
# constant defines the smallest value to accept from the kernels.
# exp(-100) is appx. 3.72e-44
EXP_CUTOFF = -100


def produce_kernel_matrices(bounds, density):
    """
    Get Kernel Matrices

    Sets up two vectors for the x and y values based on a bounds and density.
    The x and y vectors are lists of indexes at which to sample the kernel
    function.
    """       
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
    
    # kernel_x = array([matrix2sheet(r,0,bounds,density) for r in range(rows)])
    # kernel_y = array([matrix2sheet(0,c,bounds,density) for c in range(cols)])
    # # NOTE: This is correct,
    # #  kernels use x for rows and y for columns, not sure why. --jp
    # assert len(kernel_x) == rows
    # assert len(kernel_y) == cols
    # return kernel_x[:,1], kernel_y[:,0]

    # Experiment to see if swapping will work.  It did, but additional work
    # is required to make the displays consistent.  -Judah
    kernel_y = array([matrix2sheet(r,0,bounds,density) for r in range(rows)])
    kernel_x = array([matrix2sheet(0,c,bounds,density) for c in range(cols)])
    assert len(kernel_x) == cols
    assert len(kernel_y) == rows
    return kernel_x[:,0], kernel_y[:,1]



def produce_rotated_matrices(kernel_x, kernel_y, theta):
    """
    Get Rotated matrices

    Takes in two Numeric /arrays/ that specify the x and y coordinates separately
    and a theta value, returns two Numeric matrices that have their coordinates
    rotated by that theta.

    The matrix itself is rotated to match the Topographica cartesian
    style coordinates.
    """

    # theta subtracted from pi for short term fix so that rotation matches the
    # reflected kernel matrices.  Undo when the kernelfactory is reworked.
    new_kernel_x = subtract.outer(cos(pi-theta)*kernel_x, sin(pi-theta)*kernel_y)
    new_kernel_y = add.outer(sin(pi-theta)*kernel_x, cos(pi-theta)*kernel_y)

    new_kernel_x = flipud(rot90(new_kernel_x))
    new_kernel_y = flipud(rot90(new_kernel_y))
    return new_kernel_x, new_kernel_y


def gaussian(kernel_x, kernel_y, width, height):
    """
    Gaussian Kernel Factory
    """
    new_kernel = -(kernel_x / width)**2 + -(kernel_y / height)**2

    # maximum( ) is needed to avoid overflow in some situations
    k = exp(maximum(EXP_CUTOFF,new_kernel))
    k = where(k != exp(EXP_CUTOFF), k, 0.0)
    return k


def sine_grating(kernel_x, kernel_y, frequency, phase):
    """
    Sine Grating Kernel Factory
    """
    return 0.5 + 0.5*sin(frequency*2*pi*kernel_x + phase)


def gabor(kernel_x, kernel_y, width, height, frequency, phase):
    """
    Gabor Kernel Factory
    """
 
    k = exp(maximum(EXP_CUTOFF,-(kernel_x/width)**2-(kernel_y/height)**2))
    k = where(k > exp(EXP_CUTOFF), k, 0.0)
    return k * (0.5 + 0.5*cos(2*pi*frequency*kernel_x + phase))


def uniform_random(kernel_x, kernel_y,rmin,rmax):
    """
    Uniform Random Kernel Factory
    """
    return RandomArray.uniform(rmin,rmax,kernel_x.shape) 


def rectangle(kernel_x, kernel_y, x, y, width, height):
    """
    Rectangle Kernel Factory
    """
    kernel_x = bitwise_and( less_equal( kernel_x, x+width/2 ), 
                            greater_equal( kernel_x, x-width/2 ) )
    kernel_y = bitwise_and( less_equal( kernel_y, y+height/2 ), 
                            greater_equal( kernel_y, y-height/2 ) )
    
    return bitwise_and( kernel_x, kernel_y )


def fuzzy_line(kernel_x, kernel_y, width):
    """
    Fuzzy Line Kernel Factory
    """
    # TODO: This is a hack: the height should be specified in terms of
    # bounds.  This just sets the height of the gaussian so high, that
    # the small window makes it look like a line.
    fl = gaussian(kernel_x, kernel_y, width, 100)
#    print fl
    return fl



def fuzzy_disk(kernel_x, kernel_y, disk_radius, gaussian_width):
    """
    Fuzzy Disk Kernel Factory
    """
    distance_from_line = sqrt((kernel_x**2)+(kernel_y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 
    div_sigmasq = 1 / (gaussian_width*gaussian_width)

    disc = less_equal(gaussian_x_coord,0)
    k = maximum(disc, exp(maximum(EXP_CUTOFF,
                                  -gaussian_x_coord*gaussian_x_coord*div_sigmasq)))
    return where(k != exp(EXP_CUTOFF), k, 0.0)



def fuzzy_ring(kernel_x, kernel_y, disk_radius, ring_radius, gaussian_width):
    """
    Fuzzy Ring Kernel Factory
    """    
    disk_radius = disk_radius
    ring_radius = ring_radius / 2.0
    distance_from_line = abs(sqrt((kernel_x**2)+(kernel_y**2)) - disk_radius)
    inner_distance = distance_from_line - ring_radius
    outer_distance = distance_from_line + ring_radius
    div_sigmasq = 1 / (gaussian_width*gaussian_width)

    ring = less_equal(distance_from_line,ring_radius)
           
    inner_g = exp(maximum(EXP_CUTOFF,-inner_distance*inner_distance*div_sigmasq))
    outer_g = exp(maximum(EXP_CUTOFF,-outer_distance*outer_distance*div_sigmasq))
    inner_g = where(inner_g != exp(EXP_CUTOFF), inner_g, 0.0)
    outer_g = where(outer_g != exp(EXP_CUTOFF), outer_g, 0.0)
    dring = maximum(inner_g,maximum(outer_g,ring))
    return dring



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


class GaussianFactory(KernelFactory):
    """
    Gassian Kernel Generating Generator
    """

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


class SineGratingFactory(KernelFactory):
    """
    Sine Grating Kernel Generating Factory
    """

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


class GaborFactory(KernelFactory):
    """
    Gabor Kernel Generating Factory
    """
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

  
class UniformRandomFactory(KernelFactory):
    """
    Uniform Random Generating Factory
    """
    x = Parameter(default=0)
    y = Parameter(default=0)
    min = Number(default=0.0)
    max = Number(default=1.0)
    
    def function(self,**params):
        return uniform_random( self.kernel_x, self.kernel_y,
                               params.get('min',self.min),
                               params.get('max',self.max)) 


class RectangleFactory(KernelFactory):
    """
    Rectangle Generating Factory
    """

    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)
    height  = Parameter(default=1)

    def function(self,**params):
        return rectangle( self.kernel_x, 
                          self.kernel_y, 
                          params.get('x',self.x),
                          params.get('y',self.y),
                          params.get('width',self.width),
                          params.get('height',self.height))  


class FuzzyLineFactory(KernelFactory):

    """
    Fuzzy Line Generating Factory
    """
    x       = Parameter(default=0)
    y       = Parameter(default=0)
    theta   = Parameter(default=0)
    width   = Parameter(default=1)

    def function(self,**params):
        return fuzzy_line( self.kernel_x, 
                           self.kernel_y, 
                           params.get('width',self.width))  
    

class FuzzyDiskFactory(KernelFactory):

    """
    Fuzzy Disk Generating Factory
    """
    x              = Parameter(default=0)
    y              = Parameter(default=0)
    disk_radius    = Parameter(default=0.2)
    gaussian_width = Parameter(default=0.2)

    def function(self,**params):
        return fuzzy_disk( self.kernel_x, 
                           self.kernel_y, 
                           params.get('disk_radius',self.disk_radius), 
                           params.get('gaussian_width',self.gaussian_width))  
    


class FuzzyRingFactory(KernelFactory):
    """
    Fuzzy Ring Generating Factory
    """

    x              = Parameter(default=0)
    y              = Parameter(default=0)
    width          = Parameter(default=0.1)
    disk_radius    = Parameter(default=0.2)
    gaussian_width = Parameter(default=0.1)

    def function(self,**params):
        return fuzzy_ring(self.kernel_x, 
                          self.kernel_y,
                          params.get('disk_radius',self.disk_radius),
                          params.get('width',self.width),
                          params.get('gaussian_width',self.gaussian_width))  
    

# Populate the KernelFactory registry:
if __name__ != '__main__':
    l = locals()
    for i in l.keys():
        if (type(l[i]) is type(KernelFactory)) \
               and issubclass(l[i],KernelFactory) \
               and i != 'KernelFactory':
            kernel_factories[i] = l[i]
#    print 'kernelfactories', kernel_factories
