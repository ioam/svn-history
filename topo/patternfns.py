"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array).

$Id$
"""

from math import pi
from Numeric import where,maximum,exp,cos,sin,sqrt,less_equal


# CEB: This is a hack.
# For patternfns.py, this only needs to handle arguments that are of large
# magnitude and negative. A better version of this function could be put in
# topo.utils for general use, returning 0.0 if there is underflow and Inf
# if there is overflow.
def safeexp(x):
    """
    Avoid underflow of Numeric.exp() for large, negative arguments.

    Numeric.exp() gives an OverflowError ('math range error') for 
    arguments of magnitude greater than about 700 on linux.

    See e.g.
    [Python-Dev] RE: Possible bug (was Re: numpy, overflow, inf, ieee, and rich comparison)
    http://mail.python.org/pipermail/python-dev/2000-October/thread.html#9851
    """
    MIN_ARG = -700.0

    return exp(maximum(MIN_ARG,x))

def gaussian(x, y, width, height):
    """
    Two-dimensional oriented Gaussian pattern (i.e., 2D version of a
    bell curve, like a normal distribution but without necessarily
    summing to 1.0).
    """
    new_pattern = -(x / width)**2 + -(y / height)**2

    return safeexp(new_pattern)


def gabor(x, y, width, height, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """
 
    p = safeexp(-(x/width)**2-(y/height)**2)
    return p * (0.5 + 0.5*cos(2*pi*frequency*x + phase))


def fuzzy_line(x, y, center_width, gaussian_width):
    """
    Infinite-length line with a solid central region, then Gaussian fall-off at the edges.
    """
    distance_from_line = abs(x)
    gaussian_x_coord = distance_from_line - center_width/2
    
    return where(gaussian_x_coord<=0, 1.0,
                 safeexp(-(gaussian_x_coord/gaussian_width)**2))


def fuzzy_disk(x, y, disk_radius, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    distance_from_line = sqrt((x**2)+(y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 
    div_sigmasq = 1 / (gaussian_width*gaussian_width)

    disk = less_equal(gaussian_x_coord,0)
    return maximum(disk, safeexp(-gaussian_x_coord*gaussian_x_coord*div_sigmasq)) 


def fuzzy_ring(x, y, disk_radius, ring_radius, gaussian_width):
    """
    Circular ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
    """    
    disk_radius = disk_radius
    ring_radius = ring_radius / 2.0
    distance_from_line = abs(sqrt((x**2)+(y**2)) - disk_radius)
    inner_distance = distance_from_line - ring_radius
    outer_distance = distance_from_line + ring_radius
    div_sigmasq = 1 / (gaussian_width*gaussian_width)

    ring = less_equal(distance_from_line,ring_radius)
           
    inner_g = safeexp(-inner_distance*inner_distance*div_sigmasq)
    outer_g = safeexp(-outer_distance*outer_distance*div_sigmasq)
    dring = maximum(inner_g,maximum(outer_g,ring))
    return dring



