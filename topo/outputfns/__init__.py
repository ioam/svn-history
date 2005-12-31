"""
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



import topo
from topo.base.projection import OutputFunctionParameter
def make_classes_from_all_imported_modules_available():
    """
    Add all OutputFunction classes from the currently imported modules in
    the topo.outputfns namespace to the list of available OutputFunctions.

    See topo.base.parameter.ClassSelectorParameter.range().
    """
    OutputFunctionParameter.packages.append(topo.outputfns)

