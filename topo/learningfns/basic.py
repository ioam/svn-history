"""
Basic learning functions for CFProjections.

Learning functions come in two varieties: LearningFunction, and
CFLearningFunction.  A LearningFunction (e.g. Hebbian) applies to one
ConnectionField, and is used with GenericCFLF to apply learning to an
entire CFProjection.  GenericCFLF is one example of a
CFLearningFunction; these work with the entire Projection at once.
Some optimizations can only be applied at the CFLearningFunction
level, so there are other CFLearningFunctions beyond GenericCFLF.

$Id$
"""
__version__ = "$Revision$"

from topo.base.parameterclasses import Number
from topo.base.connectionfield import LearningFunction

# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import Hebbian,IdentityCFLF,GenericCFLF

