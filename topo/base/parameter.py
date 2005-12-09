"""
Module for handling experiment parameters and defaults.

This module defines an attribute descriptor for experiment parameters.
An experiment parameter is represented in Topographica as a special
kind of class attribute.  See the Parameter class documentation for
more details.

$Id$
"""
__version__='$Revision$'
from utils import classlist


class Parameter(object):
    """
    An attribute descriptor for declaring Topographica parameters.

    Simulation parameters are represented in Topographica as a special
    kind of class attribute.  Setting a class attribute to be an
    instance of this class causes that attribute of the class and its
    instances to be treated as a Topographica parameter.  This allows
    special behavior, including dynamically generated parameter values
    (using lambdas or generators), and type or range checking at
    assignment time.

    For example, suppose someone has defined a new kind of sheet, that
    has parameters alpha, sigma, and gamma.  He would begin his class
    definition something like this:

    class FooSheet(Sheet):
        alpha = Parameter(default=0.1)
        sigma = Parameter(default=0.0)
        gamma = Parameter(default=1.0)
        ...

    Parameters have several advantages over plain attributes:

    1. They can be set automatically in an instance:  The FooSheet
        __init__ method should call setup_params(self,FooSheet,**args),
        where **args is the dictionary of keyword arguments passed to the
        constructor.  This function will discover all the parameters in
        FooSheet, and set them from the arguments passed in.  E.g., if a
        script does this:

            myfoo = FooSheet(alpha=0.5)

        myfoo.alpha will return 0.5, without the foosheet constructor
        needing special code to set alpha.

    2. They can be dynamic.  If a Parameter is declared as Dynamic, it can
        be set to be a callable object (e.g a function), and getting the
        parameter's value will call that callable.  E.g.  To cause all
        FooSheets to draw their gammas from a gaussian distribution you'd
        write something like:

            from random import gauss
            FooSheet.sigma = Dynamic(lambda:gauss(0.5,0.1))

        If a Dynamic Parameter's value is set to a Python generator or iterator,
        then when the Parameter is accessed, the iterator's .next() method
        is called.  So to get a parameter that cycles through a sequence,
        you could write:
            from itertools import cycle
            FooSheet.sigma = Dynamic(cycle([0.1,0.5,0.9]))

    3. The Parameter descriptor class can be subclassed to provide more
        complex behavior, allowing special types of parameters that, for
        example, require their values to be numbers in certain ranges, or
        read their values from a file or other external source.


    One of the key benefits of __slots__ is given in the reference manual
    at http://www.python.org/doc/2.4/ref/slots.html:
    
        By default, instances of both old and new-style classes have a
        dictionary for attribute storage. This wastes space for
        objects having very few instance variables. The space
        consumption can become acute when creating large numbers of
        instances.

        The default can be overridden by defining __slots__ in a
        new-style class definition. The __slots__ declaration takes a
        sequence of instance variables and reserves just enough space
        in each instance to hold a value for each variable. Space is
        saved because __dict__ is not created for each instance.

    Note that the actual value of a Parameter is not stored in the
    Parameter object itself, but in the owning object's __dict__.

    See this HOW-TO document for a good intro to descriptors in
    Python:
        http://users.rcn.com/python/download/Descriptor.htm

    (And the other items on http://www.python.org/doc/newstyle.html)


    Note about pickling: Parameters are usually used inside
    TopoObjects, and so are pickled even though Parameter has no
    explicit support for pickling (usually if a class has __slots__ it
    can't be pickled without additional support: see the Pickle module
    documentation).
    """

    # CEBHACKALERT: to get the benefit of slots, subcclasses must
    # themselves define __slots__, whether or not they define attributes
    # not present in the base Parameter class. 
    # See the reference manual:
    # The action of a __slots__ declaration is limited to the class
    # where it is defined. As a result, subclasses will have a
    # __dict__ unless they also define __slots__.

    __slots__ = ['_name','default','doc','hidden','precedence']
    count = 0

    def __init__(self,default=None,doc=None,hidden=False,precedence=None):
        """
        Initialize a new parameter.

        Set the name of the parameter to a gensym, and initialize
        the default value.

        _name stores the Parameter's name. This is
        created automatically by TopoObject, but can also be passed in
        (see TopoObject).

        default is the value of Parameter p that is returned if
        TopoObject_class.p is requested, or if TopoObject_object.p is
        requested but has not been set.

        hidden is a flag that allows objects using Parameters to know
        whether or not to display them to the user (e.g. in GUI menus).

        precedence is a value, usually in the range 0.0 to 1.0, that
        allows the order of Parameters in a class to be defined (again
        for e.g. in GUI menus).

        default, doc, and precedence default to None. This is to allow
        inheritance of Parameter slots (attributes) from the owning-class'
        class hierarchy (see TopoMetaclass).
        """
        self._name = None
        self.hidden=hidden
        self.precedence = precedence
        Parameter.count += 1
        self.default = default
        self.__doc__ = doc

    def __get__(self,obj,objtype):
        """
        Get a parameter value.  If called on the class, produce the
        default value.  If called on an instance, produce the instance's
        value, if one has been set, otherwise produce the default value.
        """
        # For documentation on __get__() see 'Implementing Descriptors'
        # in the Python reference manual
        # (http://www.python.org/doc/2.4.2/ref/descriptors.html)

        if not obj:
            result = self.default
        else:
            result = obj.__dict__.get(self.get_name(obj),self.default)
        return result


    def __set__(self,obj,val):
        """
        Set a parameter value.  If called on a class parameter,
        set the default value, if on an instance, set the value of the
        parameter in the object, where the value is stored in the
        instance's dictionary under the parameter's _name gensym.
        """    
        if not obj:
            self.default = val
        else:
            obj.__dict__[self.get_name(obj)] = val


    def __delete__(self,obj):
        """
        Delete a parameter.  Raises an exception.
        """
        raise "Deleting parameters is not allowed."


    def get_name(self,obj):
        """
        Return the name that the specified object has for this parameter.

        The parameter instance itself does not store its name, and cannot
        know what name the object that owns it might have for it.  However,
        it can discover this if the owning object is passed to this function,
        which looks for itself in the owning object and returns the name
        assigned to it.    
        """
        if not hasattr(self,'_name') or not self._name:
            class_ = obj.__class__
            for attrib_name in dir(class_):
                desc,desctype = class_.get_param_descriptor(attrib_name)
                if desc is self:
                    self._name = '_%s_param_value'%attrib_name
                    break
        return self._name

    # CEBHACKALERT: how does the doc slot work with __doc__ attribute,
    # really? See the corresponding HACKALERT in TopoMetaclass.
    
    # Make __doc__ work as it usually does for other objects, even
    # though there is no dictionary for this type of object.  The
    # actual value of __doc__ is stored in the doc slot, which
    # can be overridden by subclasses or instances.
    def _set_doc(self,doc):
        self.doc=doc
    def _get_doc(self):
        return self.doc
    __doc__ = property(_get_doc,_set_doc)

    
