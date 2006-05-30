"""
Basic response functions.

$Id$
"""
__version__='$Revision$'

from topo.base.functionfamilies import DotProduct,ResponseFn
from topo.responsefns.optimized import CFPRF_DotProduct_opt
from topo.base.parameterclasses import Number

class DynamicThreshold_CFPRF_DotProduct_opt(CFPRF_DotProduct_opt):
    """CFPRF_DotProduct_opt with dynamic thresholding"""

    threshold = Number(default=0.3,bounds=(0,None), doc="Baseline threshold")
    decay_rate = Number(default=1.0,bounds=(0,None), doc="Dynamic threshold decay rate")
    absolute_refractory = Number(default=0.0,bounds=(0,None), doc="Absolute refractory period")
      

    def __call__(self, cfs, input_activity, activity, strength, **params):
	# call parent's version
	super(DynamicThreshold_CFPRF_DotProduct_opt,self).__call__(cfs, input_activity, activity, strength, **params)
 
	# apply threshold
        rows,cols = activity.shape
        for r in xrange(rows):
            for c in xrange(cols):
		if (activity[r,c] > self.threshold):
                    activity[r,c] = 1.0
		else:
                    activity[r,c] = 0.0

