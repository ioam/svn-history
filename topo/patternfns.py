"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array).

$Id$
"""
### JABALERT!
### 
### It would be good to remove the dependence on Numeric and RandomArray,
### but it may not be possible to do that.
###
### JABHACKALERT!
###
### Should eliminate all "import *" commands if at all possible.
from math import pi,sin,cos,exp
from Numeric import *
import RandomArray


### JABALERT!
###
### Is this really necessary?  If so, please document better why.
###
# Some kernels use math.exp() to generate a falling off of activity.
# But exp will overflow if too small a value is given, so this
# constant defines the smallest value to accept from the kernels.
# exp(-100) is appx. 3.72e-44
EXP_CUTOFF = -100


### JABHACKALERT!
### 
### They should probably all be renamed to use x,y
### instead of kernel_x, kernel_y, because they do not need to be
### in the context of a kernel to be useful.

def gaussian(kernel_x, kernel_y, width, height):
    """
    Two-dimensional oriented Gaussian pattern (i.e., 2D version of a
    bell curve, like a normal distribution but without necessarily
    summing to 1.0).
    """
    new_kernel = -(kernel_x / width)**2 + -(kernel_y / height)**2

    # maximum( ) is needed to avoid overflow in some situations
    k = exp(maximum(EXP_CUTOFF,new_kernel))
    k = where(k != exp(EXP_CUTOFF), k, 0.0)
    return k


def sine_grating(kernel_x, kernel_y, frequency, phase):
    """
    Sine grating pattern (two-dimensional sine wave).
    """
    return 0.5 + 0.5*sin(frequency*2*pi*kernel_x + phase)


# We will probably want to add anti-aliasing to this,
# and there might be an easier way to do it than by
# cropping a sine grating.
def square_grating(kernel_x, kernel_y, frequency, phase):
    """
    Square-wave grating (alternating black and white bars).
    """
    #return around(0.5 + 0.5*sin(frequency*2*pi*kernel_x + phase))
    return 0.5 + 0.5*sin(frequency*2*pi*kernel_x + phase)


def gabor(kernel_x, kernel_y, width, height, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """
 
    k = exp(maximum(EXP_CUTOFF,-(kernel_x/width)**2-(kernel_y/height)**2))
    k = where(k > exp(EXP_CUTOFF), k, 0.0)
    return k * (0.5 + 0.5*cos(2*pi*frequency*kernel_x + phase))


def uniform_random(kernel_x, kernel_y,rmin,rmax):
    """
    Uniform random noise, independent for each pixel.
    """
    return RandomArray.uniform(rmin,rmax,kernel_x.shape) 


def rectangle(kernel_x, kernel_y, width, height):
    """
    Rectangular spot.
    """
    kernel_x = abs(kernel_x)
    kernel_y = abs(kernel_y)

    return bitwise_and(where(kernel_x<=width/2,1,0),where(kernel_y<=height/2,1,0))


### JABHACKALERT!
# CEB: Needs total reimplementation (to be the way it's done in LISSOM; currently it is a disk)
def fuzzy_line(kernel_x, kernel_y, width, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    distance_from_line = sqrt((kernel_x**2)+(kernel_y**2))
    gaussian_x_coord   = distance_from_line/2.0
    div_sigmasq = 1 / (gaussian_width*gaussian_width)

    disk = less_equal(gaussian_x_coord,0)
    k = maximum(disk, exp(maximum(EXP_CUTOFF,
                                  -gaussian_x_coord*gaussian_x_coord*div_sigmasq)))
    return where(k != exp(EXP_CUTOFF), k, 0.0)


def fuzzy_disk(kernel_x, kernel_y, disk_radius, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    distance_from_line = sqrt((kernel_x**2)+(kernel_y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 
    div_sigmasq = 1 / (gaussian_width*gaussian_width)

    disk = less_equal(gaussian_x_coord,0)
    k = maximum(disk, exp(maximum(EXP_CUTOFF,
                                  -gaussian_x_coord*gaussian_x_coord*div_sigmasq)))
    return where(k != exp(EXP_CUTOFF), k, 0.0)



def fuzzy_ring(kernel_x, kernel_y, disk_radius, ring_radius, gaussian_width):
    """
    Circular ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
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



