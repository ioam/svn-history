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
from topo.base.parameterclasses import ClassSelectorParameter, ListParameter, BooleanParameter


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

    def override_plasticity_state(self, new_plasticity_state):
        """
        Temporarily disable plasticity of internal state.

        This function should be implemented by all subclasses so that
        after a call, the output should always be the same for any
        given input pattern, and no call should have any effect that
        persists after a restore_plasticity() call.
        
        By default, simply saves a copy of the plastic flag to an
        internal stack (so that it can be restored by
        restore_plasticity()), and then sets plastic to False.
        """
        pass

    def restore_plasticity_state(self):
        """
        Re-enable plasticity of internal state after a disable_plasticity call.

        This function should be implemented by all subclasses to
        remove the effect of the most recent disable_plasticity call,
        i.e. to reenable changes to the internal state, without any
        lasting effect during the time that plasticity was disabled.
        """
        pass    



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

    def override_plasticity_state(self, new_plasticity_state):
        """Call the disable_plasticity function for each output_fn."""
        
        for of in self.output_fns:
            of.override_plasticity_state(new_plasticity_state)
        
    def restore_plasticity_state(self):
        """Call the restore_plasticity function for each output_fn."""

        for of in self.output_fns:
            of.restore_plasticity_state()



class OutputFnWithState(OutputFn):
    """
    Abstract base class for OutputFns that need to maintain a self.plastic parameter.

    These OutputFns typically maintain some form of internal history
    or other state from previous calls, which can be disabled by
    disable_plasticity().
    """

    plastic = BooleanParameter(default=True, doc="""
        Whether or not to update the internal state on each call.
        Allows plasticity to be turned off during analysis, and then re-enabled.""")


    def __init__(self,**params):
        super(OutputFnWithState,self).__init__(**params)
        self._plasticity_setting_stack = []


    def override_plasticity_state(self, new_plasticity_state):
        """
        Temporarily disable plasticity of internal state.

        This function should be implemented by all subclasses so that
        after a call, the output should always be the same for any
        given input pattern, and no call should have any effect that
        persists after a restore_plasticity() call.
        
        By default, simply saves a copy of the plastic flag to an
        internal stack (so that it can be restored by
        restore_plasticity()), and then sets the plastic parameter to False.
        """
        self._plasticity_setting_stack.append(self.plastic)
        self.plastic=new_plasticity_state


    def restore_plasticity_state(self):
        """
        Re-enable plasticity of internal state after a disable_plasticity call.

        This function should be implemented by all subclasses to
        remove the effect of the most recent disable_plasticity call,
        i.e. to reenable changes to the internal state, without any
        lasting effect during the time that plasticity was disabled.

        By default, simply restores the last saved value of the
        plastic parameter.
        """
        self.plastic = self._plasticity_setting_stack.pop()                        



class OutputFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any OutputFn, i.e., a function
    mapping a 2D array to a 2D array.
    """
    def __init__(self,default=IdentityOF(),**params):
        super(OutputFnParameter,self).__init__(OutputFn,default=default,**params)




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


class LearningFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any LearningFunction.
    """
    def __init__(self,default=Hebbian(),**params):
        super(LearningFnParameter,self).__init__(LearningFn,default=default,**params)        



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



class ResponseFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any ResponseFunction.
    """
    def __init__(self,default=DotProduct(),**params):
        super(ResponseFnParameter,self).__init__(ResponseFn,default=default,**params)        




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




class CoordinateMapperFnParameter(ClassSelectorParameter):
    """
    Parameter whose value can be any CoordinateMapperFn.
    """
    def __init__(self,default=IdentityMF(),**params):
        super(CoordinateMapperFnParameter,self).__init__(CoordinateMapperFn,default=default,**params)

