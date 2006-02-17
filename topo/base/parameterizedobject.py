"""
Topographica Base

Implements the Topographica generic base class ParameterizedObject.  This class
encapsulates generic functions of all Topographica classes, such as
automatic parameter setting, message output, etc.

$Id$
"""
__version__='$Revision$'

import sys
import copy


from pprint import pprint

SILENT  = 0
WARNING = 50
NORMAL  = 100
MESSAGE = NORMAL
VERBOSE = 200
DEBUG   = 300

min_print_level = NORMAL
object_count = 0


# CEBHACKALERT: much of the documentation for Parameter subclasses
# that ought to be in the class docstring is in the __init__
# docstring so that it shows up. In some cases there is
# some repetition.
# See JABHACKALERT by __doc__.


def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) class_.

    The list is ordered from least- to most-specific.  Often useful in
    functions to get and set the full state of an object, e.g. for
    pickling.
    """
    assert isinstance(class_, type)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.append(x)
        for b in x.__bases__:
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]


def descendents(class_):
    """
    Return a list of the class hierarchy below (and including) class_.

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
    ParameterizedObjects, and so are pickled even though Parameter has no
    explicit support for pickling (usually if a class has __slots__ it
    can't be pickled without additional support: see the Pickle module
    documentation).
    """

    # To get the benefit of slots, subclasses must themselves define
    # __slots__, whether or not they define attributes not present in
    # the base Parameter class.
    # See the reference manual:
    # The action of a __slots__ declaration is limited to the class
    # where it is defined. As a result, subclasses will have a
    # __dict__ unless they also define __slots__.

    __slots__ = ['_name','default','doc','hidden','precedence','instantiate']
    count = 0

    # CEBHACKALERT: I think this can be made simpler
    def __init__(self,default=None,doc=None,hidden=False,precedence=None,instantiate=False):
        """
        Initialize a new parameter.

        Set the name of the parameter to a gensym, and initialize
        the default value.

        _name stores the Parameter's name. This is
        created automatically by ParameterizedObject, but can also be passed in
        (see ParameterizedObject).

        default is the value of Parameter p that is returned if
        ParameterizedObject_class.p is requested, or if ParameterizedObject_object.p is
        requested but has not been set.

        hidden is a flag that allows objects using Parameters to know
        whether or not to display them to the user (e.g. in GUI menus).

        precedence is a value, usually in the range 0.0 to 1.0, that
        allows the order of Parameters in a class to be defined (again
        for e.g. in GUI menus).

        default, doc, and precedence default to None. This is to allow
        inheritance of Parameter slots (attributes) from the owning-class'
        class hierarchy (see ParameterizedObjectMetaclass).
        """
        self._name = None
        self.hidden=hidden
        self.precedence = precedence
        Parameter.count += 1
        self.default = default
        self.doc = doc
        self.instantiate = instantiate

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
        which looks for itself in the owning class hierarchy and returns the name
        assigned to it.    
        """
        if not hasattr(self,'_name') or not self._name:
             classes = classlist(type(obj))[::-1]
             print classes
             for class_ in classes:
                 for attrib_name in dir(class_):
                     if hasattr(class_,'get_param_descriptor'):
                         desc,desctype = class_.get_param_descriptor(attrib_name)
                         if desc is self:
                             self._name = '_%s_param_value'%attrib_name
                             return self._name
        else:
            return self._name


    # When a Parameter is owned by a ParameterizedObject, we want the
    # documentation for that object to print the doc slot for this
    # parameter, not the __doc__ value for the Parameter class or
    # subclass.  For instance, if we have a ParameterizedObject class X with
    # parameters y(doc="All about y") and z(doc="More about z"),
    # help(X) should include "All about y" in the section describing
    # y, and "More about z" in the section about z.
    #
    # We currently achieve this by making __doc__ return the value of
    # self.doc, using the code below.
    #
    # NOTE: This code must also be copied to any subclass of
    # Parameter, or else the documentation for y and z above will
    # be the documentation for their Parameter class, not those
    # specific parameters.
    #
    # JABHACKALERT: Unfortunately, this trick makes the documentation
    # for Parameter and its subclasses invisible, so that e.g.
    # help(Parameter) and help(Number) do not include the usual
    # docstring defined in those classes.  We could save a copy of
    # that docstring in a class attribute, and it *may* be possible
    # somehow to return that for help(Parameter), without breaking the
    # current support for help(X) (where X is a ParameterizedObject and help(X)
    # describes X's specific Parameters).  Seems difficult, though.
    __doc__ = property((lambda self: self.doc))
    

