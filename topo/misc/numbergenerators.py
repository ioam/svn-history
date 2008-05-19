"""
A collection of classes that, when called, generate numbers
according to different distributions (e.g. random numbers).

$Id$
"""
__version__='$Revision$'

import random
import operator

from math import e

from .. import params



class NumberGenerator(params.Parameterized):
    """
    Abstract base class for any object that when called produces a number.

    Primarily provides support for using NumberGenerators in simple
    arithmetic expressions, such as abs((x+y)/z), where x,y,z are
    NumberGenerators or numbers.
    """
    
    def __call__(self):
        raise NotImplementedError

    # Could define any of Python's operators here, esp. if they have operator or ufunc equivalents
    def __add__      (self,operand): return BinaryOperator(self,operand,operator.add)
    def __sub__      (self,operand): return BinaryOperator(self,operand,operator.sub)
    def __mul__      (self,operand): return BinaryOperator(self,operand,operator.mul)
    def __mod__      (self,operand): return BinaryOperator(self,operand,operator.mod)
    def __pow__      (self,operand): return BinaryOperator(self,operand,operator.pow)
    def __div__      (self,operand): return BinaryOperator(self,operand,operator.div)
    def __truediv__  (self,operand): return BinaryOperator(self,operand,operator.truediv)
    def __floordiv__ (self,operand): return BinaryOperator(self,operand,operator.floordiv)

    def __radd__     (self,operand): return BinaryOperator(self,operand,operator.add,True)
    def __rsub__     (self,operand): return BinaryOperator(self,operand,operator.sub,True)
    def __rmul__     (self,operand): return BinaryOperator(self,operand,operator.mul,True)
    def __rmod__     (self,operand): return BinaryOperator(self,operand,operator.mod,True)
    def __rpow__     (self,operand): return BinaryOperator(self,operand,operator.pow,True)
    def __rdiv__     (self,operand): return BinaryOperator(self,operand,operator.div,True)
    def __rtruediv__ (self,operand): return BinaryOperator(self,operand,operator.truediv,True)
    def __rfloordiv__(self,operand): return BinaryOperator(self,operand,operator.floordiv,True)

    def __neg__ (self): return UnaryOperator(self,operator.neg)
    def __pos__ (self): return UnaryOperator(self,operator.pos)
    def __abs__ (self): return UnaryOperator(self,operator.abs)



class BinaryOperator(NumberGenerator):
    """Applies any binary operator to NumberGenerators or numbers to yield a NumberGenerator."""
    
    def __init__(self,lhs,rhs,operator,reverse=False):
        if reverse:
            self.lhs=rhs
            self.rhs=lhs
        else:
            self.lhs=lhs
            self.rhs=rhs
        self.operator=operator
    
    def __call__(self):
        return self.operator(self.lhs() if callable(self.lhs) else self.lhs,
                             self.rhs() if callable(self.rhs) else self.rhs)



class UnaryOperator(NumberGenerator):
    """Applies any unary operator to a NumberGenerator to yield another NumberGenerator."""
    
    def __init__(self,operand,operator):
        self.operand=operand
        self.operator=operator
    
    def __call__(self):
        return self.operator(self.operand())



class RandomDistribution(NumberGenerator):
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
    __abstract = True
    
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
    lbound = params.Number(default=0.0,doc="inclusive lower bound")
    ubound = params.Number(default=1.0,doc="exclusive upper bound")
    
    def __call__(self):
        return self.random_generator.uniform(self.lbound,self.ubound)


class UniformRandomInt(RandomDistribution):
    """
    Specified with lbound and ubound; when called, return a random
    number in the inclusive range [lbound, ubound].

    See the randint function in the random module for further details.    
    """
    lbound = params.Number(default=0,doc="inclusive lower bound")
    ubound = params.Number(default=1000,doc="inclusive upper bound")
    
    def __call__(self):
        x = self.random_generator.randint(self.lbound,self.ubound)
        return x


class Choice(RandomDistribution):
    """
    Return a random element from the specified list of choices.

    Accepts items of any type, though they are typically numbers.
    See the choice() function in the random module for further details.
    """
    choices = params.List(default=[0,1],
        doc="List of items from which to select.")
    
    def __call__(self):
        return self.random_generator.choice(self.choices)


class NormalRandom(RandomDistribution):
    """
    Specified with mean mu and standard deviation sigma.

    See the random module for further details.    
    """
    mu = params.Number(default=0.0,doc="mean of the distribution")
    sigma = params.Number(default=1.0,doc="standard deviation of the distribution")
    
    def __call__(self):
        return self.random_generator.normalvariate(self.mu,self.sigma)


import topo
class ExponentialDecay(NumberGenerator):
    """
    Function object that provides a value that decays according to an
    exponential function, based on topo.sim.time().

    Returns starting_value*base^(-time/time_constant).
    
    See http://en.wikipedia.org/wiki/Exponential_decay.
    """
    starting_value = params.Number(1.0, doc="Value used for time zero.")
    ending_value = params.Number(0.0, doc="Value used for time infinity.")

    time_constant = params.Number(10000,doc="""
        Time scale for the exponential; large values give slow decay.""")

    base = params.Number(e, doc="""
        Base of the exponent; the default yields starting_value*exp(-t/time_constant).
        Another popular choice of base is 2, which allows the
        time_constant to be interpreted as a half-life.""")

    # CEBALERT: default should be more like 'lambda:0', but that would
    # confuse GUI users.
    time_fn = params.Callable(default=topo.sim.time,doc="""
     Function to generate the time used for the decay.""")

    def __call__(self):
        Vi = self.starting_value
        Vm = self.ending_value
        return Vm + (Vi - Vm) * self.base**(-1.0*float(self.time_fn())/
                                                 float(self.time_constant))


class BoundedNumber(NumberGenerator):
    """
    Function object that silently enforces numeric bounds on values
    returned by a callable object.
    """
    generator = params.Callable(None, doc="Object to call to generate values.")

    bounds = params.Parameter((None,None), doc="""
        Legal range for the value returned, as a pair.
        
        The default bounds are (None,None), meaning there are actually
        no bounds.  One or both bounds can be set by specifying a
        value.  For instance, bounds=(None,10) means there is no lower
        bound, and an upper bound of 10.""")

    def __call__(self):
        val = self.generator()
        min_, max_ = self.bounds
        if   min_ != None and val < min_: return min_
        elif max_ != None and val > max_: return max_
        else: return val


