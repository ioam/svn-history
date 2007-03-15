"""
A family of function objects for transforming one set of coordinates into
another.

Coordinate mapper functions are useful for defining magnifications and
other kinds of transformations on sheet coordinates, e.g. for defining
retinal magnification using a CFProjection.  A CoordinateMapperFn
(e.g. MagnifyingMapper, applied to an (x,y) pair and returns a new
(x,y) pair.  To apply a mapping to a CF projection, set the
CFProjection's coord_mapper parameter to an instance of the desired
CoordinateMapperFn.

$Id$
"""
__version__='$Revision$'

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
