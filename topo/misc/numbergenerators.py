"""
A collection of classes that, when called, generate numbers
according to different distributions (e.g. random numbers).

$Id$
"""
__version__='$Revision$'

import random

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number


class RandomWrapper(ParameterizedObject):
    """
    Python's random module provides the Random class, which can be
    instantiated to give an object that can be asked to generate
    numbers from any of several different random distributions
    (e.g. uniform, Gaussian).

    To make it easier to use these, Topographica provides here a
    hierarchy of classes, each tied to a particular random
    distribution. This allows setting parameters on creation rather
    than passing them each call, and allows pickling to work properly.
    
    The underlying random.Random() instance and all its methods can be
    accessed from the 'random_generator' attribute.
    """
    _abstract_class_name="RandomWrapper"
    
    def __init__(self,**params):
        """
        Initialize a new Random() instance and store the supplied
        positional and keyword arguments.

        If seed=X is specified, sets the Random() instance's seed.
        Otherwise, calls the instance's jumpahead() method to get a
        state very likely to be different from any just used.
        """
        self.random_generator = random.Random()

        if 'seed' in params:
            self.random_generator.seed(params['seed'])
            del params['seed']
        else:
            self.random_generator.jumpahead(10)

        super(RandomWrapper,self).__init__(**params)        
        
    def __call__(self):
        raise NotImplementedError


class UniformRandom(RandomWrapper):
    """
    Specified with lbound and ubound; when called, return a random
    number in the range [lbound, ubound).

    See the random module for further details.    
    """
    lbound = Number(default=0.0,doc="inclusive lower bound")
    ubound = Number(default=1.0,doc="exclusive upper bound")
    
    def __call__(self):
        return self.random_generator.uniform(self.lbound,self.ubound)


class NormalRandom(RandomWrapper):
    """
    Specified with mean mu and standard deviation sigma.

    See the random module for further details.    
    """
    mu = Number(default=0.0,doc="mean of the distribution")
    sigma = Number(default=1.0,doc="standard deviation of the distribution")
    
    def __call__(self):
        return self.random_generator.normalvariate(self.mu,self.sigma)
