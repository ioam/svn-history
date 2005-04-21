"""
Superclass for sheets that take input through connection fields.

This module defines three basic classes of objects used to create
simulations of cortical sheets that take input through connection
fields projected onto other cortical sheets, or laterally onto
themselves.  These classes are:

CFSheet: a subclass of topo.sheet.Sheet.

Projection: a class to handle one projection of ConnectionFields from
one Sheet into a CFSheet.

ConnectionField: a class for specifying a single connection field within a
Projection.

The module also defines KernelProjection, a subclass of Projection
that defines projections of connection fields where each
ConnectionField's initial weight matrix is created by calling a
KernelFactory.


The CFSheet class should be sufficient to create a non-learning sheet
that computes its activation via the contribution of many local
connection fields.  The activation output can be changed by changing
the parameters CFSheet.activation_fn and CFSheet.transfer_fn.  (See
CFSheet class documentation for more details).  To implement learning
one must create a subclass and override the default .learn() method.


JEFF's IMPLEMENTATION NOTES

* Non-rectangular ConnectionField bounds *

Under the current implementation, I don't think learning rules like
the one in lissom.ty will work correctly with non-rectangular
ConnectionField bounds.  The learning rule is written to update each
ConnectionField's entire weight matrix in a single step, and it will
(I think) modify weights that are outside the bounds.  One way to
handle this without having to call bounds.contains(x,y) for each and
every weight value is to augment the current ConnectionField
implementation with a 'mask' matrix of zeroes and ones indicating
which weights actually belong in the ConnectionField.  After doing the
learning step, do cf.weights *= cf.mask.

* Computing stimulation in Projection objects *

Currently each CFSheet object explicitly computes the activation of
each ConnectionField in each projection by getting that
ConnectionField's input matrix and calling the activation function on
it with the ConnectionField's weights.  It would be more modular to
add a .simulation(input_activation) method to the Projection class
interface that would by default do what CFSheet does now.  Then
CFSheet would, on input, just call the .stimulation() methods on the
appropriate projections and add the results to its .temp_activation
matrix.  In this scenario, the activation_fn parameter would move to
Projection, or, better one of its subclasses, since one could conceive
of Projections that compute their stimulation through some entirely
different algorithm.

BTW, in this case, the class CFSheet really isn't so much an 'cf
sheet' as it is a 'projection sheet', that sums the contributions of
many projections, and then passes them through a transfer function.
This structure has an elegant kind of parsimony, where the Sheet is
the large-scale analog of a neuron and the projection is the
large-scale analog of the individual connection.

$Id$
"""

__version__ = '$Revision$'

from params import *
from sheet import Sheet
from kernelfactory import UniformRandomFactory
from utils import mdot
from boundingregion import Intersection,BoundingBox
import RandomArray,Numeric,copy
import topo.sheetview
import topo.boundingregion
import topo.bitmap
from topo.utils import flatten


###############################################
from base import TopoObject


class ConnectionField(TopoObject):
    
    def __init__(self,input_sheet,weights,bounds,**params):
        super(ConnectionField,self).__init__(**params)
        self.input_sheet = input_sheet
        self.bounds = bounds
        self.weights = weights
        self.verbose("activation matrix shape: ",self.weights.shape)

    def contains(self,x,y):
        return self.bounds.contains(x,y)

    def get_input_matrix(self, activation):
        return self.input_sheet.activation_submatrix(self.bounds,activation)


