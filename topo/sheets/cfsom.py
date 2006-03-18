"""
Defines CFSOM, a sheet class that works like a Kohonen SOM extended to
support topographically restricted receptive fields.

$Id$
"""
__version__='$Revision$'

from topo.base.arrayutils import L2norm
from topo.base.parameterclasses import Number
from Numeric import argmax,exp,floor
from topo.base.connectionfield import CFSheet
from itertools import chain
from topo.learningfns.som import SOMLF


class CFSOM(CFSheet):
    """
    Kohonen Self-Organizing Map algorithm extended to support ConnectionFields.

    This is an implementation of the Kohonen SOM algorithm extended to
    support ConnectionFields, i.e., different spatially restricted
    input regions for different units.  With fully connected input
    regions, it should be usable as a regular SOM as well.

    Most of the real work is done by the Projection, and specifically
    by the Projection's learning_fn.  The learning_fn will typically
    be a subclass of SOMLF, and will typically select a winning unit
    and modify weights according to a neighborhood function around the
    winner.  Other Projection types can also be used.
    """
    rmin = Number(0.0)
    rmax = Number(1.0)
    
    alpha_0 = Number(0.5)
    radius_0 = Number(1.0)
    precedence = Number(0.6)
    learning_length = Number(1000)
    
    def __init__(self,**params):
        super(CFSOM,self).__init__(**params)
        self.half_life = self.learning_length/8

    def decay(self, time, half_life):
        """Exponential decay."""
        return 0.5**(time/float(half_life))

    ### JCALERT! For the moment, som_retinotopy uses a super-class of
    ### CFSOM in order to override the decay (and alpha) functions. It
    ### would be good to make them Parameters here, so that we can
    ### delete that there and in obermayer, yet still override the
    ### decay and alpha function.
    def alpha(self):
        """Return the learning rate at a specified simulator time, using exponential falloff."""
        return self.alpha_0 * self.decay(float(self.simulator.time()),self.half_life)

    def radius(self):
        """Return the radius at a specified simulator time, using exponential falloff."""
        return self.radius_0 * self.decay(float(self.simulator.time()),self.half_life)

    def learn(self):
        """
        Call the learn() method on every CFProjection to the Sheet.
        """
        rows,cols = self.activity.shape
        radius = self.radius() * self.density
        for proj in chain(*self.in_projections.values()):
            proj.learning_rate = self.alpha()
            if isinstance(proj.learning_fn, SOMLF):
                proj.learning_fn.learning_radius = radius
            proj.learn()


