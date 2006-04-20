"""
Two-dimensional pattern generators drawing from various random distributions.

At present, supports uniform random distributions, but could support
normal distributions or 1/f noise.

$Id$
"""
__version__='$Revision$'

import RandomArray

from topo.base.parameterclasses import Number,Parameter
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheet import CoordinateTransformer,Slice

from topo.outputfns.basic import IdentityOF


class RandomGenerator(PatternGenerator):
    """2D random noise pattern generator abstract class."""

    _abstract_class_name = "RandomGenerator"

    # The standard x, y, and orientation variables are currently ignored,
    # so they aren't shown in auto-generated lists of parameters (e.g. in the GUI)
    x       = Number(hidden = True)
    y       = Number(hidden = True)
    orientation   = Number(hidden = True)

    def _distrib(self,shape,**params):
        """Method for subclasses to override with a particular random distribution."""
        raise NotImplementedError
    
    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params):
        bounds = params.get('bounds',self.bounds)
        xdensity = params.get('xdensity',self.xdensity)
        ydensity = params.get('ydensity',self.ydensity)
        output_fn = params.get('output_fn',self.output_fn)

        slice_ = Slice(bounds,CoordinateTransformer(bounds,xdensity,ydensity))
        shape = slice_.shape

        if output_fn is IdentityOF:
            return self._distrib(shape)
        else:
            return output_fn(self._distrib(shape))


class UniformRandom(RandomGenerator):
    """2D uniform random noise pattern generator."""

    def _distrib(self,shape,**params):
        offset_=params.get('offset',self.offset)
        scale_=params.get('scale',self.scale)
        return RandomArray.uniform( offset_, offset_+scale_, shape)


class GaussianRandom(RandomGenerator):
    """
    2D Gaussian random noise pattern generator.

    Each pixel is chosen independently from a Gaussian distribution
    of zero mean and unit variance, then multiplied by the given
    scale and adjusted by the given offset.
    """

    scale  = Number(default=0.25,softbounds=(0.0,2.0))
    offset = Number(default=0.50,softbounds=(-2.0,2.0))

    def _distrib(self,shape,**params):
        offset_=params.get('offset',self.offset)
        scale_ =params.get('scale', self.scale)
        return offset_+scale_*RandomArray.standard_normal(shape)

