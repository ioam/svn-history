"""
Homeostatic Output Functions
"""

import Numeric
import copy

from Numeric import exp

from topo.base.functionfamilies import OutputFn
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject

# Imported here so that all OutputFns will be in the same package
from topo.base.functionfamilies import IdentityOF


class HomeostaticMaxEnt(OutputFn):
    """
    Implementation of Homeostatic Intrinsic Placticity from Triesch, ICANN 2005, LNCS 3696 pp. 65-70.

    Sigmoid activation function is adapted automatically to achieve desired average firing rate and 
    approximately exponential distribution of firing rates.
    """

    a_init = Number(default=13,doc="Multiplicative parameter controlling the exponential.")
    b_init = Number(default=-4,doc="Additive parameter controlling the exponential.")
    eta = Number(default=0.0002,doc="Learning rate for homeostatic plasticity.")
    mu = Number(default=0.01,doc="Target average firing rate.")


    def __init__(self,**params):
        super(HomeostaticMaxEnt,self).__init__(**params)

	self.first_call = True

    def __call__(self,x):
	
	if self.first_call:
	    self.first_call = False
	    self.a = Numeric.ones(x.shape, x.typecode()) * self.a_init
	    self.b = Numeric.ones(x.shape, x.typecode()) * self.b_init

	# Apply sigmoid function to x, resulting in what Triesch calls y
        x_orig = copy.copy(x)
        x *= 0.0
	x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))

	# Update a and b
	self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*x_orig*x + x_orig*x*x/self.mu)
	self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)


