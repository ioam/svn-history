"""
Superclass for sheets that take input through connection fields.

This module defines two basic classes of objects used to create
simulations of cortical sheets that take input through connection
fields projected onto other cortical sheets, or laterally onto
themselves.  These classes are:

CFSheet: a subclass of sheet.Sheet.

ConnectionField: a class for specifying a single connection field within a
Projection.

The CFSheet class should be sufficient to create a non-learning sheet
that computes its activity via the contribution of many local
connection fields.  The activity output can be changed by changing
the parameters CFSheet.activation_fn and CFSheet.transfer_fn.  (See
CFSheet class documentation for more details).  To implement learning
one must create a subclass and override the default .learn() method.

$Id$
"""

__version__ = '$Revision$'


### JEFF's IMPLEMENTATION NOTES
### 
### Non-rectangular ConnectionField bounds
### 
### Under the current implementation, I don't think learning rules like
### the one in lissom.ty will work correctly with non-rectangular
### ConnectionField bounds.  The learning rule is written to update each
### ConnectionField's entire weight matrix in a single step, and it will
### (I think) modify weights that are outside the bounds.  One way to
### handle this without having to call bounds.contains(x,y) for each and
### every weight value is to augment the current ConnectionField
### implementation with a 'mask' matrix of zeroes and ones indicating
### which weights actually belong in the ConnectionField.  After doing the
### learning step, do cf.weights *= cf.mask. jbednar: See MaskedArray
### for an alternative.

import Numeric

from object import TopoObject
from parameter import Parameter,BooleanParameter
from sheet import Sheet
from learningrules import divisive_normalization

### JABHACKALERT! This should presumably move to its own file or to Projection;
### CFSheet does not use it directly.
class ConnectionField(TopoObject):
    x = Parameter(default=0)
    y = Parameter(default=0)
    normalize = BooleanParameter(default=False)
    normalize_fn = Parameter(default=divisive_normalization)

    weights = []
    slice_array = []
    
    def __init__(self,input_sheet,weight_bounds,weights_generator,weight_type=Numeric.Float32,**params):
        super(ConnectionField,self).__init__(**params)

        self.input_sheet = input_sheet
        self.bounds = weight_bounds

        self.slice = self.input_sheet.input_slice(self.bounds,self.x,self.y)
        r1,r2,c1,c2 = self.slice


        # Numeric.Int32 is specified explicitly here to avoid having it
        # default to Numeric.Int.  Numeric.Int works on 32-bit platforms,
        # but does not work properly with the optimized C activation and
        # learning functions on 64-bit machines.
        self.slice_array = Numeric.zeros((4), Numeric.Int32)
        self.slice_array[0] = r1
        self.slice_array[1] = r2
        self.slice_array[2] = c1
        self.slice_array[3] = c2


        # set up the weights
        w = weights_generator(x=0,y=0,bounds=self.bounds,density=self.input_sheet.density,theta=0,rows=r2-r1,cols=c2-c1)
        self.weights = w.astype(weight_type)

        # Maintain the original type throughout operations, i.e. do not
        # promote to double.
        self.weights.savespace(1)

        self.verbose("activity matrix shape: ",self.weights.shape)

        if self.normalize:
            self.normalize_fn(self.weights)


    def contains(self,x,y):
        return self.bounds.contains(x,y)

    def get_input_matrix(self, activity):
        r1,r2,c1,c2 = self.slice

        return activity[r1:r2,c1:c2]

    def reduce_radius(self, new_wt_bounds):
        """
        Reduce the radius of an existing connection field. Weights are copied
        from the old weight array.
        """

        slice = self.input_sheet.input_slice(new_wt_bounds, self.x, self.y)

        if slice != self.slice:
            self.bounds = new_wt_bounds
            or1,or2,oc1,oc2 = self.slice
            self.slice = slice
            r1,r2,c1,c2 = slice

            self.slice_array[0] = r1
            self.slice_array[1] = r2
            self.slice_array[2] = c1
            self.slice_array[3] = c2

            self.weights = Numeric.array(self.weights[r1-or1:r2-or1,c1-oc1:c2-oc1],copy=1)
            self.weights.savespace(1)

            if self.normalize:
                self.normalize_fn(self.weights)

