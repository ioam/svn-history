"""
Topographica Base

Implements the Topographica generic base class TopoObject.  This class
encapsulates generic functions of all Topographica classes, such as
automatic parameter setting, message output, etc.

$Id$
"""
__version__='$Revision$'

import sys
import copy


from parameter import Parameter, Constant
from utils import classlist,descendents
from pprint import pprint

SILENT  = 0
WARNING = 50
NORMAL  = 100
MESSAGE = NORMAL
VERBOSE = 200
DEBUG   = 300

min_print_level = NORMAL
object_count = 0


class TopoMetaclass(type):
    """
    The metaclass of TopoObject (and all its descendents).

    The metaclass overrides type.__setattr__ to allow us to set
    Parameter values on classes without overwriting the attribute
    descriptor.  That is, for a TopoObject of type X with a Parameter
    y, the user can type X.y=3, which sets the default value of
    Parameter y to be 3, rather than overwriting y with the constant
    value 3 (and thereby losing all other info about that Parameter,
    such as the doc string, bounds, etc.)

    The other methods get_param_descriptor and print_param_defaults
    could perhaps be made into static functions, because all they
    (appear to) do is to provide a way to call the functions without
    having a specific object available.  Perhaps they do something
    else that requires them to be in the metaclass, though?

    The __init__ method is used when defining a TopoObject class,
    usually when the module where that class is located is imported
    for the first time.  That is, the __init__ in this metaclass
    initializes the *class* object, while the __init__ method defined
    in each TopoObject class is called for each new instance of that
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
        TopoObject superclasses as described in __param_inheritance().
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
        Look for Parameter values in superclasses of this TopoObject.

        Ordinarily, when a Python object is instantiated, attributes
        not given values in the constructor will inherit the value
        given in the object's class, or in its superclasses.  For
        Parameters owned by TopoObjects, we have implemented an
        additional level of default lookup, should this ordinary
        lookup return only None.

        In such a case, i.e. when no non-None value was found for a
        Parameter by the usual inheritance mechanisms, we explicitly
        look for Parameters with the same name in superclasses of this
        TopoObject, and use the first such value that we find.

        The goal is to be able to set the default value (or other
        slots) of a Parameter within a TopoObject, just as we can set
        values for non-Parameter objects in TopoObjects, and have the
        values inherited through the TopoObject hierarchy as usual.
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


class TopoObject(object):
    """
    Base class for most Topographica objects, providing automatic
    object naming, automatic parameter setting, and message formatting
    facilities:
    
    - Automatic object naming -
    
    Every TopoObject has a name parameter.  If the user doesn't designate
    a name=<str> argument when constructing the object, the object will be
    given a name consisting of its class name followed by a unique 5-digit
    number. 
    
    - Automatic parameter setting -
    
    The TopoObject __init__ method will automatically read the list of
    keyword parameters.  If any keyword matches the name of a Parameter
    (see parameter.py) defined in the object's class or any of its
    superclasses, that parameter in the instance will get the value given
    as a keyword argument.  For example:
    
      class Foo(TopoObject):
         xx = Parameter(default=1)
    
      foo = Foo(xx=20)
    
    in this case foo.xx gets the value 20.
    
    - Message formatting -
    
    Each TopoObject has several methods for optionally printing output
    according to the current 'print level'.  The print levels are SILENT,
    WARNING, MESSAGE, VERBOSE, and DEBUG.  Each successive level allows
    more messages to be printed.  For example, when the level is VERBOSE,
    all warning, message, and verbose output will be printed.  When it is
    WARNING, only warnings will be printed.  When it is SILENT, no output
    will be printed.
    
    For each level (except SILENT) there's an associated print method:
    TopoObject.warning(), .message(), .verbose(), and .debug().
    
    Each line printed this way is prepended with the name of the object
    that printed it.  The TopoObject parameter print_level, and the module
    global variable min_print_level combine to determine what gets
    printed.  For example, if foo is a TopoObject:
    
       foo.message('The answer is',42)
    
    is equivalent to:
    
       if max(foo.print_level,base.min_print_level) >= MESSAGE:
           print foo.name+':', 'The answer is', 42
    """

    __metaclass__ = TopoMetaclass


    ### It might make sense to make the name be visible (not hidden) by default.
    name           = Parameter(default=None,hidden=True)
    print_level = Parameter(default=MESSAGE,hidden=True)
    
    def __init__(self,**config):
        """
        If **config doesn't contain a 'name' parameter, set self.name
        to a gensym formed from the object's type name and a unique number.
        """        
        global object_count

        self.name = '%s%05d' % (self.__class__.__name__ ,object_count)
        self.__setup_params(**config)
        object_count += 1

        self.nopickle = []
        self.verbose('Initialized',self)

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
    classes = descendents(TopoObject)
    classes.sort(key=lambda x:x.__name__)
    for c in classes:
        c.print_param_defaults()
    print "==========================================="

    
