"""
Basic learning functions.

A LearningFunction (e.g. Hebbian) applies to one ConnectionField.


$Id$
"""
__version__ = "$Revision$"

from topo.base.connectionfield import LearningFn

# Imported here so that all CFProjectionLearningFns will be in the same package
from topo.base.connectionfield import Hebbian



