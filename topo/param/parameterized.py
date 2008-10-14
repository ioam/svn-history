"""
Generic support for objects with full-featured Parameters and
messaging.  

$Id$
"""
__version__='$Revision$'

import sys
import copy
import re

from operator import itemgetter,attrgetter
from types import FunctionType

# JABALERT: Could consider using Python's logging facilities instead.
SILENT  = 0
WARNING = 50
NORMAL  = 100
MESSAGE = NORMAL
VERBOSE = 200
DEBUG   = 300

min_print_level = NORMAL

# Indicates whether warnings should be raised as errors, stopping
# processing.
warnings_as_exceptions = False

object_count = 0
warning_count = 0


import inspect
def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) the given class.

    Same as inspect.getmro(class_)[::-1]
    """
    return inspect.getmro(class_)[::-1]


def descendents(class_):
    """
    Return a list of the class hierarchy below (and including) the given class.

    The list is ordered from least- to most-specific.  Can be useful for
    printing the contents of an entire class hierarchy.
    """
    assert isinstance(class_,type)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.insert(0,x)
        for b in x.__subclasses__():
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]



def get_all_slots(class_):
    """
    Return a list of slot names for slots defined in this class and
    its superclasses.
    """
    # A subclass's __slots__ attribute does not contain slots defined
    # in its superclass (the superclass' __slots__ end up as
    # attributes of the subclass).
    all_slots = []
    parent_param_classes = [class_ for class_ in classlist(class_)[1::]]
    for class_ in parent_param_classes:
        if hasattr(class_,'__slots__'):
            all_slots+=class_.__slots__
    return all_slots
    



# CEBALERT: decorators hide the docstring when using help().  Consider
# the decorator module: would allow doc to be seen for the actual
# method rather than seeing 'partial object at ...'.
# Not part of standard library:
# http://www.phyast.pitt.edu/~micheles/python/documentation.html

from functools import partial
class bothmethod(object): # pylint: disable-msg=R0903
    """
    'optional @classmethod'
    
    A decorator that allows a method to receive either the class
    object (if called on the class) or the instance object
    (if called on the instance) as its first argument.

    Code (but not documentation) copied from:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/523033.
    """
    # pylint: disable-msg=R0903
    
    def __init__(self, func):
        self.func = func

    # i.e. this is also a non-data descriptor
    def __get__(self, obj, type_=None):
        if obj is None:
            return partial(self.func, type_)
        else:
            return partial(self.func, obj)


class ParameterMetaclass(type):
    """
    Metaclass allowing control over creation of Parameter classes.
    """
    def __new__(mcs,classname,bases,classdict):        
        # store the class's docstring in __classdoc
        if '__doc__' in classdict:
            classdict['__classdoc']=classdict['__doc__']
        # when asking for help on Parameter *object*, return the doc
        # slot
        classdict['__doc__']=property(attrgetter('doc'))

        # To get the benefit of slots, subclasses must themselves define
        # __slots__, whether or not they define attributes not present in
        # the base Parameter class.  That's because a subclass will have
        # a __dict__ unless it also defines __slots__.
        if '__slots__' not in classdict:
            classdict['__slots__']=[]
        
        return type.__new__(mcs,classname,bases,classdict)

    def __getattribute__(mcs,name):
        if name=='__doc__':
            # when asking for help on Parameter *class*, return the
            # stored class docstring
            return type.__getattribute__(mcs,'__classdoc')
        else:
            return type.__getattribute__(mcs,name)
        


# CEBALERT: we break some aspects of slot handling for Parameter and
# Parameterized. The __new__ methods in the metaclasses for those two
# classes omit to handle the case where __dict__ is passed in
# __slots__ (and they possibly omit other things too). Additionally,
# various bits of code in the Parameterized class assumes that all
# Parameterized instances have a __dict__, but I'm not sure that's
# guaranteed to be true (although it's true at the moment).


# CB: we could maybe reduce the complexity by doing something to allow
# a parameter to discover things about itself when created (would also
# allow things like checking a Parameter is owned by a
# Parameterized). I have some vague ideas about what to do.
class Parameter(object):
    """
    An attribute descriptor for declaring parameters.

    Parameters are a special kind of class attribute.  Setting a
    Parameterized class attribute to be a Parameter instance causes
    that attribute of the class (and the class's instances) to be
    treated as a Parameter.  This allows special behavior, including
    dynamically generated parameter values, documentation strings,
    constant and read-only parameters, and type or range checking at
    assignment time.

    For example, suppose someone wants to define two new kinds of
    objects Foo and Bar, such that Bar has a parameter delta, Foo is a
    subclass of Bar, and Foo has parameters alpha, sigma, and gamma
    (and delta inherited from Bar).  She would begin her class
    definitions with something like this:

    class Bar(Parameterized):
        delta = Parameter(default=0.6, doc='The difference between steps.')
        ...
        
    class Foo(Bar):
        alpha = Parameter(default=0.1, doc='The starting value.')
        sigma = Parameter(default=0.5, doc='The standard deviation.',
                          constant=True)
        gamma = Parameter(default=1.0, doc='The ending value.')
        ...

    Class Foo would then have four parameters, with delta defaulting
    to 0.6.

    Parameters have several advantages over plain attributes:

    1. Parameters can be set automatically when an instance is
       constructed: The default constructor for Foo (and Bar) will
       accept arbitrary keyword arguments, each of which can be used
       to specify the value of a Parameter of Foo (or any of Foo's
       superclasses).  E.g., if a script does this:

           myfoo = Foo(alpha=0.5)

       myfoo.alpha will return 0.5, without the Foo constructor
       needing special code to set alpha.

       If Foo implements its own constructor, keyword arguments will
       still be accepted if the constructor accepts a dictionary of
       keyword arguments (as in ``def __init__(self,**params):``), and
       then each class calls its superclass (as in
       ``super(Foo,self).__init__(**params)``) so that the
       Parameterized constructor will process the keywords.

    2. A Parameterized class need specify only the attributes of a
       Parameter whose values differ from those declared in
       superclasses; the other values will be inherited.  E.g. if Foo
       declares

        delta = Parameter(default=0.2) 

       the default value of 0.2 will override the 0.6 inherited from
       Bar, but the doc will be inherited from Bar.

    3. The Parameter descriptor class can be subclassed to provide
       more complex behavior, allowing special types of parameters
       that, for example, require their values to be numbers in
       certain ranges, generate their values dynamically from a random
       distribution, or read their values from a file or other
       external source.

    4. The attributes associated with Parameters provide enough
       information for automatically generating property sheets in
       graphical user interfaces, allowing Parameterized instances to
       be edited by users.

    Note that Parameters can only be used when set as class attributes
    of Parameterized classes. Parameters used as standalone objects,
    or as class attributes of non-Parameterized classes, will not have
    the behavior described here.
    """
    __metaclass__ = ParameterMetaclass
    
    # Because they implement __get__ and __set__, Parameters are known
    # as 'descriptors' in Python; see "Implementing Descriptors" and
    # "Invoking Descriptors" in the 'Customizing attribute access'
    # section of the Python reference manual:
    # http://docs.python.org/ref/attribute-access.html
    #
    # Overview of Parameters for programmers
    # ======================================
    #
    # Consider the following code:
    #
    #
    # class A(Parameterized):
    #     p = Parameter(default=1)
    #
    # a1 = A()
    # a2 = A()
    #
    #
    # * a1 and a2 share one Parameter object (A.__dict__['p']).
    #
    # * The default (class) value of p is stored in this Parameter
    #   object (A.__dict__['p'].default).
    #
    # * If the value of p is set on a1 (e.g. a1.p=2), a1's value of p
    #   is stored in a1 itself (a1.__dict__['_p_param_value'])
    #
    # * When a1.p is requested, a1.__dict__['_p_param_value'] is
    #   returned. When a2.p is requested, '_p_param_value' is not
    #   found in a2.__dict__, so A.__dict__['p'].default (i.e. A.p) is
    #   returned instead.
    #
    #
    # Be careful when referring to the 'name' of a Parameter:
    #                                                   
    # * A Parameterized class has a name for the attribute which is
    #   being represented by the Parameter ('p' in the example above);
    #   in the code, this is called the 'attrib_name'.
    #
    # * When a Parameterized instance has its own local value for a
    #   parameter, it is stored as '_X_param_value' (where X is the
    #   attrib_name for the Parameter); in the code, this is called
    #   the internal_name.

                                                   
    # So that the extra features of Parameters do not require a lot of
    # overhead, Parameters are implemented using __slots__ (see
    # http://www.python.org/doc/2.4/ref/slots.html).  Instead of having
    # a full Python dictionary associated with each Parameter instance,
    # Parameter instances have an enumerated list (named __slots__) of
    # attributes, and reserve just enough space to store these
    # attributes.  Using __slots__ requires special support for
    # operations to copy and restore Parameters (e.g. for Python
    # persistent storage pickling); see __getstate__ and __setstate__.
    __slots__ = ['_attrib_name','_internal_name','default','doc',
                 'precedence','instantiate','constant','readonly']

    # When created, a Parameter does not know which
    # Parameterized class owns it. If a Parameter subclass needs
    # to know the owning class, it can declare an 'objtype' slot
    # (which will be filled in by ParameterizedMetaclass)
                                                   
    def __init__(self,default=None,doc=None,precedence=None,  # pylint: disable-msg=R0913
                 instantiate=False,constant=False,readonly=False): 
        """
        Initialize a new Parameter object: store the supplied attributes.

        default: the owning class's value for the attribute
        represented by this Parameter.

        precedence is a value, usually in the range 0.0 to 1.0, that
        allows the order of Parameters in a class to be defined (for
        e.g. in GUI menus). A negative precedence indicates a
        parameter that should be hidden in e.g. GUI menus.

        default, doc, and precedence default to None. This is to allow
        inheritance of Parameter slots (attributes) from the owning-class'
        class hierarchy (see ParameterizedMetaclass).
        """
        self._attrib_name = None  
        self._internal_name = None
        self.precedence = precedence
        self.default = default
        self.doc = doc
        self.constant = constant or readonly # readonly => constant
        self.readonly = readonly
        self._set_instantiate(instantiate)


    def _set_instantiate(self,instantiate):
        """Constant parameters must be instantiated."""
        # CB: instantiate doesn't actually matter for read-only
        # parameters, since they can't be set even on a class.  But
        # this avoids needless instantiation.
        if self.readonly:
            self.instantiate = False
        else:
            self.instantiate = instantiate or self.constant # pylint: disable-msg=W0201


    def __get__(self,obj,objtype): # pylint: disable-msg=W0613
        """
        Return the value for this Parameter.

        If called for a Parameterized class, produce that
        class's value (i.e. this Parameter object's 'default'
        attribute).

        If called for a Parameterized instance, produce that
        instance's value, if one has been set - otherwise produce the
        class's value (default).
        """
        # NB: obj can be None (when __get__ called for a
        # Parameterized class); objtype is never None
        
        if not obj:
            result = self.default
        else:
            result = obj.__dict__.get(self._internal_name,self.default)
        return result
        

    def __set__(self,obj,val):
        """
        Set the value for this Parameter.

        If called for a Parameterized class, set that class's
        value (i.e. set this Parameter object's 'default' attribute).

        If called for a Parameterized instance, set the value of
        this Parameter on that instance (i.e. in the instance's
        __dict__, under the parameter's internal_name). 

        
        If the Parameter's constant attribute is True, only allows
        the value to be set for a Parameterized class or on
        uninitialized Parameterized instances.

        If the Parameter's readonly attribute is True, only allows the
        value to be specified in the Parameter declaration inside the
        Parameterized source code. A read-only parameter also
        cannot be set on a Parameterized class.
        
        Note that until we support some form of read-only
        object, it is still possible to change the attributes of the
        object stored in a constant or read-only Parameter (e.g. the
        left bound of a BoundingBox).
        """
        # NB: obj can be None (when __set__ called for a
        # Parameterized class)
        if self.constant or self.readonly:
            if self.readonly:
                raise TypeError("Read-only parameter '%s' cannot be modified"%self._attrib_name)
            elif not obj:
                self.default = val
            elif not obj.initialized:
                obj.__dict__[self._internal_name] = val
            else:
                raise TypeError("Constant parameter '%s' cannot be modified"%self._attrib_name)

        else:
            if not obj:
                self.default = val
            else:
                obj.__dict__[self._internal_name] = val
                

    def __delete__(self,obj):
        raise TypeError("Cannot delete '%s': Parameters deletion not allowed."%self._attrib_name)


    def _set_names(self,attrib_name):        
        self._attrib_name = attrib_name
        self._internal_name = "_%s_param_value"%attrib_name
    

    def __getstate__(self):
        """
        All Parameters have slots, not a dict, so we have to support
        pickle and deepcopy ourselves.
        """
        state = {}
        for slot in get_all_slots(type(self)):
            state[slot] = getattr(self,slot)

        return state

    def __setstate__(self,state):
        # set values of __slots__ (instead of in non-existent __dict__)
        for (k,v) in state.items():
            setattr(self,k,v)    


# Define one particular type of Parameter that is used in this file
class String(Parameter):
    __slots__ = ['allow_None']

    def __init__(self,default="",allow_None=False,**params):
        """Initialize a string parameter."""
        Parameter.__init__(self,default=default,**params)
        self.allow_None = (default is None or allow_None)
        
    def __set__(self,obj,val):
        if not isinstance(val,str) and not (self.allow_None and val is None):
            raise ValueError("String '%s' only takes a string value."%self._attrib_name)

        super(String,self).__set__(obj,val)



class ParameterizedMetaclass(type):
    """
    The metaclass of Parameterized (and all its descendents).

    The metaclass overrides type.__setattr__ to allow us to set
    Parameter values on classes without overwriting the attribute
    descriptor.  That is, for a Parameterized class of type X with a
    Parameter y, the user can type X.y=3, which sets the default value
    of Parameter y to be 3, rather than overwriting y with the
    constant value 3 (and thereby losing all other info about that
    Parameter, such as the doc string, bounds, etc.).

    The __init__ method is used when defining a Parameterized class,
    usually when the module where that class is located is imported
    for the first time.  That is, the __init__ in this metaclass
    initializes the *class* object, while the __init__ method defined
    in each Parameterized class is called for each new instance of
    that class.

    Additionally, a class can declare itself abstract by having an
    attribute __abstract set to True. The 'abstract' attribute can be
    used to find out if a class is abstract or not.
    """    
    def __init__(mcs,name,bases,dict_):
        """
        Initialize the class object (not an instance of the class, but
        the class itself).

        Initializes all the Parameters by looking up appropriate
        default values; see __param_inheritance().
        """
        type.__init__(mcs,name,bases,dict_)

        # All objects (with their names) of type Parameter that are
        # defined in this class
        parameters = [(name,obj)
                      for (name,obj) in dict_.items()
                      if isinstance(obj,Parameter)]
        
        for param_name,param in parameters:
            # parameter has no way to find out the name a
            # Parameterized class has for it
            param._set_names(param_name) 
            mcs.__param_inheritance(param_name,param)


    def __is_abstract(mcs):
        """
        Return True if the class has an attribute __abstract set to True.  
        Subclasses will return False unless they themselves have
        __abstract set to true.  This mechanism allows a class to
        declare itself to be abstract (e.g. to avoid it being offered
        as an option in a GUI), without the "abstract" property being
        inherited by its subclasses (at least one of which is
        presumably not abstract).
        """
        # Can't just do ".__abstract", because that is mangled to
        # _ParameterizedMetaclass__abstract before running, but
        # the actual class object will have an attribute
        # _ClassName__abstract.  So, we have to mangle it ourselves at
        # runtime.
        try:
            return getattr(mcs,'_%s__abstract'%mcs.__name__)
        except AttributeError:
            return False
        
    abstract = property(__is_abstract)



    def __setattr__(mcs,attribute_name,value):
        """
        Implements 'self.attribute_name=value' in a way that also supports Parameters.

        If there is already a descriptor named attribute_name, and
        that descriptor is a Parameter, and the new value is *not* a
        Parameter, then call that Parameter's __set__ method with the
        specified value.
        
        In all other cases set the attribute normally (i.e. overwrite
        the descriptor).  If the new value is a Parameter, once it has
        been set we make sure that the value is inherited from
        Parameterized superclasses as described in __param_inheritance().
        """
        # Find out if there's a Parameter called attribute_name as a
        # class attribute of this class - if not, parameter is None.
        parameter,owning_class = mcs.get_param_descriptor(attribute_name)

        if parameter and not isinstance(value,Parameter):
            if owning_class != mcs:
                type.__setattr__(mcs,attribute_name,copy.copy(parameter))
            mcs.__dict__[attribute_name].__set__(None,value)

        else:    
            type.__setattr__(mcs,attribute_name,value)
            
            if isinstance(value,Parameter):
                mcs.__param_inheritance(attribute_name,value)
            else:
                # the purpose of the warning below is to catch
                # mistakes ("thinking you are setting a parameter, but
                # you're not"). There are legitimate times when
                # something needs be set on the class, and we don't
                # want to see a warning then. Such attributes should
                # presumably be prefixed by at least one underscore.
                # (For instance, python's own pickling mechanism
                # caches __slotnames__ on the class:
                # http://mail.python.org/pipermail/python-checkins/2003-February/033517.html.)
                # CEBALERT: this warning bypasses the usual
                # mechanisms, which has have consequences for warning
                # counts, warnings as exceptions, etc.
                if not attribute_name.startswith('_'):
                    print ("Warning: Setting non-Parameter class attribute %s.%s = %s "
                           % (mcs.__name__,attribute_name,`value`))
                
                
    def __param_inheritance(mcs,param_name,param):
        """
        Look for Parameter values in superclasses of this
        Parameterized class.

        Ordinarily, when a Python object is instantiated, attributes
        not given values in the constructor will inherit the value
        given in the object's class, or in its superclasses.  For
        Parameters owned by Parameterized classes, we have implemented
        an additional level of default lookup, should this ordinary
        lookup return only None.

        In such a case, i.e. when no non-None value was found for a
        Parameter by the usual inheritance mechanisms, we explicitly
        look for Parameters with the same name in superclasses of this
        Parameterized class, and use the first such value that we
        find.

        The goal is to be able to set the default value (or other
        slots) of a Parameter within a Parameterized class, just as we
        can set values for non-Parameter objects in Parameterized
        classes, and have the values inherited through the
        Parameterized hierarchy as usual.
        """
        # get all relevant slots (i.e. slots defined in all
        # superclasses of this parameter)
        slots = {}
        for p_class in classlist(type(param))[1::]:
            slots.update(dict.fromkeys(p_class.__slots__))

        # Some Parameter classes need to know the owning Parameterized
        # class. Such classes can declare an 'objtype' slot, and the
        # owning class will be stored in it.
        if 'objtype' in slots:
            setattr(param,'objtype',mcs)            
            del slots['objtype'] 

        for slot in slots.keys():
            superclasses = iter(classlist(mcs)[::-1])

            # Search up the hierarchy until param.slot (which has to
            # be obtained using getattr(param,slot)) is not None, or
            # we run out of classes to search.
            #
            # CEBALERT: there's probably a better way than while and
            # an iterator, but it works.
            while getattr(param,slot) is None:
                try:
                    param_super_class = superclasses.next()
                except StopIteration:
                    break

                new_param = param_super_class.__dict__.get(param_name)
                if new_param != None and hasattr(new_param,slot):
                    # (slot might not be there because could be a more
                    # general type of Parameter)
                    new_value = getattr(new_param,slot)
                    setattr(param,slot,new_value)

        
    def get_param_descriptor(mcs,param_name):
        """
        Goes up the class hierarchy (starting from the current class)
        looking for a Parameter class attribute param_name. As soon as
        one is found as a class attribute, that Parameter is returned
        along with the class in which it is declared.
        """
        classes = classlist(mcs)
        for c in classes[::-1]:
            attribute = c.__dict__.get(param_name)
            if isinstance(attribute,Parameter):
                return attribute,c
        return None,None




# JABALERT: Only partially achieved so far -- objects of the same
# type and parameter values are treated as different, so anything
# for which instantiate == True is reported as being non-default.

# Whether script_repr should avoid reporting the values of parameters
# that are just inheriting their values from the class defaults.
script_repr_suppress_defaults=True



def script_repr(val,imports,prefix,settings):
    """
    Variant of repr() designed for generating a runnable script.

    Types that require special handling can use the script_repr_reg
    dictionary. Using the type as a key, add a function that returns a
    suitable representation of instances of that type, and adds the
    required import statement.
    """
    # CB: doc prefix & settings or realize they don't need to be
    # passed around, etc.
    if type(val) in script_repr_reg:
        rep = script_repr_reg[type(val)](val,imports,prefix,settings)

    elif hasattr(val,'script_repr'):
        rep=val.script_repr(imports=imports,prefix=prefix+"    ")
        
    else:
        rep=repr(val)
        
    return rep


# see script_repr()
script_repr_reg = {}


# currently only handles list and tuple
def container_script_repr(container,imports,prefix,settings):
    result=[]
    for i in container:
        result.append(script_repr(i,imports,prefix,settings))

    ## (hack to get container brackets)
    if isinstance(container,list):
        d1,d2='[',']'
    elif isinstance(container,tuple):
        d1,d2='(',')'
    else:
        raise NotImplementedError
    rep=d1+','.join(result)+d2

    # no imports to add for built-in types
    
    return rep

# why I have to type prefix and settings?
def function_script_repr(fn,imports,prefix,settings):
    name = fn.func_name
    module = fn.__module__
    imports.append('import %s'%module)
    return module+'.'+name
    

script_repr_reg[list]=container_script_repr
script_repr_reg[tuple]=container_script_repr
script_repr_reg[FunctionType]=function_script_repr


# If not None, the value of this Parameter will be called (using '()')
# before every call to __db_print, and is expected to evaluate to a
# string that is suitable for prefixing messages and warnings (such
# as some indicator of the global state).
dbprint_prefix=None


def as_uninitialized(fn):
    """
    Decorator: call fn with the parameterized_instance's
    initialization flag set to False, then revert the flag.

    (Used to decorate Parameterized methods that must alter
    a constant Parameter.)
    """
    def override_initialization(parameterized_instance,*args,**kw):
        original_initialized=parameterized_instance.initialized
        parameterized_instance.initialized=False
        fn(parameterized_instance,*args,**kw)
        parameterized_instance.initialized=original_initialized
    return override_initialization



class Parameterized(object):
    """
    Base class for named objects that support Parameters and message
    formatting.
    
    Automatic object naming: Every Parameterized instance has a name
    parameter.  If the user doesn't designate a name=<str> argument
    when constructing the object, the object will be given a name
    consisting of its class name followed by a unique 5-digit number.
    
    Automatic parameter setting: The Parameterized __init__ method
    will automatically read the list of keyword parameters.  If any
    keyword matches the name of a Parameter (see Parameter class)
    defined in the object's class or any of its superclasses, that
    parameter in the instance will get the value given as a keyword
    argument.  For example:
    
      class Foo(Parameterized):
         xx = Parameter(default=1)
    
      foo = Foo(xx=20)
    
    in this case foo.xx gets the value 20.
    
    Message formatting: Each Parameterized instance has several methods
    for optionally printing output according to the current 'print
    level', such as SILENT, WARNING, MESSAGE, VERBOSE, or DEBUG.  Each
    successive level allows more messages to be printed.  For example,
    when the level is VERBOSE, all warning, message, and verbose
    output will be printed.  When it is WARNING, only warnings will be
    printed.  When it is SILENT, no output will be printed.
    
    For each level (except SILENT) there's an associated print method:
    Parameterized.warning(), .message(), .verbose(), and .debug().
    
    Each line printed this way is prepended with the name of the
    object that printed it.  The Parameterized.print_level parameter
    and the module global variable min_print_level combine to
    determine what gets printed.  For example, if foo is a
    Parameterized:
    
       foo.message('The answer is',42)
    
    is equivalent to:
    
       if max(foo.print_level,parameterized.min_print_level) >= MESSAGE:
           print foo.name+':', 'The answer is', 42
    """

    __metaclass__ = ParameterizedMetaclass

    name           = String(default=None,constant=True,doc="""
    String identifier for this object.""")
    
    ### JABALERT: Should probably make this an Enumeration instead.
    print_level = Parameter(default=MESSAGE,precedence=-1)

    
    def __init__(self,**params):
        """
        Initialize this Parameterized instance.

        The values of parameters can be supplied as keyword arguments
        to the constructor (using parametername=parametervalue); these
        values will override the class default values for this one
        instance.

        If no 'name' parameter is supplied, self.name defaults to the
        object's class name with a unique number appended to it.
        """
        global object_count

        # Flag that can be tested to see if e.g. constant Parameters
        # can still be set
        self.initialized=False

        self.__generate_name()
        
        self._setup_params(**params)
        object_count += 1

        self.nopickle = [] # CEBALERT: remove this - we don't use it
        self.debug('Initialized',self)

        self.initialized=True


    # CEBALERT: I think I've noted elsewhere the fact that we
    # sometimes have a method on Parameter that requires passing the
    # owning Parameterized instance or class, and other times we have
    # the method on Parameterized itself.  In case I haven't written
    # that down elsewhere, here it is again.  We should clean that up
    # (at least we should be consistent).
    
    # cebalert: it's really time to stop and clean up this bothmethod
    # stuff and repeated code in methods using it.

    # CEBALERT: note there's no state_push method on the class, so
    # dynamic parameters set on a class can't have state saved. This
    # is because, to do this, state_push() would need to be a
    # @bothmethod, but that complicates inheritance in cases where we
    # already have a state_push() method. I need to decide what to do
    # about that. (isinstance(g,Parameterized) below is used to exclude classes.)
    def state_push(self):
        """
        Save this instance's state.

        For Parameterized instances, this includes the state of
        dynamically generated values.

        Subclasses that maintain short-term state should additionally
        save and restore that state using state_push() and
        state_pop().

        Generally, this method is used by operations that need to test
        something without permanently altering the objects' state.
        """
        for pname,p in self.params().items():
            g = self.get_value_generator(pname)
            if hasattr(g,'_Dynamic_last'):
                g._saved_Dynamic_last.append(g._Dynamic_last)
                g._saved_Dynamic_time.append(g._Dynamic_time)
                # CB: not storing the time_fn: assuming that doesn't
                # change.
            elif hasattr(g,'state_push') and isinstance(g,Parameterized):
                g.state_push()

    def state_pop(self):
        """
        Restore the most recently saved state.

        See state_push() for more details.
        """
        for pname,p in self.params().items():
            g = self.get_value_generator(pname)
            if hasattr(g,'_Dynamic_last'):
                g._Dynamic_last = g._saved_Dynamic_last.pop()
                g._Dynamic_time = g._saved_Dynamic_time.pop()
            elif hasattr(g,'state_pop') and isinstance(g,Parameterized):
                g.state_pop()
        
        
    

    @bothmethod
    def set_dynamic_time_fn(self_or_cls,time_fn,sublistattr=None):
        """
        Set time_fn for all Dynamic Parameters of this class or
        instance object that are currently being dynamically
        generated.

        Additionally, sets _Dynamic_time_fn=time_fn on this class or
        instance object, so that any future changes to Dynamic
        Parmeters can inherit time_fn (e.g. if a Number is changed
        from a float to a number generator, the number generator will
        inherit time_fn).

        If specified, sublistattr is the name of an attribute of this
        class or instance that contains an iterable collection of
        subobjects on which set_dynamic_time_fn should be called.  If
        the attribute sublistattr is present on any of the subobjects,
        set_dynamic_time_fn() will be called for those, too.
        """
        self_or_cls._Dynamic_time_fn = time_fn

        if isinstance(self_or_cls,type):
            a = (None,self_or_cls)
        else:
            a = (self_or_cls,)

        for n,p in self_or_cls.params().items():
            if hasattr(p,'_value_is_dynamic'):
                if p._value_is_dynamic(*a):
                    g = self_or_cls.get_value_generator(n)
                    g._Dynamic_time_fn = time_fn

        if sublistattr:
            try:
                sublist = getattr(self_or_cls,sublistattr)
            except AttributeError:
                sublist = []
        
            for obj in sublist:
                obj.set_dynamic_time_fn(time_fn,sublistattr)
                
            
    @as_uninitialized
    def _set_name(self,name):
        self.name=name


    @as_uninitialized
    def __generate_name(self):
        """
        Set name to a gensym formed from the object's type name and
        the object_count.
        """
        self._set_name('%s%05d' % (self.__class__.__name__ ,object_count))

    # CB: __repr__ is called often; methods it uses should not be too slow
    def __repr__(self):
        """
        Provide a nearly valid Python representation that could be used to recreate
        the item with its parameters, if executed in the appropriate environment.
        
        Returns 'classname(parameter1=x,parameter2=y,...)', listing
        all the parameters of this object.
        """
        settings = ['%s=%s' % (name,repr(val))
                    for name,val in self.get_param_values()]
        return self.__class__.__name__ + "(" + ", ".join(settings) + ")"




    def script_repr(self,imports=[],prefix="    "):
        """
        Variant of __repr__ designed for generating a runnable script.
        """        
        # Suppresses automatically generated names and print_levels.
        settings=[]
        for name,val in self.get_param_values(onlychanged=script_repr_suppress_defaults):
            if name == 'name' and (val is not None and
                                   re.match('^'+self.__class__.__name__+'[0-9]+$',val)):
                rep=None
            elif name == 'print_level':
                rep=None
            else:
                rep=script_repr(val,imports,prefix,settings)

            if rep is not None:
                settings.append('%s=%s' % (name,rep))

            
        # Generate import statement
        cls = self.__class__.__name__
        mod = self.__module__

        bits = mod.split('.')

        imports.append("import %s"%mod)
        imports.append("import %s"%bits[0])

        # CB: Doesn't give a nice repr, but I don't see what to do
        # otherwise that will work in all cases. Also I haven't
        # updated this code in other places (e.g. simulation).
        return mod+'.'+self.__class__.__name__ + "(" + (",\n"+prefix).join(settings) + ")"

        
    def __str__(self):
        """Return a short representation of the name and class of this object."""
        return "<%s %s>" % (self.__class__.__name__,self.name)


    # CB: I'm not sure why we allow multiple args here rather than just one
    # message (given that the caller can easily use string substitution with
    # "%s"%var etc). I think this makes things more complicated, but I might
    # be missing something.
    def __db_print(self,level=NORMAL,*args):
        """
        Print each of the given args iff print_level or
        self.db_print_level is greater than or equal to the given
        level.

        Any of args may be functions, in which case they will be
        called. This allows delayed execution, preventing
        time-consuming code from being called unless the print level
        requires it.
        """
        if level <= max(min_print_level,self.print_level):

            # call any args that are functions
            args = list(args)
            for a in args:
                if isinstance(a,FunctionType): args[args.index(a)]=a()
            
            s = ' '.join([str(x) for x in args])
            
            if dbprint_prefix and callable(dbprint_prefix):
                prefix=dbprint_prefix() # pylint: disable-msg=E1102
            else:
                prefix=""
                
            print "%s%s: %s" % (prefix,self.name,s)
            
        sys.stdout.flush()


    def warning(self,*args):
        """
        Print the arguments as a warning, unless module variable
        warnings_as_exceptions is True, then raise an Exception
        containing the arguments.
        """
        if not warnings_as_exceptions:
            global warning_count
            warning_count+=1
            self.__db_print(WARNING,"Warning:",*args)
        else:
            raise Exception, ' '.join(["Warning:",]+[str(x) for x in args])


    def message(self,*args):
        """Print the arguments as a message."""
        self.__db_print(MESSAGE,*args)
        
    def verbose(self,*args):
        """Print the arguments as a verbose message."""
        self.__db_print(VERBOSE,*args)

    def debug(self,*args):
        """Print the arguments as a debugging statement."""
        self.__db_print(DEBUG,*args)

    # CEBALERT: this is a bit ugly
    def _instantiate_param(self,param_obj,dict_=None,key=None):
        # deepcopy param_obj.default into self.__dict__ (or dict_ if supplied)
        # under the parameter's _internal_name (or key if supplied)
        dict_ = dict_ or self.__dict__
        key = key or param_obj._internal_name
        new_object = copy.deepcopy(param_obj.default)
        dict_[key]=new_object

        if isinstance(new_object,Parameterized):
            global object_count
            object_count+=1
            # CB: writes over name given to the original object;
            # should it instead keep the same name?
            new_object.__generate_name()
        

    @as_uninitialized
    def _setup_params(self,**params):
        """
        Initialize default and keyword parameter values.

        First, ensures that all Parameters with 'instantiate=True'
        (typically used for mutable Parameters) are copied directly
        into each object, to ensure that there is an independent copy
        (to avoid suprising aliasing errors).  Then sets each of the
        keyword arguments, warning when any of them are not defined as
        parameters.

        Constant Parameters can be set during calls to this method.
        """
        # Deepcopy all 'instantiate=True' parameters
        for class_ in classlist(type(self)):
            for (k,v) in class_.__dict__.items():
                # (avoid replacing name with the default of None)
                if isinstance(v,Parameter) and v.instantiate and k!="name":
                    self._instantiate_param(v)
                                        
        for name,val in params.items():
            desc = self.__class__.get_param_descriptor(name)[0] # pylint: disable-msg=E1101
            if desc:
                self.debug("Setting param %s=%s"% (name, val))
            else:
                self.warning("Setting non-parameter attribute %s=%s using a mechanism intended only for parameters" % (name, val))
            # i.e. if not desc it's setting an attribute in __dict__, not a Parameter
            setattr(self,name,val)


    def _check_params(self,params):
        """
        Print a warning if params contains something that is
        not a Parameter of this object.

        Typically invoked by a __call__() method that accepts keyword
        arguments for parameter setting.
        """
        self_params = self.params()
        for item in params:
            if item not in self_params:
                self.warning("'%s' will be ignored (not a Parameter)."%item)


    def get_param_values(self,onlychanged=False):
        """Return a list of name,value pairs for all Parameters of this object"""
        vals = []
        for name,val in self.params().items():
            value = self.get_value_generator(name)
            if (not onlychanged or value != val.default):
                vals.append((name,value))

        vals.sort(key=itemgetter(0))
        return vals

    # CB: is there a more obvious solution than making these
    # 'bothmethod's?
    # An alternative would be to lose these methods completely and
    # make users do things via the Parameter object directly.

    # CB: is there a performance hit for doing this decoration? It
    # would show up in lissom_oo_or because separated composite uses
    # this method.
    @bothmethod
    def force_new_dynamic_value(cls_or_slf,name): # pylint: disable-msg=E0213
        """
        Force a new value to be generated for the dynamic attribute
        name, and return it.

        If name is not dynamic, its current value is returned
        (i.e. equivalent to getattr(name).
        """
        param_obj = cls_or_slf.params().get(name)

        if not param_obj:
            return getattr(cls_or_slf,name)

        cls,slf=None,None
        if isinstance(cls_or_slf,type):
            cls = cls_or_slf
        else:
            slf = cls_or_slf
            
        if not hasattr(param_obj,'_force'): 
            return param_obj.__get__(slf,cls)
        else:
            return param_obj._force(slf,cls) 
            

    @bothmethod
    def get_value_generator(cls_or_slf,name): # pylint: disable-msg=E0213
        """
        Return the value or value-generating object of the named
        attribute.

        For most parameters, this is simply the parameter's value
        (i.e. the same as getattr()), but Dynamic parameters have
        their value-generating object returned.
        """
        param_obj = cls_or_slf.params().get(name)

        if not param_obj:
            value = getattr(cls_or_slf,name)

        # CompositeParameter detected by being a Parameter and having 'attribs'
        elif hasattr(param_obj,'attribs'):
            value = [cls_or_slf.get_value_generator(a) for a in param_obj.attribs]

        # not a Dynamic Parameter 
        elif not hasattr(param_obj,'_value_is_dynamic'):
            value = getattr(cls_or_slf,name)

        # Dynamic Parameter...
        else:
            internal_name = "_%s_param_value"%name
            if hasattr(cls_or_slf,internal_name):
                # dealing with object and it's been set on this object
                value = getattr(cls_or_slf,internal_name)
            else:
                # dealing with class or isn't set on the object
                value = param_obj.default

        return value


    @bothmethod
    def inspect_value(cls_or_slf,name): # pylint: disable-msg=E0213
        """
        Return the current value of the named attribute without modifying it.

        Same as getattr() except for Dynamic parameters, which have their
        last generated value returned.
        """
        param_obj = cls_or_slf.params().get(name)

        if not param_obj:
            value = getattr(cls_or_slf,name)
        elif hasattr(param_obj,'attribs'):
            value = [cls_or_slf.inspect_value(a) for a in param_obj.attribs]
        elif not hasattr(param_obj,'_inspect'):
            value = getattr(cls_or_slf,name)
        else:
            if isinstance(cls_or_slf,type):
                value = param_obj._inspect(None,cls_or_slf)
            else:
                value = param_obj._inspect(cls_or_slf,None)

        return value
            


    def print_param_values(self):
        """Print the values of all this object's Parameters."""
        for name,val in self.get_param_values():
            print '%s.%s = %s' % (self.name,name,val)


    def __getstate__(self):
        """
        Save the object's state: return a dictionary that is a shallow
        copy of the object's __dict__ and that also includes the
        object's __slots__ (if it has any).
        """
        # remind me, why is it a copy? why not just state.update(self.__dict__)?        
        state = self.__dict__.copy()

        for slot in get_all_slots(type(self)):
            state[slot] = getattr(self,slot)

        # Note that Parameterized object pickling assumes that
        # attributes to be saved are only in __dict__ or __slots__
        # (the standard Python places to store attributes, so that's a
        # reasonable assumption). (Additionally, class attributes that
        # are Parameters are also handled, even when they haven't been
        # instantiated - see PickleableClassAttributes.)

        return state


    def __setstate__(self,state):
        """
        Restore objects from the state dictionary to this object.

        During this process the object is considered uninitialized.
        """
        self.initialized=False
        for name,value in state.items():
            setattr(self,name,value)                
        self.initialized=True


    @classmethod
    def params(cls):
        """
        Return the Parameters of this class as the
        dictionary {name: parameter_object}

        Includes Parameters from this class and its
        superclasses.
        """
        # CB: we cache the parameters because this method is called
        # often, and new parameters cannot be added (or deleted)
        try:
            return getattr(cls,'_%s__params'%cls.__name__)
        except AttributeError:
            paramdict = {}
            for class_ in classlist(cls):
                for name,val in class_.__dict__.items():
                    if isinstance(val,Parameter):
                        paramdict[name] = val

            # We only want the cache to be visible to the cls on which
            # params() is called, so we mangle the name ourselves at
            # runtime (if we were to mangle it now, it would be
            # _Parameterized.__params for all classes).
            setattr(cls,'_%s__params'%cls.__name__,paramdict)
            return paramdict
        


    @classmethod
    def print_param_defaults(cls):
        """Print the default values of all cls's Parameters."""
        for key,val in cls.__dict__.items():
            if isinstance(val,Parameter):
                print cls.__name__+'.'+key, '=', repr(val.default)


    def defaults(self):
        """
        Return {parameter_name:parameter.default} for all non-constant
        Parameters.

        Note that a Parameter for which instantiate==True has its default
        instantiated.
        """
        d = {}
        for param_name,param in self.params().items():
            if param.constant:
                pass
            elif param.instantiate:
                self._instantiate_param(param,dict_=d,key=param_name)
            else:
                d[param_name]=param.default
        return d

        


def print_all_param_defaults():
    """Print the default values for all imported Parameters."""
    print "_______________________________________________________________________________"
    print ""
    print "                           Parameter Default Values"
    print ""
    classes = descendents(Parameterized)
    classes.sort(key=lambda x:x.__name__)
    for c in classes:
        c.print_param_defaults()
    print "_______________________________________________________________________________"








# Support for changing parameter names
_param_name_changes = {}
# e.g. you change topo.pattern.basic.Gaussian.aspect_ratio to aspect_ration
# _param_name_changes['topo.pattern.basic.Gaussian']={'aspect_ratio':'aspect_ration'}
#
# (not yet finished - do we need to add information about version numbers?)

# CEBALERT: Can't this stuff move to the ParameterizedMetaclass?
import __main__
class PicklableClassAttributes(object):
    """
    Supports pickling of Parameterized class attributes for a given module.

    When requested to be pickled, stores a module's PO classes' attributes,
    and any given startup_commands. On unpickling, executes the startup
    commands and sets the class attributes.
    """
    # pylint: disable-msg=R0903
    
    # CB: might have mixed up module and package in the docs.
    def __init__(self,module,exclusions=(),startup_commands=()):
        """
        module: a module object, such as topo
        
        Any submodules listed by name in exclusions will not have their
        classes' attributes saved.
        """
        self.module=module
        self.exclude=exclusions
        self.startup_commands=startup_commands
        
    def __getstate__(self):
        """
        Return a dictionary of self.module's PO classes' attributes, plus
        self.startup_commands.
        """
        # warn that classes & functions defined in __main__ won't unpickle
        import types
        for k,v in __main__.__dict__.items():
            # there's classes and functions...what else?
            if isinstance(v,type) or isinstance(v,types.FunctionType):
                if v.__module__ == "__main__":
                    Parameterized().warning("%s (type %s) has source in __main__; it will only be found on unpickling if the class is explicitly defined (e.g. by running the same script first) before unpickling."%(k,type(v)))

        
        class_attributes = {}
        self.get_PO_class_attributes(self.module,class_attributes,[],exclude=self.exclude)

        # CB: we don't want to pickle anything about this object except what
        # we want to have executed on unpickling (this object's not going to be hanging around).
        return {'class_attributes':class_attributes,
                'startup_commands':self.startup_commands}


    def __setstate__(self,state):
        """
        Execute the startup commands and set class attributes.
        """
        self.startup_commands = state['startup_commands']
        
        for cmd in self.startup_commands:
            exec cmd in __main__.__dict__
            
        for class_name,state in state['class_attributes'].items():
            # from e.g. "topo.base.parameter.Parameter", we want "topo.base.parameter"
            module_path = class_name[0:class_name.rindex('.')]

            ### ? globals()[module.split('.')[0]] = __import__(module)
            # exec 'import '+module_path in __main__.__dict__

            exec 'import '+module_path in __main__.__dict__

            try:
                class_ = eval(class_name,__main__.__dict__)
            except:
                Parameterized().warning("Could not find class %s to restore its parameter values (class might have been removed or renamed)."%class_name)
                break

            # now restore class Parameter values
            for p_name,p in state.items():

                if class_name in _param_name_changes:
                    if p_name in _param_name_changes[class_name]:
                        new_p_name = _param_name_changes[class_name][p_name]
                        Parameterized().message("%s's %s parameter has been renamed to %s."%(class_name,p_name,new_p_name))
                        p_name = new_p_name

                try:
                    setattr(class_,p_name,p)
                except:
                    Parameterized().warning('Problem restoring parameter %s=%s for class %s (Parameter object representing %s may have changed since the snapshot was created).' % (p_name,repr(p),class_name,p_name))
                


    # CB: I guess this could be simplified
    def get_PO_class_attributes(self,module,class_attributes,processed_modules,exclude=()):
        """
        Recursively search module and get attributes of Parameterized classes within it.

        class_attributes is a dictionary {module.path.and.Classname: state}, where state
        is the dictionary {attribute: value}.

        Something is considered a module for our purposes if inspect says it's a module,
        and it defines __all__. We only search through modules listed in __all__.

        Keeps a list of processed modules to avoid looking at the same one
        more than once (since e.g. __main__ contains __main__ contains
        __main__...)

        Modules can be specifically excluded if listed in exclude.
        """
        dict_ = module.__dict__
        for (k,v) in dict_.items():
            if '__all__' in dict_ and inspect.ismodule(v) and k not in exclude:
                if k in dict_['__all__'] and v not in processed_modules:
                    self.get_PO_class_attributes(v,class_attributes,processed_modules,exclude)
                processed_modules.append(v)

            else:
                if isinstance(v,type) and issubclass(v,Parameterized):

                    # Note: we take the class name as v.__name__, not
                    # k, because k might be just a label for the true
                    # class. For example, if someone imports a class
                    # using 'as', the name in the local namespace
                    # could be different from the name when the class
                    # was defined.  It is correct to set the
                    # attributes on the true class.
                    full_class_path = v.__module__+'.'+v.__name__
                    class_attributes[full_class_path] = {}
                    # POs always have __dict__, never slots
                    for (name,obj) in v.__dict__.items():
                        if isinstance(obj,Parameter):
                            class_attributes[full_class_path][name] = obj



# CEBALERT: we should incorporate overridden._check_params() here
# rather than making __call__ methods do it
# (that is, if we want to keep _check_params at all).
class ParamOverrides(dict):
    """
    A dictionary that returns the attribute of an object if that attribute is not
    present in itself.

    Used to override the parameters of an object.
    """
    def __init__(self,overridden,dict_): 
        # we'd like __init__ to be fast because it's going to be
        # called a lot. What's the fastest way to move the existing
        # params dictionary into this one? Would
        #  def __init__(self,overridden,**kw):
        #      ...
        #      dict.__init__(self,**kw)
        # be faster/easier to use?
        self.overridden = overridden
        dict.__init__(self,dict_)        
 
    def __missing__(self,attr):
        """Return the attribute from overridden object."""
        return getattr(self.overridden,attr)
        
    def __repr__(self):
        """As dict.__repr__, but indicate the overridden object."""
        # something like...
        return dict.__repr__(self)+" overriding params from %s"%repr(self.overridden)


# CB: need to make a better attempt at documenting.
class ParameterizedFunction(Parameterized):
    """
    A subclass of Parameterized that, when created, returns the result
    of __call__.

    I.e. this is a Parameterized class that cannot be instantiated
    directly.
    """
    def __new__(class_,**params):
        inst=object.__new__(class_)
        return inst.__call__(**params)

    def __call__(self,*args,**kw):
        raise NotImplementedError("Subclasses must implement __call__.")


## CB: would allow all instance methods to pickle, but we use cPickle
## rather than pickle (for speed), so we can't use this.
##
## # from http://code.activestate.com/recipes/572213/
## import pickle,new
## def save_instancemethod(self, obj):
##     """ Save an instancemethod object """
##     # Instancemethods are re-created each time they are accessed so this will not be memoized
##     args = (obj.im_func, obj.im_self, obj.im_class)
##     self.save_reduce(new.instancemethod, args)
## pickle.Pickler.dispatch[new.instancemethod] = save_instancemethod

