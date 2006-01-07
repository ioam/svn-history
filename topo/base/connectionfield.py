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
from projection import Projection,ProjectionSheet,Identity,OutputFunctionParameter
from parameter import Parameter, Number, BooleanParameter, Constant, ClassSelectorParameter
from arrayutils import mdot,divisive_normalization
from sheet import Sheet,bounds2slice,bounds2shape,sheet2matrixidx,slicearray2bounds
from sheetview import UnitView
from itertools import chain
from patterngenerator import PatternGeneratorParameter
import patterngenerator
from boundingregion import BoundingBox


import simulator
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


def hebbian(input_activity, unit_activity, weights, learning_rate):
    """Simple Hebbian learning for the weights of one single unit."""
    weights += learning_rate * unit_activity * input_activity



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

    # Specifies how to get a submatrix from the source sheet that is aligned
    # properly with this weight matrix.  The information is stored as an
    # array for speed of access from optimized C components; use
    # self.slice_tuple() for a nicer Python access method.
    slice_array = []
    
    def __init__(self,input_sheet,weights_bound_template,
                 weights_generator,weights_shape,weight_type=Numeric.Float32,
                 output_fn=Identity(),**params):
        super(ConnectionField,self).__init__(**params)
        self.input_sheet = input_sheet
        self.__weights_bound_template = weights_bound_template
        self.initialize_slice_array()

        r1,r2,c1,c2 = self.slice_tuple()

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

        self.verbose("weights shape: ",self.weights.shape)
        
        # CEBHACKALERT: weights_shape and mask aren't Parameters, but
        # should I have declared them as class attributes?
        # CEBHACKALERT: the thresholding of mask values done in the where line
        # should be done so that the threshold can be set by the user (see
        # also change_bounds), and to avoid duplicating this code. Also this
        # probably slows simulation startup time (and time when bounds are changed).
        self.weights_shape = weights_shape
        m = weights_shape(x=0,y=0,bounds=weights_bound_template,
                          density=self.input_sheet.density,theta=0,
                          rows=r2-r1,cols=c2-c1)
        self.mask = Numeric.where(m>=0.5,m,0.0)
        
        output_fn(self.weights)
        self.weights *= self.mask        


    def initialize_slice_array(self):
        """
        Calculate the slice specifying the submatrix of the sheets to which
        this connection field connects.

    	Given a bounds centered at the origin, offsets the bounds to
	The given weights_bound_template is offset to the (x,y) location of
        this unit, and the slices that specifies the weight matrix is generated.
	(The special routine used for this purpose ensure that the weight matrix
         are all of the same size, when not to close of the borders.)

        Then, the bounding-box specifying the weight matrix is calculated around the 
        location of the unit, and it will allow to retrieve the slice from the bounding box by
        using the reversed function bounds2slice.
	"""

        rows,cols = bounds2shape(self.__weights_bound_template,self.input_sheet.xdensity,self.input_sheet.ydensity)

        cr,cc = sheet2matrixidx(self.x, self.y,
                                self.input_sheet.bounds, self.input_sheet.xdensity, self.input_sheet.ydensity)

        toprow = cr - rows/2
        leftcol = cc - cols/2

        maxrow,maxcol = sheet2matrixidx(self.input_sheet.bounds.aarect().right(),
                                 self.input_sheet.bounds.aarect().bottom(),
                                 self.input_sheet.bounds,self.input_sheet.xdensity,self.input_sheet.ydensity)
        maxrow = maxrow - 1
        maxcol = maxcol - 1
        rstart = max(0,toprow)
        rbound = min(maxrow+1,cr+rows/2+1)
        cstart = max(0,leftcol)
        cbound = min(maxcol+1,cc+cols/2+1)


        # Numeric.Int32 is specified explicitly here to avoid having it
        # default to Numeric.Int.  Numeric.Int works on 32-bit platforms,
        # but does not work properly with the optimized C activation and
        # learning functions on 64-bit machines.
        self.slice_array = Numeric.zeros((4), Numeric.Int32)
	self.set_slice_array(rstart, rbound, cstart, cbound)

	# constructs and store the boundingbox corresponding to the slice.
	self.bounds = slicearray2bounds(self.slice_array, self.input_sheet.bounds, self.input_sheet.xdensity, self.input_sheet.ydensity)

    def get_input_matrix(self, activity):
        r1,r2,c1,c2 = self.slice_tuple()
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

        or1,or2,oc1,oc2 = self.slice_tuple()

        self.__weights_bound_template = weights_bound_template
        self.initialize_slice_array()
        r1,r2,c1,c2 = self.slice_tuple()

        if not (r1 == or1 and r2 == or2 and c1 == oc1 and c2 == oc2):
            self.weights = Numeric.array(self.weights[r1-or1:r2-or1,c1-oc1:c2-oc1],copy=1)
            self.weights.savespace(1)

            # CEBHACKALERT: I think this isn't right. E.g. if the mask is a Disk the
            m = (Numeric.array(self.mask[r1-or1:r2-or1,c1-oc1:c2-oc1],copy=1))
            # CEBHACKALERT: see alert in __init__
            self.mask = Numeric.where(m>=0.5,m,0.0)
            
            output_fn(self.weights)
            self.weights *= self.mask


    def slice_tuple(self):
        return self.slice_array[0],self.slice_array[1],self.slice_array[2],self.slice_array[3]


    def set_slice_array(self, r1, r2, c1, c2):
        self.slice_array[0] = r1
        self.slice_array[1] = r2
        self.slice_array[2] = c1
        self.slice_array[3] = c2


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
                r1,r2,c1,c2 = cf.slice_tuple()
                X = input_activity[r1:r2,c1:c2]
                activity[r,c] = self.single_cf_fn(X,cf.weights)
        activity *= strength


