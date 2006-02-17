"""
A family of response functions for CFProjections.

These function objects compute a response matrix when given an input
pattern and a set of ConnectionField objects.

Any new response functions added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]


import topo
from topo.base.connectionfield import ResponseFunctionParameter
def make_classes_from_all_imported_modules_available():
    """
    Add all ResponseFunction classes from the currently imported modules in
    the topo.learningfns namespace to the list of available ResponseFunctions.

    See topo.base.parameterclasses.ClassSelectorParameter.range().
    """
    ResponseFunctionParameter.packages.append(topo.responsefns)
