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


# CEBHACKALERT: see topo/outputfns/__init__.py
import topo
from topo.base.patterngenerator import PatternGenerator
from topo.base.parameter import PackageParameter
class PatternGeneratorParameter(PackageParameter):
    """
    """
    def __init__(self,default=None,doc='',**params):
        """
        """
        super(PatternGeneratorParameter,self).__init__(topo.patterns,PatternGenerator,default=default,doc=doc,**params)


# CEBHACKALERT: Parameters such as density need to be set the same in the others that
# could be chosen...or else the pattern_present stuff needs to do things like install
# the right density and bounds...
