"""
Subclasses of Parameter, implementing specific parameter types.

$Id$
"""
__version__='$Revision$'

import copy
import re
import os.path
import sys

from parameterizedobject import Parameter, descendents


# CEBHACKALERT: much of the documentation for Parameter subclasses
# that ought to be in the class docstring is in the __init__
# docstring so that it shows up. In some cases there is
# some repetition.
# See JABHACKALERT by Parameter's __doc__.

class Filename(Parameter):
    """
    Filename is a Parameter that takes a string specifying the
    path of a file and stores it in the format of the user's operating system.

    The path to the file can be absolute or relative to any paths
    specified in search_paths.

    To make your code work on all platforms, you should specify paths
    in UNIX format (e.g. examples/ellen_arthur.pgm). You can specify
    paths in your operating system's format, but only code that uses
    UNIX-style paths will run on all operating systems.
    """
    __slots__ = ['search_paths']
    __doc__ = property((lambda self: self.doc))

    # CEBHACKALERT: there's a better way, right? See the sys module documentation,
    # and consider unix and windows.
    def __init__(self,default=None,search_paths=[os.path.split(os.path.split(sys.executable)[0])[0]],**params):
        """
        Create a Filename Parameter with the specified string.
        
        The string is stored in the path format of the user's
        operating system.

        See __construct_path() for details on path resolution
        order.
        """
        self.search_paths = copy.copy(search_paths)
        
        if default==None:
            path = None
        else:
            path = self.__construct_path(default)

        Parameter.__init__(self,path,**params)


    def __set__(self,obj,val):
        """
        Call Parameter's __set__, but constructing the path first
        (see __construct_path()).
        """
        super(Filename,self).__set__(obj,self.__construct_path(val))


    def __construct_path(self,path):
        """
        Create an absolute path to the file if the path is not
        already absolute.

        A relative path is appended to the prefix paths held in
        search_paths; at each point the presence of the file is tested
        for and if there, its path is returned.

        An IOError is raised if the file is not found in any of these places.
        """
        path = os.path.normpath(path)
        
        if os.path.isabs(path): return path

        paths_tried = []
        for prefix in self.search_paths:            
            try_path = os.path.join(os.path.normpath(prefix),path)
            if os.path.isfile(try_path): return try_path
            paths_tried.append(try_path)

        raise IOError('File "'+os.path.split(path)[1]+'" was not found in the following places: '+str(paths_tried)+'.')


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
        # here (see also Number and elsewhere in this file).
        if not self.available.count(val) >= 1:
            raise ValueError("EnumeratedParamater can't be set to '" + repr(val) + "' because that's not in the list of available values " + repr(self.available) + ".")





### JABALERT: Needs to be extended to accept FixedPoint as a number.
class Number(Parameter):
    """
    """
    __slots__ = ['bounds','_softbounds']
    __doc__ = property((lambda self: self.doc))
 
    def __init__(self,default=0.0,bounds=None,softbounds=None,**params):
        """
        Number is a numeric parameter. Numbers have a default value,
        and bounds.  There are two types of bounds: `bounds' and
        `softbounds'.`bounds' are hard bounds: the parameter must have
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

        `softbounds' are present to indicate the typical range of the
        parameter, but are not enforced. Setting the soft bounds
        allows, for instance, a GUI to know what values to display on
        sliders for the Number.

        Example of creating a Number:
        AB = Number(default=0.5, bounds=(None,10),
                    softbounds=(0,1), doc='Distance from A to B.')
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
            raise ValueError("Parameter " + `self._name` + " (" + `self.__class__` + ") only takes a numeric value; " + `type(val)` + " is not numeric.")

        if self.bounds!=None:
            min,max = self.bounds
            if min != None and max != None:
                if not (min <= val <= max):
                    raise ValueError("Parameter must be between " + `min` + ' and ' + `max` + ' (inclusive).')
            elif min != None:
                if not min <= val: 
                    raise ValueError("Parameter must be at least " + `min` + '.')
            elif max != None:
                if not val <= max:
                    raise ValueError("Parameter must be at most " + `max` + '.')

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
        if not isinstance(val,int):
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

    def __init__(self,default=False,bounds=(0,1),**params):
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds

    def __set__(self,obj,val):
        if not isinstance(val,bool):
            raise ValueError("BooleanParameter only takes a Boolean value.")

        if val != True and val != False:
            raise ValueError("BooleanParameter must be True or False.")

        super(BooleanParameter,self).__set__(obj,val)


class CallableParameter(Parameter):
    """Parameter holding a value that is a callable object, such as a function."""
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=None,**params):
        Parameter.__init__(self,default=default,instantiate=True,**params)

    def __set__(self,obj,val):
        if not callable(val):
            raise ValueError("CallableParameter only takes a callable object.")
        super(CallableParameter,self).__set__(obj,val)



# This could multiply inherit from Dynamic and Number, but it's
# currently mixed together by hand for simplicity.
class DynamicNumber(Number):
    """
    """
    __slots__ = ['last_value']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=0.0,bounds=None,softbounds=None,**params):
        """
        Create Dynamic version of Number parameter.

        If set with a callable object, the bounds are checked when the
        number is retrieved (generated), rather than when it is set.
        """
        Parameter.__init__(self,default=default,**params)
        self.bounds = bounds
        self._softbounds = softbounds  
        self._check_bounds(default)  # only create this number if the default value and bounds are consistent

        # CEBHACKALERT: allows to avoid the problem of displaying the value without
        # changing its value.
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

        Non-callable values are checked to be numeric and within the hard
        bounds.  If they are not, an exception is raised.
        """

        if not callable(val):
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


