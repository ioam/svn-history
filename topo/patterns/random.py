"""
Two-dimensional pattern generators drawing from various random distributions.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric.random_array as RandomArray

from topo.base.parameterizedobject import ParamOverrides
from topo.base.parameterclasses import Number,Parameter
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem

from topo.outputfns.basic import IdentityOF


class RandomGenerator(PatternGenerator):
    """2D random noise pattern generator abstract class."""

    __abstract = True

    # The standard x, y, and orientation variables are currently ignored,
    # so they aren't shown in auto-generated lists of parameters (e.g. in the GUI)
    x       = Number(hidden = True)
    y       = Number(hidden = True)
    size    = Number(hidden = True)
    orientation   = Number(hidden = True)

    def _distrib(self,shape,pos):
        """Method for subclasses to override with a particular random distribution."""
        raise NotImplementedError
    
    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params):
        self._check_params(params)
        pos = ParamOverrides(self,params)

        shape = SheetCoordinateSystem(pos['bounds'],pos['xdensity'],pos['ydensity']).shape

        result = self._distrib(shape,pos)

        mask = pos['mask']
        if mask is not None:
            result*=mask
            
        output_fn = pos['output_fn']
        if output_fn is not IdentityOF: # Optimization (but may not actually help)
            output_fn(result)
        
        return result



class UniformRandom(RandomGenerator):
    """2D uniform random noise pattern generator."""

    def _distrib(self,shape,pos):
        return RandomArray.uniform(pos['offset'], pos['offset']+pos['scale'], shape)


class GaussianRandom(RandomGenerator):
    """
    2D Gaussian random noise pattern generator.

    Each pixel is chosen independently from a Gaussian distribution
    of zero mean and unit variance, then multiplied by the given
    scale and adjusted by the given offset.
    """

    scale  = Number(default=0.25,softbounds=(0.0,2.0))
    offset = Number(default=0.50,softbounds=(-2.0,2.0))

    def _distrib(self,shape,pos):
        return pos['offset']+pos['scale']*RandomArray.standard_normal(shape)