# CEBHACKALERT: at the moment, the path must be relative to Topographica's path.
from os.path import normpath
class Filename(Parameter):
    """
    Filename is a Parameter that takes a string specifying the
    path of a file and stores it in the format of the user's operating system.

    The path must be relative to Topographica's own path.

    To make your code work on all platforms, you should specify paths in UNIX format
    (e.g. examples/ellen_arthur.pgm). You can specify paths in your operating
    system's format, but only code that uses UNIX-style paths will run on all operating
    systems.
    """
    def __init__(self,default='',**params):
        Parameter.__init__(self,normpath(default),**params)

    def __set__(self,obj,val):
        """
        Call Parameter's __set__ with the os-specific path.
        """
        super(Filename,self).__set__(obj,normpath(val))

        
class Enumeration(Parameter):
    """
    Enumeration is a Parameter with a list of available values.

    An Enumeration's value is always one from its list of available values.
    """
    def __init__(self, default=None, available=[], **params):
        """
        Creates an Enumeration, checking that 'default' is in 'available'.
        """
        Parameter.__init__(self,default=default,**params)
        if not type(available)==list:
            raise ValueError("Enumeration must be created with a list of available values.")
        self.available = available
        self.__check_value(default) 
        
    def __set__(self,obj,val):
        """
        Set to the given value, raising an exception if that value is
        not in the list of available ones.
        """
        self.__check_value(val)
        super(Enumeration,self).__set__(obj,val)

    def __check_value(self,val):
        """
        Raises an error if the given value isn't in the list of available ones.
        """
        # CEBHACKALERT: it would be good to print the Parameter's name
        # here (see also Number and elsewhere in this file.
        if not self.available.count(val) >= 1:
            raise ValueError("EnumeratedParamater can't be set to '" + repr(val) + "' because that's not in the list of available values " + repr(self.available) + ".")



