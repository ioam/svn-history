"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array);
the functions therefore have the same mathematical behaviour as Numeric.

$Id$
"""
__version__='$Revision$'



from math import pi

from Numeric import where,maximum,cos,sin,sqrt,divide,greater_equal,bitwise_xor

from topo.base.arrayutils import exp


# CEB: Divide is imported from Numeric so that mathematical
# expressions with scalars (such as exp(-(3.0/0.0)) ) are evaluated
# correctly. Unfortunately this makes such expressions more difficult
# to read. How can Numeric's / operator be made to override Python's /
# operator for scalars?
# Also, we use x*x rather x**2 in exp argument because


def gaussian(x, y, xsigma, ysigma):
    """
    Two-dimensional oriented Gaussian pattern (i.e., 2D version of a
    bell curve, like a normal distribution but not necessarily summing
    to 1.0).
    """
    x_w = divide(x,xsigma)
    y_h = divide(y,ysigma)
    return exp(-0.5*x_w*x_w + -0.5*y_h*y_h)


def gabor(x, y, xsigma, ysigma, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """ 
    x_w = divide(x,xsigma)
    y_h = divide(y,ysigma)
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


def disk(x, y, height, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    disk_radius = height/2.0
    
    distance_from_origin = sqrt(x**2+y**2)
    distance_outside_disk = distance_from_origin - disk_radius

    sigmasq = gaussian_width*gaussian_width
    falloff = __exp(-distance_outside_disk*distance_outside_disk, 2*sigmasq)

    return where(distance_outside_disk<=0,1.0,falloff)


def ring(x, y, height, thickness, gaussian_width):
    """
    Circular ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
    """
    radius = height/2.0
    half_thickness = thickness/2.0

    distance_from_origin = sqrt(x**2+y**2)
    distance_outside_outer_disk = distance_from_origin - radius - half_thickness
    distance_inside_inner_disk = radius - half_thickness - distance_from_origin

    ring = 1.0-bitwise_xor(greater_equal(distance_inside_inner_disk,0.0),greater_equal(distance_outside_outer_disk,0.0))

    sigmasq = gaussian_width*gaussian_width  
    inner_falloff = __exp(-distance_inside_inner_disk*distance_inside_inner_disk, 2.0*sigmasq)
    outer_falloff = __exp(-distance_outside_outer_disk*distance_outside_outer_disk, 2.0*sigmasq)

    return maximum(inner_falloff,maximum(outer_falloff,ring))



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
    return where(x!=0.0, exp(divide(x,float(denom))),0.0)


                
           

