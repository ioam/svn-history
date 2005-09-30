from topo.parameter import Number
from topo.kernelfactory import KernelFactory
import RandomArray


def uniform_random(kernel_x, kernel_y,rmin,rmax):
    """
    Uniform random noise, independent for each pixel.
    """
    return RandomArray.uniform(rmin,rmax,kernel_x.shape) 


class UniformRandomFactory(KernelFactory):
    """
    Uniform random noise pattern generator
    """
    x       = Number(default=0.0,softbounds=(-1.0,1.0))
    y       = Number(default=0.0,softbounds=(-1.0,1.0))
    min     = Number(default=0.0,bounds=(0.0,1.0),softbounds=(0.0,1.0))
    max     = Number(default=1.0,bounds=(0.0,1.0),softbounds=(0.0,1.0))
    
    def function(self,**params):
        return uniform_random( self.kernel_x, self.kernel_y,
                               params.get('min',self.min),
                               params.get('max',self.max)) 
