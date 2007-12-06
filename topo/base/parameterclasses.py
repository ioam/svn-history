"""
Subclasses of Parameter, implementing specific parameter types.

$Id$
"""
__version__='$Revision$'

import copy
import re
import os.path
import sys
import types

from parameterizedobject import Parameter, descendents, ParameterizedObject

# CEBALERT: much of the documentation for Parameter subclasses
# that ought to be in the class docstring is in the __init__
# docstring so that it shows up. In some cases there is
# some repetition.
# See JAB hackalert by Parameter's __doc__.



# CEBHACKALERT: needs to be finished
class Enumeration(Parameter):
    """
    Enumeration is a Parameter with a list of available values.

    An Enumeration's value is always one from its list of available values.
    """
    __slots__ = ['available']
    __doc__ = property((lambda self: self.doc))

    def __init__(self, default=None, available=[], **params):
        """
        Create an Enumeration, checking that 'default' is in 'available'.
        """
        Parameter.__init__(self,default=default,**params)
        # CB: just needs to be list-like. has __iter__ method?
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
        # CEBALERT: it would be good to print the Parameter's name
        # here (see also Number and elsewhere in this file).
        if not self.available.count(val) >= 1:
            raise ValueError("EnumeratedParamater can't be set to '" + repr(val) + "' because that's not in the list of available values " + repr(self.available) + ".")








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


def is_dynamic(value):
    return callable(value) or is_iterator(value)



import operator
is_number = operator.isNumberType



# CB: make sure e.g. 'UniformRandom...' shows up in help(PO)

# CB: "last" should be "current"
# CB: doc out of date! (I'm updating it.)
class Dynamic(Parameter):
    """
    Parameter whose value can be generated dynamically by a callable object.
    
    If a Parameter is declared as Dynamic, it can be set to be a
    callable object (such as a function), and getting the parameter's
    value will call that callable.  E.g., to cause all objects of type
    Foo to draw the value of Parameter gammas from a Gaussian
    distribution, you'd write something like:

      from random import gauss
      Foo.sigma = Dynamic(lambda:gauss(0.5,0.1))

    If a Dynamic Parameter's value is set to a Python generator or iterator,
    then when the Parameter is accessed, the iterator's .next() method
    is called.  So to get a parameter that cycles through a sequence,
    you could write:
        
      from itertools import cycle
      Foo.sigma = Dynamic(cycle([0.1,0.5,0.9]))

    Note that at present, the callable object must be an instance of a
    callable class, rather than a named function or a lambda function,
    or else this object will not be picklable.
    """
    time_fn = None
    
    __slots__ = ['last_default','last_time']
    __doc__ = property((lambda self: self.doc))

        
    def __init__(self,**params):
        super(Dynamic,self).__init__(**params)

        self.last_time = None 
        if is_dynamic(self.default):
            self.last_default = None
            self.instantiate = True
        else:
            self.last_default = self.default


    def _needs_update(self,obj):

        if self.time_fn is None: return True
        time =  self.time_fn()
        
        if not obj:
            needs = time>(self.last_time or -1)
        else:
            name = self.internal_name(obj)
            try:
                needs = time>obj.__dict__[name+'_time']
            except KeyError:
                needs = time>(self.last_time or -1)

        return needs
                
        


    def __get__(self,obj,objtype):

        # CB: to store last default value etc on the class, put it in
        # objtype.__dict__ instead of setting on the parameter object.
        # But then need to explain why 'default' and all the rest are
        # stored on the parameter object rather than the owning class.

        if self._needs_update(obj):
            value = self._produce_value(obj)
        else:
            value =  self._last_value(obj)

        return value


    def __set__(self,obj,val):
        # 'instantiate' is kept up to date for the default value.
        super(Dynamic,self).__set__(obj,val)

        if not is_dynamic(val):
            if not obj:
                self.last_default = self.default
                self.instantiate = False
            else:
                obj.__dict__[self.internal_name(obj)+'_last']=val
        else:
            if not obj:
                self.instantiate = True


    def _last_value(self,obj):
        if not obj:
            value = self.last_default
        else:
            try:
                value = obj.__dict__[self.internal_name(obj)+'_last']
            except KeyError:
                value = self.last_default

        return value
    

    def _produce_value(self,obj):
        if self.time_fn:
            time = self.time_fn()
        else:
            time = -1

        if not obj:
            value = produce_value(self.default)
            self.last_default = value
            self.last_time = time
        else:
            try:
                name = self.internal_name(obj)
                value = produce_value(obj.__dict__[name])
                obj.__dict__[name+'_last']=value
                obj.__dict__[name+'_time']=time
            except KeyError:
                value = produce_value(self.default)
                self.last_default = value
                self.last_time = time

        return value


