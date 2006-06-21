"""
Projection classes.

A Projection is a connection between two Sheets, generally implemented
as a large set of ConnectionFields.

Any new Projection classes added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
