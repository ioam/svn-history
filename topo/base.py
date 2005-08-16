"""
Topographica Base

Implements the Topographica generic base class TopoObject.  This class
encapsulates generic functions of all Topographica classes, such as
automatic parameter setting, message output, etc.

$Id$
"""

import sys

### JABHACKALERT!
###
### Should this be rewritten to avoid 'import *'?
###
from params import *
from pprint import pprint

SILENT  = 0
WARNING = 50
NORMAL  = 100
MESSAGE = NORMAL
VERBOSE = 200
DEBUG   = 300

min_print_level = NORMAL
object_count = 0


ABOUT_TEXT = """
Pre-release version of Topographica; please do not trust this version
of the code unless you have verified it yourself.  An updated version
may be available from topographica.org.

Copyright 2005 James A. Bednar, Yoonsuck Choe, Judah B.
De Paula, Jefferson Provost, Joseph Reisinger, and Yiu Fai Sit.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details.
"""

def about():
    """Print release and licensing information."""
    print ABOUT_TEXT

class TopoMetaclass(type):

    """
    The metaclass of TopoObject (and all its descendents).  The
    metaclass overrides type.__setattr__ to allow us to set Parameter
    values on classes without overwriting the attribute descriptor.
    """

    def __setattr__(self,name,value):
        from copy import copy
        desc,class_ = self.get_param_descriptor(name)
        if desc and not isinstance(value,Parameter):
            # If the attribute already has a Parameter descriptor,
            # assign the value to the descriptor.
            if class_ != self:
                type.__setattr__(self,name,copy(desc)) 
            self.__dict__[name].__set__(None,value)            
        else:
            # in all other cases set the attribute normally
            if not isinstance(value,Parameter):
                print (" ##WARNING## Setting non-parameter class attribute %s.%s = %s "
                       % (self.__name__,name,`value`))
                                   
            type.__setattr__(self,name,value)
        
    def get_param_descriptor(self,param_name):
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
    (see params.py) defined in the object's class or any of its
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


    name           = Parameter(default=None)
    print_level = Parameter(default=MESSAGE)
    
    def __init__(self,**config):
        """
        If **config doesn't contain a 'name' parameter, set self.name
        to a gensym formed from the object's type name and a unique number.
        """        
        global object_count

        self.name = '%s%05d' % (self.__class__.__name__ ,object_count)
        self.__setup_params(**config)
        object_count += 1

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
        Iff print_level or self.db_print_level is greater than level,
        print str.
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

    def __getstate__(self):
        import copy
        try:
            state = copy.copy(self.__dict__)
            for x in self.nopickle:
                if x in state:
                    del(state[x])
                else:
                    desc,cls = type(self).get_param_descriptor(x)
                    if desc and (desc.name in state):
                        del(state[desc.name])
                
        except AttributeError,err:
            pass

        for c in classlist(type(self)):
            try:
                for k in c.__slots__:
                    state[k] = getattr(self,k)
            except AttributeError:
                pass
        return state

    def __setstate__(self,state):
        for k,v in state.items():
            setattr(self,k,v)
        self.unpickle()

    def unpickle(self):
        pass



    def get_param_dict(self,**config):
        paramdict = {}
        for class_ in classlist(type(self)):
            for name,val in class_.__dict__.items():
                if isinstance(val,Parameter):
                    paramdict[name] = getattr(self,name)
        return paramdict

def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) class_,
    from least- to most-specific.
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
    out.reverse()
    return out

def descendents(class_):
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

    
    
def print_all_param_defaults():
    print "===== Topographica Parameter Default Values ====="
    classes = descendents(TopoObject)
    classes.sort(key=lambda c:c.__name__)
    for c in classes:
        c.print_param_defaults()
    print "==========================================="

    
