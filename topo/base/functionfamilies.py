"""
Basic function objects.

OutputFns: accept and modify a 2d array
ResponseFns: accept two 2d arrays and return a scalar
LearningFns: accept two 2d arrays and a scalar, return one of the arrays modified


$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: still being built up. Documentation is just draft.

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
