"""
"""
__version__='$Revision$'

# CEBHACKALERT: should be able to remove this file.

# CEBHACKALERT: when a base class for PatternGeneratorParameter etc
# exists, consider making this a method of that class.
from inspect import ismodule
def find_classes_in_package(package,parentclass):
    """
    Return a dictionary containing all items of the type
    specified, owned by modules in the specified package.
    Only currently imported modules are searched, so
    the caller will first need to do 'from package import *'.
    Does not search packages contained within the specified
    package, only the top-level modules.

    Does not return the parentclass itself.
    """
    result = {}
    for v1 in package.__dict__.itervalues():
        if ismodule(v1):
            for v2 in v1.__dict__.itervalues():
                if (isinstance(v2,type)
                    and issubclass(v2,parentclass)
                    and v2 is not parentclass):
                    result[v2.__name__] = v2
    return result




