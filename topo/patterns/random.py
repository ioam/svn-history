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
    x       = Number(precedence=-1)
    y       = Number(precedence=-1)
    size    = Number(precedence=-1)
    orientation   = Number(precedence=-1)

    def _distrib(self,shape,pos):
        """Method for subclasses to override with a particular random distribution."""
        raise NotImplementedError
    
    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params_to_override):
        self._check_params(params_to_override)
        params = ParamOverrides(self,params_to_override)

        shape = SheetCoordinateSystem(params['bounds'],params['xdensity'],params['ydensity']).shape

        result = self._distrib(shape,params)

        mask = params['mask']
        if mask is not None:
            result*=mask
            
        output_fn = params['output_fn']
        if output_fn is not IdentityOF: # Optimization (but may not actually help)
            output_fn(result)
        
        return result



class UniformRandom(RandomGenerator):
    """2D uniform random noise pattern generator."""

    def _distrib(self,shape,params):
        return RandomArray.uniform(params['offset'], params['offset']+params['scale'], shape)


class GaussianRandom(RandomGenerator):
    """
    2D Gaussian random noise pattern generator.

    Each pixel is chosen independently from a Gaussian distribution
    of zero mean and unit variance, then multiplied by the given
    scale and adjusted by the given offset.
    """

    scale  = Number(default=0.25,softbounds=(0.0,2.0))
    offset = Number(default=0.50,softbounds=(-2.0,2.0))

    def _distrib(self,shape,params):
        return params['offset']+params['scale']*RandomArray.standard_normal(shape)

