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



class Filename(Parameter):
    """
    Filename is a Parameter that can be set to a string specifying the
    path of a file (in any OS format) and returns it in the format of
    the user's operating system.  Additionally, the specified path can
    be absolute or relative to:
    
    * any of the paths specified in the search_paths attribute;

    * any of the paths searched by resolve_filename() (see doc for that
      function).
    """
    __slots__ = ['search_paths'] 
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=None,search_paths=[],**params):
        self.search_paths = search_paths
        super(Filename,self).__init__(default,**params)

        
    def __set__(self,obj,val):
        """
        Call Parameter's __set__, but warn if the file cannot be found.
        """
        try:
            resolve_filename(val,self.search_paths)
        except IOError, e:
            ParameterizedObject(name="%s.%s"%(str(obj),self.attrib_name(obj))).warning('%s'%(e.args[0]))

        super(Filename,self).__set__(obj,val)
        
    def __get__(self,obj,objtype):
        """
        Return an absolute, normalized path (see resolve_filename).
        """
        raw_path = super(Filename,self).__get__(obj,objtype)
        return resolve_filename(raw_path,self.search_paths)




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



# CEBALERT: Now accepts FixedPoint, but not fully tested.
class Number(Parameter):
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
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds
        self._softbounds = softbounds  
        self._check_bounds(default)  # only create this number if the default value and bounds are consistent


    ### JCALERT! The __get__ method is momentarily re-implemented in Number so that to deal
    ### with the DynamicNumber. It will probably be deleted again when DynamicNumber will be
    ### removed from the Parameter class hierarchy.
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

            # CEBHACKALERT: allows a DynamicNumber to have been set as the
            # value of a Number parameter of a ParameterizedObject. If we will
            # continue to do this, we probably want one DynamicValue parameter
            # and not DynamicNumber etc.
            # This code shouldn't have any effect on existing uses of
            # DynamicNumber - they all overwrite the original Number
            # parameter anyway.
            # (See also Number.__set__().)
            if type(result)==DynamicNumber:
                result=result.__get__(obj,objtype)
        return result


    def __set__(self,obj,val):
        """
        Set to the given value, raising an exception if out of bounds.
        """
        # CEBHACKALERT: see Parameter.__get__().
        # A DynamicNumber does not currently respect the bounds
        # of the Number. (Before it couldn't have bounds at all.)
        if type(val)!=DynamicNumber:
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

    def __set__(self,obj,val):
        ###JABALERT: Should make sure the DynamicNumber is an integer
        if not isinstance(val,int) and not isinstance(val,DynamicNumber):
            raise ValueError("Parameter must be an integer.")
        super(Integer,self).__set__(obj,val)


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

        if val != True and val != False:
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
        

# This could multiply inherit from Dynamic and Number, but it's
# currently mixed together by hand for simplicity.
class DynamicNumber(Number):
    __slots__ = ['last_value']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=0.0,bounds=None,softbounds=None,**params):
        """
        Create Dynamic version of a Number parameter.

        If set with a callable or iterable object, the bounds are checked when the
        number is retrieved (generated), rather than when it is set.
        """
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds
        self._softbounds = softbounds  
        self._check_bounds(default)  # only create this number if the default value and bounds are consistent

        # Provides a way to display a value without changing it
        self.last_value = None

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

        self.last_value = result
        return result

    def _check_bounds(self,val):
        """
        Except for callable values (assumed to be checked at get time), checks against bounds.

        Non-callable, non-iterable values are checked to be numeric and within the hard
        bounds.  If they are not, an exception is raised.
        """

        if not (callable(val) or is_iterator(val)):
            super(DynamicNumber,self)._check_bounds(val)


class Dynamic(Parameter):
    """
    Parameter whose value is generated dynamically by a callable object.
    
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
    __slots__ = []
    __doc__ = property((lambda self: self.doc))
    
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


import operator
is_number = operator.isNumberType


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
                 if not (hasattr(c,'abstract') and c.abstract==True)])


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
    _abstract_class_name = "SelectorParameter"
    
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
        if type(val)!=DynamicNumber:
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
            min,max = self.bounds
            l=len(val)
            if min != None and max != None:
                if not (min <= l <= max):
                    raise ValueError("List length must be between " + `min` + ' and ' + `max` + ' (inclusive).')
            elif min != None:
                if not min <= l: 
                    raise ValueError("List length must be at least " + `min` + '.')
            elif max != None:
                if not l <= max:
                    raise ValueError("List length must be at most " + `max` + '.')

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





# Is there a more obvious way of getting this path?
# (Needs to work on unix and windows.)
# the application base directory
application_path = os.path.split(os.path.split(sys.executable)[0])[0]

def resolve_filename(path,search_paths=[]):
    """
    Create an absolute path to the file if the path is not
    already absolute.

    To turn a supplied relative path into an absolute one, the path is
    appended to each path in (search_paths+the current working
    directory+the application's base path) until the file is found.
    
    An IOError is raised if the file is not found anywhere.
    """
    path = os.path.normpath(path)

    if os.path.isabs(path): return path

    all_search_paths = search_paths + [os.getcwd()] + [application_path]

    paths_tried = []
    for prefix in set(all_search_paths): # does set() keep order?            
        try_path = os.path.join(os.path.normpath(prefix),path)
        if os.path.isfile(try_path): return try_path
        paths_tried.append(try_path)

    raise IOError('File "'+os.path.split(path)[1]+'" was not found in the following place(s): '+str(paths_tried)+'.')


