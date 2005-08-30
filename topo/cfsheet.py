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
add a .stimulation(input_activation) method to the Projection class
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

jbednar050621: The approach Jeff describes above sounds very
reasonable, except that instead of just adding the results to the
temp_activation matrix, each Projection also needs to store the
intermediate results, so that they can be retrieved when processing
subsequent input events (which will likely change only some of the
inputs, not all, e.g. only lateral weights, not afferent).  For
generality, the CFSheet should also not simply sum, but should sum by
default (and could e.g. multiply or gate one by another, though it is
not clear to me right now how that could be done.)

-- DONE: yfsit 2005/08 --

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
from MLab import flipud, rot90
from utils import *
from learningrules import *
from topo.utils import flatten


###############################################
from base import TopoObject


class ConnectionField(TopoObject):
    normalize = Parameter(default=0)
    x = Parameter(default=0)
    y = Parameter(default=0)
    weights = []
    slice_array = []
    
    def __init__(self,input_sheet,weight_bounds,weights_factory,**params):
        super(ConnectionField,self).__init__(**params)

        self.input_sheet = input_sheet
        self.bounds = weight_bounds

        self.slice = self.input_sheet.input_slice(self.bounds,self.x,self.y)
        r1,r2,c1,c2 = self.slice

        self.slice_array = Numeric.zeros((4), Numeric.Int32)
        self.slice_array[0] = r1
        self.slice_array[1] = r2
        self.slice_array[2] = c1
        self.slice_array[3] = c2


        if isinstance(weights_factory, UniformRandomFactory):
            self.weights = RandomArray.uniform(0,1,[r2-r1,c2-c1])
            #self.weights = Numeric.ones([r2-r1,c2-c1], Numeric.Float)
        else:
            self.weights = weights_factory(x=0,y=0,bounds=self.bounds,density=self.input_sheet.density,theta=0,rows=r2-r1,cols=c2-c1)

        self.verbose("activation matrix shape: ",self.weights.shape)

        if self.normalize:
            wts = self.weights
            s = sum(wts.flat)
            if s > 0:
                s = self.normalize/s
                wts *= s


    def contains(self,x,y):
        return self.bounds.contains(x,y)

    def get_input_matrix(self, activation):
        r1,r2,c1,c2 = self.slice

        return activation[r1:r2,c1:c2]


class Projection(TopoObject):
    """
    Projection takes one parameter:

    activation_fn: A function f(X,W) that takes two identically shaped
    matrices X (the input) and W (the ConnectionField weights) and
    computes a scalar stimulation value based on those weights.  The
    default is plastk.utils.mdot

    Any subclass of Projection has to implement the interface
    compute_response(self,input_activation,rows,cols) that computes
    the response resulted from the input and store them in the 
    temp_activation[] array.
    """

    activation_fn = Parameter(default=mdot)
    src = Parameter(default=None)
    dest = Parameter(default=None)
    cf_type = Parameter(default=ConnectionField)
    strength = Number(default=1.0)
#   shape = property(get_shape)
    temp_activation = []

    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.cfs = None
        self.input_buffer = None
        self.temp_activation = Numeric.array(self.dest.activation)

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

    def compute_response(self,input_activation,rows,cols):
        pass


class KernelProjection(Projection):

    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_factory = Parameter(default=UniformRandomFactory())
    normalize = Parameter(default=0.0)
    dest_port = Parameter(default="")
    learning_rate = Parameter(default=0.0)

    def __init__(self,**params):
        super(KernelProjection,self).__init__(**params)
        
        # set up array of ConnectionFields translated to each x,y in the src sheet
        cfs = []
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                row.append(self.cf_type(input_sheet=self.src,weight_bounds=self.weights_bounds,normalize=self.normalize,weights_factory=self.weights_factory,x=x,y=y))

            cfs.append(row)
        self.set_cfs(cfs)


    def compute_response(self,input_activation, rows, cols):
        self.input_buffer = input_activation
        if self.activation_fn.func_name == "compute_response_mdot_c":
            # compute_response_mdot_c computes the mdot for all the units
            compute_response_mdot_c(input_activation, rows, cols, self.temp_activation, self.cfs, self.strength)
	else:
            for r in xrange(rows):
                for c in xrange(cols):
                    cf = self.cfs[r][c]
                    r1,r2,c1,c2 = cf.slice
                    X = input_activation[r1:r2,c1:c2]

                    self.temp_activation[r,c] = self.activation_fn(X,cf.weights)
            self.temp_activation *= self.strength


