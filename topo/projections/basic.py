"""

Repository for the basic Projection types.

Mainly provides a place where additional Projections can be added in
future, so that all will be in a well-defined, searchable location.

$Id$
"""

__version__ = "$Revision$"

import Numeric

from topo.base.topoobject import TopoObject
from topo.base.parameter import Parameter,Number,Constant
from topo.base.arrayutils import mdot
from topo.base.connectionfield import CFProjection,IdentityCFLF,ResponseFunctionParameter
from topo.base.patterngenerator import PatternGeneratorParameter
from topo.base.sheetview import UnitView

from topo.outputfns.basic import Identity


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
        single_cf_fn = self.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                r1,r2,c1,c2 = (cf_slice_and_bounds[r][c])[0]
                X = input_activity[r1:r2,c1:c2]
                
                assert cf.weights.shape==X.shape, "sharedcf at (" + str(cf.x) + "," + str(cf.y) + ") has an input_matrix slice that is not the same shape as the sharedcf.weights matrix weight matrix (" + repr(X.shape) + " vs. " + repr(cf.weights.shape) + ")."
                
                activity[r,c] = single_cf_fn(X,cf.weights)
        activity *= strength
        

class SharedWeightCFProjection(CFProjection):
    """
    A Projection with a single ConnectionField shared by all units.

    Otherwise similar to CFProjection, except that learning is
    currently disabled.
    """
    response_fn = ResponseFunctionParameter(default=SharedWeightCFResponseFn())
    ### JABHACKALERT: Learning won't actually work yet.
    learning_fn = Constant(IdentityCFLF())
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
        ### Skips call to super(SharedWeightProjection,self), because
        ### we don't want the whole set of cfs initialized, but we
        ### do want anything that Projection defines.
        ###
        ### JABHACKALERT: This approach might lead to problems later
        ### if someone adds code to CFProjection, because we won't
        ### inherit that.  Instead, we might want to add a flag to
        ### CFProjection.__init__ to allow the weight intialization
        ### to be selectively disabled, which is all we really need.
        CFProjection.__init__(self,**params)
        
        ### JABHACKALERT: cfs is a dummy, here only so that learning will
        ### run without an exception
        self.cfs = []
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


    def change_bounds(self, weights_bound_template):
        """
        Change the bounding box for all of the ConnectionFields in this Projection.

	Not yet implemented.
	"""
        raise NotImplementedError


    def change_density(self, new_wt_density):
        """
        Rescales the weight matrix in place, interpolating or resampling as needed.
	
	Not yet implemented.
	"""
        raise NotImplementedError