class ProjectionSheet(Sheet):
    """
    A Sheet whose activity is computed using projections from other sheets.

    A standard ProjectionSheet expects its input to be generated from
    other Sheets. Upon receiving an input event, the ProjectionSheet
    interprets the event data to be (a copy of) an activity matrix
    from another sheet.  The ProjectionSheet provides a copy of this
    matrix to each Projection from that input Sheet, asking each one
    to compute their own activity in response.  The same occurs for
    any other pending input events.

    After all events have been processed for a given time, the
    ProjectionSheet computes its own activity matrix using its
    activate() method, which by default sums all its Projections'
    activity matrices and passes the result through a user-specified
    transfer_fn() before sending it out on the default output port.
    The activate() method can be overridden to treat sum some of the
    connections, multiply that by the sum of other connections, etc.,
    to model modulatory or other more complicated types of connection
    influences.

    The transfer_fn is a function s(A) that takes an activity matrix
    A and produces and identically shaped output matrix. The default
    is the identity function.

    A ProjectionSheet connection from another sheet takes two parameters:

    projection_type: The type of projection to use for the connection.

    projection_params: A dictionary of keyword arguments for the
    projection constructor (defaulting to the empty dictionary {}).

    For instance, given a simulator sim, an input sheet s1 and a
    ProjectionSheet s2, one might connect them thus:

    sim.connect(s1,s2,projection_type=MyProjectionType,
                      projection_params=dict(a=1,b=2))

    s2 would then construct a new projection of type MyProjectionType
    with the parameters (a=1,b=2).
    """

    transfer_fn  = Parameter(default=lambda x:Numeric.array(x))
    # default learning function does nothing
    learning_fn = Parameter(default=lambda *args: 0)
                             
    def __init__(self,**params):
        super(ProjectionSheet,self).__init__(**params)
        self.projections = {}
        self.new_input = False

    ### JABHACKALERT!
    ###
    ### What's the projections list for?  Isn't it redundant with
    ### the connections list?  Seems like that's a relic from
    ### back when projections were not a subclass of EPConnection.
    ### This implementation needs to be cleaned up and unified with
    ### the corresponding implementation in EventProcessor.
    def _connect_from(self, proj, **args):
        """
        Accept a connection from src, on src_port, for dest_port.
        Construct a new Projection of type projection_type using the
        parameters in projection_params.
        """
        
        Sheet._connect_from(self,proj,**args)
        if proj.src.name not in self.projections:
            self.projections[proj.src.name] = []
        self.projections[proj.src.name].append(proj)

    def input_event(self,src,src_port,dest_port,data):
        """
        Accept input from some sheet.  Call .present_input() to
        compute the stimulation from that sheet.
        """
        #self.message("Received input from",src,"at time",self.simulator.time())
        self.present_input(data,src,dest_port)
        self.new_input = True


    def activate(self):
        """
        Collect activity from each projection, combine it to calculate
        the activity for this sheet, and send the result out.
        """
        self.activity *= 0.0
        for name in self.projections:
            for proj in self.projections[name]:
                self.activity+= proj.activity
        self.activity = self.transfer_fn(self.activity)
        self.send_output(data=self.activity)

        if self._learning:
            self.learn()

    def pre_sleep(self):
        """
        Called by the simulator after all the events are processed for the 
        current time but before time advances.  Allows the event processor
        to send any events that must be sent before time advances to drive
        the simulation. 
        """
        if self.new_input:
            self.activate()
            self.new_input = False

    def learn(self):
        """
        Override this method to implement learning/adaptation.  Called
        from self.pre_sleep() _after_ activity has been propagated.
        """
        pass

    def present_input(self,input_activity,input_sheet,dest_port):
        """
        Compute the stimulation caused by the given input_activity
        (matrix) produced by the given sheet.  Applies f(X,W) for each
        ConnectionField's weight matrix W and input matrix X for each
        projection from self to input_sheet and adds the result to the
        stimulation buffer.
        """
        rows,cols = self.activity.shape

        for proj in self.projections[input_sheet.name]:
            if proj.dest_port == dest_port:
                proj.activate(input_activity,rows,cols)
		break

    def get_projection_by_name(self,tname):
        """
        More often than not, a Projection is requested by name from a
        sheet, rather than by the location in the projections list.
        This code hides the complex reverse addressing necessary.
        Always returns a list in case of multiple name hits, but the
        list may be empty if no projections have a name matching the
        one passed in as t(arget)name.
        """
        
        prjns = [p for name in self.projections
                       for p in self.projections[name]
                           if p.name == tname]
        return prjns



class CFSheet(ProjectionSheet):
    """
    A ProjectionSheet providing access to the ConnectionFields in its CFProjections.

    ProjectionSheet classes do not assume that the Projections can
    provide a set of weights for individual units, or indeed that
    there are units or weights at all.  In contrast, CFSheet is built
    around the assumption that there are units in this Sheet, indexed
    by Sheet coordinates (x,y), and that these units have one or more
    ConnectionField connections on another Sheet (via CFProjections).
    It then provides a way to visualize these ConnectionFields for
    each unit.
    """

    
    ### JABALERT
    ###
    ### Need to figure whether this code (and sheet_view) is ok,
    ### i.e. whether there really is any need to handle multiple views
    ### from the same call.
    def unit_view(self,x,y):
        """
        Get a list of UnitView objects for a particular unit
        in this CFSheet.  Can return multiple UnitView objects.
        """
        from itertools import chain
        views = [p.get_view(x,y) for p in chain(*self.projections.values())]

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

    
    ### JABALERT
    ###
    ### Is it necessary to provide this special case?  It seems like
    ### the database can be populated beforehand so that this code
    ### can be basic and simple, but I may be forgetting something.
    def sheet_view(self,request='Activity'):
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
        