class CFSheet(Sheet):
    """
    A Sheet that computes activation via sets of weighted projections
    onto other sheets.

    A standard CFSheet expects its input to be generated from other
    Sheets. Upon receiving an input event, the CFSheet interprets the
    event data to be (a copy of) an activation matrix from another
    sheet.  The CFSheet computes a 'response' matrix for the
    Projection to the sheet that generated the event by calling the
    Projection's .compute_response() with the input activation region 
    as parameters.  This response is added to the Projection's temporary 
    activation buffer.  After all events have been processed for a given
    time, the CFSheet computes it's .activation matrix as 
    self.transfer_fn(self.temp_activation), where self.temp_activation
    is computed by summing all the Projections' temporary activation 
    buffers.  This activation is then sent on the default output port.

    CFSheet takes one parameters:

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
    
    transfer_fn  = Parameter(default=lambda x:Numeric.array(x))
    learning_fn = Parameter(default=hebbian_c)
                             
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
        self.projections[src.name].append(projection_type(src=src,dest=self,dest_port=dest_port,**projection_params))

    def input_event(self,src,src_port,dest_port,data):
        """
        Accept input from some sheet.  Call .present_input() to
        compute the stimulation from that sheet.
        """
        #self.message("Received input from",src,"at time",self.simulator.time())
        self.present_input(data,src,dest_port)
        self.new_input = True


    def pre_sleep(self):
        """
        Pass the accumulated stimulation through self.transfer_fn and
        send it out on the default output port.
        """
        if self.new_input:
            self.new_input = False
            self.temp_activation *= 0.0
            for name in self.projections:
                for proj in self.projections[name]:
                    self.temp_activation += proj.temp_activation
            self.activation = self.transfer_fn(self.temp_activation)
            self.send_output(data=self.activation)

            if self._learning:
                self.learn()

            #self.debug("max activation =",max(self.activation.flat))
            #print self.activation 

    def learn(self):
        """
        Override this method to implement learning/adaptation.  Called
        from self.pre_sleep() _after_ activation has been propagated.

        Important:  This function will not be called by pre_sleep()
        when the Sheet has learning disabled.  (See enable_learning(),
        and disable_learning())
        """
        pass

    def present_input(self,input_activation,input_sheet,dest_port):
        """
        Compute the stimulation caused by the given input_activation
        (matrix) produced by the given sheet.  Applies f(X,W) for each
        ConnectionField's weight matrix W and input matrix X for each
        projection from self to input_sheet and adds the result to the
        stimulation buffer.
        """
        rows,cols = self.activation.shape

        for proj in self.projections[input_sheet.name]:
            if proj.dest_port == dest_port:
                proj.compute_response(input_activation,rows,cols)
		break

    def get_projection_by_name(self,tname):
        """
        More often than not, a Projection is requested from a sheet,
        based upon it's name.  This hides the complex reverse
        addressing necessary.  Always returns a list in case of
        multiple name hits, but list may be empty if no projections
        have the name passed in as t(arget)name.
        """
        
        prjns = [p for name in self.projections
                       for p in self.projections[name]
                           if p.name == tname]
        return prjns


    #########################################################################
    # GUI support
    def unit_view(self,x,y):
        """
        Get a list of UnitView objects for a particular unit
        in this CFSheet.  Can return multiple UnitView objects.
        """
        from itertools import chain
        views = [p.get_view(x,y) for p in chain(*self.projections.values())]

        # Old version to delete:
        # self.debug('views = '+str(views)+'type = '+str(type(views[0]))+str(views[0].view()))
        # key = ('Weights',x,y)
        # self.add_sheet_view(key,views)      # Will be adding a list
        # self.debug('Added to sheet_view_dict', views, 'at', key)

        # Delete previous entry if it exists.  Allows appending in next block.
        for v in views:
            key = ('Weights',v.projection.dest.name,v.projection.name,x,y)
            if v.projection.src.sheet_view_dict.has_key(key):
                v.projection.src.release_sheet_view(key)

        for v in views:
            src = v.projection.src
            key = ('Weights',v.projection.dest.name,v.projection.name,x,y)
            unit_list = src.sheet_view_dict.get(key,[])
            unit_list.append(v)
            src.add_sheet_view(key,unit_list)      # Will be adding a list
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
            (name,s,p,x,y) = request
            return self.unit_view(x,y)
        else:
            return Sheet.sheet_view(self,request)
        
