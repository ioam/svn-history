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

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number
from topo.base.arrayutils import L2norm, norm
from topo.base.functionfamilies import OutputFn
from topo.base.arrayutils import clip_in_place

# Imported here so that all OutputFns will be in the same package
from topo.base.functionfamilies import IdentityOF

### JCALERT! The functions below have been re-written to work as
### procedure; Nonetheless, I kept the return x statement in order to
### not be worry about changing the call anywhere else in the
### code. That might have to be done later.  Also note that the test
### file still test the method for both procedure and function calls

# CEBHACKALERT: these need to respect the mask - which will be passed in.


class PiecewiseLinear(OutputFn):
    """ 
    Piecewise-linear output function with lower and upper thresholds
    as constructor parameters.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    
    def __call__(self,x):
        fact = 1.0/(self.upper_bound-self.lower_bound)        
        x -= self.lower_bound
        x *= fact
        clip_in_place(x,0.0,1.0)
        return x


# CEBHACKALERT: should be DivisiveNormalizeL1 (i.e. use the
# absolute values). Delete this and replace its uses with
# the DivisiveNormalizeL1 class below (see also optimized.py).
# This hasn't been done because it would require altering the C++
# functions to use the L1 norm rather than the sum.
# We keep these basic ones around as the unoptimized alternatives.
class DivisiveSumNormalize(OutputFn):
    """
    OutputFn that divides an array by its sum.

    This operation ensures that an array has a sum equal to the specified 
    norm_value, rescaling each value to make this true.  The array is 
    unchanged if the sum is zero.

    If the array's current norm_value is known (e.g. from some earlier
    calculation), it can be passed in as an optimization.
    """
    norm_value = Number(default=1.0)

    def __call__(self,x,current_norm_value=None):
        """
        Normalize the input array.

        If the array's current norm_value is already equal to the required
        norm_value, the operation is skipped.
        """
        if current_norm_value==None:
            current_norm_value = 1.0*Numeric.sum(x.flat)
        
        if current_norm_value==self.norm_value:
            return x
        
        if current_norm_value != 0:
            factor = (self.norm_value/current_norm_value)
            x *= factor

        return x


class DivisiveNormalizeL1(OutputFn):
    """
    OutputFn that divides an array by its L1 norm.

    This operation ensures that an array has a sum equal to the specified 
    norm_value, rescaling each value to make this true.  The array is 
    unchanged if the sum is zero.

    If the array's current norm_value is known (e.g. from some earlier
    calculation), it can be passed in as an optimization.
    """
    norm_value = Number(default=1.0)

    def __call__(self,x,current_norm_value=None):
        """
        Normalize the input array.

        If the array's current norm_value is already equal to the required
        norm_value, the operation is skipped.
        """

        if current_norm_value==None:
            current_norm_value = 1.0*Numeric.sum(abs(x.flat))
        
        if current_norm_value==self.norm_value:
            return x
            
        if current_norm_value != 0:
            factor = (self.norm_value/current_norm_value)
            x *= factor

        return x


class DivisiveLengthNormalize(OutputFn):
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
        return x


class DivisiveMaxNormalize(OutputFn):
    """
    OutputFn to divide an array by the absolute value of its maximum.

    For a given array interpreted as a flattened vector, scales the
    elements divisively so that the maximum absolute value is the
    specified norm_value.  This is also called the divisive
    L-infinity, infinity, or Chebyshev norm.
    """
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*max(abs(x.flat))
        if tot != 0:
            factor = (self.norm_value/tot)
            x *= factor
        return x

    
class DivisiveLpNormalize(OutputFn):
    """
    OutputFn to divide an array by its Lp-Norm, where p is specified.

    For a parameter p and a given array interpreted as a flattened
    vector, keeps the Lp-norm of the vector at a specified norm_value.
    Faster versions are provided separately for the typical L1-norm
    and L2-norm cases.  Defaults to be the same as an L2-norm, i.e.,
    DivisiveLengthNormalize.
    """
    p = Number(default=2)
    norm_value = Number(default=1.0)
    
    def __call__(self,x):
        tot = 1.0*norm(x.flat,self.p)
        if tot != 0:
            factor = (self.norm_value/tot)
            x *=factor 
	return x

