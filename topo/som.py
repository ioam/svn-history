from Numeric import *
import RandomArray

from debug import VERBOSE,Debuggable
from params import setup_params
from utils import norm,inf
from sheet import Sheet


def gaussian(dist,radius):
    return exp( - dist/radius)

def decay(time,half_life):
    return 0.5**(time/float(half_life))

class SOM(Sheet):

    dim = 2
    
    rmin = 0.0
    rmax = 1.0
    
    alpha_0 = 0.5
    radius_0 = 1.0
    
    response_exponent = 2

    training_length = 1000
    
    def __init__(self,**params):

        super(SOM).__init__(**params)

        self.weights = RandomArray.uniform(self.rmin,self.rmax,
                                           self.activation.shape + (self.dim,))

        self.count = 0

        self.half_life = self.training_length/8
        
    def alpha(self):
        return self.alpha_0 * decay(self.count,self.half_life)
    def radius(self):
        return self.radius_0 * decay(self.count,self.half_life)

    ##########################################
    def present_input(self,X):

        rows,cols = self.activation.shape
        for r in range(rows):
            for c in range(cols):
                self.activation[r,c] = norm(X - self.weights[r,c])**self.response_exponent

        self.activation = 1/self.activation
        
        if inf in self.activation:
            win = self.winner()
            self.activation.flat[win] = 0
            self.activation -= self.activation
            self.activation.flat[win] = 1.0
        else:
            self.activation /= sum(self.activation.flat)


    def train(self,X):

        self.present_input(X)

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
                if  lattice_dist <= radius:
                    rate = self.alpha() * gaussian(lattice_dist,radius)
                    self.weights[r,c] += rate * (X - self.weights[r,c])
                                   
        self.count += 1 

    def input_event(self,src,src_port,dest_port,data):
        self.train(data)
        self.send_output(data=self.activation)

    def winner(self):
        return argmax(self.activation.flat)

    def winner_coords(self,matrix_coords=False):
        rows,cols = self.activation.shape
        pos = argmax(self.activation.flat)
        if matrix_coords:
            return (pos/rows,pos%cols)
        else:            
            return self.matrix2sheet(pos/rows, pos%cols)

    def get_model_vector(self,index):
        if type(index) == int:
            y = index/self.ydim
            x = index%self.xdim
        else:
            # assume it's a tuple of sheet coords
            r,c = self.sheet2matrix(*index)
        return self.weights[y,x]


class NoveltySOM(SOM):

    alpha_gain = 2.0
    radius_gain = 2.0

    def __init__(self,**params):
        super(NoveltySOM).__init__(**params)
        self.error_ratio = 1.0

    def present_input(self,X):        
        SOM.present_input(self,X)        
        dist = norm( self.get_model_vector(self.winner()) - X )
        self.error_ratio = dist / norm(X)
    
    def alpha(self):
        return SOM.alpha(self) * tanh(self.error_ratio * self.alpha_gain)

    def radius(self):
        return SOM.radius(self) * tanh(self.error_ratio * self.radius_gain)


from simulator import PulseGenerator
import RandomArray
class RandomVector(PulseGenerator):
    mean = 0.0
    std  = 0.2

    def __init__(self,**params):
        super(RandomVector,self).__init__(**params)
        
        
    def input_event(self,src,src_port,dest_port,data):
        vec = RandomArray.normal(self.mean,self.std,2)
        self.verbose('Sending '+`vec`)
        self.send_output(data=vec)


if __name__ == '__main__':

    from simulator import Simulator

    s = Simulator(step_mode=True)

    SOM.rmin = -0.5
    SOM.rmax = 0.5
    
    som = SOM()
    input = RandomVector(period=1.0)

    s.add(input,som)

    input.connect_to(som)

