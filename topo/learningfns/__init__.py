"""
Learning functions come in two varieties: LearningFunction, and
CFProjectionLearningFunction.  A LearningFunction (e.g. Hebbian)
applies to one ConnectionField, and is used with
GenericCFProjectionLearningFn to apply learning to an entire
CFProjection.  GenericCFProjectionLearningFn is one example of a
CFProjectionLearningFunction; these work with the entire Projection at
once.  Some optimizations can only be applied at the
CFProjectionLearningFn level, so there are other
CFProjectionLearningFns beyond GenericCFProjectionLearningFn.

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
from topo.base.cf import LearningFnParameter
def make_classes_from_all_imported_modules_available():
    """
    Add all LearningFunction classes from the currently imported modules in
    the topo.learningfns namespace to the list of available LearningFunctions.

    See topo.base.parameterclasses.ClassSelectorParameter.range().
    """
    LearningFnParameter.packages.append(topo.learningfns)
