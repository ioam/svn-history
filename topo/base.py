"""
Topographica Base

Implements the Topographica generic base class TopoObject.  This class
encapsulates generic functions of all Topographica classes, such as
automatic parameter setting, message output, etc.

=== FACILITIES PROVIDED ===

-Automatic object naming-

Every TopoObject has a name parameter.  If the user doesn't designate
a name=<str> argument when constructing the object, the object will be
given a name consisting of its class name followed by a unique 5-digit
number. 

-Automatic parameter setting-

The TopoObject __init__ method will automatically read the list of
keyword parameters.  If any keyword matches the name of a Parameter
(see params.py) defined in the object's class or any of its
superclasses, that parameter in the instance will get the value given
as a keyword argument.  For example:

  class Foo(TopoObject):
     xx = Parameter(default=1)

  foo = Foo(xx=20)

in this case foo.xx gets the value 20.

- Advanced output -

Each TopoObject has several methods for optionally printing output
according to the current 'print level'.  The print levels are SILENT,
WARNING, MESSAGE, VERBOSE, and DEBUG.  Each successive level allows
more messages to be printed.  For example, when the level is VERBOSE,
all warning, message, and verbose output will be printed.  When it is
WARNING, only warnings will be printed.  When it is SILENT, no output
will be printed.

For each level (except SILENT) there's an associated print method:
TopoObject.warning(), .message(), .verbose(), and .debug().

Each lined printed this way is prepended with the name of the object
that printed it.  The TopoObject parameter print_level, and the module
global variable min_print_level combine to determine what gets
printed.  For example, if foo is a TopoObject:

   foo.message('The answer is',42)

is equivalent to:

   if max(foo.print_level,base.min_print_level) >= MESSAGE:
       print foo.name+':', 'The answer is', 42

$Id$
"""

import sys
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

class TopoObject(object):
    """
    A mixin class for debuggable objects.  Makes sure every debuggable
    object has a name,, and __repr__(), __str__(), and db_print() methods.
    """

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
        """
        Traverse this object's family tree of classes discovering the
        Parameters in the class dictionary, and set parameters that
        are named in the config dictionary.
        """
        for class_ in classlist(type(self)):
            self.debug('setting params for ', class_)
            for name,val in class_.__dict__.items():
                if isinstance(val,Parameter):
                    try:
                        setattr(self,name,config[name])
                    except KeyError:
                        pass
            

def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) class_,
    from least- to most-specific.
    """
    assert type(class_) == type(object)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.append(x)
        for b in x.__bases__:
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]


if __name__ == '__main__':

    from pprint import pprint
    class A(TopoObject):
        a = Parameter('A Param')
    class B1(A):
        b1 = Parameter('B1 Param')
    class B2(A):
        b2 = Parameter('B2 Param')
    class C(B1,B2):
        c = Parameter('C Param')

    pprint(classlist(C))
    
    ob = C(a=1,b1=2,b2=3,c=4)
    
    
