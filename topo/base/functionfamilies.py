"""
Basic function objects.

OutputFns: accept and modify a 2d array
ResponseFns: accept two 2d arrays and return a scalar
LearningFns: accept two 2d arrays and a scalar, return one of the arrays modified


$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: Documentation is just draft.

import Numeric

from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import ClassSelectorParameter


class OutputFn(ParameterizedObject):
    """
    Object to map a numeric item into another of the same size.

    Typically used for transforming an array of intermediate results
    into a final version.  For instance, when computing the output of
    a Sheet, one will often first compute a linear sum, then use a
    sigmoidal OutputFunction to transform that into the final result.

    Objects in this class must support being called as a function with
    one argument, typically a matrix, and return a matrix of the same
    size.  If implemented using Numeric functions, subclasses of this
    class should also work for scalars.  For matrix or other mutable
    objects, the argument x may be modified by the call to this function,
    and is not currently guaranteed to have the same value as the one
    returned by this function.
    """
    _abstract_class_name = "OutputFn"
    
    # CEBHACKALERT: can we have this here - is there a more appropriate
    # term for it, general to output functions?
    norm_value = Parameter(default=None)
    
    def __call__(self,x):
        raise NotImplementedError


# Trivial example of an OutputFn, provided for when a default
# is needed.  The other concrete OutputFunction classes are stored
# in outputfns/, to be imported as needed.
class IdentityOF(OutputFn):
    """
    Identity function, returning its argument as-is.

    For speed, calling this function object is sometimes optimized
    away entirely.  To make this feasible, it is not allowable to
    derive other classes from this object, modify it to have different
    behavior, add side effects, or anything of that nature.
    """

    def __call__(self,x,sum=None):
        return x


class OutputFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any OutputFn, i.e., a function
    mapping a 2D array to a 2D array.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    packages = []
    
    def __init__(self,default=IdentityOF(),**params):
        super(OutputFnParameter,self).__init__(OutputFn,default=default,**params)




class LearningFn(ParameterizedObject):
    """
    Abstract base class for learning functions that plug into
    GenericCFPLearningFn.
    """

    _abstract_class_name = "LearningFn"

    # JABALERT: Shouldn't the single_connection_learning_rate be
    # omitted from the call and instead made into a class parameter?
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        """
        Apply this learning function given the input and output
        activities and current weights.
        
        Must be implemented by subclasses.
        """
        raise NotImplementedError


class Hebbian(LearningFn):
    """
    Basic Hebbian rule; Dayan and Abbott, 2001, equation 8.3.

    Increases each weight in proportion to the product of this
    neuron's activity and the input activity.
    
    Requires some form of output_fn normalization for stability.
    """
    
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        weights += single_connection_learning_rate * unit_activity * input_activity


class IdentityLF(LearningFn):
    """
    Identity function; does not modify the weights.

    For speed, calling this function object is sometimes optimized
    away entirely.  To make this feasible, it is not allowable to
    derive other classes from this object, modify it to have different
    behavior, add side effects, or anything of that nature.
    """
    
    def __call__(self,input_activity, unit_activity, weights, single_connection_learning_rate):
        pass





class LearningFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any LearningFunction.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    packages = []

    def __init__(self,default=Hebbian(),**params):
        super(LearningFnParameter,self).__init__(LearningFn,default=default,**params)        



class ResponseFn(ParameterizedObject):
    """Abstract base class for response functions that plug into GenericCFPResponseFn."""

    _abstract_class_name = "ResponseFn"

    def __call__(self,m1,m2):
        """
        Apply the response function; must be implemented by subclasses.
        """
        raise NotImplementedError


### JAB: Could be rewritten using weave.blitz to avoid creating a temporary
# CB: that comment also applies to all the functions in Numeric that
# create an intermediate array, so don't operate in-place.
class DotProduct(ResponseFn):
    """
    Return the sum of the element-by-element product of two 2D
    arrays.  
    """
    def __call__(self,m1,m2):
        # Works in cases where dot(a.flat,b.flat) fails, e.g, with
        # matrix slices or submatrices.
        # CB: presumably that is to do with whether or not the arrays
        # are each contiguous.        
        a = m1*m2
        return Numeric.sum(a.flat)


class ResponseFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any ResponseFunction.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    packages = []

    def __init__(self,default=DotProduct(),**params):
        super(ResponseFnParameter,self).__init__(ResponseFn,default=default,**params)        

