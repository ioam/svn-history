"""
CEBHACKALERT: documentation here and in the other dirs needs to point out
projfns and basic.


A family of functions mapping from a value into another of the same shape.

A set of endomorphic functions, i.e., functions mapping from an object
into another of the same matrix shape.  These are useful for neuron
output functions, normalization of matrices, etc.

Any new output functions added to this directory will automatically
become available for any model.

$Id$
"""
__version__='$Revision$'

# Automatically discover all .py files in this directory. 
import re,os
__all__ = [re.sub('\.py$','',f) for f in os.listdir(__path__[0])
           if re.match('^[^_].*\.py$',f)]


# CEBHACKALERT: here and elsewhere, consider what things are made
# available. There used to be just OutputFn, now there is also
# CFOutputFn but for e.g. the GUI it's necessary to allow the
# relevant parameter to have its package list set. What I mean is,
# this is out of date and needs to be cleaned up.

import topo
from topo.base.projection import OutputFnParameter
def make_classes_from_all_imported_modules_available():
    """
    Add all OutputFn classes from the currently imported modules in
    the topo.outputfns namespace to the list of available OutputFunctions.

    See topo.base.parameterclasses.ClassSelectorParameter.range().
    """
    OutputFnParameter.packages.append(topo.outputfns)

