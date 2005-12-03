"""
Defines CFSOM, a sheet class that works like a Kohonen SOM, but
uses receptive fields.


$Id$
"""
__version__='$Revision$'

from topo.base.arrayutils import L2norm
from topo.base.parameter import Number
from Numeric import argmax,exp,floor
from topo.base.connectionfield import CFSheet
from itertools import chain


class CFSOM(CFSheet):
    """
    An implementation of the Kohonen Self-Organizing Map algorithm
    extended to support ConnectionFields, i.e., different spatially
    restricted input regions for different units.  With fully
    connected input regions, should be usable as a regular SOM as
    well.
    
    Learning operates by selecting a single winning unit from the SOM
    at each input, and learning the units in a Gaussian neighborhood
    around the winner.

    """
    rmin = Number(0.0)
    rmax = Number(1.0)
    
    alpha_0 = Number(0.5)
    radius_0 = Number(1.0)
    
    learning_length = Number(1000)
    
    def __init__(self,**params):
        super(CFSOM,self).__init__(**params)
        self.half_life = self.learning_length/8

    def decay(self, time, half_life):
        return 0.5**(time/float(half_life))

    def alpha(self):
        return self.alpha_0 * self.decay(float(self.simulator.time()),self.half_life)

    def radius(self):
        return self.radius_0 * self.decay(float(self.simulator.time()),self.half_life)

    def learn(self):
        rows,cols = self.activity.shape
        wr,wc = self.winner_coords(matrix_coords=True)
        radius = self.radius() * self.density
        
        learning_rate = self.alpha()
        for proj in chain(*self.in_projections.values()):
            if proj.input_buffer:
                inp = proj.input_buffer
                cfs = proj.cfs
                proj.learning_fn(cfs, inp, self.activity, learning_rate, winner_r=wr, winner_c=wc, radius=radius)
        

    def winner(self):
        return argmax(self.activity.flat)

    def winner_coords(self,matrix_coords=False):
        pos = argmax(self.activity.flat)
        rows,cols = self.activity.shape
        row = pos/cols
        col = pos%cols
        if matrix_coords:
            return row,col
        else:
            return self.matrixidx2sheet(row,col)


