"""
Repository for the basic Projection types.

Mainly provides a place where additional Projections can be added in
future, so that all will be in a well-defined, searchable location.

$Id$
"""

__version__ = "$Revision$"

import copy
import Numeric
from math import exp

# So all Projections are present in this package
from topo.base.projection import Projection

from topo.base.functionfamilies import OutputFnParameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number,BooleanParameter,Parameter
from topo.base.cf import CFProjection,CFPLearningFnParameter,IdentityCFPLearningFn,CFPResponseFnParameter,CFPOutputFnParameter,IdentityCFPOutputFn,CFPOutputFn,CFPResponseFn, DotProduct, ResponseFnParameter
from topo.base.patterngenerator import PatternGeneratorParameter
from topo.base.sheetview import UnitView

from topo.outputfns.basic import IdentityOF



# CEBHACKALERT: This file contains numerous hacks, all around
# to allow there to be a collection of cfs which all share one
# set of weights. The classes in here could be implemented much
# better, it just hasn't been done yet.
# SharedWeightCFProjection should have the list of 'cfs', and
# it should contain CFs that allow the standard CFP functions to work as
# normal with the list, but these CFs should not each have a set of weights.
# ConnectionField could e.g. be subclassed. At the moment,
# a shared ConnectionField is in a list of 'DummyCF' wrappers.


class SharedWeightCFPOutputFn(CFPOutputFn):
    single_cf_fn = OutputFnParameter(default=IdentityOF())
    
    def __call__(self, cfs, output_activity, norm_values=None, **params):
        """Apply the specified single_cf_fn to every CF."""
        if type(self.single_cf_fn) is not IdentityOF:
            cf = cfs[0][0]
            self.single_cf_fn(cf.weights)


class SharedWeightCFPResponseFn(CFPResponseFn):
    """
    Response function accepting a single CF applied to all units.
    Otherwise similar to GenericCFResponseFn.
    """
    single_cf_fn = ResponseFnParameter(default=DotProduct())
    
    def __call__(self, cfs, input_activity, activity, strength):
        rows,cols = activity.shape
        single_cf_fn = self.single_cf_fn
        shared_weights = cfs[0][0].weights
        
        for r in xrange(rows):
            for c in xrange(cols):
                # get right submatrix from input_activity
                act_r1,act_r2,act_c1,act_c2 = cfs[r][c].slice_array
                X = input_activity[act_r1:act_r2,act_c1:act_c2]
                # get right submatrix from weights
                w_r1,w_r2,w_c1,w_c2 = cfs[r][c].weights_slice
                weights = shared_weights[w_r1:w_r2,w_c1:w_c2]

                activity[r,c] = single_cf_fn(X,weights)
        activity *= strength


# CEBHACKALERT: this is a temporary implementation!
# It isn't the right way to allow a collection of CFs
# sharing one set of weights.
class DummyCF(ParameterizedObject):

    weights = property(lambda self: self.cf.weights)
    
    def __init__(self,cf,x,y,bounds_template):
        cf.x=x; cf.y=y
        cf.offset_bounds(bounds_template)

        self.bounds = copy.deepcopy(cf.bounds)
        self.slice_array =  copy.deepcopy(cf.slice_array)
        self.weights_slice = cf.get_slice(bounds_template)
        
        self.cf = cf
        self.x=x; self.y=y



# CEBHACKALERT: users should not access .sharedcf or .cfs directly,
# but should use .cf(r,c). That all needs to be cleaned up, here and
# in connectionfield.py.
class SharedWeightCFProjection(CFProjection):
    """
    A Projection with a single set of weights, shared by all units.

    Otherwise similar to CFProjection, except that learning is
    currently disabled.
    """
    response_fn = CFPResponseFnParameter(
        default=SharedWeightCFPResponseFn())
    
    ### JABHACKALERT: Set to be constant as a clue that learning won't
    ### actually work yet.
    learning_fn = CFPLearningFnParameter(
        IdentityCFPLearningFn(),constant=True)

    output_fn  = OutputFnParameter(default=IdentityOF())
    
    strength = Number(default=1.0)

    weights_output_fn = CFPOutputFnParameter(
        default=SharedWeightCFPOutputFn())


    def __init__(self,**params):
        """
        Initialize the Projection with a single cf_type object
        (typically a ConnectionField),
        """
        # we don't want the whole set of cfs initialized, but we
        # do want anything that Projection defines.
        super(SharedWeightCFProjection,self).__init__(initialize_cfs=False,**params)

        dest_sheetrows = self.dest.sheet_rows()[::-1]
        dest_sheetcols = self.dest.sheet_cols()

        # want the sharedcf to be located on the grid, so
        # pick a central unit and use its center
        center_unit_x = dest_sheetcols[len(dest_sheetcols)/2]
        center_unit_y = dest_sheetrows[len(dest_sheetrows)/2]        

        self.__sharedcf=self.cf_type(center_unit_x,center_unit_y,
                                     self.src,
                                     self.bounds_template,
                                     self.weights_generator,
                                     self.mask_template,
                                     self.weights_output_fn.single_cf_fn)
        

        cflist = []
        scf = self.__sharedcf
        bounds_template = self.bounds_template
        for y in dest_sheetrows:
            row = []
            for x in dest_sheetcols:
                cf = DummyCF(scf,x,y,bounds_template)
                row.append(cf)
            cflist.append(row)

        ### JABHACKALERT: cfs is a dummy, here only so that learning will
        ### run without an exception
        #self.cfs = [self.sharedcf]
        self.cfs = cflist
        
    
    def cf(self,r,c):
        """Return the shared ConnectionField, for all coordinates."""
        # CEBHACKALERT: there's probably a better way to do this than
        # just replacing the sharedcf's bounds and slice_array. 
        self.__sharedcf.bounds = self.cfs[r][c].bounds
        self.__sharedcf.slice_array = self.cfs[r][c].slice_array
        return self.__sharedcf

    
    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        self.response_fn(self.cfs, input_activity, self.activity, self.strength)
        self.activity = self.output_fn(self.activity)


    def change_bounds(self, nominal_bounds_template):
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

class LeakyCFProjection(CFProjection):
    """
    A projection that has a decay_rate parameter so that incoming
    input is decayed over time as x(t) = input + x(t-1)*exp(-decay_rate),
    and then the weighted sum of x(t) is calculated.
    """

    decay_rate = Number(default=1.0,
		        bounds=(0,None),
                        doc="input decay rate for each leaky synapse")

    leaky_input_buffer = None

    def __init__(self,**params):
        super(LeakyCFProjection,self).__init__(**params)
	# YC hack alert
	# This is a crude hack to initialize the leaky_input_buffer
	# to a zero matrix that has the same size as the src sheet.
	self.leaky_input_buffer = self.src.activity * 0.0

    def activate(self,input_activity):
	"""
	Retain input_activity from the previous step in leaky_input_buffer
	and add a leaked version of it to the current input_activity. This 
	function needs to deal with a finer time-scale.
	"""
	self.leaky_input_buffer = input_activity +self.leaky_input_buffer*exp(-self.decay_rate) 
        super(LeakyCFProjection,self).activate(self.leaky_input_buffer)

