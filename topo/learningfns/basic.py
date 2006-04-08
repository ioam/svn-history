"""
Basic learning functions for CFProjections.

Learning functions come in two varieties: LearningFunction, and
CFProjectionLearningFunction.  A LearningFunction (e.g. Hebbian)
applies to one ConnectionField, and is used with
GenericCFProjectionLearningFn to apply learning to an entire
CFProjection.  GenericCFProjectionLearningFn is one example of a
CFProjectionLearningFunction; these work with the entire Projection at
once.  Some optimizations can only be applied at the
CFProjectionLearningFn level, so there are other
CFProjectionLearningFns beyond GenericCFProjectionLearningFn.

$Id$
"""
__version__ = "$Revision$"

# CEBHACKALERT: file to be renamed projfns.py; basic.py will contain
# the single-cf learning functions.

from topo.base.parameterclasses import Number
from topo.base.connectionfield import LearningFn

# Imported here so that all CFProjectionLearningFns will be in the same package
from topo.base.connectionfield import Hebbian,CFProjectionIdentityLearningFn,CFProjectionGenericLearningFn

