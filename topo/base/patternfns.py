"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array);
the functions therefore have the same mathematical behaviour as Numeric.

$Id$
"""

from math import pi
from Numeric import where,maximum,cos,sin,sqrt,less_equal,divide
from utils import exp

# CEB:
# Divide is imported from Numeric so that mathematical expressions with scalars
# (such as exp(-(3.0/0.0)) ) are evaluated correctly. Unfortunately this makes
# such expressions more difficult to read. How can Numeric's / operator
# be made to override Python's / operator for scalars?


def gaussian(x, y, width, height):
    """
    Two-dimensional oriented Gaussian pattern (i.e., 2D version of a
    bell curve, like a normal distribution but without necessarily
    summing to 1.0).
    """
    x_w = divide(x,width)
    y_h = divide(y,height)
    return exp(-0.5*x_w*x_w + -0.5*y_h*y_h)


def gabor(x, y, width, height, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """ 
    x_w = divide(x,width)
    y_h = divide(y,height)
    p = exp(-0.5*x_w*x_w + -0.5*y_h*y_h)    
    return p * (0.5 + 0.5*cos(2*pi*frequency*x + phase))


def line(x, center_width, gaussian_width):
    """
    Infinite-length line with a solid central region, then Gaussian fall-off at the edges.
    """
    distance_from_line = abs(x)
    gaussian_x_coord = distance_from_line - center_width/2
    sigmasq = 2*gaussian_width*gaussian_width

    falloff = __exp(-gaussian_x_coord*gaussian_x_coord, sigmasq)
    
    return where(gaussian_x_coord<=0, 1.0, falloff)


def disk(x, y, disk_radius, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    distance_from_line = sqrt((x**2)+(y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 
    disk = less_equal(gaussian_x_coord,0)
    sigmasq = 2*gaussian_width*gaussian_width

    falloff = __exp(-gaussian_x_coord*gaussian_x_coord, sigmasq)

    return maximum(disk, falloff)


def ring(x, y, radius, width, gaussian_width):
    """
    Circular ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
    """    
    distance_from_line = abs(sqrt((x**2)+(y**2)) - radius/2.0)
    ring = less_equal(distance_from_line,width)

    inner_distance = distance_from_line - width
    outer_distance = distance_from_line + width
    sigmasq = 2*gaussian_width*gaussian_width

    inner_falloff = __exp(-inner_distance*inner_distance, sigmasq)
    outer_falloff = __exp(-outer_distance*outer_distance, sigmasq)

    return maximum(inner_falloff,maximum(outer_falloff,ring))


def __exp(x,sigmasq):
    """
    Special-case exp() function for some functions in this file:

    Return  0.0             if x==0.0 and sigmasq==0
            exp(x/sigmasq)  otherwise

    Functions in this file that calculate an exp(x/sigmasq) need
    to have well-defined behaviour when x is 0, whatever the value
    of sigmasq.
    """
    # x/sigmasq is nan if x==sigmasq==0
    return where(x!=0.0, exp(divide(x,sigmasq)),0.0)


                
           

