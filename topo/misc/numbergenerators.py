"""
A collection of classes that, when called, generate numbers
according to different distributions (e.g. random numbers).

$Id$
"""
__version__='$Revision$'

import random
from math import e

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number, ListParameter, CallableParameter


class RandomDistribution(ParameterizedObject):
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
    _abstract_class_name="RandomDistribution"
    
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

        super(RandomDistribution,self).__init__(**params)        
        
    def __call__(self):
        raise NotImplementedError


class UniformRandom(RandomDistribution):
    """
    Specified with lbound and ubound; when called, return a random
    number in the range [lbound, ubound).

    See the random module for further details.    
    """
    lbound = Number(default=0.0,doc="inclusive lower bound")
    ubound = Number(default=1.0,doc="exclusive upper bound")
    
    def __call__(self):
        return self.random_generator.uniform(self.lbound,self.ubound)


class UniformRandomInt(RandomDistribution):
    """
    Specified with lbound and ubound; when called, return a random
    number in the inclusive range [lbound, ubound].

    See the randint function in the random module for further details.    
    """
    lbound = Number(default=0,doc="inclusive lower bound")
    ubound = Number(default=1000,doc="inclusive upper bound")
    
    def __call__(self):
        x = self.random_generator.randint(self.lbound,self.ubound)
        return x


class Choice(RandomDistribution):
    """
    Return a random element from the specified list of choices.

    Accepts items of any type, though they are typically numbers.
    See the choice() function in the random module for further details.
    """
    choices = ListParameter(default=[0,1],
        doc="List of items from which to select.")
    
    def __call__(self):
        return self.random_generator.choice(self.choices)


class NormalRandom(RandomDistribution):
    """
    Specified with mean mu and standard deviation sigma.

    See the random module for further details.    
    """
    mu = Number(default=0.0,doc="mean of the distribution")
    sigma = Number(default=1.0,doc="standard deviation of the distribution")
    
    def __call__(self):
        return self.random_generator.normalvariate(self.mu,self.sigma)


class ExponentialDecay(ParameterizedObject):
    """
    Function object that provides a value that decays according to an
    exponential function, based on a given timebase.

    Returns starting_value*base^(-time/time_constant).
    
    See http://en.wikipedia.org/wiki/Exponential_decay.
    """
    starting_value = Number(1.0, doc="Value used for time zero.")

    time_constant = Number(10000,doc="""
        Time scale for the exponential; large values give slow decay.""")

    base = Number(e, doc="""
        Base of the exponent; the default yields starting_value*exp(-t/time_constant.""")

    timebase = CallableParameter(None, doc="Function to call to determine current time.")
    
    def __init__(self,**params):
        super(ExponentialDecay,self).__init__(**params)
        if not callable(self.timebase):
            self.warning("ExponentialDecay timebase must be a callable object (e.g. a function)")

    def __call__(self):
        return self.starting_value * self.base**(-1.0*float(self.timebase())/
                                                 float(self.time_constant))



