"""
Defines CFSOM, a sheet class that works like a Kohonen SOM, but
uses receptive fields.


$Id$
"""


from utils import L2norm
from params import Parameter
from Numeric import argmax,sqrt,exp,floor

from cfsheet import CFSheet

def gaussian(dist,radius):
    return exp( - dist/radius)

def decay(time,half_life):
    return 0.5**(time/float(half_life))



class CFSOM(CFSheet):
    """
    Training operates by selecting a single winning unit from the SOM
    at each input, and training the units in a gaussian neighborhood
    around the winner.

    """
    rmin = Parameter(0.0)
    rmax = Parameter(1.0)
    
    alpha_0 = Parameter(0.5)
    radius_0 = Parameter(1.0)
    
    training_length = Parameter(1000)
    
    def __init__(self,**params):
        super(CFSOM,self).__init__(**params)
        self.half_life = self.training_length/8                      
    def alpha(self):
        return self.alpha_0 * decay(self.simulator.time(),self.half_life)
    def radius(self):
        return self.radius_0 * decay(self.simulator.time(),self.half_life)

    ##########################################

    def train(self):

        rows,cols = self.activation.shape
        wr,wc = self.winner_coords(matrix_coords=True)

        radius = self.radius() * sqrt(self.density)
        
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
        return argmax(self.activation.flat)

    def winner_coords(self,matrix_coords=False):
        pos = argmax(self.activation.flat)
        rows,cols = self.activation.shape
        row = pos/cols
        col = pos%cols
        if matrix_coords:
            return row,col
        else:
            return self.matrix2sheet(row,col)




if __name__ == '__main__':

    from simulator import Simulator
    from image import ImageGenerator,ImageSaver
    import pdb
    from boundingregion import BoundingBox
    
    s = Simulator(step_mode=True)

    CFSOM.cf_width = 0.1

    input = ImageGenerator(filename='main.ppm',density=10000,
                           bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))


    save = ImageSaver(pixel_scale=1.5)
    som = CFSOM()
    
    s.add(som,input,save)
    s.connect(input,som)
    s.connect(som,save)
    s.run(duration=10)
    
