"""
Transfer functions for computing activation patterns.

A transfer function is a mapping from a matrix into an identically
sized matrix (or, rarely, a scalar to a scalar).  Typical transfer
functions for neural networks are sigmoidal, linear, or piecewise
linear.  Any new transfer functions added to this directory will
automatically become available for any model.

$Id$
"""

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
