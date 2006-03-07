"""
The module defines CFProjection_CPointer, a subclass of CFProjection
that is faster but less flexible.

$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: commented out because cpointer learning functions
# have fallen out of date.

from topo.base.connectionfield import CFProjection, ResponseFunctionParameter,LearningFunctionParameter
from topo.base.parameterclasses import Parameter
from topo.base.projection import Identity
from topo.base.parameterizedobject import ParameterizedObject
## from topo.responsefns.optimized import CFDotProduct_CPointer
## from topo.learningfns.optimized import DivisiveHebbian_CPointer
from topo.misc.inlinec import inline, optimized
from Numeric import ones, Int

## class CFProjection_CPointer(CFProjection):
##     """
##     Faster but less flexible version of CFProjection.
    
##     Same as CFProjection except faster and limited to the special
##     case of the CFDotProduct_CPointer response_fn.  Contains extra data
##     structures to store the pointers to the weights and slice arrays
##     of connection fields.  The response_fn CFDotProduct_CPointer() uses these
##     pointers directly, thus bypassing the slow Python/C API for
##     accessing the arrays.
##     """

##     weight_ptrs = [] 
##     slice_ptrs = []
##     mask_ptrs = []
##     response_fn = ResponseFunctionParameter(default=CFDotProduct_CPointer())
##     learning_fn = LearningFunctionParameter(default=DivisiveHebbian_CPointer())

##     def __init__(self,**params):
##         super(CFProjection_CPointer,self).__init__(**params)
##         # store the pointers to the weight and slice_array array in cf
##         x,y = self.get_shape()
##         self.weight_ptrs = ones((x,y), Int)
##         setup_wp(self.cfs, self.weight_ptrs, x, y)
##         self.slice_ptrs = ones((x,y), Int)
##         setup_sp(self.cfs, self.slice_ptrs, x, y)
##         self.mask_ptrs = ones((x,y), Int)
##         setup_mp(self.cfs, self.mask_ptrs, x, y)

        
##     def activate(self,input_activity):
##         """Activate using the specified response_fn and output_fn."""
##         self.input_buffer = input_activity
##         # need to pass the pointer arrays into the response function
##         self.response_fn(self.cfs, input_activity, self.activity, self.strength, weight_ptrs=self.weight_ptrs, slice_ptrs=self.slice_ptrs,mask_ptrs=self.mask_ptrs)
##         self.activity = self.output_fn(self.activity)


##     def change_bounds(self, new_wt_bounds):
##         CFProjection.change_bounds(self, new_wt_bounds)
## 	# the weight arrays have been changed, so the pointer arrays have to be updated
##         x,y = self.get_shape()
##         self.weight_ptrs = ones((x,y), Int)
##         setup_wp(self.cfs, self.weight_ptrs, x, y)
##         self.slice_ptrs = ones((x,y), Int)
##         setup_sp(self.cfs, self.slice_ptrs, x, y)
##         self.mask_ptrs = ones((x,y), Int)
##         setup_mp(self.cfs, self.mask_ptrs, x, y)


## # Optimized version is overwritten by the unoptimized version if the
## # code does not have optimized set.
## if not optimized:
##     CFProjection_CPointer = CFProjection
##     ParameterizedObject().message('Inline-optimized components not available; using CFProjection instead of CFProjection_CPointer.')
        

## def setup_wp(cfs, wp, rows, cols):
##     """
##     Find out the pointer to the weight array in each connection field in cfs
##     and store it in wp.
##     """
##     hebbian_code = """
##         float *wi;
##         float **wj;
##         int i, j, r, l;
##         PyObject *cf, *cfsr;
##         PyObject *weights = PyString_FromString("weights");

##         wj = (float **)wp;
##         for (r=0; r<rows; ++r) {
##             cfsr = PyList_GetItem(cfs,r);
##             for (l=0; l<cols; ++l) {
##                 cf = PyList_GetItem(cfsr,l);
##                 wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
##                 *wj = wi;
##                 wj++;
##             }
##         }
##     """
##     inline(hebbian_code, ['cfs', 'wp', 'rows', 'cols'], local_dict=locals())


## def setup_sp(cfs, sp, rows, cols):
##     """
##     Find out the pointer to the slice_array array in each connection field in 
##     cfs and store it in sp.
##     """
##     hebbian_code = """
##         int *wi;
##         int **wj;
##         int i, j, r, l;
##         PyObject *cf, *cfsr;
##         PyObject *sarray = PyString_FromString("slice_array");

##         wj = (int **)sp;
##         for (r=0; r<rows; ++r) {
##             cfsr = PyList_GetItem(cfs,r);
##             for (l=0; l<cols; ++l) {
##                 cf = PyList_GetItem(cfsr,l);
##                 wi = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
##                 *wj = wi;
##                 wj++;
##             }
##         }
##     """
##     inline(hebbian_code, ['cfs', 'sp', 'rows', 'cols'], local_dict=locals())


## def setup_mp(cfs, mp, rows, cols):
##     """
##     Find out the pointer to the weight array in each connection field in cfs
##     and store it in wp.
##     """
##     hebbian_code = """
##         float *wi;
##         float **wj;
##         int i, j, r, l;
##         PyObject *cf, *cfsr;
##         PyObject *mask = PyString_FromString("mask");

##         wj = (float **)mp;
##         for (r=0; r<rows; ++r) {
##             cfsr = PyList_GetItem(cfs,r);
##             for (l=0; l<cols; ++l) {
##                 cf = PyList_GetItem(cfsr,l);
##                 wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,mask))->data);
##                 *wj = wi;
##                 wj++;
##             }
##         }
##     """
##     inline(hebbian_code, ['cfs', 'mp', 'rows', 'cols'], local_dict=locals())
