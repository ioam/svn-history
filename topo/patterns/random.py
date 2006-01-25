"""
Two-dimensional pattern generators drawing from various random distributions.

At present, supports uniform random distributions, but could support
normal distributions or 1/f noise.

$Id$
"""
__version__='$Revision$'

from topo.base.parameter import Number,Parameter
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheet import bounds2slice
import RandomArray


class UniformRandom(PatternGenerator):
    """2D uniform random noise pattern generator."""

    # The standard x, y, and orientation variables are currently ignored,
    # so they aren't shown in auto-generated lists of parameters (e.g. in the GUI)
    x       = Number(hidden = True)
    y       = Number(hidden = True)
    orientation   = Number(hidden = True)
    
    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params):
        slice_array = params.get('slice_array',None)
        bounds = params.get('bounds',self.bounds)
        density = params.get('density',self.density)

        left,bottom,right,top = bounds.aarect().lbrt()
        xdensity = int(density*(right-left)) / float((right-left))
        ydensity = int(density*(top-bottom)) / float((top-bottom))

        # avoid calculating the slice if we've already done it; otherwise,
        # want a matrix for the whole of the bounds
        if slice_array==None:
            r1,r2,c1,c2 = bounds2slice(bounds,bounds,xdensity,ydensity)
        else:
            r1,r2,c1,c2 = slice_array

        offset_=params.get('offset',self.offset)
        scale_=params.get('scale',self.scale)
     
        return RandomArray.uniform( offset_, offset_+scale_, (r2-r1,c2-c1))