class Number(Parameter):
    """
    Number is a numeric parameter. Numbers have a default value, and
    bounds.  There are two types of bounds: `bounds' and
    `softbounds'.`bounds' are hard bounds: the parameter must have a
    value within the specified range.  The default bounds are
    (None,None), meaning there are actually no hard bounds.  One or both
    bounds can be set by specifying a value (e.g. bounds=(None,10) means
    there is no lower bound, and an upper bound of 10).

    Bounds are checked when a Number is created or set. Using a default
    value outside the hard bounds, or one that is not numeric, results
    in an exception. It is therefore not possible to create a parameter
    with a default value that is inconsistent with the bounds.

    A separate function set_in_bounds() is provided that will silently
    crop the given value into the legal range, for use in, for instance,
    a GUI.

    `softbounds' are present to indicate the typical range of the
    parameter, but are not enforced. Setting the soft bounds allows, for
    instance, a GUI to know what values to display on sliders for the
    Number.

    Example of creating a Number:
    AB = Number(default=0.5, bounds=(None,10), softbounds=(0,1), doc='Distance from A to B.')
    """
    def __init__(self,default=0.0,bounds=(None,None),softbounds=(None,None),**params):
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds
        self._softbounds = softbounds  
        self._check_bounds(default)  # only create this number if the default value and bounds are consistent

    def __set__(self,obj,val):
        """
        Set to the given value, raising an exception if out of bounds.
        """
        self._check_bounds(val)
        super(Number,self).__set__(obj,val)

    def set_in_bounds(self,obj,val):
        """
        Set to the given value, but cropped to be within the legal bounds.
        All objects are accepted, and no exceptions will be raised.  See
        crop_to_bounds for details on how cropping is done.
        """
        bounded_val = self.crop_to_bounds(val)
        super(Number,self).__set__(obj,bounded_val)

    def crop_to_bounds(self,val):
        """
        Return the given value cropped to be within the hard bounds
        for this parameter.

        If a numeric value is passed in, check it is within the hard
        bounds. If it is larger than the high bound, return the high
        bound. If it's smaller, return the low bound. In either case, the
        returned value could be None.  If a non-numeric value is passed
        in, set to be the default value (which could be None).  In no
        case is an exception raised; all values are accepted.
        """
        # Currently, values outside the bounds are silently cropped to
        # be inside the bounds; it may be appropriate to add a warning
        # in such cases.
        if (is_number(val)):
            min, max = self.bounds 
            if min != None: 
                if val < min:
                    return  min

            if max != None:
                if val > max:
                    return max

        else:
            # non-numeric value sent in: reverts to default value
            return  self.default

        return val



    def _check_bounds(self,val):
        """
        Checks that the value is numeric and that it is within the hard
        bounds; if not, an exception is raised.
        """

        # CEB: all the following error messages should probably print out the parameter's name
        # ('x', 'theta', or whatever)
        if not (is_number(val)):
            raise _NumberBoundsException("Parameter " + `self._name` + " (" + `self.__class__` + ") only takes a numeric value.")

        min,max = self.bounds
        if min != None and max != None:
            if not (min <= val <= max):
                raise _NumberBoundsException("Parameter must be between " + `min` + ' and ' + `max` + ' (inclusive).')
        elif min != None:
            if not min <= val: 
                raise _NumberBoundsException("Parameter must be at least " + `min` + '.')
        elif max != None:
            if not val <= max:
                raise _NumberBoundsException("Parameter must be at most " + `min` + '.')

    def get_soft_bounds(self):
        """
        For each soft bound (upper and lower), if there is a defined bound (not equal to None)
        then it is returned, otherwise it defaults to the hard bound. The hard bound could still be None.
        """
        hl,hu = self.bounds
        sl,su = self._softbounds

        if (sl==None): l = hl
        else:          l = sl

        if (su==None): u = hu
        else:          u = su

        return (l,u)


