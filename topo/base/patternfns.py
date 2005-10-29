"""
Family of two-dimensional functions indexed by x and y.

All functions are written to be valid both for scalar x and y, and for
Numeric arrays of x and y (in which case the result is also an array);
the functions therefore have the same mathematical behaviour as Numeric.

$Id$
"""

from math import pi
from Numeric import where,maximum,exp,cos,sin,sqrt,less_equal,divide

# CEB:
# There are three kinds of hack in this file. The first is safeexp: there
# because Numeric gives an overflow error for e.g. exp(-800) (although it's
# happy with exp(-inf) ).
# The second is in gabor() and gaussian(). Numeric will return -inf*inf as -inf,
# but -(inf**2) raises an error.
# The third is in line(), disk(), and ring(). In line(), there could be
# an attempt to do 0/0, which is undefined and raises an error. In disk and ring,
# there could be attempts to calculate 0*inf, which is again undefined.
# The hack in line() could be changed to be like that in disk() and ring() for
# consistency, but probably there is a better solution than either.
# E.g. SciPy supposedly returns nan and inf values properly in arrays. Then, where()
# could be used to return either a value calculated with exp or the limit, as required.


# CEB:
# Divide is imported from Numeric so that mathematical expressions such
# as exp(-(3.0/0.0)) are evaluated correctly. Unfortunately this makes
# such as expressions more difficult to read. How can Numeric's / operator
# be made to override Python's / operator for scalars?


# CEBHACKALERT: 
# For patternfns.py, this only needs to handle arguments that are of large
# magnitude and negative. A better version of this function could be put in
# utils for general use, returning 0.0 if there is underflow and Inf
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
    # CEBHACKALERT:
    # Allows exp(a^2) in the case that a is inf
    x_arg = divide(x,width)
    x_arg = -x_arg * x_arg
    y_arg = divide(y,height)
    y_arg = -y_arg * y_arg
    return safeexp(x_arg + y_arg)


def gabor(x, y, width, height, frequency, phase):
    """
    Gabor pattern (sine grating multiplied by a circular Gaussian).
    """ 
    # CEBHACKALERT:
    # Allows exp(a^2) in the case that a is inf
    x_arg = divide(x,width)
    x_arg = -x_arg * x_arg
    y_arg = divide(y,height)
    y_arg = -y_arg * y_arg
    p = safeexp(x_arg + y_arg)
    
    return p * (0.5 + 0.5*cos(2*pi*frequency*x + phase))


def line(x, center_width, gaussian_width):
    """
    Infinite-length line with a solid central region, then Gaussian fall-off at the edges.
    """
    distance_from_line = abs(x)
    gaussian_x_coord = distance_from_line - center_width/2

    # CEBHACKALERT:
    # temporary fix to avoid 0/0 error (see below).
    if gaussian_width==0:
        return where(gaussian_x_coord<=0.0,1.0,0.0)
    else:
        return where(gaussian_x_coord<=0.0, 1.0,
                 safeexp(-(divide(gaussian_x_coord,gaussian_width))**2))
        
# CEB: the second "where" doesn't work on its own because where calculates safeexp for gaussian_x_coord==0.0,
# even though it doesn't actually use it (it should return 1.0 in such cases). This is a problem because
# if gaussian_width is also 0, then it tries 0/0 which is undefined.
#
# ( It seems that the where(test,pass_expression,fail_expression) function calculates fail_expression
#   and pass_expression every time, though it will only return the result of pass_expression. )


def disk(x, y, disk_radius, gaussian_width):
    """
    Circular disk with Gaussian fall-off after the solid central region.
    """
    distance_from_line = sqrt((x**2)+(y**2)) 
    gaussian_x_coord   = distance_from_line - disk_radius/2.0 
    div_sigmasq = divide(1.0,(gaussian_width*gaussian_width))

    # CEBHACKALERT:
    # avoids math range error which would result from trying to do exp(0*inf) (0*inf being nan)
    if gaussian_width == 0.0:
        exp_arg = where(gaussian_x_coord==0.0,-float('inf'),-gaussian_x_coord*gaussian_x_coord*div_sigmasq)
    else:
        exp_arg = -gaussian_x_coord*gaussian_x_coord*div_sigmasq

    disk = less_equal(gaussian_x_coord,0)
    return maximum(disk, safeexp(exp_arg))



def ring(x, y, disk_radius, ring_radius, gaussian_width):
    """
    Circular ring (annulus) with Gaussian fall-off after the solid ring-shaped region.
    """    
    ring_radius = ring_radius / 2.0
    distance_from_line = abs(sqrt((x**2)+(y**2)) - disk_radius)
    inner_distance = distance_from_line - ring_radius
    outer_distance = distance_from_line + ring_radius
    div_sigmasq = divide(1.0,(gaussian_width*gaussian_width))

    ring = less_equal(distance_from_line,ring_radius)

    # CEBHACKALERT:
    # avoids math range error which would result from trying to do exp(0*inf) (0*inf being nan)
    if gaussian_width == 0.0:
        inner_exp_arg = where(inner_distance==0.0,-float('inf'),-inner_distance*inner_distance*div_sigmasq)
        outer_exp_arg = where(outer_distance==0.0,-float('inf'),-outer_distance*outer_distance*div_sigmasq)
    else:
        inner_exp_arg = -inner_distance*inner_distance*div_sigmasq
        outer_exp_arg = -outer_distance*outer_distance*div_sigmasq


    inner_g = safeexp(-inner_distance*inner_distance*div_sigmasq)
    outer_g = safeexp(-outer_distance*outer_distance*div_sigmasq)

    dring = maximum(inner_g,maximum(outer_g,ring))
    return dring



