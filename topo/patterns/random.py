"""
Two-dimensional pattern generators drawing from various random distributions.

$Id$
"""
__version__='$Revision$'

import numpy.oldnumeric.random_array as RandomArray

from .. import param
from ..param.parameterized import ParamOverrides

from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.outputfns.basic import IdentityOF


class RandomGenerator(PatternGenerator):
    """2D random noise pattern generator abstract class."""

    __abstract = True

    # The standard x, y, and orientation variables are currently ignored,
    # so they aren't shown in auto-generated lists of parameters (e.g. in the GUI)
    x       = param.Number(precedence=-1)
    y       = param.Number(precedence=-1)
    size    = param.Number(precedence=-1)
    orientation   = param.Number(precedence=-1)

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



class BinaryUniformRandom(RandomGenerator):
    """
    2D binary uniform random noise pattern generator.

    Generates an array of random numbers that are 1.0 with the given
    on_probability, or else 0.0, then scales it and adds the offset as
    for other patterns.  For the default scale and offset, the result
    is a binary mask where some elements are on at random.
    """

    on_probability = param.Number(default=0.5,bounds=[0.0,1.0],doc="""
        Probability (in the range 0.0 to 1.0) that the binary value
        (before scaling) is on rather than off (1.0 rather than 0.0).""")

    def _distrib(self,shape,params):
        rmin = params['on_probability']-0.5
        return params['offset']+params['scale']*(RandomArray.uniform(rmin,rmin+1.0,shape).round())


class GaussianRandom(RandomGenerator):
    """
    2D Gaussian random noise pattern generator.

    Each pixel is chosen independently from a Gaussian distribution
    of zero mean and unit variance, then multiplied by the given
    scale and adjusted by the given offset.
    """

    scale  = param.Number(default=0.25,softbounds=(0.0,2.0))
    offset = param.Number(default=0.50,softbounds=(-2.0,2.0))

    def _distrib(self,shape,params):
        return params['offset']+params['scale']*RandomArray.standard_normal(shape)

