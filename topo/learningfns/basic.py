"""
Basic learning functions.

A LearningFn (e.g. Hebbian) applies to one ConnectionField.


$Id$
"""
__version__ = "$Revision$"

from topo.base.functionfamilies import LearningFn

# Imported here so that all learning functions will be in the same package
from topo.base.functionfamilies import Hebbian



