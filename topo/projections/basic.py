"""
Repository for the basic Projection types.

Mainly provides a place where additional Projections can be added in
future, so that all will be in a well-defined, searchable location.

$Id$
"""

__version__ = "$Revision$"

import copy
import numpy.oldnumeric as Numeric
from math import exp

# So all Projections are present in this package
from topo.base.projection import Projection

from topo.base.cf import CFProjection,CFPLearningFnParameter,CFPLF_Identity,CFPResponseFnParameter,CFPOutputFnParameter,CFPOF_Identity,CFPOutputFn,CFPResponseFn, DotProduct, ResponseFnParameter
from topo.base.functionfamilies import OutputFnParameter
from topo.base.parameterclasses import Number,BooleanParameter,Parameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.patterngenerator import PatternGeneratorParameter
from topo.base.sheetview import UnitView
from topo.base.cf import ConnectionField, CFPRF_Plugin

from topo.outputfns.basic import IdentityOF


class CFPOF_SharedWeight(CFPOutputFn):
    """
    CFPOutputFn for use with SharedWeightCFProjections.

    Applies the single_cf_fn to the single shared CF's weights.
    """
    single_cf_fn = OutputFnParameter(default=IdentityOF())
    
    def __call__(self, cfs, output_activity, norm_values=None, **params):
        """Apply the specified single_cf_fn to every CF."""
        if type(self.single_cf_fn) is not IdentityOF:
            cf = cfs[0][0]
            self.single_cf_fn(cf.weights)


class SharedWeightCF(ConnectionField):
	
    # JAHACKALERT: This implementation copies some of the CEBHACKALERTS 
    # of the ConnectionField.__init__ function from which it is dervied
    def __init__(self,cf,x,y,bounds_template,mask_template,input_sheet):
        """
        From an existing copy of ConnectionField (CF) that acts as a
	template, create a new CF that shares weights with the
	template CF.  Copies all the properties of CF to stay
	identical except the weights variable that actually contains
	the data.
	
	The only difference from a normal CF is that the weights of
	the CF are implemented as a numpy view into the single master
	copy of the weights stored in the CF template.
        """
        self.x = x; self.y = y
        self.input_sheet = input_sheet
	self.bounds_template = bounds_template

        # Move bounds to correct (x,y) location, and convert to an array
        # CEBHACKALERT: make this clearer by splitting into two functions.
        # JANOTE: sets self.bounds and self.slice_array; not sure
	# whether this has to be still called!!!!
	self.offset_bounds()

        # Now we have to get the right submatrix of the mask (in case
        # it is near an edge)
        r1,r2,c1,c2 =  self.get_slice()
        self.weights = cf.weights[r1:r2,c1:c2]
	
	# JAHACKALERT the OutputFn cannot be applied in SharedWeightCF
	# - another inconsistency in the class tree design - there
	# should be nothing in the parent class that is ignored in its
	# children.  Probably need to extract some functionality of
        # ConnectionField into a shared abstract parent class.
	# We have agreed to make this right by adding a constant property that
	# will be set true if the learning should be active
	# The SharedWeightCFProjection class and its anccestors will
	# have this property set to false which means that the 
	# learning will be deactivated
	

class SharedWeightCFProjection(CFProjection):
    """
    A Projection with a single set of weights, shared by all units.

    Otherwise similar to CFProjection, except that learning is
    currently disabled.
    """
    
    ### JABHACKALERT: Set to be constant as a clue that learning won't
    ### actually work yet.
    learning_fn = CFPLearningFnParameter(CFPLF_Identity(),constant=True)
    output_fn  = OutputFnParameter(default=IdentityOF())
    weights_output_fn = CFPOutputFnParameter(default=CFPOF_SharedWeight())


    def __init__(self,**params):
        """
        Initialize the Projection with a single cf_type object
        (typically a ConnectionField),
        """
        # We don't want the whole set of cfs initialized, but we
        # do want anything that CFProjection defines.
        super(SharedWeightCFProjection,self).__init__(initialize_cfs=False,**params)

        # We want the sharedcf to be located on the grid, so
        # pick a central unit and use its center
        self.__sharedcf=self.cf_type(self.center_unitxcenter,
                                     self.center_unitycenter,
                                     self.src,
                                     self.bounds_template,
                                     self.weights_generator,
                                     self.mask_template,
                                     self.weights_output_fn.single_cf_fn)

        cflist = []
        scf = self.__sharedcf
        bounds_template = self.bounds_template
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                cf = SharedWeightCF(scf,x,y,bounds_template,self.mask_template,self.src)
                row.append(cf)
            cflist.append(row)
        self._cfs = cflist

    
    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
	self.response_fn(self._cfs, input_activity, self.activity, self.strength)
        self.output_fn(self.activity)


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
    
    
    def learn(self):
	"""
        Because of how output functions are applied, it is not currently
        possible to use learning functions and output functions for
        SharedWeightCFProjections, so we disable them here.
	"""
        pass
    
    
    def apply_learn_output_fn(self,mask):
	"""
        Because of how output functions are applied, it is not currently
        possible to use learning functions and output functions for
        SharedWeightCFProjections, so we disable them here.
	"""
	pass


class LeakyCFProjection(CFProjection):
    """
    A projection that has a decay_rate parameter so that incoming
    input is decayed over time as x(t) = input + x(t-1)*exp(-decay_rate),
    and then the weighted sum of x(t) is calculated.
    """

    decay_rate = Number(default=1.0,bounds=(0,None),
                        doc="Input decay rate for each leaky synapse")

    def __init__(self,**params):
        super(LeakyCFProjection,self).__init__(**params)
	self.leaky_input_buffer = Numeric.zeros(self.src.activity.shape)

    def activate(self,input_activity):
	"""
	Retain input_activity from the previous step in leaky_input_buffer
	and add a leaked version of it to the current input_activity. This 
	function needs to deal with a finer time-scale.
	"""
	self.leaky_input_buffer = input_activity + self.leaky_input_buffer*exp(-self.decay_rate) 
        super(LeakyCFProjection,self).activate(self.leaky_input_buffer)



