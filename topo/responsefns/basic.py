"""
Basic response functions for CFProjections.

These function objects compute a response matrix when given an input
pattern and a set of ConnectionField objects.

$Id$
"""
__version__='$Revision$'

from topo.base.connectionfield import CFResponseFunction
from topo.base.parameter import Parameter
from topo.base.topoobject import TopoObject
from topo.misc.inlinec import inline, optimized

class CFDotProduct_Py(CFResponseFunction):
    """
    Dot-product response function.

    Written entirely in Python; see CFDotProduct for a much faster
    (but otherwise equivalent) version.
    """
    def __init__(self,**params):
        super(CFDotProduct_Py,self).__init__(**params)

    def __call__(self, cfs, input_activity, activity, strength, **params):
        rows,cols = activity.shape
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_tuple()
                X = input_activity[r1:r2,c1:c2]
        
                a = X*cf.weights
                activity[r,c] = sum(a.flat)
        activity *= strength
