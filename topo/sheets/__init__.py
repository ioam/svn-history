"""
Sheet classes.

A Sheet is a two-dimensional arrangement of processing units,
typically modeling a neural region or a subset of cells in a neural
region.  Any new Sheet classes added to this directory will
automatically become available for any model.

$Id$
"""

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
