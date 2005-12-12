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


# CEBHACKALERT: intermediate state (see HACKALERT in topo/base/utils.py)
import topo
from topo.base.projection import OutputFunction
from topo.base.parameter import PackageParameter
class OutputFunctionParameter(PackageParameter):
    """
    """
    def __init__(self,default=None,doc='',**params):
        """
        """
        super(OutputFunctionParameter,self).__init__(topo.outputfns,OutputFunction,default=default,doc=doc,**params)        

