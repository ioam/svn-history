"""
Basic function objects.

OutputFns: accept and modify a 2d array
ResponseFns: accept two 2d arrays and return a scalar
LearningFns: accept two 2d arrays and a scalar, return one of the arrays modified

$Id$
"""
__version__='$Revision$'

# CEBALERT: Documentation is just draft.

import numpy

from topo.base.parameterizedobject import ParameterizedObject,Parameter
from topo.base.parameterclasses import ListParameter


class OutputFn(ParameterizedObject):
    """
    Function object to modify a matrix in place, e.g. for normalization.

    Used for transforming an array of intermediate results into a
    final version, by cropping it, normalizing it, squaring it, etc.
    
    Objects in this class must support being called as a function with
    one matrix argument, and are expected to change that matrix in place.
    """
    __abstract = True
    
    # CEBALERT: can we have this here - is there a more appropriate
    # term for it, general to output functions?  JAB: Please do rename it!
    norm_value = Parameter(default=None)


    def __call__(self,x):
        raise NotImplementedError

    def __add__(self,of):
        assert isinstance(of,OutputFn), "OutputFns can only be added to other OutputFns"
        return PipelineOF(output_fns=[self,of])




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



class PipelineOF(OutputFn):
    """
    Applies a list of other OutputFns in order, to combine their effects.


    Also, passes through method call requests to the list of
    OutputFns. For instance, if an OutputFn o1 has a method m(arg1),
    then the following results in m being called on o1:
    
     p = PipelineOF(output_fns=[IdentityOF(),o1])
     p.m(7)  # calls m(7) on o1 but not on the IdentityOF
    """
    output_fns = ListParameter(default=[],class_=OutputFn,doc="""
        List of OutputFns to apply, in order.  The default is an empty list, 
        which should be overridden for any useful work.""")

    def __call__(self,x):
        for of in self.output_fns:
            of(x)

    def __iadd__(self,of):
        assert isinstance(of,OutputFn), "OutputFns can only be added to other OutputFns"
        self.output_fns.append(of)

    def __add__(self,of):
        # Returns a single new Pipeline rather than a nested Pipeline
        assert isinstance(of,OutputFn), "OutputFns can only be added to other OutputFns"
        return PipelineOF(output_fns=self.output_fns+[of])

    def override_plasticity_state(self, new_plasticity_state):
        """
        Calls override_plasticity_state on every output_fn
        in the list that defines that method.
        """
        for of in self.output_fns:
            if hasattr(of,"override_plasticity_state"):
                of.override_plasticity_state(new_plasticity_state)

    def restore_plasticity_state(self):
        """
        Calls restore_plasticity_state on every output_fn
        in the list that defines that method.
        """
        for of in self.output_fns:
            if hasattr(of,"restore_plasticity_state"):
                of.restore_plasticity_state()


    # We don't use norm_value ourselves, so if someone asks for it,
    # return an underlying value from self.output_fns.  Only in the
    # case where a single underlying OF defines norm_value is that
    # meaningful to do, so we ensure that we only return something in
    # that specific case.
    def __get_norm_value(self):
        found=False
        for of in self.output_fns:
            if of.norm_value is not None:
                if found==True:
                    raise ValueError("At most one OF in a PipelineOF may define norm_value")
                val=of.norm_value
                found=True
        if found: return val
        return None

    def __set_norm_value(self,norm_value):
        raise ValueError("Set the norm_value on one of the individual output_fns instead.")

    norm_value = property(__get_norm_value,__set_norm_value)



class LearningFn(ParameterizedObject):
    """
    Abstract base class for learning functions that plug into
    CFPLF_Plugin.
    """

    __abstract = True

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



class ResponseFn(ParameterizedObject):
    """Abstract base class for response functions that plug into CFPRF_Plugin."""

    __abstract = True

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



class CoordinateMapperFn(ParameterizedObject):
    """Abstract base class for functions mapping from a 2D coordinate into another one."""

    __abstract = True

    def __call__(self,x,y):
        """
        Apply the coordinate mapping function; must be implemented by subclasses.
        """
        raise NotImplementedError


class IdentityMF(CoordinateMapperFn):
    """Return the x coordinate of the given coordinate."""
    def __call__(self,x,y):
        return x,y


