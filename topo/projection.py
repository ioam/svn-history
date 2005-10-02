"""
Projection: a class to handle a projection of ConnectionFields from
one Sheet into a CFSheet.
"""

from topo.parameter import Parameter, Number
from topo.utils import mdot
import Numeric
from topo.learningrules import *
from topo.base import TopoObject
from topo.cfsheet import ConnectionField


class Projection(TopoObject):
    """
    Projection takes one parameter:

    activation_fn: A function f(X,W) that takes two identically shaped
    matrices X (the input) and W (the ConnectionField weights) and
    computes a scalar stimulation value based on those weights.  The
    default is plastk.utils.mdot

    Any subclass of Projection has to implement the interface
    compute_response(self,input_activity,rows,cols) that computes
    the response resulted from the input and store them in the 
    temp_activity[] array.
    """

    ### JABHACKALERT!
    ### 
    ### The temp_activity array should be named something more
    ### informative, i.e. whatever it actually is.  In this case it's
    ### not really an activity, just the scalar result of applying
    ### the weight matrix to the input matrix.
    activation_fn = Parameter(default=mdot)
    src = Parameter(default=None)
    dest = Parameter(default=None)
    cf_type = Parameter(default=ConnectionField)
    strength = Number(default=1.0)
#   shape = property(get_shape)
    temp_activity = []

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.cfs = None
        self.input_buffer = None
        self.temp_activity = Numeric.array(self.dest.activity)

    def cf(self,r,c):
        return self.cfs[r][c]

    def set_cfs(self,cf_list):
        self.cfs = cf_list

    def get_shape(self):
        return len(self.cfs),len(self.cfs[0])


    def get_view(self,sheet_x, sheet_y, pixel_scale = 255, offset = 0):
        """
        Return a single connection field UnitView, for the unit at
        sheet_x, sheet_y.  sheet_x and sheet_y are assumed to be in
        sheet coordinates.

        offset and pixel scale are currently unused.  The original
        version of the function passed it to a PIL Image object, but
        this does not, though it should in the future.

        NOTE: BOUNDS MUST BE PROPERLY SET. CURRENTLY A STUB IS IN EFFECT.
        """
        (r,c) = (self.dest).sheet2matrix(sheet_x,sheet_y)
        # composite_name = '%s: %0.3f, %0.3f' % (self.name, sheet_x, sheet_y)
        #matrix_data = Numeric.array(Numeric.transpose(self.cf(r,c).weights))
        matrix_data = Numeric.array(self.cf(r,c).weights)
        #matrix_data = Numeric.array(self.cf(r,c).weights)*50
        new_box = self.dest.bounds  # TURN INTO A PROPER COPY
        assert matrix_data != None, "Projection Matrix is None"
        return topo.sheetview.UnitView((matrix_data,new_box),
                                       sheet_x,sheet_y,self,
                                       view_type='UnitView')


    
    def plot_cfs(self,montage=True,file_format='ppm',file_prefix='',
                 pixel_scale = 255, pixel_offset = 0):
        """
        DEPRECATED:  This function can still be used to dump the weights to
        files, but any reason to use this function means that the necessary
        replacement has not yet been written.
        """
        from Numeric import concatenate as join
        import Image
        from utils import add_border

        file_stem = file_prefix + self.__src.name + '-' + self.__dest.name
        if not montage:
            for r,row in enumerate(self.cfs):
                for c,cf in enumerate(row):                    
                    im = Image.new('L',cf.weights.shape[::-1])
                    im.putdata(cf.weights.flat,scale=pixel_scale,offset=pixel_offset)

                    f = open(file_stem+'-CF-%0.4d-%0.4d.'%(r,c)+file_format,'w')
                    im.save(f,file_format)
                    f.close()
        else:
            data = join([join([add_border(cf.weights) for cf in row],axis=1) for row in self.cfs])
            im = Image.new('L',data.shape[::-1])
            im.putdata(data.flat,scale=pixel_scale,offset=pixel_offset)

            f = open(file_stem+'-CFS.'+file_format,'w')
            im.save(f,file_format)
            f.close()

    def compute_response(self,input_activity,rows,cols):
        pass

    def reduce_cfsize(self, new_wt_bounds):
        pass

