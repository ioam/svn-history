import RandomArray

from utils import norm,inf,mdot
from params import Parameter
from sheet import Sheet
from Numeric import argmax,sqrt,exp

def gaussian(dist,radius):
    return exp( - dist/radius)

def decay(time,half_life):
    return 0.5**(time/float(half_life))

class RFSOM(Sheet):

    rmin = Parameter(0.0)
    rmax = Parameter(1.0)
    
    alpha_0 = Parameter(0.5)
    radius_0 = Parameter(1.0)
    
    training_length = Parameter(1000)

    # rf params
    rf_width = 0.1
    
    def __init__(self,**params):

        super(RFSOM,self).__init__(**params)

        self.projections = {}
        self.count = 0
        self.half_life = self.training_length/8

    def _connect_from(self,src,src_port=None,dest_port=None):
        Sheet._connect_from(self,src,src_port,dest_port)
        self.projections[src.name] = Projection(src=src, dest=self,
                                                rfs = [[ RF(src,center=(x,y),width=self.rf_width)
                                                         for x in self.sheet_cols() ]
                                                       for y in self.sheet_rows()[::-1] ])
                      
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
                rf = self.projections[input_sheet.name].rf(r,c)
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

        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                lattice_dist = norm((wc-c,wr-r))
                if  lattice_dist <= radius:
                    rf = self.projections[input_sheet.name].rf(r,c)
                    rate = self.alpha() * gaussian(lattice_dist,radius)
                    X = rf.get_input_matrix(input_activation)
                    rf.weights += rate * (X - rf.weights)
                                   
        self.count += 1 

    def input_event(self,src,src_port,dest_port,data):
        self.message("Received input from,",src,"at time",self.simulator.time())
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

class Projection(TopoObject):

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.__rfs = params['rfs']
        self.__src = params['src']
        self.__dest = params['dest']

    def src(self): return self.__src
    def dest(self): return self.__dest

    def rf(self,r,c):
        return self.__rfs[r][c]

    def plot_rfs(self,montage=True,file_format='ppm',file_prefix='',
                 pixel_scale = 255, pixel_offset = 0):
        from Numeric import concatenate as join
        import Image

        file_stem = file_prefix + self.__src.name + '-' + self.__dest.name
        if not montage:
            for r,row in enumerate(self.__rfs):
                for c,rf in enumerate(row):                    
                    im = Image.new('L',rf.weights.shape[::-1])
                    im.putdata(rf.weights.flat,scale=pixel_scale,offset=pixel_offset)

                    f = open(file_stem+'-RF-%0.4d-%0.4d.'%(r,c)+file_format,'w')
                    im.save(f,file_format)
                    f.close()
        else:
            data = join([join([rf.weights for rf in row],axis=1) for row in self.__rfs])
            im = Image.new('L',data.shape[::-1])
            im.putdata(data.flat,scale=pixel_scale,offset=pixel_offset)

            f = open(file_stem+'-RFS.'+file_format,'w')
            im.save(f,file_format)
            f.close()
            
            


class RF(TopoObject):
    
    def __init__(self,input_sheet,width=1.0,center=(0,0)):
        from boundingregion import BoundingBox
        from sheet import activation_submatrix

        super(RF,self).__init__()

        self.input_sheet = input_sheet

        self.verbose('center = %s, width= %.2f'%(`center`,width))
        xc,yc = center
        radius = width/2
        self.__bounds = BoundingBox(points=((xc-radius,yc-radius),(xc+radius,yc+radius)))

        weights_shape = activation_submatrix(self.__bounds,
                                             input_sheet.activation,
                                             input_sheet.bounds,
                                             input_sheet.density).shape
        self.verbose("activation matrix shape: ",weights_shape)
        self.weights = RandomArray.random(weights_shape)

    def bounds(self):
        return self.__bounds
    def contains(self,x,y):
        return self.__bounds.contains(x,y)

    def get_input_matrix(self, activation):
        from sheet import activation_submatrix
        return activation_submatrix(self.__bounds,activation,
                                    self.input_sheet.bounds,
                                    self.input_sheet.density)



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
    
