"""
Generic class for sheets that take input through receptive fields.

$Id$
"""

from params import Parameter
from sheet import Sheet
from kernelfactory import UniformRandomFactory
from utils import mdot
from boundingregion import Intersection
import RandomArray,Numeric,copy
import topo.sheetview
import topo.boundingregion
import topo.bitmap
from topo.base import flatten


###############################################
from base import TopoObject

class Projection(TopoObject):

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.__rfs = params['rfs']
        self.__src = params['src']
        self.__dest = params['dest']
        self.input_buffer = None

    def src(self): return self.__src
    def dest(self): return self.__dest

    def rf(self,r,c):
        return self.__rfs[r][c]

    def get_shape(self):
        return len(self.__rfs),len(self.__rfs[0])

    shape = property(get_shape)


    def get_view(self,sheet_r, sheet_c, pixel_scale = 255, offset = 0):
        """
        Return a single receptive field UnitView, for the unit at
        sheet_r, sheet_c.  sheet_r and sheet_c are assumed to be in
        sheet coordinates.

        offset and pixel scale are currently unused.  The original
        version of the function passed it to a PIL Image object, but
        this does not, though it should in the future.

        NOTE: BOUNDS MUST BE PROPERLY SET. CURRENTLY A STUB IS IN EFFECT.
        """
        (r,c) = (self.dest()).sheet2matrix(sheet_r,sheet_c)
        composite_name = self.name + ': ' + str(sheet_r) + ',' + str(sheet_c)
        matrix_data = Numeric.array(self.rf(r,c).weights)
        # print 'matrix_data = ', matrix_data
        new_box = self.dest().bounds  # TURN INTO A PROPER COPY
        assert matrix_data != None, "Projection Matrix is None"
        return topo.sheetview.UnitView((matrix_data,new_box),
                                       sheet_r,sheet_c,name=composite_name)


    def get_arrayview(self,skip, pixel_scale = 255, offset = 0):
        """
        INCOMPLETE.  MAY NOT EVEN EXECUTE CORRECTLY SINCE NEVER CALLED.

        Return a single receptive field UnitView, for the unit at
        sheet_r, sheet_c.  sheet_r and sheet_c are assumed to be in
        sheet coordinates.

        offset and pixel scale are currently unused.  The original
        version of the function passed it to a PIL Image object, but
        this does not, though it should in the future.

        NOTE: BOUNDS MUST BE PROPERLY SET. CURRENTLY A STUB IS IN EFFECT.
        """
        (r,c) = (self.dest()).sheet2matrix(sheet_r,sheet_c)
        composite_name = self.name + ' Array'
        # print 'matrix_data = ', matrix_data
        new_box = self.dest().bounds  # WHAT DOES A BBOX MEAN FOR AN ARRAY?
        assert matrix_data != None, "Projection Matrix is None"
        for r,row in enumerate(self.__rfs):
            for c,rf in enumerate(row):                    
                im = Image.new('L',rf.weights.shape[::-1])
                im.putdata(rf.weights.flat,scale=pixel_scale,offset=pixel_offset)
                
                bm = topo.bitmap.BWMap(im)
        return topo.sheetview.UnitView((bm,new_box),
                                       sheet_r,sheet_c,name=composite_name)

    
    def plot_rfs(self,montage=True,file_format='ppm',file_prefix='',
                 pixel_scale = 255, pixel_offset = 0):
        """
        DEPRICATED:  This function can still be used to dump the weights to
        files, but any reason to use this function means that the necessary
        replacement has not been written yet.
        """
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
        self.verbose("activation matrix shape: ",self.weights.shape)

    def contains(self,x,y):
        return self.bounds.contains(x,y)

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
        self.ports = {}
        self.new_input = False

    def _connect_from(self,src,src_port=None,dest_port=None):
        Sheet._connect_from(self,src,src_port,dest_port)
        # set up array of RFs translated to each x,y in the sheet
        rfs = []
        old_bounds = self.weights_factory.bounds
        old_x,old_y = self.weights_factory.x,self.weights_factory.y
        for y in self.sheet_rows()[::-1]:
            row = []
            for x in self.sheet_cols():
                # Move the kernel factory to the right position,
                bounds = copy.deepcopy(old_bounds)
                bounds.translate(x,y)
                bounds = Intersection(bounds,src.bounds)
                weights = self.weights_factory(x=x,y=y,bounds=bounds,density=src.density)
                row.append(self.rf_type(src,weights=weights,bounds=bounds))
            rfs.append(row)

        if dest_port not in self.ports:
            self.ports[dest_port] = dict(projections={})
        projections = self.ports[dest_port]['projections']
        if src.name in projections:
            self.warning('Overwriting projection to "%s" on port "%s"' % (src.name,dest_port))
        projections[src.name] = Projection(src=src, dest=self, rfs=rfs)

    def get_projections(self):
        from operator import add
        return reduce(add,[port['projections'].values() for port in self.ports.values()])

    projections = property(get_projections,
                           doc="The list of all projections on all ports (read only).")

    def input_event(self,src,src_port,dest_port,data):
        self.message("Received input from,",src,"at time",self.simulator.time())
        self.present_input(data,src,dest_port)
        self.new_input = True

    def pre_sleep(self):
        if self.new_input:
            self.new_input = False
            self.activation = self.transfer_fn(self.temp_activation)
            self.send_output(data=self.activation)
            self.temp_activation *= 0.0

            self.train()

            for port in self.ports.values():
                for proj in port['projections'].values():
                    proj.input_buffer = None
            self.debug("max activation =",max(self.activation.flat))

    def train(self):
        pass

    def present_input(self,input_activation,input_sheet,port):
        rows,cols = self.activation.shape
        proj = self.ports[port]['projections'][input_sheet.name]
        proj.input_buffer = input_activation
        for r in range(rows):
            for c in range(cols):
                    rf = proj.rf(r,c)
                    X = rf.get_input_matrix(input_activation)
                    self.temp_activation[r,c] += self.activation_fn(X,rf.weights)


    ################################################################################
    # GUI support
    def unit_view(self,r,c):
        """
        Get a list of UnitView objects for a particular unit
        in this RFSheet.  Can return multiple UnitView objects.
        """
        views = flatten([p.get_view(r,c) for p in self.projections])
        self.debug('views = '+str(views)+'type = '+str(type(views[0]))+str(views[0].view()))
        key = ('Weights',r,c)
        self.add_sheet_view(key,views)      # Will be adding a list
        self.debug('Added to sheet_view_dict', views, 'at', key)
        return views


    def sheet_view(self,request='Activation'):
        """
        Check for unit_view, but then call Sheet.sheet_view().  The
        addition of unit_view() means that it's now possible for one
        sheet_view request to return multiple UnitView objects, which
        are subclasses of SheetViews.
        """
        self.debug('request = ' + str(request))
        if isinstance(request,tuple) and request[0] == 'Weights':
            (name,r,c) = request
            return self.unit_view(r,c)
        else:
            return Sheet.sheet_view(self,request)
        
