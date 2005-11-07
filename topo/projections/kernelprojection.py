"""
The module defines KernelProjection, a subclass of CFProjection
that defines projections of connection fields where each
ConnectionField's initial weight matrix is created by calling a
PatternGenerator.

$Id$
"""
__version__='$Revision$'

### JABHACKALERT!
###
### Should eliminate import *.
from topo.base.connectionfield import CFProjection
from topo.base.parameter import Parameter,Constant
from topo.patterns.random import UniformRandomGenerator
from topo.base.boundingregion import Intersection,BoundingBox
from topo.base.utils import *
from topo.base.projection import Identity
from topo.responsefns.basic import CFDotProduct, CFDotProductP
from Numeric import ones, Int

import weave

class KernelProjection(CFProjection):
    """
    Projection that is based on an array of weight patterns generated
    by a PatternGenerator.  The activity of the Projection is
    calculated by a specified response_fn (typically a CF-aware
    version of mdot) and output_fn (which is typically Identity).
    """
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = Parameter(default=UniformRandomGenerator())
    learning_rate = Parameter(default=0.0)

    # Should be changed to a OutputFunctionParameter
    output_fn  = Parameter(default=Identity())
    response_fn = Parameter(default=CFDotProduct())

    def __init__(self,**params):
        super(KernelProjection,self).__init__(**params)
        
        # set up array of ConnectionFields translated to each x,y in the src sheet
        cfs = []
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                row.append(self.cf_type(input_sheet=self.src,weight_bounds=self.weights_bounds,weights_generator=self.weights_generator,weight_type=self.weight_type,normalize=self.normalize,normalize_fn=self.normalize_fn,x=x,y=y))

            cfs.append(row)
        self.set_cfs(cfs)


    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        self.response_fn(input_activity, self.activity, self.cfs, self.strength)
        self.activity = self.output_fn(self.activity)


    def change_bounds(self, new_wt_bounds):
        """
        Change the bounding box for all ConnectionFields in this Projection.

        Currently only allows reducing the size, but should be
        extended to allow increasing as well.
        """
        if not self.weights_bounds.containsbb_exclusive(new_wt_bounds):
            self.warning('Unable to change_bounds; currently allows reducing only.')
            return

        self.weights_bounds = new_wt_bounds
        rows,cols = self.get_shape()
        cfs = self.cfs
        for r in xrange(rows):
            for c in xrange(cols):
                cfs[r][c].change_bounds(new_wt_bounds)


    def change_density(self, new_wt_density):
        """
        Rescales the weight matrix in place, interpolating or decimating as nececessary.

        Not yet implemented.
        """
        raise NotImplementedError



class KernelPointerProjection(KernelProjection):
    """
    Faster but less flexible version of KernelProjection.
    
    Same as KernelProjection except faster and limited to the special
    case of the CFDotProductP response_fn.  Contains extra data
    structures to store the pointers to the weights and slice arrays
    of connection fields.  The response_fn CFDotProductP() uses these
    pointers directly, thus bypassing the slow Python/C API for
    accessing the arrays.
    """

    weight_ptrs = [] 
    slice_ptrs = []
    response_fn = Parameter(default=CFDotProductP())

    def __init__(self,**params):
        super(KernelPointerProjection,self).__init__(**params)
        # store the pointers to the weight and slice_array array in cf
        x,y = self.get_shape()
        self.weight_ptrs = ones((x,y), Int)
        setup_wp(self.cfs, self.weight_ptrs, x, y)
        self.slice_ptrs = ones((x,y), Int)
        setup_sp(self.cfs, self.slice_ptrs, x, y)
        
    def activate(self,input_activity):
        """Activate using the specified response_fn and output_fn."""
        self.input_buffer = input_activity
        # need to pass the pointer arrays into the response function
        self.response_fn(input_activity, self.activity, self.cfs, self.strength, weight_ptrs=self.weight_ptrs, slice_ptrs=self.slice_ptrs)
        self.activity = self.output_fn(self.activity)


    def change_bounds(self, new_wt_bounds):
        KernelProjection.change_bounds(self, new_wt_bounds)
	# the weight arrays have been changed, so the pointer arrays have to be updated
        x,y = self.get_shape()
        self.weight_ptrs = ones((x,y), Int)
        setup_wp(self.cfs, self.weight_ptrs, x, y)
        self.slice_ptrs = ones((x,y), Int)
        setup_sp(self.cfs, self.slice_ptrs, x, y)
        

def setup_wp(cfs, wp, rows, cols):
    """
    Find out the pointer to the weight array in each connection field in cfs
    and store it in wp.
    """
    hebbian_code = """
        float *wi;
        float **wj;
        int i, j, r, l;
        PyObject *cf, *cfsr;
        PyObject *weights = PyString_FromString("weights");

        wj = (float **)wp;
        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                cf = PyList_GetItem(cfsr,l);
                wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                *wj = wi;
                wj++;
            }
        }
    """
    weave.inline(hebbian_code, ['cfs', 'wp', 'rows', 'cols'],  extra_compile_args=['-fomit-frame-pointer -funroll-loops'], extra_link_args=['-lstdc++'])


def setup_sp(cfs, sp, rows, cols):
    """
    Find out the pointer to the slice_array array in each connection field in 
    cfs and store it in sp.
    """
    hebbian_code = """
        int *wi;
        int **wj;
        int i, j, r, l;
        PyObject *cf, *cfsr;
        PyObject *sarray = PyString_FromString("slice_array");

        wj = (int **)sp;
        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                cf = PyList_GetItem(cfsr,l);
                wi = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                *wj = wi;
                wj++;
            }
        }
    """
    weave.inline(hebbian_code, ['cfs', 'sp', 'rows', 'cols'],  extra_compile_args=['-fomit-frame-pointer -funroll-loops'], extra_link_args=['-lstdc++'])

