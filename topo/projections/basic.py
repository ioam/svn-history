"""
Repository for the basic Projection types.

Mainly provides a place where additional Projections can be added in
future, so that all will be in a well-defined, searchable location.

$Id$
"""

__version__ = "$Revision$"

import Numeric

# So all Projections are present in this package
from topo.base.projection import Projection

from topo.base.functionfamilies import OutputFnParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number,BooleanParameter
from topo.base.cf import CFProjection,CFPLearningFnParameter,IdentityCFPLearningFn,CFPResponseFnParameter,CFProjectionOutputFnParameter,CFProjectionIdentityOutputFn,CFProjectionOutputFn, Mdot, ResponseFnParameter
from topo.base.patterngenerator import PatternGeneratorParameter
from topo.base.sheetview import UnitView

from topo.outputfns.basic import IdentityOF



class SharedCFProjectionOutputFn(CFProjectionOutputFn):
    single_cf_fn = OutputFnParameter(default=IdentityOF())
    
    def __call__(self, cfs, output_activity, norm_values=None, **params):
        """Apply the specified single_cf_fn to every CF."""
        if type(self.single_cf_fn) is not IdentityOF:
            cf = cfs[0]
            self.single_cf_fn(cf.weights)



class SharedCFProjectionResponseFn(ParameterizedObject):
    """
    Response function accepting a single CF applied to all units.
    Otherwise similar to GenericCFResponseFn.
    """
    ### JABALERT: It may be possible to eliminate this, and instead
    ### implemented a wrapper around the cfs argument of
    ### GenericCFResponseFn, so that GenericCFResponseFn will work
    ### whether there is an actual full set of cfs or not.
    single_cf_fn = ResponseFnParameter(default=Mdot())
    
    def __call__(self, cf, cf_slice_and_bounds, input_activity, activity, strength):
        rows,cols = activity.shape
        single_cf_fn = self.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                # get right submatrix from input_activity
                act_r1,act_r2,act_c1,act_c2 = (cf_slice_and_bounds[r][c])[0]
                X = input_activity[act_r1:act_r2,act_c1:act_c2]
                # get right submatrix from weights
                w_r1,w_r2,w_c1,w_c2 = (cf_slice_and_bounds[r][c])[2]
                weights = cf.weights[w_r1:w_r2,w_c1:w_c2]

                activity[r,c] = single_cf_fn(X,weights)
        activity *= strength
        

# CEBHACKALERT: users should not access .sharedcf or .cfs directly,
# but should use .cf(r,c). That all needs to be cleaned up, here and
# in connectionfield.py.
class SharedCFProjection(CFProjection):
    """
    A Projection with a single ConnectionField shared by all units.

    Otherwise similar to CFProjection, except that learning is
    currently disabled.
    """
    response_fn = CFPResponseFnParameter(
        default=SharedCFProjectionResponseFn())
    
    ### JABHACKALERT: Set to be constant as a clue that learning won't
    ### actually work yet.
    learning_fn = CFPLearningFnParameter(
        IdentityCFPLearningFn(),constant=True)

    output_fn  = OutputFnParameter(default=IdentityOF())
    
    strength = Number(default=1.0)

    weights_output_fn = CFProjectionOutputFnParameter(
        default=SharedCFProjectionOutputFn())


    def __init__(self,**params):
        """
        Initialize the Projection with a single cf_type object
        (typically a ConnectionField),
        """
        # we don't want the whole set of cfs initialized, but we
        # do want anything that Projection defines.
        super(SharedCFProjection,self).__init__(initialize_cfs=False,**params)

        self.sharedcf=self.cf_type(0,0,
                                   self.src,
                                   self.weights_bounds,
                                   self.weights_generator,
                                   self.mask_template,
                                   self.weights_output_fn.single_cf_fn)

        # CEBHACKALERT: Calculate and store the the slice of the
        # sheet, the bounds, and the slice of the weights matrix for
        # each unit. Although there is only one cf here in the code,
        # it is used to represent units all round the sheet - and
        # units around the edge might not be able to have the full
        # matrix. To avoid calculating the correct slice of the
        # weights matrix to take at each activation, it's stored
        # in cf.slice_and_bounds[2]. The bounds are also stored for
        # access by plotting routines in [1]. The slice of the sheet to
        # which these bounds correspond is stored in [0].

        self.cf_slice_and_bounds = []
        
        cf = self.sharedcf
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                cf.x,cf.y = x,y
                cf.offset_bounds(self.weights_bounds)
                weights_slice = cf.get_slice(self.weights_bounds)
                row.append((cf.slice_array,cf.bounds,weights_slice))
            self.cf_slice_and_bounds.append(row)

        ### JABHACKALERT: cfs is a dummy, here only so that learning will
        ### run without an exception
        self.cfs = [self.sharedcf]

    
    def cf(self,r,c):
        """Return the shared ConnectionField, for all coordinates."""
        # CEBHACKALERT: there's probably a better way to do this than
        # just replacing the sharedcf's bounds and slice_array. 
        bounds = self.cf_slice_and_bounds[r][c][1]
        slice_array = self.cf_slice_and_bounds[r][c][0]
        self.sharedcf.bounds = bounds
        self.sharedcf.slice_array = slice_array
        return self.sharedcf

    
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




