"""
Defines RFSOM, a sheet class that works like a Kohonen SOM, but
uses receptive fields.  

"""


from utils import norm
from params import Parameter
from Numeric import argmax,sqrt,exp

from rfsheet import RFSheet

def gaussian(dist,radius):
    return exp( - dist/radius)

def decay(time,half_life):
    return 0.5**(time/float(half_life))



class RFSOM(RFSheet):
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

        super(RFSOM,self).__init__(**params)

        self.projections = {}
        self.half_life = self.training_length/8

                      
    def alpha(self):
        return self.alpha_0 * decay(self.simulator.time(),self.half_life)
    def radius(self):
        return self.radius_0 * decay(self.simulator.time(),self.half_life)

    ##########################################

    def train(self,input_activation,input_sheet):

        self.present_input(input_activation,input_sheet)

        rows,cols = self.activation.shape
        wr,wc = self.winner_coords(matrix_coords=True)

        radius = self.radius() * sqrt(self.density)
        
        cmin = max(0,wc-radius)
        cmax = min(wc+radius,cols)
        rmin = max(0,wr-radius)
        rmax = min(wr+radius,rows)

        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                lattice_dist = norm((wc-c,wr-r))
                for sheet,proj_list in self.projections.items():
                    for proj in proj_list:
                        if  lattice_dist <= radius:
                            rf = proj.rf(r,c)
                            rate = self.alpha() * gaussian(lattice_dist,radius)
                            X = rf.get_input_matrix(input_activation)
                            rf.weights += rate * (X - rf.weights)
                                   


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

    def get_model_vector(self,index):
        if type(index) == int:
            y = index/self.ydim
            x = index%self.xdim
        else:
            # assume it's a tuple of sheet coords
            r,c = self.sheet2matrix(*index)
        return self.weights[y,x]




if __name__ == '__main__':

    from simulator import Simulator
    from image import ImageGenerator,ImageSaver
    import pdb
    from boundingregion import BoundingBox
    
    s = Simulator(step_mode=True)

    RFSOM.rf_width = 0.1

    input = ImageGenerator(filename='main.ppm',density=10000,
                           bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))


    save = ImageSaver(pixel_scale=1.5)
    som = RFSOM()
    
    s.add(som,input,save)
    s.connect(input,som)
    s.connect(som,save)
    s.run(duration=10)
    
