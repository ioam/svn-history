"""
Generic class for sheets that take input through receptive fields.

$Id$
"""
from params import Parameter
from sheet import Sheet
from utils import mdot
import RandomArray,Numeric


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
        from utils import add_border

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
            data = join([join([add_border(rf.weights) for rf in row],axis=1) for row in self.__rfs])
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



class RFSheet(Sheet):

    # rf params
    projection_type = Parameter(Projection)
    rf_type = Parameter(default=RF)

    activation_fn = Parameter(default=mdot)
    transfer_fn  = Parameter(default=lambda x:Numeric.array(x))
                             

    def __init__(self,**params):
        super(RFSheet,self).__init__(**params)
        self.temp_activation = Numeric.array(self.activation)

    def _connect_from(self,src,src_port=None,dest_port=None):
        Sheet._connect_from(self,src,src_port,dest_port)
        if src.name not in self.projections:
            self.projections[src.name] = []
        self.projections[src.name].append(Projection(src=src, dest=self,
                                                     rfs = [[ RF(src,center=(x,y),width=self.rf_width)
                                                              for x in self.sheet_cols() ]
                                                            for y in self.sheet_rows()[::-1] ]) )

    def input_event(self,src,src_port,dest_port,data):
        self.message("Received input from,",src,"at time",self.simulator.time())
        self.train(data,src)

    def pre_sleep(self):
        self.activation = self.transfer_fn(self.temp_activation)
        self.send_output(data=self.activation)
        self.temp_activation *= 0.0


    def present_input(self,input_activation,input_sheet):
        rows,cols = self.activation.shape
        for r in range(rows):
            for c in range(cols):
                for proj in self.projections[input_sheet.name]:
                    rf = proj.rf(r,c)
                    X = rf.get_input_matrix(input_activation)
                    self.temp_activation[r,c] += self.activation_fn(X,rf.weights)

    def train(self,input_activation,input_sheet):
        raise NYI
