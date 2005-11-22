"""
Basic learning functions for CFProjections.

$Id$
"""
__version__ = "$Revision$"

import weave

from topo.base.topoobject import TopoObject
from topo.base.parameter import Parameter,Constant
from topo.base.projection import Identity
from topo.base.connectionfield import CFLearningFunction
from topo.outputfns.basic import DivisiveL1Normalize

# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import IdentityCFLF,GenericCFLF


### JABALERT!  Untested.
class Hebbian(CFLearningFunction):
    """
    CF-aware Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    GenericCFLF(single_cf_fn=hebbian), except faster.  Callers can set
    the output_fn to perform normalization if desired.
    """
    output_fn = Parameter(default=Identity())
    
    def __init__(self,**params):
        super(Hebbian,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
        len, len2 = input_activity.shape

        hebbian_code = """
            float *wi, *wj;
            double *x, *inpi, *inpj;
            int *slice;
            int rr1, rr2, cc1, cc2, rc;
            int i, j, r, l;
            PyObject *cf, *cfsr;
            PyObject *sarray = PyString_FromString("slice_array");
            PyObject *weights = PyString_FromString("weights");
            double load, delta;
            double totald;
    
            x = output_activity;
            for (r=0; r<rows; ++r) {
                cfsr = PyList_GetItem(cfs,r);
                for (l=0; l<cols; ++l) {
                    load = *x++;
                    if (load != 0) {
                        load *= learning_rate;
    
                        cf = PyList_GetItem(cfsr,l);
                        wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                        wj = wi;
                        slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                        rr1 = *slice++;
                        rr2 = *slice++;
                        cc1 = *slice++;
                        cc2 = *slice;
    
                        totald = 0.0;
    
                        inpj = input_activity+len*rr1+cc1;
                        for (i=rr1; i<rr2; ++i) {
                            inpi = inpj;
                            for (j=cc1; j<cc2; ++j) {
                                delta = load * *inpi;
                                *wi += delta;
                                totald += delta;
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }
                    }
                }
            }
        """
        
        weave.inline(hebbian_code, ['input_activity', 'output_activity', 'rows', 'cols', 'len', 'cfs', 'learning_rate'], extra_compile_args=['-O2','-fomit-frame-pointer','-funroll-loops'], extra_link_args=['-lstdc++'])

        # Apply output_fn to each CF
        # (skipped entirely for no-op case, as an optimization)
        if type(output_fn) is not Identity:
            for r in range(rows):
                for c in range(cols):
                    cfs[r][c].weights = output_fn(cfs[r][c].weights)


### JABALERT!  Untested.
class DivisiveHebbian(CFLearningFunction):
    """
    CF-aware Hebbian learning rule with built-in divisive normalization.

    Implemented in C for speed.  Should be equivalent to
    GenericCFLF(single_cf_fn=hebbian,output_fn=DivisiveL1Normalize()),
    except faster.  The output_fn cannot be modified, because the
    divisive normalization is performed in C while doing the weight
    modification; the output_fn is not actually called from within
    this function.
    """
    output_fn = Constant(DivisiveL1Normalize())

    def __init__(self,**params):
        super(DivisiveHebbian,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
        len, len2 = input_activity.shape

        hebbian_div_norm_code = """
            float *wi, *wj;
            double *x, *inpi, *inpj;
            int *slice;
            int rr1, rr2, cc1, cc2, rc;
            int i, j, r, l;
            PyObject *cf, *cfsr;
            PyObject *sarray = PyString_FromString("slice_array");
            PyObject *weights = PyString_FromString("weights");
            double load, delta;
            double totald;

            x = output_activity;
            for (r=0; r<rows; ++r) {
                cfsr = PyList_GetItem(cfs,r);
                for (l=0; l<cols; ++l) {
                    load = *x++;
                    if (load != 0) {
                        load *= learning_rate;

                        cf = PyList_GetItem(cfsr,l);
                        wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                        wj = wi;
                        slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                        rr1 = *slice++;
                        rr2 = *slice++;
                        cc1 = *slice++;
                        cc2 = *slice;

                        totald = 0.0;

                        inpj = input_activity+len*rr1+cc1;
                        for (i=rr1; i<rr2; ++i) {
                            inpi = inpj;
                            for (j=cc1; j<cc2; ++j) {
                                delta = load * *inpi;
                                *wi += delta;
                                totald += delta;
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }

                        // normalize the weights
                        totald += 1.0;
                        totald = 1.0/totald;
                        rc = (rr2-rr1)*(cc2-cc1);

                        for (i=0; i<rc; ++i) {
                            *wj *= totald;
                            ++wj;
                        }
                    }
                }
            }
        """
        
        weave.inline(hebbian_div_norm_code, ['input_activity', 'output_activity','rows', 'cols', 'len', 'cfs', 'learning_rate'], extra_compile_args=['-O2','-fomit-frame-pointer','-funroll-loops'], extra_link_args=['-lstdc++'])




### JABALERT!  Untested.
class DivisiveHebbian_CPointer(CFLearningFunction):
    """
    CF-aware Hebbian learning rule with built-in divisive normalization.

    Same as DivisiveHebbian except it takes 2 extra arguments, weights_ptrs
    and slice_ptrs, in __call__. These 2 argument store the pointers to the
    weight and slice_array, respectively, of each ConnectionField in
    CFProjection_CPointer. This class should only be used by a sheet that
    only has CFProjection_CPointers connected to it. 
    """
    output_fn = Constant(DivisiveL1Normalize())

    def __init__(self,**params):
        super(DivisiveHebbian_CPointer,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        weight_ptrs = params['weight_ptrs']
        slice_ptrs = params['slice_ptrs']
        rows,cols = output_activity.shape
        len, len2 = input_activity.shape

        hebbian_div_norm_code = """
            float *wi, *wj;
            double *x, *inpi, *inpj;
            int *slice;
            int rr1, rr2, cc1, cc2;
            int i, j, r, l;
            double load, delta;
            double totald;
            float **wip = (float **)weight_ptrs;
            int **sip = (int **)slice_ptrs;
    
            x = output_activity;
            for (r=0; r<rows; ++r) {
                for (l=0; l<cols; ++l) {
                    load = *x++;
                    if (load != 0) {
                        load *= learning_rate;
    
                        wi = *wip;
                        wj = wi;

                        slice = *sip;
                        rr1 = *slice++;
                        rr2 = *slice++;
                        cc1 = *slice++;
                        cc2 = *slice;
    
                        totald = 0.0;
    
                        inpj = input_activity+len*rr1+cc1;

                        const int rr1c = rr1;
                        const int rr2c = rr2;
                        const int cc1c = cc1;
                        const int cc2c = cc2;

                        for (i=rr1c; i<rr2c; ++i) {
                            inpi = inpj;
                            for (j=cc1c; j<cc2c; ++j) {
                                delta = load * *inpi;
                                *wi += delta;
                                totald += delta;
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }
    
                        // normalize the weights
                        totald += 1.0; 
                        totald = 1.0/totald;
                        const int rc = (rr2-rr1)*(cc2-cc1);
    
                        for (i=0; i<rc; ++i) {
                            *wj *= totald;
                            ++wj;
                        }
                    }
                    ++wip;
                    ++sip;
                }
            }
        """
        
        weave.inline(hebbian_div_norm_code, ['input_activity', 'output_activity', 'rows', 'cols', 'len', 'learning_rate','weight_ptrs','slice_ptrs'], extra_compile_args=['-fomit-frame-pointer','-funroll-loops'], extra_link_args=['-lstdc++'])