def is_number(obj):
    """
    Predicate that returns whether an object is a number.
    """
    # This may need to be extended to work with FixedPoint values.
    return (isinstance(obj,int) or isinstance(obj,float))




# CEBALERT: this should be a method of ClassSelectorParameter.
def concrete_descendents(parentclass):
    """
    Return a dictionary containing all subclasses of the specified
    parentclass, including the parentclass.  Only classes that are
    defined in scripts that have been run or modules that have been
    imported are included, so the caller will usually first do 'from
    package import *'.

    If the class has an attribute 'abstract', and it's True, the class
    will not be included.
    """
    return dict([(c.__name__,c) for c in descendents(parentclass)
                 if not (hasattr(c,'abstract') and c.abstract==True)])


class ClassSelectorParameter(Parameter):
    """
    Parameter whose value is an instance of the specified class.

    Offers a range() method to return possible types that the
    value could be an instance of.
    """
    __slots__ = ['class_','suffix_to_lose']
    __doc__ = property((lambda self: self.doc))

    def __init__(self,class_,default=None,instantiate=True,
                 suffix_to_lose='',**params):
        
        self.class_ = class_

        # CEBALERT: Currently offers the possibility to cut off the
        # end of a class name (suffix_to_lose), but this could be
        # extended to any processing of the class name.
        self.suffix_to_lose = suffix_to_lose

        # CEBHACKALERT: check default's in range!
        Parameter.__init__(self,default=default,instantiate=instantiate,
                           **params)

        
    def range(self):
        """
        Return {visible_name: <class>} for all classes in self.packages.
        If self.packages is empty, return the default.

        Only classes from already-imported modules are added.        
        """
        # CEBHACKALERT: e.g. PatternGenerators come out in GUI in the arbitrary
        # order of the keys of this dict. They used to come out at least in the
        # same order every time because it was a keyedlist. Don't forget to fix
        # that.
        k = {}
        classes = concrete_descendents(self.class_)
        for (name,class_) in classes.items():
            k[self.__classname_repr(name)] = class_

        if len(k)==0:
            return {self.__classname_repr(self.default.__class__.__name__):self.default}
        else:
            return k

    def __classname_repr(self, class_name):
        """
        Return class_name stripped of self.suffix_to_lose.
        """
        return re.sub(self.suffix_to_lose+'$','',class_name)



class ListParameter(Parameter):
    """
    Parameter whose value is a list of objects, usually of a specified type.

    The bounds allows a minimum and/or maximum length of
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
            raise ValueError("Parameter " + `self._name` + " (" + `self.__class__` + ") must be a list.")

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



# For the moment, this takes the string name in the form
# module.function
# and does 'import module' itself.
# Ideally this would instead take the function itself,
# and work out the right string to re-generate it.
# random.uniform, for example, has __name__ and __module__:
# it would be easy for that. But Numeric.add has no useful
# attributes and would need to be taken from repr(Numeric.add),
# in a way that would work for random etc. too.
# I haven't tried that yet...
class Wrapper(object):
    """
    Why Wrapper has to exist...
    """
    __slots__ = ['function_','function_as_text','module_name','args','kw']

    def __repr__(self):
        # CEBHACKALERT: not quite right, need to format args and kw
        return "Wrapper('"+self.function_as_text+"', "+`self.args`+", "+`self.kw`+")"

    def __str__(self):
        return "Wrapper('"+self.function_as_text+"')"

    def __getattribute__(self,attribute):
        """
        If the Wrapper object has the attribute, return it; if the
        function_ object has the attribute, return it; otherwise,
        raise an AttributeError.
        """
        try:
            x= object.__getattribute__(self,attribute)
        except AttributeError:
            function_ = object.__getattribute__(self,'function_')
            if hasattr(function_,attribute):
                x = getattr(function_,attribute)
            else:
                raise AttributeError("Neither "+`self`+" nor "+`self.function_`+" has the attribute '"+ attribute+"'.")
        return x        
        
    
    def __init__(self,function_as_text,*args,**kw):
        """
        Create the function from the text.
        function_as_text must be in the form 'module.function'.
        """
        self.function_as_text = function_as_text

        breakdown = function_as_text.split('.')
        assert len(breakdown)==2, "Wrapper must be given function in the form 'module.function'."
        
        self.module_name = breakdown[0]
        self.args=args
        self.kw=kw
        self.function_ = self.__get_real_function()
        
              
    def __call__(self,*args,**kw):
        """
        If args or kw passed, return self.function_(*args,**kw);
        otherwise, return self.function_(**self.args,**self.kw).

        Allows Wrapper to be used when functions take arguments
        at call-time (e.g. Numeric.add(1,2)) and when functions
        have arguments specified on creation (e.g. when they are
        in a DynamicNumber and will be called without arguments).
        """
        if len(args)==0 and len(kw)==0:
            return self.function_(*self.args,**self.kw)
        else:
            return self.function_(*args,**kw)

    def __get_real_function(self):
        exec('import '+self.module_name)
        return eval(self.function_as_text)

    def __getstate__(self):
        """
        Can't pickle self.function_, so don't return it
        as part of the state. Instead, we recreate it
        in __setstate__().
        """
        state = {}
        
        for slot in self.__slots__:
            state[slot]=getattr(self,slot)

        del state['function_']

        return state

    def __setstate__(self,state):
        """
        Restore the state.
        """
        for (k,v) in state.items():
            setattr(self,k,v)
        self.function_ = self.__get_real_function()
        



        
        
        

