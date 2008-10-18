"""
Two-dimensional pattern generators drawing from various random distributions.

$Id$
"""
__version__='$Revision$'

import numpy

from .. import param
from ..param.parameterized import ParamOverrides

from topo.base.patterngenerator import PatternGenerator
from topo.pattern import Composite, Gaussian
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.outputfn.basic import IdentityOF


def seed(seed=None):
    """
    Set the seed on the shared RandomState instance.

    Convenience function: shortcut to RandomGenerator.random_generator.seed().
    """
    RandomGenerator.random_generator.seed(seed)
    

class RandomGenerator(PatternGenerator):
    """2D random noise pattern generator abstract class."""

    __abstract = True

    # The orientation is ignored, so we don't show it in
    # auto-generated lists of parameters (e.g. in the GUI)
    orientation = param.Number(precedence=-1)

    random_generator = param.Parameter(
        default=numpy.random.RandomState(seed=(500,500)),precedence=-1,doc=
        """
        numpy's RandomState provides methods for generating random
        numbers (see RandomState's help for more information).

        Note that all instances will share this RandomState object,
        and hence its state. To create a RandomGenerator that has its
        own state, set this parameter to a new RandomState instance.
        """)

        
    def _distrib(self,shape,pos):
        """Method for subclasses to override with a particular random distribution."""
        raise NotImplementedError
    
    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)

        shape = SheetCoordinateSystem(params['bounds'],params['xdensity'],params['ydensity']).shape

        result = self._distrib(shape,params)
        self._apply_mask(params,result)

        output_fn = params['output_fn']
        if output_fn is not IdentityOF: # Optimization (but may not actually help)
            output_fn(result)
        
        return result



class UniformRandom(RandomGenerator):
    """2D uniform random noise pattern generator."""

    def _distrib(self,shape,params):
        return self.random_generator.uniform(params['offset'], params['offset']+params['scale'], shape)



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
        return params['offset']+params['scale']*(self.random_generator.uniform(rmin,rmin+1.0,shape).round())



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
        return params['offset']+params['scale']*self.random_generator.standard_normal(shape)



class GaussianCloud(Composite):
    """Uniform random noise masked by a circular Gaussian."""
    ### JABALERT: Should be possible to eliminate this class; see teststimuli.py.
    
    operator = param.Parameter(numpy.multiply)
    
    gaussian_size = param.Number(default=1.0,doc="Size of the Gaussian pattern.")

    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,doc="""
        Ratio of gaussian width to height; width is gaussian_size*aspect_ratio.""")

    def __call__(self,**params_to_override):
        params = ParamOverrides(self,params_to_override)
        params['generators']=[
            Gaussian(aspect_ratio=params['aspect_ratio'],size=params['gaussian_size']),
            UniformRandom()]
        return super(GaussianCloud,self).__call__(**params)
