"""
Simple transfer functions.

These functions should work for either scalar or array arguments.  Can
easily be extended to include Sigmoid or other functions.

$Id$
"""

import Numeric
from Numeric import clip
from topo.base.object import TopoObject
from topo.base.parameter import Number
from topo.base.utils import TransferFunction,Identity

class PiecewiseLinear(TransferFunction):
    """ 
    Piecewise-linear transfer function with lower and upper thresholds
    as constructor parameters.
    """
    lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
    upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    
    def __init__(self,**params):
        super(PiecewiseLinear,self).__init__(**params)

    def __call__(self,x):
        fact = 1.0/(self.upper_bound-self.lower_bound)
        x = (x-self.lower_bound)*fact
        return Numeric.clip(x,0.0,1.0)

