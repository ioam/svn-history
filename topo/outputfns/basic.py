"""
Simple functions mapping from a value into another of the same shape.

A set of endomorphic functions, i.e., functions mapping from an object
into another of the same matrix shape.  These are useful for neuron
output functions, normalization of matrices, etc.

All of these function objects (callable objects) should work for
Numeric array arguments of arbitrary shape.  Some will also work for
scalars.

$Id$
"""
__version__='$Revision$'

import Numeric
from Numeric import clip
from topo.base.topoobject import TopoObject
from topo.base.parameter import Number
from topo.base.arrayutils import L2norm, norm
from topo.base.projection import OutputFunction

# Imported here so that all OutputFunctions will be in the same package
from topo.base.projection import Identity

### JCALERT! The functions below have been re-written to work as procedure;
### Nonetheless, I kept the return x statement in order to not be worry about
### changing the call anywhere else in the code. That might have to be done later.
### Also note that the test file still test the method for both procedure and function calls

class PiecewiseLinear(OutputFunction):
    """ 
    Piecewise-linear output function with lower and upper thresholds
    as constructor parameters.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    
    def __init__(self,**params):
        super(PiecewiseLinear,self).__init__(**params)

    def __call__(self,x):
        fact = 1.0/(self.upper_bound-self.lower_bound)        
        x -= self.lower_bound
        x *= fact
        # CEBHACKALERT: Numeric.clip() is really a lot faster than
        # utils.clip_in_place() so I changed it. Was there
        # a special reason for not using Numeric.clip()?
        # Is it because internally it creates a new array?
        clip(x,0.0,1.0)
        return x

class DivisiveSumNormalize(OutputFunction):
    """
    OutputFunction that divides an array by its sum (aka its L1 norm).

    This operation ensures that an array has a sum equal to the specified 
    norm_value, rescaling each value to make this true.  The array is 
    unchanged if the sum is zero.
    """
    norm_value = Number(default=1.0)
    
    def __init__(self,**params):
        super(DivisiveSumNormalize,self).__init__(**params)

    def __call__(self,x):
        tot = 1.0*sum(x.flat)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor
        return x


class DivisiveLengthNormalize(OutputFunction):
    """
    OutputFunction to divide an array by its Euclidean length (aka its L2 norm).

    For a given array interpreted as a flattened vector, keeps the
    Euclidean length of the vector at a specified norm_value.
    """
    norm_value = Number(default=1.0)
    
    def __init__(self,**params):
        super(DivisiveLengthNormalize,self).__init__(**params)

    def __call__(self,x):
        tot = 1.0*L2norm(x.flat)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor
        return x


class DivisiveMaxNormalize(OutputFunction):
    """
    OutputFunction to divide an array by the absolute value of its maximum.

    For a given array interpreted as a flattened vector, scales the
    elements divisively so that the maximum absolute value is the
    specified norm_value.  This is also called the divisive
    L-infinity, infinity, or Chebyshev norm.
    """
    norm_value = Number(default=1.0)
    
    def __init__(self,**params):
        super(DivisiveMaxNormalize,self).__init__(**params)

    def __call__(self,x):
        tot = 1.0*max(abs(x.flat))
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor
        return x

    
class DivisiveLpNormalize(OutputFunction):
    """
    OutputFunction to divide an array by its Lp-Norm, where p is specified.

    For a parameter p and a given array interpreted as a flattened
    vector, keeps the Lp-norm of the vector at a specified norm_value.
    Faster versions are provided separately for the typical L1-norm
    and L2-norm cases.  Defaults to be the same as an L2-norm, i.e.,
    DivisiveLengthNormalize.
    """
    p = Number(default=2)
    norm_value = Number(default=1.0)
    
    def __init__(self,**params):
        super(DivisiveLpNormalize,self).__init__(**params)

    def __call__(self,x):
        tot = 1.0*norm(x.flat,self.p)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *=factor 
	return x
