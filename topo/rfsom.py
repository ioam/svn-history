import RandomArray

from params import Parameter
from utils import norm,inf,Struct,mdot
from sheet import Sheet,activation_submatrix,input_slice
from Numeric import argmax,sqrt,exp

def gaussian(dist,radius):
    return exp( - dist/radius)

def decay(time,half_life):
    return 0.5**(time/float(half_life))

class RFSOM(Sheet):

    rmin = 0.0
    rmax = 1.0
    
    alpha_0 = 0.5
    radius_0 = 1.0
    
    training_length = 1000

    # rf params
    rf_width = 0.1
    
    def __init__(self,**params):

        super(RFSOM,self).__init__(**params)

        self.projections = {}
        self.count = 0
        self.half_life = self.training_length/8

    def _connect_from(self,src,src_port=None,dest_port=None):
        Sheet._connect_from(self,src,src_port,dest_port)
        self.projections[src.name] = Struct()
        self.projections[src.name].sheet = src
        self.projections[src.name].rfs = [[ RF(src,center=(x,y),width=self.rf_width)
                                            for y in self.sheet_cols() ]
                                          for x in self.sheet_rows() ]
                      
    def alpha(self):
        return self.alpha_0 * decay(self.count,self.half_life)
    def radius(self):
        return self.radius_0 * decay(self.count,self.half_life)

    ##########################################
    def present_input(self,input_activation,input_sheet):
        """
        NOTE: doesn't really work for multiple input connections -- each input
        erases the results of the last.
        """
        rows,cols = self.activation.shape
        for r in range(rows):
            for c in range(cols):
                rf = self.projections[input_sheet.name].rfs[r][c]
                X = rf.get_input_matrix(input_activation)
                self.activation[r,c] = mdot(X,rf.weights)


    def train(self,input_activation,input_sheet):

        self.present_input(input_activation,input_sheet)

        rows,cols = self.activation.shape
        wr,wc = self.winner_coords(matrix_coords=True)

        radius = self.radius() * sqrt(self.density)
        
        cmin = max(0,wc-radius)
        cmax = min(wc+radius,cols)
        rmin = max(0,wr-radius)
        rmax = min(wr+radius,rows)

        rfs = self.projections[input_sheet.name].rfs
        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                lattice_dist = norm((wc-c,wr-r))
                if  lattice_dist <= radius:
                    rate = self.alpha() * gaussian(lattice_dist,radius)
                    X = rfs[r][c].get_input_matrix(input_activation)
                    rfs[r][c].weights += rate * (X - rfs[r][c].weights)
                                   
        self.count += 1 

    def input_event(self,src,src_port,dest_port,data):
        self.train(data,src)
        self.send_output(data=self.activation)

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

###############################################
from base import TopoObject

class RF(TopoObject):

    def __init__(self,input_sheet,width=1.0,center=(0,0)):
        from boundingregion import BoundingBox
        from sheet import input_slice
        
        Debuggable.__init__(self)

        self.input_sheet = input_sheet

        self.verbose('center = %s, width= %.2f'%(`center`,width))
        xc,yc = center
        self.__bounds = BoundingBox(points=((xc-width,yc-width),(xc+width,yc+width)))

        rmin,rbound,cmin,cbound = input_slice(self.__bounds,
                                              input_sheet.bounds,
                                              input_sheet.density)
        self.verbose("activation matrix slice: "+`(rmin,rbound,cmin,cbound)`)
        self.weights = RandomArray.random((rbound-rmin,cbound-cmin))

    def contains(self,x,y):
        self.__bounds.contains(x,y)

    def get_input_matrix(self, activation):        
        return activation_submatrix(self.__bounds,activation,
                                    self.input_sheet.bounds,
                                    self.input_sheet.density)



if __name__ == '__main__':

    from simulator import Simulator
    from image import ImageGenerator,ImageSaver
    import pdb
    from boundingregion import BoundingBox
    
    s = Simulator(step_mode=True)

    RFSOM.rmin = -0.5
    RFSOM.rmax = 0.5
    RFSOM.rf_width = 0.1

    input = ImageGenerator(filename='main.ppm',density=10000,
                           bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))


    save = ImageSaver(pixel_scale=1.5)
    som = RFSOM()
    
    s.add(som,input,save)
    s.connect(input,som)
    s.connect(som,save)
    s.run()
    
