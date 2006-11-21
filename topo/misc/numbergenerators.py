"""
A collection of classes that, when called, generate numbers
according to different distributions (e.g. random numbers).

$Id$
"""
__version__='$Revision$'

import random

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number, ListParameter


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
        print x
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


# CEBHACKALERT: Probably temporary. Duplicates a lot of Wrapper.
class RandomWrapper(object):
    __slots__ = ['random_generator','function_name','function','args','kw']

    def __repr__(self):
        # CEBHACKALERT: not quite right, need to format args and kw
        return "RandomWrapper('"+self.function_name+"', "+`self.args`+", "+`self.kw`+")"

    def __str__(self):
        return "RandomWrapper('"+self.function_name+"')"


    def __getattribute__(self,attribute):
        """
        If the Wrapper object has the attribute, return it; if the
        function_ object has the attribute, return it; otherwise,
        raise an AttributeError.
        """
        try:
            x= object.__getattribute__(self,attribute)
        except AttributeError:
            function = object.__getattribute__(self,'function')
            if hasattr(function,attribute):
                x = getattr(function,attribute)
            else:
                raise AttributeError("Neither "+`self`+" nor "+`self.function`+" has the attribute '"+ attribute+"'.")
        return x        
        
    
    def __init__(self,function_name,*args,**kw):
        """
        Initialize a new Random() instance and set the function
        to the one specified by function_name.

        If seed=X is specified, sets the Random() instance's seed.
        Otherwise, calls the instance's jumpahead()
        method to get a state very likely to be different from
        any just used.
        """
        self.function_name=function_name
        self.random_generator = random.Random()
        self.function = getattr(self.random_generator,function_name)

        if 'seed' in kw:
            self.random_generator.seed(kw['seed'])
            del kw['seed']
        else:
            self.random_generator.jumpahead(10)

        self.args=args
        self.kw=kw

              
    def __call__(self,*args,**kw):
        """
        If args or kw passed, return self.function_(*args,**kw);
        otherwise, return self.function_(**self.args,**self.kw).

        Allows Wrapper to be used when functions take arguments
        at call-time (e.g. Numeric.add(1,2)) and when functions
        have arguments specified on creation (e.g. when they are
        in a DynamicNumber and will be called without arguments).
        """
        if len(args)==0 and len(kw)==0:
            return self.function(*self.args,**self.kw)
        else:
            return self.function(*args,**kw)


    # CB: I added a hack to allow state saving for the random generator,
    # but it's possible we won't need any special code when we use the
    # RandomDistributionClasses.
    def __getstate__(self):
        """
        Can't pickle self.function, so don't return it
        as part of the state. Instead, we recreate it
        in __setstate__().
        """
        state = {}
        
        for slot in self.__slots__:
            state[slot]=getattr(self,slot)

        del state['function']

        state['rg_state'] = self.random_generator.getstate()

        return state

    def __setstate__(self,state):
        """
        Restore the state.
        """
        rg_state = state['rg_state']
        del state['rg_state']
        
        for (k,v) in state.items():
            setattr(self,k,v)
        self.function = getattr(self.random_generator,self.function_name)
        self.random_generator.setstate(rg_state)
