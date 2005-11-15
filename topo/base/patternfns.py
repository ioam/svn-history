"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array);
the functions therefore have the same mathematical behaviour as Numeric.

$Id$
"""
__version__='$Revision$'

from math import pi
from Numeric import where,maximum,cos,sin,sqrt,less_equal,divide,greater_equal,bitwise_xor
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
    return p * (0.5 + 0.5*cos(2*pi*frequency*y + phase))


def line(y, thickness, gaussian_width):
    """
    Infinite-length line with a solid central region, then Gaussian fall-off at the edges.
    """
    distance_from_line = abs(y)
    gaussian_y_coord = distance_from_line - thickness/2.0
    sigmasq = gaussian_width*gaussian_width
    falloff = __exp(-gaussian_y_coord*gaussian_y_coord, 2*sigmasq)
    return where(gaussian_y_coord<=0, 1.0, falloff)


# CEBHACKALERT:
# I think I have something wrong with gaussian falloffs for ring() and disk()
# (c.f. line())

# CEBHACKALERT:
# I have used 'ellipse' in a confusing way. Change the variable and function names.

def disk(x, y, width, height, gaussian_width):
    """
    Elliptical disk with Gaussian fall-off after the solid central region.
    """
    disk_perimeter = __ellipse(x,y,width/2.0,height/2.0)  
    disk = greater_equal(disk_perimeter,0)

    sigmasq = gaussian_width*gaussian_width
    falloff = __exp(-disk_perimeter*disk_perimeter, 2.0*sigmasq)

    return maximum(disk, falloff)


def ring(x, y, width, height, thickness, gaussian_width):
    """
    Elliptical ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
    """    
    ellipse = __ellipse(x,y,width/2.0,height/2.0)  

    inner_perimeter = ellipse - thickness
    outer_perimeter = ellipse + thickness

    ring = bitwise_xor(greater_equal(inner_perimeter,0.0),greater_equal(outer_perimeter,0.0)) 

    sigmasq = gaussian_width*gaussian_width
    inner_falloff = __exp(-inner_perimeter*inner_perimeter, 2.0*sigmasq)
    outer_falloff = __exp(-outer_perimeter*outer_perimeter, 2.0*sigmasq)

    return maximum(inner_falloff,maximum(outer_falloff,ring))


def __ellipse(x,y,a,b):
    """
    Return the ellipse specified by (x/a)^2 + (y/b)^2 = 1.
    """
    x_a = divide(x,a)
    y_b = divide(y,b)
    
    return 1.0 - (x_a*x_a + y_b*y_b)  


def __exp(x,denom):
    """
    Special-case exp() function for some functions in this file:

    Return  0.0             if x==0.0 and denom==0
            exp(x/denom)    otherwise

    Functions in this file that calculate an exp(x/denom) need
    to have well-defined behaviour when x is 0, whatever the value
    of denom.
    """
    # x/denom==nan if x==denom==0; 0 is returned in that case
    return where(x!=0.0, exp(divide(x,denom)),0.0)


                
           

