"""
A family of learning functions for CFProjections.

These function objects compute a new set of ConnectionFields when given an input
and output pattern and a set of ConnectionField objects.

Any new learning functions added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'
# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]


import topo
from topo.base.connectionfield import LearningFunctionParameter
def make_classes_from_all_imported_modules_available():
    """
    Add all LearningFunction classes from the currently imported modules in
    the topo.learningfns namespace to the list of available LearningFunctions.

    See topo.base.parameterclasses.ClassSelectorParameter.range().
    """
    LearningFunctionParameter.packages.append(topo.learningfns)
