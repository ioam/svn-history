"""
ConnectionField and associated classes.

This module defines some basic classes of objects used to create
simulations of cortical sheets that take input through connection
fields that project from other cortical sheets (or laterally from
themselves):

ConnectionField: Holds a single connection field within a CFProjection.

CFProjection: A set of ConnectionFields mapping from a Sheet into a
ProjectionSheet.

CFSheet: A subclass of ProjectionSheet that provides an interface to
the underlying ConnectionFields in any projection of type CFProjection.

$Id$
"""

__version__ = '$Revision$'


import Numeric

from topoobject import TopoObject
from projection import Projection,ProjectionSheet,Identity
from parameter import Parameter, Number, BooleanParameter
from utils import mdot,hebbian,divisive_normalization
from sheet import Sheet
from sheetview import UnitView
from itertools import chain



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


class ConnectionField(TopoObject):
    """
    A set of weights on one input Sheet.

    Each ConnectionField contributes to the activity of one unit on
    the output sheet, and is normally used as part of a Projection
    including many other ConnectionFields.
    """
    
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


    ### JABHACKALERT! Need to figure out how to handle the normalization
    ### here once the learning functions handle that internally.
    ###
    ### JABALERT! Seems to have a strange definition of bounds, if it
    ### is all relative to self.x and self.y.  Needs better documentation.
    def change_bounds(self, new_wt_bounds):
        """
        Change the bounding box for this existing ConnectionField.

        Discards weights or adds new (zero) weights as necessary,
        preserving existing values where possible.

        Currently only supports reducing the size, not increasing, but
        should be extended to support increasing as well.
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


    def change_density(self, new_wt_density):
        """Rescale the weight matrix in place, interpolating or decimating as necessary."""
        raise NotImplementedError



class CFResponseFunction(TopoObject):
    """
    Map an input activity matrix into an output matrix using CFs.

    Objects in this hierarchy of callable function objects compute a
    response matrix when given an input pattern and a set of
    ConnectionField objects.  Typically used as part of the activation
    function for a neuron, computing activation for one Projection.

    Objects in this class must support being called as a function with
    the arguments specified below, and must return a matrix the same
    size as the activity matrix supplied.
    """
    def __call__(self,input_activity, activity, cfs, strength, **params):
        raise NotImplementedError


class GenericCFResponseFn(CFResponseFunction):
    """
    Generic large-scale response function based on a simple single-CF function.

    Applies the single_cf_fn to each CF in turn.  For the default
    single_cf_fn of mdot, does a basic dot product of each CF with the
    corresponding slice of the input array.  This function is likely
    to be slow to run, but it is easy to extend with any arbitrary
    single-CF response function.

    The single_cf_fn must be a function f(X,W) that takes two
    identically shaped matrices X (the input) and W (the
    ConnectionField weights) and computes a scalar activation value
    based on those weights.
    """
    single_cf_fn = Parameter(default=mdot)
    
    def __init__(self,**params):
        super(GenericCFResponseFn,self).__init__(**params)

    def __call__(self,input_activity, activity, cfs, strength):
        rows,cols = activity.shape
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice
                X = input_activity[r1:r2,c1:c2]
                activity[r,c] = self.single_cf_fn(X,cf.weights)
        activity *= strength
        

class CFLearningFunction(TopoObject):
    """
    Compute new CFs based on input and output activity values.

    Objects in this hierarchy of callable function objects compute a
    new set of CFs when given input and output patterns and a set of
    ConnectionField objects.  Typically used for updating the weights
    of one CFProjection.

    Objects in this class must support being called as a function with
    the arguments specified below.
    """
    def __call__(self, input_activity, output_activity, cfs, learning_rate, **params):
        raise NotImplementedError


class IdentityCFLF(CFLearningFunction):
    """CFLearningFunction performing no learning."""

    ### JABALERT! Can this function be omitted entirely?
    def __init__(self,**params):
        super(IdentityCFLF,self).__init__(**params)

    def __call__(self, input_activity, output_activity, cfs, learning_rate, **params):
        pass


### JABALERT! Untested.
class GenericCFLF(CFLearningFunction):
    """CFLearningFunction applying the specified single_cf_fn to each CF."""
    single_cf_fn = Parameter(default=hebbian)
    output_fn = Parameter(default=Identity())
    
    def __init__(self,**params):
        super(GenericCFLF,self).__init__(**params)

    def __call__(self, input_activity, output_activity, cfs, learning_rate, **params):
        """Apply the specified single_cf_fn to every CF."""
        rows,cols = output_activity.shape
        for r in range(rows):
            for c in range(cols):
                cf = cfs[r][c]
                self.single_cf_fn(cf.get_input_matrix(input_activity),
                                  output_activity[r,c], cf.weights, learning_rate)
                cfs[r][c].weights=self.output_fn(cf.weights)
                

class CFProjection(Projection):
    """
    A projection composed of ConnectionFields from a Sheet into a ProjectionSheet.

    CFProjection computes its activity using a response_fn of type
    CFResponseFunction.  Any subclass has to implement the interface
    activate(self,input_activity) that computes the response
    from the input and stores it in the activity array.
    """

    response_fn = Parameter(default=GenericCFResponseFn())
    cf_type = Parameter(default=ConnectionField)
    normalize = BooleanParameter(default=False)
    normalize_fn = Parameter(default=divisive_normalization)
    weight_type = Parameter(default=Numeric.Float32)

    strength = Number(default=1.0)
    activity = []


    def __init__(self,**params):
        super(Projection,self).__init__(**params)
        self.cfs = None
        self.input_buffer = None
        self.activity = Numeric.array(self.dest.activity)


    def cf(self,r,c):
        """Return the specified ConnectionField"""
        return self.cfs[r][c]


    def set_cfs(self,cf_list):
        self.cfs = cf_list


    def get_shape(self):
        return len(self.cfs),len(self.cfs[0])


    def get_view(self,sheet_x, sheet_y):
        """
        Return a single connection field UnitView, for the unit
        located at sheet coordinate (sheet_x,sheet_y).
        """
        (r,c) = (self.dest).sheet2matrix(sheet_x,sheet_y)
        matrix_data = Numeric.array(self.cf(r,c).weights)

        ### JABHACKALERT!
        ###
        ### The bounds are currently set to a default; what should
        ### they really be set to?
        new_box = self.dest.bounds
        assert matrix_data != None, "Projection Matrix is None"
        return UnitView((matrix_data,new_box),sheet_x,sheet_y,self,view_type='UnitView')


    def activate(self,input_activity):
        raise NotImplementedError


    def change_bounds(self, new_wt_bounds):
        """
        Change the bounding box for this existing ConnectionField.

        Discards weights or adds new (zero) weights as necessary.
        """
        raise NotImplementedError


    def change_density(self, new_wt_density):
        """Rescales the weight matrix in place, interpolating or decimating as needed."""
        raise NotImplementedError


class CFSheet(ProjectionSheet):
    """
    A ProjectionSheet providing access to the ConnectionFields in its CFProjections.

    ProjectionSheet classes do not assume that the Projections can
    provide a set of weights for individual units, or indeed that
    there are units or weights at all.  In contrast, CFSheet is built
    around the assumption that there are units in this Sheet, indexed
    by Sheet coordinates (x,y), and that these units have one or more
    ConnectionField connections on another Sheet (via CFProjections).
    It then provides an interface for visualizing or analyzing these
    ConnectionFields for each unit.  A ProjectionSheet should work
    just the same as this sheet, except that it will not provide those routines.
    """

    learning_fn = Parameter(default=GenericCFLF())
    def learn(self):
        rows,cols = self.activity.shape
        for proj in chain(*self.in_projections.values()):
            if proj.input_buffer:
                learning_rate = proj.learning_rate
                inp = proj.input_buffer
                cfs = proj.cfs
                len, len2 = inp.shape
                self.learning_fn(inp, self.activity, cfs, learning_rate)

    
    ### JABALERT
    ###
    ### Need to figure whether this code (and sheet_view) is ok,
    ### i.e. whether there really is any need to handle multiple views
    ### from the same call.
    ###
    ### JABHACKALERT!
    ###
    ### This code should be checking to see if the projection is a CFProjection
    ### before doing a get_view, because only CFProjections support that call.
    def unit_view(self,x,y):
        """
        Get a list of UnitView objects for a particular unit in this CFSheet.
        
        Can return multiple UnitView objects.
        """
        from itertools import chain
        views = [p.get_view(x,y) for p in chain(*self.in_projections.values())]

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
        Check for 'Weights' or 'WeightsArray', but then call Sheet.sheet_view().  

        The addition of unit_view() means that it's now possible for
        one sheet_view request to return multiple UnitView objects,
        which are subclasses of SheetViews.

        """
        self.debug('request = ' + str(request))
        if isinstance(request,tuple) and request[0] == 'Weights':
            (name,s,p,x,y) = request
            return self.unit_view(x,y)
        else:
            return Sheet.sheet_view(self,request)
        