class Constant(Parameter):
    """
    Constant Parameter that can be constructed and used but not set on an
    initialized object.

    The default value of the Parameter can, however, be set on a class.
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,value,**params):
        """
        This Constant gets a deepcopy of the value passed in when it is declared.
        """
        Parameter.__init__(self,default=value,instantiate=True,**params)

    def __set__(self,obj,val):
        """
        Does not allow set commands except on the classobj or
        on an uninitialized ParameterizedObject.
        """
        if obj==None or obj.initialized==False:
            super(Constant,self).__set__(obj,val)
        else:
            raise TypeError("Constant parameter cannot be modified")


class ParameterizedObjectMetaclass(type):
    """
    The metaclass of ParameterizedObject (and all its descendents).

    The metaclass overrides type.__setattr__ to allow us to set
    Parameter values on classes without overwriting the attribute
    descriptor.  That is, for a ParameterizedObject of type X with a Parameter
    y, the user can type X.y=3, which sets the default value of
    Parameter y to be 3, rather than overwriting y with the constant
    value 3 (and thereby losing all other info about that Parameter,
    such as the doc string, bounds, etc.)

    The other methods get_param_descriptor and print_param_defaults
    could perhaps be made into static functions, because all they
    (appear to) do is to provide a way to call the functions without
    having a specific object available.  Perhaps they do something
    else that requires them to be in the metaclass, though?

    The __init__ method is used when defining a ParameterizedObject class,
    usually when the module where that class is located is imported
    for the first time.  That is, the __init__ in this metaclass
    initializes the *class* object, while the __init__ method defined
    in each ParameterizedObject class is called for each new instance of that
    class.
    """   
    def __init__(self,name,bases,dict):
        """
        Initialize the class object (not an instance of the class, but the class itself).

        Initializes all the Parameters by looking up appropriate
        default values; see __param_inheritance().
        """
        type.__init__(self,name,bases,dict)

        # All objects (with their names) of type Parameter that are
        # defined in this class
        parameters = [(name,obj)
                      for (name,obj) in dict.items()
                      if isinstance(obj,Parameter)]
        
        for param_name,param in parameters:
            self.__param_inheritance(param_name,param,bases)


    def __setattr__(self,attribute_name,value):
        """
        Implements 'self.attribute_name=value' in a way that also supports Parameters.

        If there is already a descriptor named attribute_name, and
        that descriptor is a Parameter, and the new value is *not* a
        Parameter, then call that Parameter's __set__ method with the
        specified value.
        
        In all other cases set the attribute normally (i.e. overwrite
        the descriptor).  If the new value is a Parameter, once it has
        been set we make sure that the value is inherited from
        ParameterizedObject superclasses as described in __param_inheritance().
        """        

        # Find out if there's a Parameter called attribute_name as a
        # class attribute of this class - if not, parameter is None.
        parameter,owning_class = self.get_param_descriptor(attribute_name)

        if parameter and not isinstance(value,Parameter):
            if owning_class != self:
                type.__setattr__(self,attribute_name,copy.copy(parameter))
            self.__dict__[attribute_name].__set__(None,value)

        else:    
            type.__setattr__(self,attribute_name,value)
            
            if isinstance(value,Parameter):
                bases = classlist(self)[::-1]
                self.__param_inheritance(attribute_name,value,bases)
            else:
                print (" ##WARNING## Setting non-Parameter class attribute %s.%s = %s "
                       % (self.__name__,attribute_name,`value`))

                
    def __param_inheritance(self,param_name,param,bases):
        """
        Look for Parameter values in superclasses of this ParameterizedObject.

        Ordinarily, when a Python object is instantiated, attributes
        not given values in the constructor will inherit the value
        given in the object's class, or in its superclasses.  For
        Parameters owned by ParameterizedObjects, we have implemented an
        additional level of default lookup, should this ordinary
        lookup return only None.

        In such a case, i.e. when no non-None value was found for a
        Parameter by the usual inheritance mechanisms, we explicitly
        look for Parameters with the same name in superclasses of this
        ParameterizedObject, and use the first such value that we find.

        The goal is to be able to set the default value (or other
        slots) of a Parameter within a ParameterizedObject, just as we can set
        values for non-Parameter objects in ParameterizedObjects, and have the
        values inherited through the ParameterizedObject hierarchy as usual.
        """
        for slot in param.__slots__:
            base_classes = iter(bases)

            # Search up the hierarchy until param.slot (which
            # has to be obtained using getattr(param,slot))
            # is not None, or we run out of classes to search.
            #
            # CEBALERT: there's probably a better way than while
            # and an iterator, but it works.
            while getattr(param,slot)==None:
                try:
                    param_base_class = base_classes.next()
                except StopIteration:
                    break

                new_param = param_base_class.__dict__.get(param_name)
                if new_param != None:
                    new_value = getattr(new_param,slot)
                    setattr(param,slot,new_value)

        
    def get_param_descriptor(self,param_name):
        """
        Goes up the class hierarchy (starting from the current class)
        looking for a Parameter class attribute param_name. As soon as
        one is found as a class attribute, that Parameter is returned
        along with the class in which it is declared.
        """
        classes = classlist(self)
        for c in classes[::-1]:
            attribute = c.__dict__.get(param_name)
            if isinstance(attribute,Parameter):
                return attribute,c
        return None,None

    def print_param_defaults(self):
        for key,val in self.__dict__.items():
            if isinstance(val,Parameter):
                print self.__name__+'.'+key, '=', val.default


class ParameterizedObject(object):
    """
    Base class for most Topographica objects, providing automatic
    object naming, automatic parameter setting, and message formatting
    facilities:
    
    - Automatic object naming -
    
    Every ParameterizedObject has a name parameter.  If the user doesn't designate
    a name=<str> argument when constructing the object, the object will be
    given a name consisting of its class name followed by a unique 5-digit
    number. 
    
    - Automatic parameter setting -
    
    The ParameterizedObject __init__ method will automatically read the list of
    keyword parameters.  If any keyword matches the name of a Parameter
    (see parameter.py) defined in the object's class or any of its
    superclasses, that parameter in the instance will get the value given
    as a keyword argument.  For example:
    
      class Foo(ParameterizedObject):
         xx = Parameter(default=1)
    
      foo = Foo(xx=20)
    
    in this case foo.xx gets the value 20.
    
    - Message formatting -
    
    Each ParameterizedObject has several methods for optionally printing output
    according to the current 'print level'.  The print levels are SILENT,
    WARNING, MESSAGE, VERBOSE, and DEBUG.  Each successive level allows
    more messages to be printed.  For example, when the level is VERBOSE,
    all warning, message, and verbose output will be printed.  When it is
    WARNING, only warnings will be printed.  When it is SILENT, no output
    will be printed.
    
    For each level (except SILENT) there's an associated print method:
    ParameterizedObject.warning(), .message(), .verbose(), and .debug().
    
    Each line printed this way is prepended with the name of the object
    that printed it.  The ParameterizedObject parameter print_level, and the module
    global variable min_print_level combine to determine what gets
    printed.  For example, if foo is a ParameterizedObject:
    
       foo.message('The answer is',42)
    
    is equivalent to:
    
       if max(foo.print_level,base.min_print_level) >= MESSAGE:
           print foo.name+':', 'The answer is', 42
    """

    __metaclass__ = ParameterizedObjectMetaclass


    ### It might make sense to make the name be visible (not hidden) by default.
    name           = Parameter(default=None,hidden=True)
    print_level = Parameter(default=MESSAGE,hidden=True)
    
    def __init__(self,**config):
        """
        If **config doesn't contain a 'name' parameter, self.name defaults
        to a gensym formed from the object's type name and a unique number.
        """        
        global object_count

        # Flag that can be tested to see if e.g. Constant Parameters
        # can still be set
        self.initialized=False

        # CEBHACKALERT: it's possible for ParameterizedObjects to share the same name.
        # (E.g. two can be created with the same name passed in.)
        self.__generate_name()
        
        self.__setup_params(**config)
        object_count += 1

        self.nopickle = []
        self.verbose('Initialized',self)

        self.initialized=True

    def __generate_name(self):
        """
        Sets name to a gensym formed from the object's type name and a unique number.
        """
        self.name = '%s%05d' % (self.__class__.__name__ ,object_count)

    def __repr__(self):
        """
        Returns '<self.name>'.
        """
        return "<%s>" % self.name

    def __str__(self):
        """
        Returns '<self.name>'.
        """
        return "<%s>" % self.name


    def __db_print(self,level=NORMAL,*args):
        """
        Iff print_level or self.db_print_level is greater than or
        equal to the given level, print str.
        """
        if level <= max(min_print_level,self.print_level):
            s = ' '.join([str(x) for x in args])
            print "%s: %s" % (self.name,s)
        sys.stdout.flush()

    def warning(self,*args):
        """
        Print the arguments as a warning.
        """
        self.__db_print(WARNING,"##WARNING##",*args)
    def message(self,*args):
        """
        Print the arguments as a message.
        """
        self.__db_print(MESSAGE,*args)
    def verbose(self,*args):
        """
        Print the arguments as a verbose message.
        """
        self.__db_print(VERBOSE,*args)
    def debug(self,*args):
        """
        Print the arguments as a debugging statement.
        """
        self.__db_print(DEBUG,*args)


    def __setup_params(self,**config):
        """
        """
        # deepcopy a Parameter if its 'instantiate' attribute is True,
        # and put it in this ParameterizedObject's dictionary - so it has its
        # own copy, rather than sharing the class'.        
        for class_ in classlist(type(self)):
            for (k,v) in class_.__dict__.items():
                if isinstance(v,Parameter) and v.instantiate==True:
                    parameter_name = v.get_name(self) 
                    new_object = copy.deepcopy(v.default)
                    self.__dict__[parameter_name]=new_object

                    # a new ParameterizedObject needs a new name
                    # CEBHACKALERT: this will write over any name given;
                    # instead, maybe the name function could accept
                    # a prefix? To do when HACKALERT about naming is
                    # fixed in __init__.
                    if isinstance(new_object,ParameterizedObject):
                        global object_count
                        object_count+=1
                        new_object.__generate_name()
                        
                    
                    
        for name,val in config.items():
            desc,desctype = self.__class__.get_param_descriptor(name)
            if desc:
                self.debug("Setting param %s ="%name, val)
            else:
                self.warning("CANNOT SET non-parameter %s ="%name, val)
            setattr(self,name,val)


    def get_param_values(self):
        """Return a list of name,value pairs for all Parameters of this object"""
        vals = []
        for name in dir(self):
            desc,desctype = self.__class__.get_param_descriptor(name)
            if desc:
                vals.append((name,getattr(self,name)))
        vals.sort(key=lambda x:x[0])
        return vals

    def print_param_values(self):
        for name,val in self.get_param_values():
            print '%s.%s = %s' % (self.name,name,val)


    def __getstate__(self):
        """
        CEBHACKALERT: I will document this function.
        """
        state = {}
        
        # CEBHACKALERT: 
        # what this ought to do is traverse the classes in order most general to specific to get the
        # attributes, writing over more general ones with more specific.
        # I have code that uses classlist() do that, but I know for certain that the current code does not affect
        # the operation of LISSOM.
        # The exclusion of Constant is because we currently load a script first, so Constants get set.
        
        # first get class-level attributes
        c = self.__class__

        for entry in c.__dict__.keys():
            if isinstance(c.__dict__[entry], Parameter) and not isinstance(c.__dict__[entry], Constant):
                state[entry] = getattr(self, entry)

        # end CEBHACKALERT

        # now get the object's __dict__
        try:
            state.update(copy.copy(self.__dict__))
            
        except AttributeError,err:
            # object doesn't have a __dict__
            pass

        # get slots for this object's classes
        for c in classlist(type(self)):
            try:
                for k in c.__slots__:
                    state[k] = getattr(self,k)
                    
            except AttributeError:
                # class doesn't have __slots__
                pass

        return state


    def __setstate__(self,state):
        for k,v in state.items():
            setattr(self,k,v)
        self.unpickle()

    def unpickle(self):
        pass

    ### Need to decide whether this is redundant with get_param_dict, and if
    ### so which one to delete.
    def get_param_dict(self,**config):
        paramdict = {}
        for class_ in classlist(type(self)):
            for name,val in class_.__dict__.items():
                if isinstance(val,Parameter):
                    paramdict[name] = getattr(self,name)
        return paramdict

    def get_paramobj_dict(self,**config):
        """
        For getting the parameter objects directly, not just the
        values.
        """
        paramdict = {}
        for class_ in classlist(type(self)):
            for name,val in class_.__dict__.items():
                if isinstance(val,Parameter):
                    paramdict[name] = val
        return paramdict


def print_all_param_defaults():
    print "===== Topographica Parameter Default Values ====="
    classes = descendents(ParameterizedObject)
    classes.sort(key=lambda x:x.__name__)
    for c in classes:
        c.print_param_defaults()
    print "==========================================="

    


def class_parameters(topo_class):
    """
    Return the non-hidden Parameters of the specified ParameterizedObject class as {parameter_name: parameter}.

    E.g. for a class that has one Parameter
    x=Number()
    this function returns
    {'x':<topo.base.parameter.Number object at ...>}

    The specified class must be of type ParameterizedObject.
    """
    assert isinstance(topo_class, type)

    # Create the object so that Parameters of any superclasses are also present.
    topo_obj = topo_class()
    
    if not isinstance(topo_obj,ParameterizedObject):
        raise TypeError("Can only get Parameters for a class derived from ParameterizedObject.")
    
    parameters = [(parameter_name,parameter)
                  for (parameter_name,parameter)
                  in topo_obj.get_paramobj_dict().items()
                  if not parameter.hidden
                 ]
                 
    return dict(parameters)
