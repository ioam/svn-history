"""
A family of response functions for CFProjections.

These function objects compute a response matrix when given an input
pattern and a set of ConnectionField objects.

Any new response functions added to this directory will automatically
become available for any model.

$Id$
"""

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