##     def _value_is_dynamic(self,obj):
##         if not obj:
##             dynamic = is_dynamic(self.default)
##         else:
##             try:
##                 dynamic = is_dynamic(obj.__dict__[self.internal_name(obj)])
##             except KeyError:
##                 dynamic = is_dynamic(self.default)

##         return dynamic
        


# CEBALERT: Now accepts FixedPoint, but not fully tested.
# CB: doc out of date
class Number(Dynamic):
    """
    """
    __slots__ = ['bounds','_softbounds']
    __doc__ = property((lambda self: self.doc))
 
    def __init__(self,default=0.0,bounds=None,softbounds=None,**params):
        """
        Number is a numeric parameter. Numbers have a default value,
        and bounds.  There are two types of bounds: ``bounds`` and
        ``softbounds``.  ``bounds`` are hard bounds: the parameter must have
        a value within the specified range.  The default bounds are
        (None,None), meaning there are actually no hard bounds.  One
        or both bounds can be set by specifying a value
        (e.g. bounds=(None,10) means there is no lower bound, and an
        upper bound of 10).

        Bounds are checked when a Number is created or set. Using a
        default value outside the hard bounds, or one that is not
        numeric, results in an exception. It is therefore not possible
        to create a parameter with a default value that is
        inconsistent with the bounds.

        A separate function set_in_bounds() is provided that will
        silently crop the given value into the legal range, for use
        in, for instance, a GUI.

        ``softbounds`` are present to indicate the typical range of the
        parameter, but are not enforced. Setting the soft bounds
        allows, for instance, a GUI to know what values to display on
        sliders for the Number.

        Example of creating a Number::
        
          AB = Number(default=0.5, bounds=(None,10), softbounds=(0,1), doc='Distance from A to B.')
        """
        super(Number,self).__init__(default=default,**params)
        
        self.bounds = bounds
        self._softbounds = softbounds  
        if not is_dynamic(default): self._check_bounds(default)  
        

    def __get__(self,obj,objtype):
        """
        Get a parameter value.  If called on the class, produce the
        default value.  If called on an instance, produce the instance's
        value, if one has been set, otherwise produce the default value.
        """
        result = super(Number,self).__get__(obj,objtype)
        if is_dynamic(result): self._check_bounds(result)
        return result


    def __set__(self,obj,val):
        """
        Set to the given value, raising an exception if out of bounds.
        """
        if not is_dynamic(val): self._check_bounds(val)
        super(Number,self).__set__(obj,val)
        

    def set_in_bounds(self,obj,val):
        """
        Set to the given value, but cropped to be within the legal bounds.
        All objects are accepted, and no exceptions will be raised.  See
        crop_to_bounds for details on how cropping is done.
        """
        if not is_dynamic(val):
            bounded_val = self.crop_to_bounds(val)
        else:
            bounded_val = val
            
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
            if self.bounds==None:
                return val
            vmin, vmax = self.bounds 
            if vmin != None: 
                if val < vmin:
                    return  vmin

            if vmax != None:
                if val > vmax:
                    return vmax

        else:
            # non-numeric value sent in: reverts to default value
            return  self.default

        return val


    # CB: rename to _check_value or something because it also checks the type
    # and gets hijacked to do that more in subclasses (e.g. Integer)
    def _check_bounds(self,val):
        """
        Checks that the value is numeric and that it is within the hard
        bounds; if not, an exception is raised.
        """
        # CEB: all the following error messages should probably print out the parameter's name
        # ('x', 'theta', or whatever)
        if not (is_number(val)):
            raise ValueError("Parameter " + `self.attrib_name()` + " (" + `self.__class__.__name__` +
                             ") only takes a numeric value; " + `type(val)` + " is not numeric.")

        if self.bounds!=None:
            vmin,vmax = self.bounds
            if vmin != None and vmax != None:
                if not (vmin <= val <= vmax):
                    raise ValueError("Parameter must be between " + `vmin` + ' and ' + `vmax` + ' (inclusive).')
            elif vmin != None:
                if not vmin <= val: 
                    raise ValueError("Parameter must be at least " + `vmin` + '.')
            elif vmax != None:
                if not val <=vmax:
                    raise ValueError("Parameter must be at most " + `vmax` + '.')

    def get_soft_bounds(self):
        """
        For each soft bound (upper and lower), if there is a defined bound (not equal to None)
        then it is returned, otherwise it defaults to the hard bound. The hard bound could still be None.
        """
        if self.bounds==None:
            hl,hu=(None,None)
        else:
            hl,hu=self.bounds

        if self._softbounds==None:
            sl,su=(None,None)
        else:
            sl,su=self._softbounds

                
        if (sl==None): l = hl
        else:          l = sl

        if (su==None): u = hu
        else:          u = su

        return (l,u)


