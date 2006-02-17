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


import topo
from topo.base.patterngenerator import PatternGeneratorParameter
def make_classes_from_all_imported_modules_available():
    """
    Add all PatternGenerator classes from the currently imported modules in
    the topo.patterns namespace to the list of available PatternGenerators.

    See topo.base.parameterclasses.ClassSelectorParameter.range().
    """
    PatternGeneratorParameter.packages.append(topo.patterns)



# CEBHACKALERT: Parameters such as density need to be set the same in the others that
# could be chosen...or else the pattern_present stuff needs to do things like install
# the right density and bounds...
