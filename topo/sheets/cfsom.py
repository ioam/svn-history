"""
Defines CFSOM, a sheet class that works like a Kohonen SOM, but
uses receptive fields.


$Id$
"""

from topo.base.utils import L2norm
from topo.base.parameter import Parameter
from Numeric import argmax,exp,floor
from topo.base.connectionfield import CFSheet

def gaussian(dist,radius):
    return exp( - dist/radius)

def decay(time,half_life):
    return 0.5**(time/float(half_life))



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
    rmin = Parameter(0.0)
    rmax = Parameter(1.0)
    
    alpha_0 = Parameter(0.5)
    radius_0 = Parameter(1.0)
    
    learning_length = Parameter(1000)
    
    def __init__(self,**params):
        super(CFSOM,self).__init__(**params)
        self.half_life = self.learning_length/8                      
    def alpha(self):
        return self.alpha_0 * decay(float(self.simulator.time()),self.half_life)
    def radius(self):
        return self.radius_0 * decay(float(self.simulator.time()),self.half_life)


    ### JABHACKALERT!
    ###
    ### Would it make sense to move any of this to learningrules.py?  If not, document why not.
    def learn(self):

        rows,cols = self.activity.shape
        wr,wc = self.winner_coords(matrix_coords=True)

        radius = self.radius() * self.density
        
        cmin = int(max(0,wc-radius))
        cmax = int(min(wc+radius,cols))
        rmin = int(max(0,wr-radius))
        rmax = int(min(wr+radius,rows))

        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                lattice_dist = L2norm((wc-c,wr-r))
                for proj_list in self.projections.values():
                    for proj in proj_list:
                        if  lattice_dist <= radius:
                            cf = proj.cf(r,c)
                            rate = self.alpha() * gaussian(lattice_dist,radius)
                            X = cf.get_input_matrix(proj.input_buffer)
                            cf.weights += rate * (X - cf.weights)
                                   


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
            return self.matrix2sheet(row,col)


