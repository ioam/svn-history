"""
EventProcessor classes.

An EventProcessor is an object that the Simulator is aware of, and can
accept simulator Events. EventProcessors can also generate Events, and
will presumably do some computation as well.  Most EventProcessors
will be in other more specific packages, such as topo.sheets; those
here are the remaining uncategorized EventProcessors.  Any new
EventProcessors classes added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'
# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]
