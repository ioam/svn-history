"""
Generic support for objects with full-featured Parameters and
messaging.  Potentially useful for any large Python program that needs
user-modifiable object attributes.

$Id$
"""
__version__='$Revision$'

import sys
import copy
import re


from pprint import pprint

# JABALERT: Could consider using Python's logging facilities instead.
SILENT  = 0
WARNING = 50
NORMAL  = 100
MESSAGE = NORMAL
VERBOSE = 200
DEBUG   = 300

min_print_level = NORMAL
object_count = 0



def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) the given class.

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




class Parameter(object):
    """
    An attribute descriptor for declaring parameters.

    Parameters are a special kind of class attribute.  Setting a class
    attribute to be an instance of this class causes that attribute of
    the class and its instances to be treated as a Parameter.  This
    allows special behavior, including dynamically generated parameter
    values (using lambdas or generators), documentation strings,
    read-only (constant) parameters, and type or range checking at
    assignment time.

    For example, suppose someone wants to define two new kind of
    objects Foo and Bar, such that Bar has a parameter delta, Foo is a
    subclass of Bar, and Foo has parameters alpha, sigma, and gamma
    (and delta inherited from Bar).  She would begin her class
    definitions with something like this:

    class Bar(ParameterizedObject):
        delta = Parameter(default=0.6, doc='The difference between steps.')
        ...
        
    class Foo(Bar):
        alpha = Parameter(default=0.1, doc='The starting value.')
        sigma = Parameter(default=0.5, doc='The standard deviation.', constant=True)
        gamma = Parameter(default=1.0, doc='The ending value.')
        ...

    Class Foo would then have four parameters, with delta defaulting to 0.6.

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
       ParameterizedObject constructor will process the keywords.

    2. A ParameterizedObject need specify only the attributes of a
       Parameter whose values differ those declared in superclasses of
       the ParameterizedObject; the other values will be inherited.
       E.g. if Foo declares

        delta = Parameter(default=0.2) 

       the default value of 0.2 will override the 0.6 inherited from
       Bar, but the doc will be inherited from Bar.

    3. The Parameter descriptor class can be subclassed to provide more
       complex behavior, allowing special types of parameters that, for
       example, require their values to be numbers in certain ranges,
       generate their values dynamically from a random distribution, or 
       read their values from a file or other external source.

    4. The attributes associated with Parameters provide enough
       information for automatically generating property sheets in
       graphical user interfaces, to allow Parameters
       ParameterizedObjects to be edited by users.
    """

    # Because they implement __get__ and __set__, Parameters are
    # known as 'descriptors' in Python.  See 
    # http://users.rcn.com/python/download/Descriptor.htm
    # (and the other items on http://www.python.org/doc/newstyle.html)
    # for more information.
    #
    # So that the extra features of Parameters do not require a lot of
    # overhead, Parameters are implemented using __slots__ (see
    # http://www.python.org/doc/2.4/ref/slots.html).  Instead of having
    # a full Python dictionary associated with each Parameter instance,
    # Parameter instances have an enumerated list (named __slots__) of
    # attributes, and reserve just enough space to store these
    # attributes.  Using __slots__ requires special support for
    # operations to copy and restore Parameters (e.g. for Python
    # persistent storage pickling); see __getstate__ and __setstate__.
    # 
    # Note that the actual value of a Parameter is not stored in the
    # Parameter object itself, but in the owning
    # ParameterizedObject's __dict__.
    # 
    # To get the benefit of slots, subclasses must themselves define
    # __slots__, whether or not they define attributes not present in
    # the base Parameter class.  That's because a subclass will have
    # a __dict__ unless it also defines __slots__.

    ### JABALERT: hidden could perhaps be replaced with a very low
    ### (e.g. negative) precedence value.  That way by default the
    ### GUI could display those with precedence >0, but the user could
    ### select a level.
    __slots__ = ['_name','default','doc','hidden','precedence','instantiate','constant']
    count = 0

    __doc__ = property((lambda self: self.doc))
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


    # CEBALERT: I think this can be made simpler
    def __init__(self,default=None,doc=None,hidden=False,precedence=None,instantiate=False,constant=False):
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
        # Make sure subclass authors read all the documentation...
        assert not hasattr(self,'__dict__'), \
               "Subclasses of Parameter should define __slots__; " \
               + `type(self)` + " does not."

        # CEBHACKALERT: not sure how to check that a subclass has
        # __doc__ as a class attribute.

        self._name = None
        self.hidden=hidden
        self.precedence = precedence
        Parameter.count += 1
        self.default = default
        self.doc = doc
        self.constant = constant

        # CEBALERT: constants must be instantiated: should this
        # instead be a check and raise an error to inform the user?
        if self.constant:
            self.instantiate = True
        else:
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

        If the Parameter's constant attribute is True, does not allow
        set commands except on the classobj or on an uninitialized
        ParameterizedObject.  Note that until Topographica supports
        some form of read-only object, it is still possible to change
        the attributes of the object stored in a constant (e.g. the
        left bound of a BoundingBox).
        """
        
        if self.constant:
            if not obj:
                self.default = val
            elif not obj.initialized:
                obj.__dict__[self.get_name(obj)] = val
            else:
                raise TypeError("Constant parameter cannot be modified")

        else:
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
             for class_ in classes:
                 for attrib_name in dir(class_):
                     if hasattr(class_,'get_param_descriptor'):
                         desc,desctype = class_.get_param_descriptor(attrib_name)
                         if desc is self:
                             self._name = '_%s_param_value'%attrib_name
                             return self._name
        else:
            return self._name


    def __getstate__(self):
        """
        All Parameters have slots, not a dict, so we have to support
        pickle and deepcopy ourselves.
        """
        # The only complication is that a subclass' __slots__ do
        # not contain superclass' __slots__ (the superclass' __slots__
        # end up as attributes of the subclass).
        classes = [klass for klass in classlist(type(self))
                   if hasattr(klass,'__slots__')]
        
        all_slots = []
        for klass in classes:
            all_slots+=klass.__slots__
        
        state = {}
        for slot in all_slots:
            state[slot] = getattr(self,slot)

        return state


    def __setstate__(self,state):
        """See __getstate__()"""
        for (k,v) in state.items():
            setattr(self,k,v)    



class ParameterizedObjectMetaclass(type):
    """
    The metaclass of ParameterizedObject (and all its descendents).

    The metaclass overrides type.__setattr__ to allow us to set
    Parameter values on classes without overwriting the attribute
    descriptor.  That is, for a ParameterizedObject of type X with a
    Parameter y, the user can type X.y=3, which sets the default value
    of Parameter y to be 3, rather than overwriting y with the
    constant value 3 (and thereby losing all other info about that
    Parameter, such as the doc string, bounds, etc.).

    The __init__ method is used when defining a ParameterizedObject
    class, usually when the module where that class is located is
    imported for the first time.  That is, the __init__ in this
    metaclass initializes the *class* object, while the __init__
    method defined in each ParameterizedObject class is called for
    each new instance of that class.

    Additionally, a class can declare itself abstract by having an
    attribute _abstract_class_name set equal to its class name
    (e.g. PatternGenerator is abstract, and has
    _abstract_class_name='PatternGenerator').

    The 'abstract' attribute can be used to find out if a class
    is abstract or not.
    """
    abstract = property(lambda self: self.__is_abstract())

    # The other methods get_param_descriptor and print_param_defaults
    # could perhaps be made into static functions, because all they
    # (appear to) do is to provide a way to call the functions without
    # having a specific object available.  Perhaps they do something
    # else that requires them to be in the metaclass, though?
    
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
            self.__param_inheritance(param_name,param)


    def __is_abstract(self):
        """
        Return True if this class has an __abstract_class_name attribute,
        and it's equal to this class' __name__. Otherwise, return False.

        Allows detection of abstract classes, since a concrete subclass
        of an abstract class will have a name not equal to the
        __abstract_class_name.
        """
        if hasattr(self,'_abstract_class_name') and self.__name__==self._abstract_class_name:
            return True
        else:
            return False


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
                self.__param_inheritance(attribute_name,value)
            else:
                print ("Warning: Setting non-Parameter class attribute %s.%s = %s "
                       % (self.__name__,attribute_name,`value`))

                
    def __param_inheritance(self,param_name,param):
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
        # get all relevant slots (i.e. slots defined in all superclasses of
        # this parameter)
        slots = {}
        for p_class in classlist(type(param)):
            if hasattr(p_class,'__slots__'):
                slots.update(dict.fromkeys(p_class.__slots__))

        for slot in slots.keys():
            superclasses = iter(classlist(self)[::-1])

            # Search up the hierarchy until param.slot (which
            # has to be obtained using getattr(param,slot))
            # is not None, or we run out of classes to search.
            #
            # CEBALERT: there's probably a better way than while
            # and an iterator, but it works.
            while getattr(param,slot)==None:
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
                print self.__name__+'.'+key, '=', repr(val.default)


    def classparams(self):
        """
        Return the Parameters of this class as the
        dictionary {name: Parameter}, where Parameter
        is the Parameter object rather than its value.

        Includes Parameters from this class and its
        superclasses.
        """
        paramdict = {}
        for class_ in classlist(self):
            for name,val in class_.__dict__.items():
                if isinstance(val,Parameter):
                    paramdict[name] = val
        return paramdict



# JABALERT: Only partially achieved so far -- objects of the same
# type and parameter values are treated as different, so anything
# for which instantiate == True is reported as being non-default.
# Note that this module-level Parameter won't actually do most 
# of the things a Parameter does, but using a Parameter here
# should be more readable anyway.
script_repr_suppress_defaults=Parameter(True, hidden=True, doc="""
    Whether script_repr should avoid reporting the values of parameters
    that are just inheriting their values from the class defaults.""")
    

class ParameterizedObject(object):
    """
    Base class for named objects that support Parameters and message formatting.
    
    Automatic object naming: Every ParameterizedObject has a name
    parameter.  If the user doesn't designate a name=<str> argument
    when constructing the object, the object will be given a name
    consisting of its class name followed by a unique 5-digit number.
    
    Automatic parameter setting: The ParameterizedObject __init__
    method will automatically read the list of keyword parameters.  If
    any keyword matches the name of a Parameter (see Parameter class)
    defined in the object's class or any of its superclasses, that
    parameter in the instance will get the value given as a keyword
    argument.  For example:
    
      class Foo(ParameterizedObject):
         xx = Parameter(default=1)
    
      foo = Foo(xx=20)
    
    in this case foo.xx gets the value 20.
    
    Message formatting: Each ParameterizedObject has several methods
    for optionally printing output according to the current 'print
    level', such as SILENT, WARNING, MESSAGE, VERBOSE, or DEBUG.  Each
    successive level allows more messages to be printed.  For example,
    when the level is VERBOSE, all warning, message, and verbose
    output will be printed.  When it is WARNING, only warnings will be
    printed.  When it is SILENT, no output will be printed.
    
    For each level (except SILENT) there's an associated print method:
    ParameterizedObject.warning(), .message(), .verbose(), and .debug().
    
    Each line printed this way is prepended with the name of the
    object that printed it.  The ParameterizedObject parameter
    print_level, and the module global variable min_print_level
    combine to determine what gets printed.  For example, if foo is a
    ParameterizedObject:
    
       foo.message('The answer is',42)
    
    is equivalent to:
    
       if max(foo.print_level,base.min_print_level) >= MESSAGE:
           print foo.name+':', 'The answer is', 42
    """

    __metaclass__ = ParameterizedObjectMetaclass


    name           = Parameter(default=None,doc="String identifier for this object.")
    ### JABALERT: Should probably make this an Enumeration instead.
    print_level = Parameter(default=MESSAGE,hidden=True)

    
    def __init__(self,abstract_class=None,**params):
        """
        Initialize this ParameterizedObject.

        The values of parameters can be supplied as keyword arguments
        to the constructor (using parametername=parametervalue); these
        values will override the class default values for this one
        instance.

        If no 'name' parameter is supplied, self.name defaults to a
        gensym formed from the object's type name and a unique number.
        """
        global object_count

        # Flag that can be tested to see if e.g. constant Parameters
        # can still be set
        self.initialized=False

        self.__generate_name()
        
        self.__setup_params(**params)
        object_count += 1

        self.nopickle = []
        self.debug('Initialized',self)

        self.initialized=True


    def __generate_name(self):
        """
        Sets name to a gensym formed from the object's type name and a unique number.
        """
        self.name = '%s%05d' % (self.__class__.__name__ ,object_count)


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


    def script_repr(self,imports={},prefix="    "):
        """
        Variant of __repr__ designed for generating a runnable script.

        May replace __repr__ at some point, so that the default representation
        is runnable.
        """
        # Suppresses automatically generated names and print_levels.
        #
        # JABHACKALERT: Dynamic parameters are currently silently
        # reported as their current value; they should instead get a
        # representation that allows them to be regenerated.
        settings=[]
        for name,val in self.get_param_values(onlychanged=script_repr_suppress_defaults):
            if name == 'name' and re.match('^'+self.__class__.__name__+'[0-9]+$',val):
                rep=None
            elif name == 'print_level':
                rep=None
            elif isinstance(val,ParameterizedObject):
                rep=val.script_repr(imports=imports,prefix=prefix+"    ")
            elif isinstance(val,list):
                result=[]
                for i in val:
                    if hasattr(i,'script_repr'):
                        result.append(i.script_repr(imports=imports,prefix=prefix+"    "))
                    else:
                        result.append(repr(i))
                rep=','.join(result)
            else:
                rep=repr(val)
            if rep is not None:
                settings.append('%s=%s' % (name,rep))

        # Generate import statement
        cls = self.__class__.__name__
        mod = self.__module__
        imports[mod+'.'+cls]="from %s import %s" % (mod,cls)

        return self.__class__.__name__ + "(" + (",\n"+prefix).join(settings) + ")"

        
    def __str__(self):
        """Return a short representation of the name and class of this object."""
        return "<%s %s>" % (self.__class__.__name__,self.name)


    def __db_print(self,level=NORMAL,*args):
        """
        Print each of the given args iff print_level or
        self.db_print_level is greater than or equal to the given
        level.
        """
        if level <= max(min_print_level,self.print_level):
            s = ' '.join([str(x) for x in args])
            print "%s: %s" % (self.name,s)
        sys.stdout.flush()


    def warning(self,*args):
        """Print the arguments as a warning."""
        self.__db_print(WARNING,"Warning:",*args)

    def message(self,*args):
        """Print the arguments as a message."""
        self.__db_print(MESSAGE,*args)
        
    def verbose(self,*args):
        """Print the arguments as a verbose message."""
        self.__db_print(VERBOSE,*args)
        
    def debug(self,*args):
        """Print the arguments as a debugging statement."""
        self.__db_print(DEBUG,*args)


    def __setup_params(self,**params):
        """
        Initialize default and keyword parameter values.

        First, ensures that all Parameters with 'instantiate=True'
        (typically used for mutable Parameters) are copied directly
        into each object, to ensure that there is an independent copy
        (to avoid strange aliasing errors).  Then sets each of the
        keyword arguments, warning when any of them are not defined as
        parameters.
        """
        # Deepcopy all 'instantiate=True' parameters
        for class_ in classlist(type(self)):
            for (k,v) in class_.__dict__.items():
                if isinstance(v,Parameter) and v.instantiate:
                    parameter_name = v.get_name(self) 
                    new_object = copy.deepcopy(v.default)
                    self.__dict__[parameter_name]=new_object

                    # a new ParameterizedObject needs a new name
                    # CEBHACKALERT: this will write over any name given
                    # to the original object.
                    if isinstance(new_object,ParameterizedObject):
                        global object_count
                        object_count+=1
                        new_object.__generate_name()
                    
        for name,val in params.items():
            desc,desctype = self.__class__.get_param_descriptor(name)
            if desc:
                self.debug("Setting param %s ="%name, val)
            else:
                self.warning("CANNOT SET non-parameter %s ="%name, val)
            setattr(self,name,val)


    def _check_params(self,params):
        """
        Print a warning if params contains something that is
        not a Parameter of this object.

        Typically invoked by a __call__() method that accepts keyword
        arguments for parameter setting.
        """
        for item in params:
            if item not in self.params():
                self.warning("'%s' was ignored (not a Parameter)."%item)


    def get_param_values(self,onlychanged=False):
        """Return a list of name,value pairs for all Parameters of this object"""
        vals = []
        for name,val in self.params().items():
            value = self.inspect_value(name)
            if (not onlychanged or value != val.default):
                vals.append((name,value))

        vals.sort(key=lambda x:x[0])
        return vals


    def inspect_value(self,name):
        """
        Return the value of the specified parameter without modifying it.

        Same as getattr() except for DynamicNumbers
        """
        from parameterclasses import DynamicNumber
        
        # Avoids getting a new value for a DynamicNumber. Otherwise,
        # all that would be here is value=getattr(self,name).)
        k = "_%s_param_value"%(name)
        if k in self.__dict__:
            if isinstance(self.__dict__[k],DynamicNumber):
                value = self.__dict__[k].last_value
            else:
                value = getattr(self,name)
        else:
            value = getattr(self,name)                    

        return value


    def print_param_values(self):
        for name,val in self.get_param_values():
            print '%s.%s = %s' % (self.name,name,val)


    def __getstate__(self):
        """
        Save the object's state: return a dictionary that is a shallow
        copy of the object's __dict__, except that entries in __dict__
        which are Parameters get deep copied.

        (i.e. we assume mutable objects are in Parameters.)

        ParameterizedObjects always have a __dict__ and do not have __slots__.
        """
        # shallow copy the __dict__ because we change some entries
        state = self.__dict__.copy()

        # deep copy Parameters; overwrites their original shallow copies 
        for (k,v) in self.__dict__.items():
            if isinstance(v,Parameter):
                state[k] = copy.deepcopy(v)

        return state


    def __setstate__(self,state):
        """
        Restore objects from the state dictionary to this object.

        During this process the object is considered uninitialized.
        """
        self.initialized=False
        
        for k,v in state.items():
            setattr(self,k,v)
            
        self.initialized=True


    def params(self):
        """
        See ParameterizedObjectMetaClass.classparams(),
        which this method calls on the class of this object.
        """
        return type(self).classparams()


    def reset_params(self):
        """
        Return Parameters with modifiable values to the class defaults.
        """
        for (attr_name,param) in self.params().items():
            # CEBALERT: name should be Constant - should stop faking it
            # everywhere (see current task list).
            if param.constant or attr_name=="name": # CB:what about instantiate & dynamic?
                pass
            else:
                setattr(self,attr_name,param.default)



def print_all_param_defaults():
    print "_______________________________________________________________________________"
    print ""
    print "                           Parameter Default Values"
    print ""
    classes = descendents(ParameterizedObject)
    classes.sort(key=lambda x:x.__name__)
    for c in classes:
        c.print_param_defaults()
    print "_______________________________________________________________________________"





import __main__
import inspect
class PicklableClassAttributes(object):
    """
    Supports pickling of ParameterizedObject class attributes for a given module.

    When requested to be pickled, stores a module's PO classes' attributes,
    and any given startup_commands. On unpickling, executes the startup
    commands and sets the class attributes.
    """
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
                    ParameterizedObject().warning("%s (type %s) has source in __main__; it will only be found on unpickling if the class is explicitly defined (e.g. by running the same script first) before unpickling."%(k,type(v)))

        
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
            
            # from "topo.base.parameter.Parameter", we want "topo.base.parameter"
            module_path = class_name[0:class_name.rindex('.')]
            exec 'import '+module_path in __main__.__dict__
            
            # now restore class Parameter values
            for p_name,p in state.items():
                __main__.__dict__['val'] = p
                try:
                    exec 'setattr('+class_name+',"'+p_name+'",val)' in __main__.__dict__
                except:
                    ParameterizedObject().warning('Problem restoring parameter %s=%s for class %s; name may have changed since the snapshot was created.' % (p_name,repr(p),class_name))


    # CEBALERT: might could be simplified
    # (in addition to simplifications that could be made now this is a method rather than
    # a standalone function).
    def get_PO_class_attributes(self,module,class_attributes,processed_modules,exclude=()):
        """
        Recursively search module and get attributes of ParameterizedObject classes within it.

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
                if isinstance(v,type) and issubclass(v,ParameterizedObject):

                    # Note: we take the class name as v.__name__, not k, because
                    # k might be just a label for the true class. For example,
                    # if Topographica falls back to the unoptimized components,
                    # k could be "CFPRF_DotProduct_opt", but v.__name__
                    # - and the actual class - is "CFPRF_DotProduct". It
                    # is correct to set the attributes on the true class.
                    full_class_path = v.__module__+'.'+v.__name__
                    class_attributes[full_class_path] = {}
                    # POs always have __dict__, never slots
                    for (name,obj) in v.__dict__.items():
                        if isinstance(obj,Parameter):
                            class_attributes[full_class_path][name] = obj

