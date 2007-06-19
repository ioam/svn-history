"""
Repository for the basic Projection types.

Mainly provides a place where additional Projections can be added in
future, so that all will be in a well-defined, searchable location.

$Id$
"""

__version__ = "$Revision$"

import copy
import numpy
from math import exp

# So all Projections are present in this package
from topo.base.projection import Projection

from topo.base.cf import CFProjection,CFPLearningFnParameter,CFPLF_Identity,CFPResponseFnParameter,CFPOutputFnParameter,CFPOF_Identity,CFPOutputFn,CFPResponseFn, DotProduct, ResponseFnParameter
from topo.base.functionfamilies import OutputFnParameter,LearningFnParameter,IdentityLF
from topo.base.parameterclasses import Number,BooleanParameter,Parameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.patterngenerator import PatternGeneratorParameter,Constant
from topo.base.sheetview import UnitView
from topo.base.cf import ConnectionField, CFPRF_Plugin, MaskedCFIter
from topo.base.functionfamilies import CoordinateMapperFnParameter,IdentityMF

from topo.misc.utils import rowcol2idx
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
	self.leaky_input_buffer = numpy.zeros(self.src.activity.shape)

    def activate(self,input_activity):
	"""
	Retain input_activity from the previous step in leaky_input_buffer
	and add a leaked version of it to the current input_activity. This 
	function needs to deal with a finer time-scale.
	"""
	self.leaky_input_buffer = input_activity + self.leaky_input_buffer*exp(-self.decay_rate) 
        super(LeakyCFProjection,self).activate(self.leaky_input_buffer)



class OneToOneProjection(Projection):
    """
    A projection that has at most one input connection for each unit.

    This projection has exactly one weight for each destination unit.
    The input locations on the input sheet are determined by a
    coordinate mapper.  Inputs that map outside the bounds of the
    input sheet are treated as having zero weight.
    """
    coord_mapper = CoordinateMapperFnParameter(default=IdentityMF(),
        doc='Function to map a destination unit coordinate into the src sheet.')

    weights_generator = PatternGeneratorParameter(
        default=Constant(),constant=True,
        doc="""Generate initial weight values for each unit of the destination sheet.""")

    output_fn  = OutputFnParameter(default=IdentityOF(),
        doc='Function applied to the Projection activity after it is computed.')

    learning_fn = LearningFnParameter(default=IdentityLF,
        doc="""Learning function applied to weights.""")

    learning_rate = Number(default=0)
    
    def __init__(self,**kw):
        super(OneToOneProjection,self).__init__(**kw)

        dx,dy = self.dest.bounds.centroid()

        # JPALERT: Not sure if this is the right way to generate weights.
        # For full specificity, each initial weight should be dependent on the
        # coordinates of both the src unit and the dest unit.
        self.weights = self.weights_generator(bounds=self.dest.bounds,
                                              xdensity=self.dest.xdensity,
                                              ydensity=self.dest.ydensity)


        # JPALERT: CoordMapperFns should really be made to take
        # matrices of x/y points and apply their mapping to all.  This
        # could give great speedups, esp for AffineTransform mappings,
        # which can be applied to many points with a single matrix
        # multiplication.
        srccoords = [self.coord_mapper(x,y) 
                     for y in reversed(self.dest.sheet_rows())
                     for x in self.dest.sheet_cols()]
        
        self.src_idxs = numpy.array([rowcol2idx(r,c,self.src.activity.shape)
                                     for r,c in (self.src.sheet2matrixidx(u,v)
                                                 for u,v in srccoords)])

        # dest_idxs contains the indices of the dest units whose weights project
        # in bounds on the src sheet.
        src_rows,src_cols = self.src.activity.shape
        def in_bounds(x,y):
            r,c = self.src.sheet2matrixidx(x,y)
            return (0 <= r < src_rows) and (0 <= c < src_cols)
        destmask = [in_bounds(x,y) for x,y in srccoords]

        # The [0] is required because numpy.nonzero returns the
        # nonzero indices wrapped in a one-tuple.
        self.dest_idxs = numpy.nonzero(destmask)[0]
        self.src_idxs = self.src_idxs.take(self.dest_idxs)
        assert len(self.dest_idxs) == len(self.src_idxs)

        self.activity = numpy.zeros(self.dest.shape,dtype=float)

    def activate(self,input):
        self.input_buffer = input
        result = self.weights.take(self.dest_idxs) * input.take(self.src_idxs)
        self.activity.put(self.dest_idxs,result)
        self.output_fn(self.activity)

    def learn(self):
        if self.input_buffer is not None:
            self.learning_fn(self.input_buffer,
                             self.dest.activity,
                             self.weights,
                             self.learning_rate)
