"""
Learning functions for Projections.


For example, CFProjectionLearningFunctions compute a new set of
ConnectionFields when given an input and output pattern and a set of
ConnectionField objects.

$Id$
"""
__version__ = "$Revision$"

# Imported here so that all ProjectionLearningFns will be in the same package
from topo.base.cf import CFProjectionIdentityLearningFn,CFProjectionGenericLearningFn

