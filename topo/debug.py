"""
Debugging module.

Implements the Debuggable mixin class, and sets debugging levels.

 $Id$
"""
import sys
from params import *
from pprint import pprint

SILENT  = 0
NORMAL  = 100
VERBOSE = 200
DEBUG   = 300

print_level = NORMAL
object_count = 0

class Debuggable:
    """
    A mixin class for debuggable objects.  Makes sure every debuggable
    object has a name,, and __repr__(), __str__(), and db_print() methods.
    """

    name = None
    db_print_level = NORMAL
    
    def __init__(self,**config):
        """
        If **config doesn't contain a 'name' parameter, set self.name
        to a gensym formed from the object's type name and a unique number.
        """        
        global object_count

        self.name = '%s%05d' % (self.__class__.__name__ ,object_count)
        setup_params(self,Debuggable,**config)
        object_count += 1

        self.db_print("Initialized " + `self`,VERBOSE)

    def __repr__(self):
        """
        Returns '<self.name>'.
        """
        return "<%s>" % self.name

    def __str__(self):
        """
        Returns 'self.name'.
        """
        return self.name

    def db_print(self,str,level=NORMAL):
        """
        Iff print_level or self.db_print_level is greater than level,
        print str.
        """
        if level <= max(print_level,self.db_print_level):
            print "%s: %s" % (self.name,str)
        sys.stdout.flush()

    def db_pprint(self,str,level=NORMAL):
        """
        Like db_print, but it uses pprint instead of print.
        """
        if level <= max(print_level,self.db_print_level):
            pprint("%s: %s" % (self.name,str))
        sys.stdout.flush()
    