class Projection(TopoObject):

    src = Parameter(default=None)
    dest = Parameter(default=None)
    cf_type = Parameter(default=ConnectionField)

    strength = Number(default=1.0)

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.__cfs = None
        self.input_buffer = None

    def cf(self,r,c):
        return self.__cfs[r][c]

    def set_cfs(self,cf_list):
        self.__cfs = cf_list

    def get_shape(self):
        return len(self.__cfs),len(self.__cfs[0])

    shape = property(get_shape)

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
        (x,y) = (self.dest).sheet2matrix(sheet_x,sheet_y)
        # composite_name = '%s: %0.3f, %0.3f' % (self.name, sheet_x, sheet_y)
        matrix_data = Numeric.array(self.cf(y,x).weights)
        # print 'matrix_data = ', matrix_data
        new_box = self.dest.bounds  # TURN INTO A PROPER COPY
        assert matrix_data != None, "Projection Matrix is None"
        return topo.sheetview.UnitView((matrix_data,new_box),
                                       sheet_x,sheet_y,self,
                                       view_type='UnitView')


    
    def plot_cfs(self,montage=True,file_format='ppm',file_prefix='',
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
            for r,row in enumerate(self.__cfs):
                for c,cf in enumerate(row):                    
                    im = Image.new('L',cf.weights.shape[::-1])
                    im.putdata(cf.weights.flat,scale=pixel_scale,offset=pixel_offset)

                    f = open(file_stem+'-CF-%0.4d-%0.4d.'%(r,c)+file_format,'w')
                    im.save(f,file_format)
                    f.close()
        else:
            data = join([join([add_border(cf.weights) for cf in row],axis=1) for row in self.__cfs])
            im = Image.new('L',data.shape[::-1])
            im.putdata(data.flat,scale=pixel_scale,offset=pixel_offset)

            f = open(file_stem+'-CFS.'+file_format,'w')
            im.save(f,file_format)
            f.close()


class KernelProjection(Projection):

    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_factory = Parameter(default=UniformRandomFactory())

    def __init__(self,**params):
        super(KernelProjection,self).__init__(**params)
        
        # set up array of ConnectionFields translated to each x,y in the src sheet
        cfs = []
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                # Move the kernel factory to the right position,
                bounds = copy.deepcopy(self.weights_bounds)
                bounds.translate(x,y)
                bounds = Intersection(bounds,self.src.bounds)
                weights = self.weights_factory(x=x,y=y,bounds=bounds,density=self.src.density)
                row.append(self.cf_type(self.src,weights=weights,bounds=bounds))
            cfs.append(row)
        self.set_cfs(cfs)

    


class CFSheet(Sheet):
    """
    A Sheet that computes activation via sets of weighted projections
    onto other sheets.

    A standard CFSheet expects its input to be generated from other
    Sheets. Upon receiving an input event, the CFSheet interprets the
    event data to be (a copy of) an activation matrix from another
    sheet.  The CFSheet computes a 'stimulation' matrix for each
    Projection to the sheet that generated the event by looping over
    the Projection's matrix of ConnectionFields and calling the
    CFSheet's .activation_fn() with the ConnectionField's weight
    matrix and input activation region as parameters.  This
    stimulation is added to a temporary activation buffer.  After all
    events have been processed for a given time, the CFSheet computes
    it's .activation matrix as self.transfer_fn(self.temp_activation).
    This activation is then sent on the default output port.

    CFSheet takes two parameters:

    activation_fn: A function f(X,W) that takes two identically shaped
    matrices X (the input) and W (the ConnectionField weights) and
    computes a scalar stimulation value based on those weights.  The
    default is plastk.utils.mdot

    transfer_fn: A function that s(A) that takes an activation matrix
    A and produces and identically shaped output matrix. The default
    is the identity function.

    * Connections *

    A CFSheet connection from another sheet takes two parameters:

    projection_type: The type of projection to use for the
    connection. default = KernelProjection

    projection_params: A dictionary of keyword arguments for the
    projection constructor.  default = {}

    e.g. Given a simulator sim, an input sheet s1 and a CFSheet s2,
    one might connect them thus:

    sim.connect(s1,s2,projection_type=MyProjectionType,
                      projection_params=dict(a=1,b=2))

    s2 would then construct a new projection of type MyProjectionType
    with the parameters (a=1,b=2).
    """
    
    activation_fn = Parameter(default=mdot)
    transfer_fn  = Parameter(default=lambda x:Numeric.array(x))
                             
    def __init__(self,**params):
        super(CFSheet,self).__init__(**params)
        self.temp_activation = Numeric.array(self.activation)
        self.projections = {}
        self.new_input = False

    def _connect_from(self,src,src_port,dest_port,
                      projection_type=KernelProjection,
                      projection_params={},
                      **args):

        """
        Accept a connection from src, on src_port, for dest_port.
        Construct a new Projection of type projection_type using the
        parameters in projection_params.
        """
        
        Sheet._connect_from(self,src,src_port,dest_port,**args)
        if src.name not in self.projections:
            self.projections[src.name] = []
        self.projections[src.name].append(projection_type(src=src, dest=self,**projection_params))

    def input_event(self,src,src_port,dest_port,data):
        """
        Accept input from some sheet.  Call .present_input() to
        compute the stimulation from that sheet.
        """
        self.message("Received input from",src,"at time",self.simulator.time())
        self.present_input(data,src)
        self.new_input = True

    def pre_sleep(self):
        """
        Pass the accumulated stimulation through self.transfer_fn and
        send it out on the default output port.
        """
        if self.new_input:
            self.new_input = False
            self.activation = self.transfer_fn(self.temp_activation)
            self.send_output(data=self.activation)
            self.temp_activation *= 0.0

            if self.learning:
                self.learn()

            self.debug("max activation =",max(self.activation.flat))

    def learn(self):
        """
        Override this method to implement learning/adaptation.  Called
        from self.pre_sleep() _after_ activation has been propagated.

        Important:  This function will not be called by pre_sleep()
        when the Sheet has learning disabled.  (See enable_learning(),
        and disable_learning())
        """
        pass

    def present_input(self,input_activation,input_sheet):
        """
        Compute the stimulation caused by the given input_activation
        (matrix) produced by the given sheet.  Applies f(X,W) for each
        ConnectionField's weight matrix W and input matrix X for each
        projection from self to input_sheet and adds the result to the
        stimulation buffer.
        """
        rows,cols = self.activation.shape

        for proj in self.projections[input_sheet.name]:
            proj.input_buffer = input_activation
            for r in range(rows):
                for c in range(cols):
                        cf = proj.cf(r,c)
                        X = cf.get_input_matrix(input_activation)
                        self.temp_activation[r,c] += proj.strength * self.activation_fn(X,cf.weights)


    #########################################################################
    # GUI support
    def unit_view(self,x,y):
        """
        Get a list of UnitView objects for a particular unit
        in this CFSheet.  Can return multiple UnitView objects.
        """
        from itertools import chain
        views = [p.get_view(x,y) for p in chain(*self.projections.values())]
        self.debug('views = '+str(views)+'type = '+str(type(views[0]))+str(views[0].view()))
        key = ('Weights',x,y)
        self.add_sheet_view(key,views)      # Will be adding a list
        self.debug('Added to sheet_view_dict', views, 'at', key)
        return views

    def release_unit_view(self,x,y):
        self.release_sheet_view(('Weights',x,y))

    def sheet_view(self,request='Activation'):
        """

        Check for 'Weights' or 'WeightsArray', but then call
        Sheet.sheet_view().  The addition of unit_view() means that
        it's now possible for one sheet_view request to return
        multiple UnitView objects, which are subclasses of SheetViews.

        """
        self.debug('request = ' + str(request))
        if isinstance(request,tuple) and request[0] == 'Weights':
            (name,x,y) = request
            return self.unit_view(x,y)
        else:
            return Sheet.sheet_view(self,request)
        