class Integer(Number):
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def _check_bounds(self,val):
        if not isinstance(val,int):
            raise ValueError("Parameter must be an integer.")
        super(Integer,self)._check_bounds(val)


class Magnitude(Number):
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=1.0,softbounds=None,**params):
        Number.__init__(self,default=default,bounds=(0.0,1.0),softbounds=softbounds,**params)


class BooleanParameter(Parameter):
    __slots__ = ['bounds']
    __doc__ = property((lambda self: self.doc))


    # CB: what does bounds=(0,1) mean/do for this Parameter?
    def __init__(self,default=False,bounds=(0,1),**params):
        """Initialize a Boolean parameter, allowing values True or False."""
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds

    def __set__(self,obj,val):
        if not isinstance(val,bool):
            raise ValueError("BooleanParameter only takes a Boolean value.")

        if val is not True and val is not False:
            raise ValueError("BooleanParameter must be True or False.")

        super(BooleanParameter,self).__set__(obj,val)


class StringParameter(Parameter):
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default="",**params):
        """Initialize a string parameter."""
        Parameter.__init__(self,default=default,**params)
        
    def __set__(self,obj,val):
        if not isinstance(val,str):
            raise ValueError("StringParameter only takes a string value.")

        super(StringParameter,self).__set__(obj,val)


class NumericTuple(Parameter):
    __slots__ = ['length']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=(0,0),length=None,**params):
        """
        Initialize a numeric tuple parameter with a fixed length.
        The length is determined by the initial default value, and
        is not allowed to change after instantiation.
        """
        if length is None:
            self.length = len(default)
        else:
            self.length = length
            
        self._check(default)
        Parameter.__init__(self,default=default,**params)
        
    def _check(self,val):
        if not isinstance(val,tuple):
            raise ValueError("NumericTuple only takes a tuple value.")
        
        if not len(val)==self.length:
            raise ValueError("Tuple is not of the correct length (%d instead of %d)." %
                             (len(val),self.length))
        for n in val:
            if not is_number(n):
                raise ValueError("Tuple element is not numeric: %s." % (str(n)))
            
    def __set__(self,obj,val):
        self._check(val)
        super(NumericTuple,self).__set__(obj,val)


