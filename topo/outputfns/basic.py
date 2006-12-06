"""
Simple functions operating on a matrix, potentially modifying it.

These are useful for neuron output functions, normalization of
matrices, etc.

All of these function objects (callable objects) should work for
Numeric array arguments of arbitrary shape.  Some may also work for
scalars.

$Id$
"""
__version__='$Revision$'


import Numeric
import copy
from Numeric import dot, exp
from math import ceil

from topo.base.arrayutils import clip_in_place,clip_lower
from topo.base.arrayutils import L2norm, norm, array_argmax
from topo.base.functionfamilies import OutputFn
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.patterngenerator import PatternGeneratorParameter
from topo.base.boundingregion import BoundingBox
from topo.patterns.basic import Gaussian

# Imported here so that all OutputFns will be in the same package
from topo.base.functionfamilies import IdentityOF


# CEBHACKALERT: these need to respect the mask - which will be passed in.


class PiecewiseLinear(OutputFn):
    """ 
    Piecewise-linear OutputFn with lower and upper thresholds.
    
    Values below the lower_threshold are set to zero, those above
    the upper threshold are set to 1.0, and those in between are
    scaled linearly.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        fact = 1.0/(self.upper_bound-self.lower_bound)        
        x -= self.lower_bound
        x *= fact
        clip_in_place(x,0.0,1.0)



class Sigmoid(OutputFn):
    """ 
    Sigmoidal (logistic) output function 1/(1+exp-(r*x+k)).
    Parameters r and k control the growth rate (r) and the x-position (k)
    of the exponential. As defined in Jochen Triesch,ICANN 2005, LNCS 3696 pp.65-70. 
    
    This function is also a special case of the Generalized Logistic function below with r=r l=0, u=1, m=-k/2r and b=1
    Richards, F.J. 1959 A flexible growth function for empirical use. J. Experimental Botany 10: 290--300, 1959
    http://en.wikipedia.org/wiki/Generalised_logistic_curve
    
    """
    r = Number(default=1,doc="Parameter controlling the growth rate")
    k = Number(default=0,doc="Parameter controlling the x-postion")
    
    def __call__(self,x):

        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.r*x_orig+self.k)))
                  

class GeneralizedLogistic(OutputFn):
    """ 
    The generalized logistic curve (Richards' curve), flexible function for specifying a nonlinear growth curve.
    y = l + ( u /(1 + b exp(-r (x - 2m)) ^ (1 / b)) )

    It has five parameters:

    * l: the lower asymptote;
    * u: the upper asymptote minus l;
    * m: the time of maximum growth;
    * r: the growth rate;
    * b: affects near which asymptote maximum growth occurs.

    Richards, F.J. 1959 A flexible growth function for empirical use. J. Experimental Botany 10: 290--300, 1959
    http://en.wikipedia.org/wiki/Generalised_logistic_curve

    """
    l = Number(default=1,doc="Parameter controlling the lower asymptote")
    u = Number(default=1,doc="Parameter controlling the upper asymptote (upper asymptote minus lower asymptote")
    m = Number(default=1,doc="Parameter controlling the time of maximum growth.")
    r = Number(default=1,doc="Parameter controlling the growth rate.")
    b = Number(default=1,doc="Parameter which affects near which asymptote maximum growth occurs")
    
    def __call__(self,x):
        
        x_orig = copy.copy(x)
        x *= 0.0
        x += self.l + ( self.u /(1 + self.b*exp(-self.r *(x_orig - 2*self.m))**(1 / self.b)) )    


class DivisiveNormalizeL1(OutputFn):
    """
    OutputFn that divides an array by its L1 norm.

    This operation ensures that the sum of the absolute values of the
    array is equal to the specified norm_value, rescaling each value
    to make this true.  The array is unchanged if the sum of absolute
    values is zero.  For arrays of non-negative values where at least
    one is non-zero, this operation is equivalent to a divisive sum
    normalization.
    """
    norm_value = Number(default=1.0)

    def __call__(self,x):
        """L1-normalize the input array, if it has a nonzero sum."""
        current_sum = 1.0*Numeric.sum(abs(x.flat))
        if current_sum != 0:
            factor = (self.norm_value/current_sum)
            x *= factor


class DivisiveNormalizeL2(OutputFn):
    """
    OutputFn to divide an array by its Euclidean length (aka its L2 norm).

    For a given array interpreted as a flattened vector, keeps the
    Euclidean length of the vector at a specified norm_value.
    """
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*L2norm(x.flat)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor


class DivisiveNormalizeLinf(OutputFn):
    """
    OutputFn to divide an array by its L-infinity norm
    (i.e. the maximum absolute value of its elements).

    For a given array interpreted as a flattened vector, scales the
    elements divisively so that the maximum absolute value is the
    specified norm_value.

    The L-infinity norm is also known as the divisive infinity norm
    and Chebyshev norm.
    """
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*max(abs(x.flat))
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor

    
class DivisiveNormalizeLp(OutputFn):
    """
    OutputFn to divide an array by its Lp-Norm, where p is specified.

    For a parameter p and a given array interpreted as a flattened
    vector, keeps the Lp-norm of the vector at a specified norm_value.
    Faster versions are provided separately for the typical L1-norm
    and L2-norm cases.  Defaults to be the same as an L2-norm, i.e.,
    DivisiveNormalizeL2.
    """
    p = Number(default=2)
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*norm(x.flat,self.p)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *=factor 


class HalfRectifyAndSquare(OutputFn):
    """
    Output function that applies a half-wave rectification (clips at zero)
    and then squares the values.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        clip_lower(x,self.lower_bound)
        x *= x

class HalfRectify(OutputFn):
    """
    Output function that applies a half-wave rectification (clips at zero)
    
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        clip_lower(x,self.lower_bound)


class Square(OutputFn):
    """
    Output function that applies a squaring nonlinearity

    """

    def __call__(self,x):
    
        x *= x     
        

class BinaryThreshold(OutputFn):
    """
    Forces all values below a threshold to zero, and above it to 1.0.
    """
    threshold = Number(default=0.25, doc="Decision point for determining binary value.")

    def __call__(self,x):
        above_threshold = x>=self.threshold
        x *= 0.0
        x += above_threshold

class KernelMax(OutputFn):
    """
    Based upon CFPLF_HebbianSOM but without learning. Finds the maximum activity and
    replaces the output with a kernel centered around the max

    The radius of the surround is specified by the parameter
    kernel_radius, which should be set before using __call__.  The
    shape of the surround is determined by the neighborhood_kernel_generator, 
    and can be any PatternGenerator instance, or any function accepting
    bounds, density, radius, and height to return a kernel matrix.
    """
    kernel_radius = Number(default=0.0)  
    crop_radius_multiplier = Number(default=3.0,doc=
        """
        Factor by which the radius should be multiplied,
        when deciding how far from the winner to extend the kernel.
        """)
    
    neighborhood_kernel_generator = PatternGeneratorParameter(
        default=Gaussian(x=0.0,y=0.0,aspect_ratio=1.0),
        doc="Neighborhood function")
  
    def __call__(self, x):
      	output_activity=x
        rows,cols = output_activity.shape
        radius = self.kernel_radius
        crop_radius = max(1.25,radius*self.crop_radius_multiplier)

        # find out the matrix coordinates of the winner
        wr,wc = array_argmax(output_activity)

        # Calculate the bounding box around the winner
        cmin = int(max(0,wc-crop_radius))
        cmax = int(min(wc+crop_radius+1,cols)) # at least 1 between cmin and cmax
        rmin = int(max(0,wr-crop_radius))
        rmax = int(min(wr+crop_radius+1,rows))

        # generate the kernel matrix and set output activity to it.
        nk_generator = self.neighborhood_kernel_generator
        radius_int = int(ceil(crop_radius))
        rbound = radius_int + 0.5
        bb = BoundingBox(points=((-rbound,-rbound), (rbound,rbound)))
        x = nk_generator(bounds=bb,xdensity=1,ydensity=1,
                                           size=2*radius)

