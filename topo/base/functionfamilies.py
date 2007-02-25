"""
Basic function objects.

OutputFns: accept and modify a 2d array
ResponseFns: accept two 2d arrays and return a scalar
LearningFns: accept two 2d arrays and a scalar, return one of the arrays modified

$Id$
"""
__version__='$Revision$'

# CEBALERT: Documentation is just draft.

import numpy.oldnumeric as Numeric
import numpy

from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import ClassSelectorParameter


class OutputFn(ParameterizedObject):
    """
    Function object to modify a matrix in place, e.g. for normalization.

    Used for transforming an array of intermediate results into a
    final version, by cropping it, normalizing it, squaring it, etc.
    
    Objects in this class must support being called as a function with
    one matrix argument, and are expected to change that matrix in place.
    """
    _abstract_class_name = "OutputFn"
    
    # CEBALERT: can we have this here - is there a more appropriate
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
        pass


class OutputFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any OutputFn, i.e., a function
    mapping a 2D array to a 2D array.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=IdentityOF(),**params):
        super(OutputFnParameter,self).__init__(OutputFn,default=default,**params)




class LearningFn(ParameterizedObject):
    """
    Abstract base class for learning functions that plug into
    CFPLF_Plugin.
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

    def __init__(self,default=Hebbian(),**params):
        super(LearningFnParameter,self).__init__(LearningFn,default=default,**params)        



class ResponseFn(ParameterizedObject):
    """Abstract base class for response functions that plug into CFPRF_Plugin."""

    _abstract_class_name = "ResponseFn"

    def __call__(self,m1,m2):
        """
        Apply the response function; must be implemented by subclasses.
        """
        raise NotImplementedError



class DotProduct(ResponseFn):
    """
    Return the sum of the element-by-element product of two 2D
    arrays.  
    """
    def __call__(self,m1,m2):
        return numpy.dot(m1.ravel(),m2.ravel())



class ResponseFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any ResponseFunction.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=DotProduct(),**params):
        super(ResponseFnParameter,self).__init__(ResponseFn,default=default,**params)        




class CoordinateMapperFn(ParameterizedObject):
    """Abstract base class for functions mapping from a 2D coordinate into another one."""

    _abstract_class_name = "CoordinateMapperFn"

    def __call__(self,x,y):
        """
        Apply the coordinate mapping function; must be implemented by subclasses.
        """
        raise NotImplementedError


class XIdentity(CoordinateMapperFn):
    """Return the x coordinate of the given coordinate."""
    def __call__(self,x,y):
        return x


class YIdentity(CoordinateMapperFn):
    """Return the y coordinate of the given coordinate."""
    def __call__(self,x,y):
        return y


class CoordinateMapperFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any ResponseFunction.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=XIdentity(),**params):
        super(CoordinateMapperFnParameter,self).__init__(CoordinateMapperFn,default=default,**params)

