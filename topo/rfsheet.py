"""
Generic class for sheets that take input through receptive fields.

$Id$
"""

from params import Parameter
from sheet import Sheet
from kernelfactory import UniformRandomFactory
from utils import mdot
import RandomArray,Numeric,copy


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
    
    def __init__(self,input_sheet,weights,bounds,**params):
        from sheet import activation_submatrix
        super(RF,self).__init__(**params)
        self.input_sheet = input_sheet
        self.bounds = bounds
        self.weights = weights
        self._crop_to_src()
        self.verbose("activation matrix shape: ",self.weights.shape)

    def contains(self,x,y):
        return self.bounds.contains(x,y)

    def _crop_to_src(self):
        l,b,r,t = self.bounds.aarect().lbrt()
        src_l,src_b,src_r,src_t = self.input_sheet.bounds.aarect().lbrt()
        rmin,cmin = 0,0
        rmax,cmax = self.weights.shape

        slice_rows,slice_cols = self.get_input_matrix(self.input_sheet.activation).shape

        if rmax != slice_rows:
            if t >= src_t:
                rmin += rmax - slice_rows
            if b <= src_b:
                rmax -= (rmax - rmin) - slice_rows
        if cmax != slice_cols:
            if l <= src_l:
                cmin += cmax - slice_cols
            if r >= src_r:
                cmax -= (cmax - cmin) - slice_cols

        self.weights = self.weights[rmin:rmax,cmin:cmax]
        assert self.weights.shape == (slice_rows,slice_cols)

    def get_input_matrix(self, activation):
        from sheet import activation_submatrix
        return activation_submatrix(self.bounds,activation,
                                    self.input_sheet.bounds,
                                    self.input_sheet.density)



class RFSheet(Sheet):

    # rf params
    rf_type = Parameter(default=RF)

    activation_fn = Parameter(default=mdot)
    transfer_fn  = Parameter(default=lambda x:Numeric.array(x))
                             
    weights_factory = Parameter(default=UniformRandomFactory())

    def __init__(self,**params):
        super(RFSheet,self).__init__(**params)
        self.temp_activation = Numeric.array(self.activation)
        self.projections = {}

    def _connect_from(self,src,src_port=None,dest_port=None):
        Sheet._connect_from(self,src,src_port,dest_port)
        if src.name not in self.projections:
            self.projections[src.name] = []
        # set up array of RFs translated to each x,y in the sheet
        rfs = []
        old_bounds = self.weights_factory.bounds
        old_x,old_y = self.weights_factory.x,self.weights_factory.y
        for y in self.sheet_rows()[::-1]:
            row = []
            for x in self.sheet_cols():
                # Move the kernel factory to the right position,
                # TODO: this is a hack, the factory should allow parameter
                # overiding when called.
                bounds = copy.deepcopy(old_bounds)
                bounds.translate(x,y)
                self.weights_factory.x = x
                self.weights_factory.y = y
                self.weights_factory.bounds = bounds
                weights = self.weights_factory()
                row.append(self.rf_type(src,weights=weights,bounds=bounds))
            rfs.append(row)
            self.weights_factory.x = old_x
            self.weights_factory.y = old_y
            self.weights_factory.bounds = old_bounds
                          
        self.projections[src.name].append(Projection(src=src, dest=self, rfs=rfs))

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
        pass
