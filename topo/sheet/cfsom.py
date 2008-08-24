"""
Defines CFSOM, a sheet class that works like a Kohonen SOM extended to
support topographically restricted receptive fields.

$Id$
"""
__version__='$Revision$'

from numpy.oldnumeric import argmax,exp,floor

from .. import param

from topo.base.arrayutil import L2norm
from topo.base.cf import CFSheet
from topo.learningfn.som import CFPLF_SOM


### JABHACKALERT: This class (and this file) will be removed once the
### examples no longer rely upon it
class CFSOM(CFSheet):
    """
    Kohonen Self-Organizing Map algorithm extended to support ConnectionFields.

    This is an implementation of the Kohonen SOM algorithm extended to
    support ConnectionFields, i.e., different spatially restricted
    input regions for different units.  With fully connected input
    regions, it should be usable as a regular SOM as well.

    This implementation is obsolete and will be removed soon.
    Please see examples/cfsom_or.ty for current SOM support.
    """
    alpha_0 = param.Number(0.5, doc="Initial value of the learning rate.")
    radius_0 = param.Number(1.0, doc="Initial value of the neighborhood radius.")
    precedence = param.Number(0.6)
    learning_length = param.Number(1000, doc="Number of input presentations to use, by default.")
    
    def __init__(self,**params):
        super(CFSOM,self).__init__(**params)
        self.half_life = self.learning_length/8
        self.warning("CFSOM is deprecated -- see the example in cfsom_or.ty for how to build a SOM")

    def decay(self, time, half_life):
        """Exponential decay."""
        return 0.5**(time/float(half_life))

    def alpha(self):
        """Return the learning rate at a specified simulation time, using exponential falloff."""
        return self.alpha_0 * self.decay(float(self.simulation.time()),self.half_life)

    def radius(self):
        """Return the radius at a specified simulation time, using exponential falloff."""
        return self.radius_0 * self.decay(float(self.simulation.time()),self.half_life)

    def learn(self):
        """
        Call the learn() method on every CFProjection to the Sheet.
        """
        rows,cols = self.activity.shape
        radius = self.radius() * self.xdensity
        for proj in self.in_connections:
            proj.learning_rate = self.alpha()
            if isinstance(proj.learning_fn, CFPLF_SOM):
                proj.learning_fn.learning_radius = radius
            proj.learn()


