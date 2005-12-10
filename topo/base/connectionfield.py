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
from utils import hebbian
from arrayutils import mdot,divisive_normalization
from sheet import Sheet, matrix2sheet
from sheetview import UnitView
from itertools import chain
from patterngenerator import ConstantGenerator
from boundingregion import BoundingBox
import topo.misc.inlinec as inlinec


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
    
    x = Parameter(default=0,doc='The x coordinate of the location of the center of this ConnectionField\non the input Sheet, e.g. for use when determining where the weight matrix\nlines up with the input Sheet matrix.')
    y = Parameter(default=0,doc='The y coordinate of the location of the center of this ConnectionField\non the input Sheet, e.g. for use when determining where the weight matrix\nlines up with the input Sheet matrix.')

    # Weights matrix; not yet initialized.
    weights = []

    ### JABHACKALERT!  Why is this code relevant only for the
    ### optimized C versions here, in the base ConnectionField class?
    ### Surely it should only be in a subclass that has been
    ### optimized, so that the base class is readable and general.
    
    # Stores a copy of the slice as an array that can be read easily from C,
    # for use in optimized C versions of functions using this object.
    slice_array = []
    
    def __init__(self,input_sheet,weights_bound_template,
                 weights_generator,weight_type=Numeric.Float32,
                 output_fn=Identity(),**params):
        super(ConnectionField,self).__init__(**params)
        self.input_sheet = input_sheet

        r1,r2,c1,c2 = self.__initialize_slice(weights_bound_template)

        # set up the weights centered around 0,0 to avoid problems
        # with different-sized results at different floating-point
        # locations in the Sheet
        w = weights_generator(x=0,y=0,bounds=weights_bound_template,
                              density=self.input_sheet.density,theta=0,
                              rows=r2-r1,cols=c2-c1)
        self.weights = w.astype(weight_type)
        # Maintain the original type throughout operations, i.e. do not
        # promote to double.
        self.weights.savespace(1)

        self.verbose("activity matrix shape: ",self.weights.shape)

        output_fn(self.weights)


    def __initialize_slice(self,weights_bound_template):
        """
        Calculate the slice specifying the submatrix of the sheet's to which
        this connection field connects.

        The given weights_bound_template is offset to the (x,y) location of
        this unit, and the bounds are calculated around that point.
        """
        
        self.slice = self.input_sheet.input_slice(weights_bound_template,self.x,self.y)

        # Numeric.Int32 is specified explicitly here to avoid having it
        # default to Numeric.Int.  Numeric.Int works on 32-bit platforms,
        # but does not work properly with the optimized C activation and
        # learning functions on 64-bit machines.
        r1,r2,c1,c2 = self.slice
        self.slice_array = Numeric.zeros((4), Numeric.Int32)
        self.slice_array[0] = r1
        self.slice_array[1] = r2
        self.slice_array[2] = c1
        self.slice_array[3] = c2

        # Construct and store the bounds exactly enclosing this slice
        left,bottom = matrix2sheet(r2,c1,self.input_sheet.bounds,self.input_sheet.density)
        right, top   = matrix2sheet(r1,c2,self.input_sheet.bounds,self.input_sheet.density)
        self.bounds = BoundingBox(points=((left,bottom),(right,top)))

        return self.slice
    
    def get_input_matrix(self, activity):
        r1,r2,c1,c2 = self.slice
        return activity[r1:r2,c1:c2]


    def change_bounds(self, weights_bound_template, output_fn=Identity()):
        """
        Change the bounding box for this existing ConnectionField. The
        weights_bound_template should center at the sheet coordinate
        (0,0), just as weights_bound_template in __init__,
        i.e. weights_bound_template only specifies the size of the new
        bounding box, but not the location. The exact location and
        extent of the new bounding box is found by translating the
        center of weights_bound_template to the center of this
        connection field. If the new bound falls outside of the sheet,
        it is cropped to just cover the sheet.

        Discards weights or adds new (zero) weights as necessary,
        preserving existing values where possible.

        Currently only supports reducing the size, not increasing, but
        should be extended to support increasing as well.
        """

        old_slice=self.slice
        or1,or2,oc1,oc2 = old_slice
        r1,r2,c1,c2 = self.__initialize_slice(weights_bound_template)

        if self.slice != old_slice:
            self.weights = Numeric.array(self.weights[r1-or1:r2-or1,c1-oc1:c2-oc1],copy=1)
            self.weights.savespace(1)
            output_fn(self.weights)


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
    def __call__(self, cfs, input_activity, activity, strength, **params):
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

    def __call__(self, cfs, input_activity, activity, strength):
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
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        raise NotImplementedError


class IdentityCFLF(CFLearningFunction):
    """CFLearningFunction performing no learning."""

    output_fn = Parameter(default=Identity())
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        pass


