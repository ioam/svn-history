"""
Two-dimensional pattern generators drawing from various random distributions.

At present, supports uniform random distributions, but could support
normal distributions or 1/f noise.

$Id$
"""

from topo.base.parameter import Number,Parameter
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheet import bounds2shape
import RandomArray


class UniformRandomGenerator(PatternGenerator):
    """
    Uniform random noise pattern generator.
    """
    x       = Number(hidden = True)
    y       = Number(hidden = True)
    theta   = Number(hidden = True)
    min     = Number(default=0.0, hidden = True)  # CEB:
    max     = Number(default=1.0, hidden = True)  # to be removed
    
    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params):
        return self.function(**params)

    def function(self,**params):
        r = params.get('rows',0)
        c = params.get('cols',0)

        # CEB:
        # max and min will be calculated from scale and offset.

        if r == 0 and c == 0:
            r,c = bounds2shape( params.get('bounds',self.bounds),
                                params.get('density',self.density))

        return self.scale*RandomArray.uniform( params.get('min',self.min),
                                    params.get('max',self.max),
                                    (r,c))+self.offset