# CEBHACKALERT: don't need to pass through stuff like doc because of **params
class ResponseFunctionParameter(ClassSelectorParameter):
    """
    """
    def __init__(self,default=GenericCFResponseFn(),doc='',**params):
        """
        """
        super(ResponseFunctionParameter,self).__init__(CFResponseFunction,default=default,doc=doc,**params)        


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


# CEBHACKALERT: don't need to pass through stuff like doc because of **params
class LearningFunctionParameter(ClassSelectorParameter):
    """
    """
    def __init__(self,default=IdentityCFLF(),doc='',**params):
        """
        """
        super(LearningFunctionParameter,self).__init__(CFLearningFunction,default=default,doc=doc,**params)        


class GenericCFLF(CFLearningFunction):
    """CFLearningFunction applying the specified single_cf_fn to each CF."""
    single_cf_fn = Parameter(default=hebbian)
    output_fn = Parameter(default=Identity())
    
    def __init__(self,**params):
        super(GenericCFLF,self).__init__(**params)

    ### JABHACKALERT!  The learning_rate currently has very different
    ### effects when the density changes, and lissom_or.ty calculates
    ### corrections for that.  Instead, this code (and EVERY OTHER
    ### CFLearningFunction) should accept a learning_rate specified as if
    ### there is a single unit in the connection field.  That is, the
    ### learning_rate specifies the total change across the
    ### ConnectionField, assuming that all units in the CF are equally
    ### activated (which is a reasonable default assumption on
    ### average).  Thus the user-specified learning rate should be
    ### divided by the number of units in the CF before the single_cf_fn
    ### is called here.  In general, every GenericCFLF would do such
    ### calculation before the learning_rate is used to calculate any
    ### new weight.
    ### Something like: single_cf_learning_rate=learning_rate/number_of_units_in_the(cf)
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        """Apply the specified single_cf_fn to every CF."""
        rows,cols = output_activity.shape
        for r in range(rows):
            for c in range(cols):
                cf = cfs[r][c]
                self.single_cf_fn(cf.get_input_matrix(input_activity),
                                  output_activity[r,c], cf.weights, learning_rate)
                cf.weights=self.output_fn(cf.weights)
                cf.weights *= cf.mask
                

class CFProjection(Projection):
    """
    A projection composed of ConnectionFields from a Sheet into a ProjectionSheet.

    CFProjection computes its activity using a response_fn of type
    CFResponseFunction (typically a CF-aware version of mdot) and output_fn 
    (which is typically Identity). Any subclass has to implement the interface
    activate(self,input_activity) that computes the response from the input 
    and stores it in the activity array.
    """
    response_fn = ResponseFunctionParameter(default=GenericCFResponseFn())
    cf_type = Parameter(default=ConnectionField)
    weight_type = Parameter(default=Numeric.Float32)
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = PatternGeneratorParameter(default=patterngenerator.Constant())
    weights_shape = PatternGeneratorParameter(default=patterngenerator.Constant())
    learning_fn = LearningFunctionParameter(default=GenericCFLF())
    learning_rate = Parameter(default=0.0)
    output_fn  = OutputFunctionParameter(default=Identity())
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
                                        weights_shape=self.weights_shape,
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

        # CEBHACKALERT: why is this necessary? Isn't cf[r][c].weights
        # already a Numeric array? (Same in SharedWeightProjection.)
        matrix_data = Numeric.array(self.cf(r,c).weights)

        new_box = self.cf(r,c).bounds

	### JC: tempoarary debug (to get rid of pretty soon)
# 	print "bounding_box",new_box.aarect().lbrt()
#  	r1,r2,c1,c2 = self.cf(r,c).slice
#   	print "slice",r1,r2,c1,c2
#  	x=self.cf(r,c).x
#  	y=self.cf(r,c).y
#  	print "x,y",x,y
#         a,b,c,d = bounds2slice(new_box,self.cf(r,c).input_sheet.bounds,
#                                   self.cf(r,c).input_sheet.density)
#         print "new_slice",a,b,c,d
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



