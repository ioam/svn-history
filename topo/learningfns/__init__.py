"""
Learning functions come in two varieties: LearningFunction, and
CFProjectionLearningFunction.  A LearningFunction (e.g. Hebbian)
applies to one ConnectionField, and is used with
GenericCFPLearningFn to apply learning to an entire
CFProjection.  GenericCFPLearningFn is one example of a
CFProjectionLearningFunction; these work with the entire Projection at
once.  Some optimizations can only be applied at the
CFPLearningFn level, so there are other
CFPLearningFns beyond GenericCFPLearningFn.

Any new learning functions added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'
# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