class XYCoordinates(NumericTuple):
    __slots__ = []
    __doc__ = property((lambda self: self.doc))
  
    def __init__(self,default=(0.0,0.0),**params):
        super(XYCoordinates,self).__init__(default=default,length=2,**params)

                 
class CallableParameter(Parameter):
    """
    Parameter holding a value that is a callable object, such as a function.
    
    A keyword argument instantiate=True should be provided when a
    function object is used that might have state.  On the other hand,
    regular standalone functions cannot be deepcopied as of Python
    2.4, so instantiate must be False for those values.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=None,**params):
        Parameter.__init__(self,default=wrap_callable(default),**params)

    def __set__(self,obj,val):
        if not callable(val):
            raise ValueError("CallableParameter only takes a callable object.")
        super(CallableParameter,self).__set__(obj,wrap_callable(val))


def wrap_callable(c):
    """
    Wrap a callable object in an InstanceMethodWrapper, if necessary.

    If c is an instancemethod, then wrap it and return the wrapper,
    otherwise return c.
    """
    if isinstance(c,types.MethodType):
        return InstanceMethodWrapper(c)
    else:
        return c
        

# CEBALERT: this should be a method of ClassSelectorParameter.
def concrete_descendents(parentclass):
    """
    Return a dictionary containing all subclasses of the specified
    parentclass, including the parentclass.  Only classes that are
    defined in scripts that have been run or modules that have been
    imported are included, so the caller will usually first do ``from
    package import *``.

    If the class has an attribute ``abstract``, and it is True, the
    class will not be included.
    """
    return dict([(c.__name__,c) for c in descendents(parentclass)
                 if not c.abstract])


class CompositeParameter(Parameter):
    """
    A parameter that is in fact a composite of a set of other
    parameters or attributes of the class.  The constructor argumentt
    'attribs' takes a list of attribute names.  Getting the parameter
    returns a list of the values of the constituents of the composite,
    in the order specified.  Likewise, setting the parameter takes a
    sequence of values and sets the value of the constituent
    attributes sets all the constituents
    """

    __slots__=['attribs','objtype']

    def __init__(self,attribs=[],**kw):
        super(CompositeParameter,self).__init__(default=None,**kw)
        self.attribs = attribs

    def __get__(self,obj,objtype):
        """
        Return the values of all the attribs, as a list.
        """
        if not obj:
            return [getattr(objtype,a) for a in self.attribs]
        else:
            return [getattr(obj,a) for a in self.attribs]

    def __set__(self,obj,val):
        """
        Set the values of all the attribs.
        """
        assert len(val) == len(self.attribs),"Compound parameter %s got the wrong number of values (needed %d, but got %d)." % (self.attrib_name(obj=obj),len(self.attribs),len(val))
        
        if not obj:
            for a,v in zip(self.attribs,val):
                setattr(self.objtype,a,v)
        else:
            for a,v in zip(self.attribs,val):
                setattr(obj,a,v)


class SelectorParameter(Parameter):
    """
    Parameter whose value is set to some form of one of the
    possibilities in its range.

    Subclasses must implement get_range().
    """
    __abstract = True
    
    __slots__=[]
    __doc__ = property((lambda self: self.doc))

    def get_range(self):
        raise NotImplementedError("get_range() must be implemented in subclasses.")

    
class ObjectSelectorParameter(SelectorParameter):
    """
    Parameter whose value is set to an object from its list of possible objects.
    """
    __slots__ = ['objects'] 
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=None,objects=[],instantiate=True,**params):
        self.objects = objects
        self._check_value(default)
        Parameter.__init__(self,default=default,instantiate=instantiate,**params)
        
    # CBNOTE: if the list of objects is changed, the current value for
    # this parameter in existing POs could be out of the new range.
    
    def _check_value(self,val,obj=None):
        """
        val must be None or one of the objects in self.objects.
        """
        if val is not None and val not in self.objects:
            raise ValueError("%s not in Parameter %s's list of possible objects" \
                             %(val,self.attrib_name(obj=obj)))

# CBNOTE: I think it's not helpful to do a type check for the value of
# an ObjectSelectorParameter. If we did such type checking, any user
# of this Parameter would have to be sure to update the list of possible
# objects before setting the Parameter's value. As it is, only users who care about the
# correct list of objects being displayed need to update the list.
##     def __set__(self,obj,val):
##         self._check_value(val,obj)
##         super(ObjectSelectorParameter,self).__set__(obj,val)


    def get_range(self):
        """
        Return the possible objects to which this parameter could be set.

        (Returns the dictionary {object.name:object}.)
        """
        return dict([(obj.name,obj) for obj in self.objects])

    
class ClassSelectorParameter(SelectorParameter):
    """
    Parameter whose value is an instance of the specified class.    
    """
    __slots__ = ['class_','suffix_to_lose']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,class_,default=None,instantiate=True,
                 suffix_to_lose='',**params):
        self.class_ = class_

        # CBENHANCEMENT: currently offers the possibility to cut off
        # the end of a class name (suffix_to_lose), but this could be
        # extended to any processing of the class name.
        self.suffix_to_lose = suffix_to_lose

        self._check_value(default)
        Parameter.__init__(self,default=default,instantiate=instantiate,**params)


    def _check_value(self,val,obj=None):
        """
        val must be None or an instance of self.class_
        """
        if not (isinstance(val,self.class_) or val is None):
            raise ValueError("Parameter " + `self.attrib_name(obj=obj)` + " (" + \
                             `self.__class__.__name__` + ") must be an instance of " + \
                             self.class_.__name__ + "; " + `val` + \
                             " is " + `type(val)` + ".")
        

    def __set__(self,obj,val):
        self._check_value(val,obj)
        super(ClassSelectorParameter,self).__set__(obj,val)

        
    def get_range(self):
        """
        Return the possible types for this parameter's value.

        (I.e. return {visible_name: <class>} for all classes that are
        concrete_descendents() of self.class_.)

        Only classes from modules that have been imported are added
        (see concrete_descendents()).
        """
        classes = concrete_descendents(self.class_)
        return dict([(self.__classname_repr(name),class_) for name,class_ in classes.items()])


    def __classname_repr(self, class_name):
        """
        Return class_name stripped of self.suffix_to_lose.
        """
        return re.sub(self.suffix_to_lose+'$','',class_name)




class ListParameter(Parameter):
    """
    Parameter whose value is a list of objects, usually of a specified type.

    The bounds allow a minimum and/or maximum length of
    list to be enforced.  If the class is non-None, all
    items in the list are checked to be of that type.
    """
    __slots__ = ['class_','bounds']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=[],class_=None,instantiate=True,
                 bounds=(0,None),**params):
        self.class_ = class_
        self.bounds = bounds
        self._check_bounds(default)
        Parameter.__init__(self,default=default,instantiate=instantiate,
                           **params)

    # Could add range() method from ClassSelectorParameter, to allow
    # list to be populated in the GUI

    def __set__(self,obj,val):
        """Set to the given value, raising an exception if out of bounds."""

        # CB: think this is ok
        if not (hasattr(val,'_dynamic') and val._dynamic):
        #if type(val)!=DynamicNumber:
            self._check_bounds(val)
        super(ListParameter,self).__set__(obj,val)

    def _check_bounds(self,val):
        """
        Checks that the list is of the right length and has the right contents.
        Otherwise, an exception is raised.
        """

        # CEB: all the following error messages should probably print out the parameter's name
        # ('x', 'theta', or whatever)
        if not (isinstance(val,list)):
            raise ValueError("Parameter " + `self.attrib_name()` + " (" + `self.__class__.__name__` + ") must be a list.")

        if self.bounds!=None:
            min_length,max_length = self.bounds
            l=len(val)
            if min_length != None and max_length != None:
                if not (min_length <= l <= max_length):
                    raise ValueError("List length must be between " + `min_length` + ' and ' + `max_length` + ' (inclusive).')
            elif min_length != None:
                if not min_length <= l: 
                    raise ValueError("List length must be at least " + `min_length` + '.')
            elif max_length != None:
                if not l <= max_length:
                    raise ValueError("List length must be at most " + `max_length` + '.')

        if self.class_!=None:
            for v in val:
                assert isinstance(v,self.class_),repr(v)+" is not an instance of " + repr(self.class_) + "."


class DictParameter(ClassSelectorParameter):
    """
    Parameter whose value is a dictionary.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,**params):
        super(DictParameter,self).__init__(dict,**params)