class Integer(Number):
    def __set__(self,obj,val):
        if not isinstance(val,int):
            raise "Parameter must be an integer."
        super(Integer,self).__set__(obj,val)


class Magnitude(Number):
    def __init__(self,default=1.0,softbounds=(None,None),**params):
        Number.__init__(self,default=default,bounds=(0.0,1.0),softbounds=softbounds,**params)


class BooleanParameter(Parameter):
    def __init__(self,default=False,bounds=(0,1),**params):
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds

    def __set__(self,obj,val):
        if not isinstance(val,bool):
            raise "BooleanParameter only takes a Boolean value."

        if val != True and val != False:
            raise "BooleanParameter must be True or False"

        super(BooleanParameter,self).__set__(obj,val)



### Should this multiply inherit from Dynamic and Number?
### (Currently mixed together by hand)
class DynamicNumber(Number):
    """
    Dynamic version of Number parameter.

    If set with a callable object, the bounds are checked when the number is
    retrieved (generated), rather than when it is set.
    """
    def __init__(self,default=0.0,bounds=(None,None),softbounds=(None,None),**params):
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds
        self._softbounds = softbounds  
        self._check_bounds(default)  # only create this number if the default value and bounds are consistent


    def __get__(self,obj,objtype):
        """
        Get a parameter value.  If called on the class, produce the
        default value.  If called on an instance, produce the instance's
        value, if one has been set, otherwise produce the default value.
        """
        if not obj:
            result = produce_value(self.default)
        else:
            result = produce_value(obj.__dict__.get(self.get_name(obj),self.default))
        self._check_bounds(result)
        return result

    def _check_bounds(self,val):
        """
        Except for callable values (assumed to be checked at get time), checks against bounds.

        Non-callable values are checked to be numeric and within the hard
        bounds.  If they are not, an exception is raised.
        """

        if not callable(val):
            super(DynamicNumber,self)._check_bounds(val)


class Dynamic(Parameter):
    def __get__(self,obj,objtype):
        """
        Get a parameter value.  If called on the class, produce the
        default value.  If called on an instance, produce the instance's
        value, if one has been set, otherwise produce the default value.
        """
        if not obj:
            result = produce_value(self.default)
        else:
            result = produce_value(obj.__dict__.get(self.get_name(obj),self.default))
        return result


class Constant(Parameter):
    """Constant Parameter that can be constructed and used but not set."""

    def __set__(self,obj,val):
        """Does not allow set commands."""
        raise "Constant parameter cannot be modified"


### JABALERT! Should this be replaced with simply ValueError?
class _NumberBoundsException(Exception):
    """
    This exception should be raised when there is an attempt
    to create a Number with a default outside its hard bounds.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def produce_value(value_obj):
    """
    A helper function that produces an actual parameter from a stored
    object.  If the object is callable, call it, else if it's an
    iterator, call its .next(), otherwise return the object.
    """
    if callable(value_obj):
        return value_obj()
    if is_iterator(value_obj):
        return value_obj.next()
    return value_obj


def is_iterator(obj):
    """
    Predicate that returns whether an object is an iterator.
    """
    import types
    return type(obj) == types.GeneratorType or ('__iter__' in dir(obj) and 'next' in dir(obj))


def is_number(obj):
    """
    Predicate that returns whether an object is a number.
    """
    # This may need to be extended to work with FixedPoint values.
    return (isinstance(obj,int) or isinstance(obj,float))





