"""
Basic response functions for CFProjections.

These function objects compute a response matrix when given an input
pattern and a set of ConnectionField objects.

$Id$
"""
__version__='$Revision$'

from Numeric import zeros, Float, ravel

from topo.base.arrayutils import L2norm
from topo.base.connectionfield import CFResponseFunction
from topo.base.parameterclasses import Parameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.inlinec import inline, optimized

class CFDotProduct(CFResponseFunction):
    """
    Dot-product response function.

    Written entirely in Python; see CFDotProduct_opt1 for a much faster
    (but otherwise equivalent) version.
    """
    def __init__(self,**params):
        super(CFDotProduct,self).__init__(**params)

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


class CFEuclideanDistance(CFResponseFunction):
    """
    Euclidean-distance--based response function.
    """
    def __init__(self,**params):
        super(CFEuclideanDistance,self).__init__(**params)

    def __call__(self, cfs, input_activity, activity, strength, **params):
        rows,cols = activity.shape
	euclidean_dist_mat = zeros((rows,cols),Float)
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_tuple()
                X = input_activity[r1:r2,c1:c2]
		diff = ravel(X) - ravel(cf.weights)
		euclidean_dist_mat[r,c] = L2norm(diff)

        max_dist = max(euclidean_dist_mat.flat)
        activity *= 0.0
        activity += (max_dist - euclidean_dist_mat)
        activity *= strength