class InstanceMethodWrapper(object):
    """
    Wrapper for pickling instance methods.

    Constructor takes an instance method (e.g. topo.sim.time) as
    its only argument.  Wrapper instance is callable, picklable, etc.
    """
    # CEBALERT: Both repr and name disguise that this is an
    # InstanceMethodWrapper (note that we probably won't need this
    # class in python 2.5).

    def __repr__(self):
        return repr(self.im.im_func)

    # Hope __name__ doesn't get set...
    def _fname(self):
        return self.im.im_func.func_name
    __name__ = property(_fname)
    
    def __init__(self,im):
        self.im = im

    def __getstate__(self):
        return (self.im.im_self,
                self.im.im_func.func_name)

    def __setstate__(self,state):
        obj,func_name = state
        self.im = getattr(obj,func_name)

    def __call__(self,*args,**kw):
        return self.im(*args,**kw)





## CEB: this whole chunk awaiting removal.
class DynamicNumber(object):
    """
    Provide support for exising code that uses DynamicNumber: see __new__().
    """
    warnedA = True#False  # suppress warnings for the moment.
    warnedB = True#False
    
    def __new__(cls,default=None,**params):
        """
        If bounds or softbounds or any params are supplied, assume we're dealing
        with DynamicNumber declared as a parameter of a ParameterizedObject class.
        In this case, return a new *Number* parameter instead.

        Otherwise, assume we're dealing with DynamicNumber supplied as the value
        of a Number Parameter. In this case, return a DynamicNumber (but one which is
        not a Parameter, just a simple wrapper).

        * Of course, this is not 100% reliable: if someone defines a class with
        * a DynamicNumber but doesn't pass any doc or bounds or whatever. But in such
        * cases, they'll get the ParameterizedObject warning about being unable to
        * set a class attribute.

        Most of the code is to generate warning messages.
        """
        if len(params)>0:
            ####################
            m = "\n------------------------------------------------------------\nPlease update your code - instead of using the 'DynamicNumber' Parameter in the code for your class, please use the 'Number' Parameter; the Number Parameter now supports dynamic values automatically.\n\nE.g. change\n\nclass X(ParameterizedObject):\n    y=DynamicNumber(NumberGenerator())\n\nto\n\n\nclass X(ParameterizedObject):\n    y=Number(NumberGenerator())\n------------------------------------------------------------\n"
            if not cls.warnedA:
                ParameterizedObject().warning(m)
                cls.warnedA=True
            ####################

            n = Number(default,**params)
            return n
        else:
            ####################
            m = "\n------------------------------------------------------------\nPlease update your code - instead of using DynamicNumber to contain a number generator, pass the number generator straight to the Number parameter:\n\nE.g. in code using the class below...\n\nclass X(ParameterizedObject):\n    y=Number(0.0)\n\n\nchange\n\nx = X(y=DynamicNumber(NumberGenerator()))\n\nto\n\nx = X(y=NumberGenerator())\n------------------------------------------------------------\n"
            if not cls.warnedB:
                ParameterizedObject().warning(m)
                cls.warnedB=True
            ####################
            return object.__new__(cls,default)

    
    def __init__(self,default=0.0,bounds=None,softbounds=None,**params):        
        self.val = default
    def __call__(self):
        return self.val()
