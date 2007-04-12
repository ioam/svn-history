"""
Projection-level response functions.

For CFProjections, these function objects compute a response matrix
when given an input pattern and a set of ConnectionField objects.

$Id$
"""
__version__='$Revision$'


from numpy.oldnumeric import zeros, Float, ravel

from topo.base.functionfamilies import ResponseFnParameter,DotProduct
from topo.base.arrayutils import L2norm
from topo.base.cf import CFPResponseFn

from topo.misc.inlinec import inline, optimized

# Imported here so that all ResponseFns will be in the same package
from topo.base.cf import CFPRF_Plugin


class CFPRF_EuclideanDistance(CFPResponseFn):
    """
    Euclidean-distance--based response function.
    """
    def __call__(self, iterator, input_activity, activity, strength, **params):
        rows,cols = activity.shape
	euclidean_dist_mat = zeros((rows,cols),Float)
        for cf,r,c in iterator():
            r1,r2,c1,c2 = cf.slice_array
            X = input_activity[r1:r2,c1:c2]
            diff = ravel(X) - ravel(cf.weights)
            euclidean_dist_mat[r,c] = L2norm(diff)

        max_dist = max(euclidean_dist_mat.ravel())
        activity *= 0.0
        activity += (max_dist - euclidean_dist_mat)
        activity *= strength
