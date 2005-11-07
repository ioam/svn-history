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
