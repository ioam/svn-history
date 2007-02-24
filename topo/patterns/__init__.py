"""
Objects capable of generating a two-dimensional array of values.

Such patterns can be used as input to a Sheet, as initial or fixed
weight patterns, or for any other purpose where a two-dimensional
pattern may be needed.  Any new PatternGenerator classes added to this
directory will automatically become available for any model.

$Id$
"""
__version__='$Revision$'

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]


# CB: temporarily hide the audio module until it works and is properly
# supported by the GUI etc.
__all__.remove('audio')
