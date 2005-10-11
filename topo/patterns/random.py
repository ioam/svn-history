"""
Two-dimensional pattern generators drawing from various random distributions.

At present, supports uniform random distributions, but could support
normal distributions or 1/f noise.

$Id$
"""

from topo.base.parameter import Number,Parameter
from topo.base.patterngenerator import PatternGenerator
import RandomArray


class UniformRandomGenerator(PatternGenerator):
    """
    Uniform random noise pattern generator.
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    min     = Number(default=0.0,bounds=(0.0,1.0),softbounds=(0.0,1.0))
    max     = Number(default=1.0,bounds=(0.0,1.0),softbounds=(0.0,1.0))
    
    def __call__(self,**params):
        self.verbose("params = ",params)
	# doesn't need to transform coordinates, so we can call function() 
        # directly to speed things up
        return self.function(**params)

    def function(self,**params):
        return RandomArray.uniform( params.get('min',self.min),
                                    params.get('max',self.max),
                                    (params.get('rows',0),
				     params.get('cols',0)))