class SharedWeightCFResponseFn(TopoObject):
    """
    Response function accepting a single CF applied to all units.
    Otherwise similar to GenericCFResponseFn.
    """
    ### JABALERT: It may be possible to eliminate this, and instead
    ### implemented a wrapper around the cfs argument of
    ### GenericCFResponseFn, so that GenericCFResponseFn will work
    ### whether there is an actual full set of cfs or not.
    single_cf_fn = Parameter(default=mdot)
    
    def __init__(self,**params):
        super(SharedWeightCFResponseFn,self).__init__(**params)

    def __call__(self, cf, cf_slice_and_bounds, input_activity, activity, strength):
        rows,cols = activity.shape
        for r in xrange(rows):
            for c in xrange(cols):
                r1,r2,c1,c2 = (cf_slice_and_bounds[r][c])[0]
                X = input_activity[r1:r2,c1:c2]
                
                assert cf.weights.shape==X.shape, "sharedcf at (" + str(cf.x) + "," + str(cf.y) + ") has an input_matrix slice that is not the same shape as the sharedcf.weights matrix weight matrix (" + repr(X.shape) + " vs. " + repr(cf.weights.shape) + ")."
                
                activity[r,c] = self.single_cf_fn(X,cf.weights)
        activity *= strength
        

### JABALERT: This should move to topo/projections/basic.py, because
### nothing actually relies on it in base.
class SharedWeightProjection(Projection):
    """
    A Projection with a single ConnectionField shared by all units.

    Otherwise similar to CFProjection, except that learning is
    currently disabled.
    """
    response_fn = ResponseFunctionParameter(default=SharedWeightCFResponseFn())
    cf_type = Parameter(default=ConnectionField)
    weight_type = Parameter(default=Numeric.Float32)
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = PatternGeneratorParameter(default=patterngenerator.Constant())
    weights_shape = PatternGeneratorParameter(default=patterngenerator.Constant())
    ### JABHACKALERT: Learning won't actually work yet.
    learning_fn = Constant(IdentityCFLF())
    learning_rate = Parameter(default=0.0)
    ### JABHACKALERT: cfs is a dummy, here only so that learning will
    ### run without an exception
    cfs = None
    cf_slice_and_bounds = []
    output_fn  = PatternGeneratorParameter(default=Identity())
    strength = Number(default=1.0)

    def __init__(self,**params):
        """
        Initialize the Projection with a set of cf_type objects
        (typically ConnectionFields), each located at the location
        in the source sheet corresponding to the unit in the target
        sheet.
        """
        super(SharedWeightProjection,self).__init__(**params)
        self.sharedcf=self.cf_type(input_sheet=self.src,
                                   weights_bound_template=self.weights_bounds,
                                   weights_generator=self.weights_generator,
                                   weights_shape=self.weights_shape,
                                   weight_type=self.weight_type,
                                   output_fn=self.learning_fn.output_fn,
                                   x=0,y=0)
        
        # calculate the slice array and bounds for the location of each unit
        # CEBHACKALERT: uses the existing function initialize_slice_array()
        # and calculates the slices and bounds just once, but maybe there
        # is a cleaner way? Leaves the sharedcf with (x,y) of last unit
        # instead of (0,0) as before, but (x,y) is meaningless anyway for
        # the sharedcf.
        cf = self.sharedcf
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                cf.x,cf.y = x,y
                cf.initialize_slice_array()
                row.append((cf.slice_tuple(),cf.bounds))
            self.cf_slice_and_bounds.append(row)

        self.input_buffer = None
        self.activity = Numeric.array(self.dest.activity)


    def cf(self,r,c):
        """Return the shared ConnectionField, for all coordinates."""
        return self.sharedcf


    def get_view(self,sheet_x, sheet_y):
        """
        Return the shared ConnectionField as a UnitView, but with
        the appropriate bounding box depending on the
        sheet coordinate (sheet_x,sheet_y).
        """
        (r,c) = (self.dest).sheet2matrixidx(sheet_x,sheet_y)

        # CEBHACKALERT: see get_view() in CFProjection
        matrix_data = Numeric.array(self.sharedcf.weights)

        # get weights bounds for each unit
        new_box = (self.cf_slice_and_bounds[r][c])[1]

        assert matrix_data != None, "Projection Matrix is None"
        return UnitView((matrix_data,new_box),sheet_x,sheet_y,self,view_type='UnitView')

    
    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        self.response_fn(self.sharedcf, self.cf_slice_and_bounds, input_activity, self.activity, self.strength)
        self.activity = self.output_fn(self.activity)



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
                ### JABALERT: This code should be moved into a learn()
                ### function in Projection, so that individual projections
                ### can use different arguments to their learning functions.
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
    ###
    ### This code is outdated, because it was originally meant to
    ### retrieve a unit view from the database, and had to be
    ### different from sheet_view() because of needing to supply x,y.
    ### Now, the sheet_view_dict accepts keys of any type, and
    ### UnitView keys encode the x,y directly.  Thus the lookup
    ### function is no longer needed.  Instead, this code is now used
    ### for installing UnitViews in the sheet_view_dict, and so it
    ### should be renamed to update_unit_view(self,x,y), or something
    ### like that.  In addition, it should probably accept a
    ### projection parameter so that individual projections can be
    ### updated; otherwise a Projection plot will result in a huge
    ### number of wasted UnitView additions.
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
