"""
Projection-level response functions.

For CFProjections, these function objects compute a response matrix
when given an input pattern and a set of ConnectionField objects.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric as Numeric
import numpy.oldnumeric.random_array as RandomArray
from numpy.oldnumeric import sum,ones,exp
import numpy
import copy
import fixedpoint

from math import pi, sqrt
from fixedpoint import FixedPoint
from topo.base.parameterclasses import DynamicNumber, Number
from topo.base.cf import CFSheet, CFPResponseFn
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
        cfs = iterator.proj._cfs
        rows,cols = activity.shape
	euclidean_dist_mat = zeros((rows,cols),Float)
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_array
                X = input_activity[r1:r2,c1:c2]
		diff = ravel(X) - ravel(cf.weights)
		euclidean_dist_mat[r,c] = L2norm(diff)

        max_dist = max(euclidean_dist_mat.ravel())
        activity *= 0.0
        activity += (max_dist - euclidean_dist_mat)
        activity *= strength

class CFPRF_ActivityBased(CFPResponseFn):
    """
    Response function which calculates the activity of each unit individually based on the input activity, the weights and
    strength which is a function of the input activity. This allows connections to have either an excitatory or inhibitory
    strength which is dependent on the activity of the unit in question. 
    The strength function is a generalized logistic curve (Richards' curve), a flexible function for specifying a nonlinear growth curve.
    y = l + ( u /(1 + b exp(-r (x - 2m)) ^ (1 / b)) )

    It has five parameters:

    * l: the lower asymptote;
    * u: the upper asymptote minus l;
    * m: the time of maximum growth;
    * r: the growth rate;
    * b: affects near which asymptote maximum growth occurs.

    Richards, F.J. 1959 A flexible growth function for empirical use. J. Experimental Botany 10: 290--300, 1959
    http://en.wikipedia.org/wiki/Generalised_logistic_curve
    
    """

    l = Number(default=-1.3,doc="Parameter controlling the lower asymptote")
    u = Number(default=1.2,doc="Parameter controlling the upper asymptote (upper asymptote minus lower asymptote")
    m = Number(default=0.25,doc="Parameter controlling the time of maximum growth.")
    r = Number(default=-200,doc="Parameter controlling the growth rate.")
    b = Number(default=2,doc="Parameter which affects near which asymptote maximum growth occurs")

    single_cf_fn = ResponseFnParameter(default=DotProduct(),
                                       doc="Accepts a ResponseFn that will be applied to each CF individually.")
  
    def __call__(self, iterator, input_activity, activity, strength):
        single_cf_fn = self.single_cf_fn
        normalize_factor=max(input_activity.flat)
        for cf,r,c in iterator():
            r1,r2,c1,c2 = cf.slice_array
            X = input_activity[r1:r2,c1:c2]
            avg_activity=sum(X.flat)/len(X.flat)
            x=avg_activity/normalize_factor
            strength_fn=self.l+(self.u/(1+exp(-self.r*(x-2*self.m)))**(1.0/self.b))
            activity[r,c] = single_cf_fn(X,cf.weights)
            activity[r,c] *= strength_fn
