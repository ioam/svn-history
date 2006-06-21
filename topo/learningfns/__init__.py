"""
A family of function objects for changing a set of weights over time.

Learning functions come in two varieties: LearningFunction, and
CFPLearningFunction.  A LearningFunction (e.g. Hebbian) applies to one
set of weights, typically from one ConnectionField.  To apply learning
to an entire CFProjection, a LearningFunction can be plugged in to
CFPLF_Plugin.  CFPLF_Plugin is one example of a CFPLearningFunction,
which is a function that works with the entire Projection at once.
Some optimizations and algorithms can only be applied at the full
CFPLearningFn level, so there are other CFPLearningFns beyond
CFPLF_Plugin.

Any new learning functions added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'
# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