### JABALERT! Untested.
class GenericCFLF(CFLearningFunction):
    """CFLearningFunction applying the specified single_cf_fn to each CF."""
    single_cf_fn = Parameter(default=hebbian)
    
    def __init__(self,**params):
        super(GenericCFLF,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
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
    CFResponseFunction (typically a CF-aware version of mdot) and output_fn 
    (which is typically Identity). Any subclass has to implement the interface
    activate(self,input_activity) that computes the response from the input 
    and stores it in the activity array.
    """

    from topo.responsefns.basic import CFDotProduct, CFDotProduct_Py
    if inlinec.optimized:
        response_fn = Parameter(default=CFDotProduct())
    else:
        response_fn = Parameter(default=CFDotProduct_Py)
        self.verbose('CFProjection using non-optimized CFDotProduct_Py()')

    cf_type = Parameter(default=ConnectionField)
    weight_type = Parameter(default=Numeric.Float32)
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = Parameter(default=ConstantGenerator())
    learning_fn = Parameter(GenericCFLF())
    learning_rate = Parameter(default=0.0)
    output_fn  = Parameter(default=Identity())

    strength = Number(default=1.0)

    def __init__(self,**params):
        """
        Initialize the Projection with a set of cf_type objects
        (typically ConnectionFields), each located at the location
        in the source sheet corresponding to the unit in the target
        sheet.
        """
        super(CFProjection,self).__init__(**params)
        # set up array of ConnectionFields translated to each x,y in the src sheet
        cfs = []
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                # JABALERT: Currently computes the location of the
                # ConnectionField as the exact location in the input
                # sheet corresponding to the unit in the destination
                # sheet.  Instead, we will need to add the ability to
                # use some other type of mapping, e.g. to add jitter
                # in the initial mapping.
                row.append(self.cf_type(input_sheet=self.src,
                                        weights_bound_template=self.weights_bounds,
                                        weights_generator=self.weights_generator,
                                        weight_type=self.weight_type,
                                        output_fn=self.learning_fn.output_fn,
                                        x=x,y=y))

            cfs.append(row)

        self.set_cfs(cfs)
        self.input_buffer = None
        self.activity = Numeric.array(self.dest.activity)


    def cf(self,r,c):
        """Return the specified ConnectionField"""
        return self.cfs[r][c]


    def set_cfs(self,cf_list):
        self.cfs = cf_list


    def get_shape(self):
        return len(self.cfs),len(self.cfs[0])


    ### JCALERT! This function has to be review, so that the size of the UnitView
    ### matrix is actually the same size as the sheet.
    ### Like that it would be possible to color unitView with Orientation Preference 
    ### for instance.
    def get_view(self,sheet_x, sheet_y):
        """
        Return a single connection field UnitView, for the unit
        located at sheet coordinate (sheet_x,sheet_y).
        """
        (r,c) = (self.dest).sheet2matrixidx(sheet_x,sheet_y)

        matrix_data = Numeric.array(self.cf(r,c).weights)

        new_box = self.cf(r,c).bounds
	### JC: debug
	#print "bounding_box",new_box.aarect().lbrt()
	# r1,r2,c1,c2 = self.cf(r,c).slice
# 	print "slice",r1,r2,c1,c2
# 	x=self.cf(r,c).x
# 	y=self.cf(r,c).y
# 	print "x,y",x,y
	###
        assert matrix_data != None, "Projection Matrix is None"
        return UnitView((matrix_data,new_box),sheet_x,sheet_y,self,view_type='UnitView')


    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        self.response_fn(self.cfs, input_activity, self.activity, self.strength)
        self.activity = self.output_fn(self.activity)



    def change_bounds(self, weights_bound_template):
        """
        Change the bounding box for all of the ConnectionFields in this Projection.

        Calls change_bounds() on each ConnectionField.

	Currently only allows reducing the size, but should be
        extended to allow increasing as well.
        """
        if not self.weights_bounds.containsbb_exclusive(weights_bound_template):
            self.warning('Unable to change_bounds; currently allows reducing only.')
            return

        self.weights_bounds = weights_bound_template
        rows,cols = self.get_shape()
        cfs = self.cfs
        output_fn = self.learning_fn.output_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cfs[r][c].change_bounds(weights_bound_template,output_fn=output_fn)



    def change_density(self, new_wt_density):
        """
        Rescales the weight matrix in place, interpolating or resampling as needed.
	
	Not yet implemented.
	"""
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
    just the same as this sheet, except that it will not provide those
    routines.
    """

    def learn(self):
        for proj in chain(*self.in_projections.values()):
            if proj.input_buffer:
                learning_rate = proj.learning_rate
                inp = proj.input_buffer
                cfs = proj.cfs
                proj.learning_fn(cfs, inp, self.activity, learning_rate)

    
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
	Creates the list of UnitView objects for a particular unit in this CFSheet,
	(There is one UnitView for each projection to this CFSheet).

	Each UnitView is then added to the sheet_view_dict of its source sheet.
	It return the list of all UnitView for the given unit.
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
	    src.add_sheet_view(key,v)
            self.debug('Added to sheet_view_dict', views, 'at', key)

        return views

    def release_unit_view(self,x,y):
        self.release_sheet_view(('Weights',x,y))

    
