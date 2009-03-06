from __future__ import with_statement
"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
numpy arrays of x and y (in which case the result is also an array);
the functions therefore have the same mathematical behaviour as numpy.

$Id$
"""
__version__='$Revision$'



from math import pi

from numpy.oldnumeric import where,maximum,cos,sin,sqrt,divide,greater_equal,bitwise_xor,exp
from numpy import seterr

from contextlib import contextmanager

@contextmanager
def float_error_ignore():
    """
    Many of the functions in this module use Gaussian smoothing, which
    is based on a calculation like exp(divide(x*x,sigma)).  When sigma
    is zero the value of this expression should be zero at all points
    in the plane, because such a Gaussian is infinitely small.
    Obtaining the correct answer using finite-precision floating-point
    array computations requires allowing infinite values to be
    returned from divide(), and allowing exp() to underflow silently
    to zero when given an infinite value.  In numpy this is achieved
    by using its seterr() function to disable divide-by-zero and
    underflow warnings temporarily while these values are being
    computed.
    """
    oldsettings=seterr(divide='ignore',under='ignore')
    yield
    seterr(**oldsettings)



def gaussian(x, y, xsigma, ysigma):
    """
    Two-dimensional oriented Gaussian pattern (i.e., 2D version of a
    bell curve, like a normal distribution but not necessarily summing
    to 1.0).
    """
    if xsigma==0.0 or ysigma==0.0:
        return x*0.0

    with float_error_ignore():
        x_w = divide(x,xsigma)
        y_h = divide(y,ysigma)
        return exp(-0.5*x_w*x_w + -0.5*y_h*y_h)


def exponential(x, y, xscale, yscale):
    """
    Two-dimensional oriented exponential decay pattern.
    """
    if xscale==0.0 or yscale==0.0:
        return x*0.0
    
    with float_error_ignore():
        x_w = divide(x,xscale)
        y_h = divide(y,yscale)
        return exp(-sqrt(x_w*x_w+y_h*y_h))


def gabor(x, y, xsigma, ysigma, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """
    if xsigma==0.0 or ysigma==0.0:
        return x*0.0
    
    with float_error_ignore():
        x_w = divide(x,xsigma)
        y_h = divide(y,ysigma)
        p = exp(-0.5*x_w*x_w + -0.5*y_h*y_h)
    return p * 0.5*cos(2*pi*frequency*y + phase)


# JABHACKALERT: Shouldn't this use 'size' instead of 'thickness',
# for consistency with the other patterns?  Right now, it has a
# size parameter and ignores it, which is very confusing.  I guess
# it's called thickness to match ring, but matching gaussian and disk
# is probably more important.
def line(y, thickness, gaussian_width):
    """
    Infinite-length line with a solid central region, then Gaussian fall-off at the edges.
    """
    distance_from_line = abs(y)
    gaussian_y_coord = distance_from_line - thickness/2.0
    sigmasq = gaussian_width*gaussian_width

    if sigmasq==0.0:
        falloff = x*0.0
    else:
        with float_error_ignore():
            falloff = exp(divide(-gaussian_y_coord*gaussian_y_coord,2*sigmasq))

    return where(gaussian_y_coord<=0, 1.0, falloff)


def disk(x, y, height, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    disk_radius = height/2.0

    distance_from_origin = sqrt(x**2+y**2)
    distance_outside_disk = distance_from_origin - disk_radius
    sigmasq = gaussian_width*gaussian_width

    if sigmasq==0.0:
        falloff = x*0.0
    else:
        with float_error_ignore():
            falloff = exp(divide(-distance_outside_disk*distance_outside_disk,
                                  2*sigmasq))

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

    if sigmasq==0.0:
        inner_falloff = x*0.0
        outer_falloff = x*0.0
    else:
        with float_error_ignore():
            inner_falloff = exp(divide(-distance_inside_inner_disk*distance_inside_inner_disk, 2.0*sigmasq))
            outer_falloff = exp(divide(-distance_outside_outer_disk*distance_outside_outer_disk, 2.0*sigmasq))

    return maximum(inner_falloff,maximum(outer_falloff,ring))
