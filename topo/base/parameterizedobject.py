"""
Generic support for objects with full-featured Parameters and
messaging.  Potentially useful for any large Python program that needs
user-modifiable object attributes.

$Id$
"""
__version__='$Revision$'

import sys
import copy


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

### JABALERT: The documentation for Dynamic needs to be moved out of here,
### with only a general mention that dynamic subclasses can be implemented,
### unless support for Dynamic is moved into this file.
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
       keyword arguments (as in'def __init__(self,**params):'), and
       then each class calls its superclass (as in
       'super(Foo,self).__init__(**params)') so that the
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
    # persistent storage pickling), and these are implemented for
    # ParameterizedObjects.
    # 
    # Note that the actual value of a Parameter is not stored in the
    # Parameter object itself, but in the owning
    # ParameterizedObject'ss __dict__.
    # 
    # Note about pickling: Parameters are usually used inside
    # ParameterizedObjects, and so can be pickled even though
    # Parameter has no explicit support for pickling (usually if a
    # class has __slots__ it can't be pickled without additional
    # support: see the Pickle module documentation).
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

    # CEBHACKALERT: I think this can be made simpler
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
        self._name = None
        self.hidden=hidden
        self.precedence = precedence
        Parameter.count += 1
        self.default = default
        self.doc = doc
        self.constant = constant

        # CEBHACKALERT: constants must be instantiated: should this
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
        ParameterizedObject.
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
    """

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


    ### JABALERT: It might make sense to make the name be visible (not hidden) by default.
    name           = Parameter(default=None,hidden=True)
    print_level = Parameter(default=MESSAGE,hidden=True)
    
    def __init__(self,**config):
        """
        If **config doesn't contain a 'name' parameter, self.name defaults
        to a gensym formed from the object's type name and a unique number.
        """        
        global object_count

        # Flag that can be tested to see if e.g. constant Parameters
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

        # first get class-level attributes

        # CEBHACKALERT: I think this can be re-written properly
        # now...traversing the class hierarchy ought to be possible when
        # e.g. lambdas aren't hidden away in DynamicNumbers. Currently
        # this code avoids the problem because unpicklable things
        # are never reached.
        c = self.__class__
        for entry in c.__dict__.keys():
            if isinstance(c.__dict__[entry], Parameter): 
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
        """
        Restore objects from the state dictionary to this object.

        During this process the object is considered uninitialized.
        """
        del state['initialized']  # (we restore this attribute ourselves)
        self.initialized=False
        
        for k,v in state.items():
            setattr(self,k,v)
            
        self.unpickle()
        self.initialized=True


    def unpickle(self):
        pass

    # CEBHACKALERT: this is used once, under a HACKALERT. It could be
    # deleted: when most external objects want a ParameterizedObject's
    # Parameters, they don't want them all and usually take some
    # subset. So using this function would be a little wasteful,
    # because two loops would be required in those cases.  But, to a
    # user of ParameterizedObject (who doesn't use the rest of
    # Topographica) this would be a useful function - so I think it
    # should be kept and this HACKALERT removed.
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
    print "========= Parameter Default Values ========"
    classes = descendents(ParameterizedObject)
    classes.sort(key=lambda x:x.__name__)
    for c in classes:
        c.print_param_defaults()
    print "==========================================="

    


def class_parameters(parameterized_class):
    """
    Return the non-hidden Parameters of the specified ParameterizedObject class
    as {parameter_name: parameter}.

    E.g. for a class that has one Parameter x=Number(), this function returns
    {'x':<topo.base.parameterclasses.Number object at ...>}

    The specified class must be of type ParameterizedObject.
    """
    assert isinstance(parameterized_class, type)

    # Create the object so that Parameters of any superclasses are also present.
    parameterized_obj = parameterized_class()
    
    if not isinstance(parameterized_obj,ParameterizedObject):
        raise TypeError("Can only get Parameters for a class derived from ParameterizedObject.")
    
    parameters = [(parameter_name,parameter)
                  for (parameter_name,parameter)
                  in parameterized_obj.get_paramobj_dict().items()
                  if not parameter.hidden
                 ]
                 
    return dict(parameters)



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
