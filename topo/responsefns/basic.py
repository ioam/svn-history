"""
Basic response functions for CFProjections.

These function objects compute a response matrix when given an input
pattern and a set of ConnectionField objects.

$Id$
"""
__version__='$Revision$'

from topo.base.connectionfield import CFResponseFunction
from topo.base.parameter import Parameter
from topo.base.topoobject import TopoObject
from topo.misc.inlinec import inline, optimized

class CFDotProduct_Py(CFResponseFunction):
    """
    Dot-product response function.

    Written entirely in Python; see CFDotProduct for a much faster
    (but otherwise equivalent) version.
    """
    def __init__(self,**params):
        super(CFDotProduct_Py,self).__init__(**params)

    def __call__(self, cfs, input_activity, activity, strength, **params):
        rows,cols = activity.shape
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice
                X = input_activity[r1:r2,c1:c2]
        
                a = X*cf.weights
                activity[r,c] = sum(a.flat)
        activity *= strength

### JABHACKALERT!  This needs to move to a new file optimized.py.
class CFDotProduct(CFResponseFunction):
    """
    Dot-product response function.

    Written in C for a several-hundred-times speedup; see
    CFDotProduct_Py for an easier-to read (but otherwise equivalent)
    version in Python.
    """
    def __init__(self,**params):
        super(CFDotProduct,self).__init__(**params)

    def __call__(self, cfs, input_activity, activity, strength, **params):
        temp_act = activity
        rows,cols = activity.shape
        len, len2 = input_activity.shape
        X = input_activity.flat
    
        code = """
            double tot;
            float *wi, *wj; 
            double *xi, *xj, *xjtmp;
            double *tact = temp_act;
            int *slice;
            int rr1, rr2, cc1, cc2;
            int oc2, cact, nonzero_act;
            int i, j, r, l, it;
            PyObject *cf, *cfsr;
            PyObject *sarray = PyString_FromString("slice_array");
            PyObject *weights = PyString_FromString("weights");
            int slice_cols;
            int or2;
            int *prev_act = (int *)malloc(cols*sizeof(int));

            memset(prev_act, 0, cols*sizeof(int));
            rr2 = 0;
    
            for (r=0; r<rows; ++r) {
                cfsr = PyList_GetItem(cfs,r);
		nonzero_act = 1;
		cact = -1;
                or2 = rr2;
                for (l=0; l<cols; ++l) {
                    cf = PyList_GetItem(cfsr,l);
                    slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                    rr1 = *slice++;
                    rr2 = *slice++;
                    cc1 = *slice++;
                    cc2 = *slice;

                    slice_cols = cc2-cc1;
    
                    if (prev_act[l] == 0)
                        rr1 = or2;

                    // check if previous cf contains any activity
                    if (nonzero_act==0) {
                        // if previous cf is not active, only need to start
                        // to check from the new column
                        cc1 = oc2-1;
                        oc2 = cc2;
                    } else {
                        oc2 = cc2;
                        // if there is activity at column cact, check if it is
                        // in the current cf, if so, jump to compute activity.
                        // NOTE: work for retangular cf only.
                        if (cc1<=cact && cact<cc2) {
                            it = rr1;
                            xj = X+len*rr1+cc1;
                            goto need_compute;
                        }
                    }

                    xj = X+len*rr1+cc1;
                    xjtmp = xj;

                    // parse through the cf to see if there is any activity
                    // If there isn't any, just don't bother to fetch the
                    // weight object and compute the result (which is 0).
                    for (it=rr1; it<rr2; ++it) {
                        xi = xjtmp;
			nonzero_act = 0;
                        for (j=cc1; j<cc2; ++j) {
			    if (*xi != 0) {
			        cact = j;
				nonzero_act = 1;
				goto need_compute;
			    }
                            ++xi;
                        }
                        xjtmp += len;
                    }
                    // The input in the connection field is 0, so just set the 
                    // activity to 0 and continue.
                    prev_act[l] = 0;
                    *tact = 0.0;
                    ++tact;
                    continue;

             need_compute:
                    prev_act[l] = 1; 
                    tot = 0.0;
                    wj = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
    
                    // computes the dot product
                    xj += (it-rr1)*len;
                    wj += (it-rr1)*slice_cols - (cc2 - cc1);

                    for (i=it; i<rr2; ++i) {
                        xi = xj;
                        wj += slice_cols;
                        wi = wj;
                        for (j=cc1; j<cc2; ++j) {
                            tot += *wi * *xi;
                            ++wi;
                            ++xi;
                        }
                        xj += len;
                    }
    
                    *tact = tot*strength;
                    ++tact;
                }
            }
            free(prev_act);
        """
    
        inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows'], local_dict=locals())

# Optimized version is overwritten by the unoptimized version if the
# code does not have optimized set.
if not optimized:
    CFDotProduct = CFDotProduct_Py
    TopoObject().message('Inline-optimized components not available; using CFDotProduct_Py instead of CFDotProduct.')
        



### JABHACKALERT!  This needs to move to a new file optimized.py.
class CFDotProduct_CPointer(CFResponseFunction):
    """
    Dot-product response function.

    Same as CFDotProduct, but it takes 2 extra named arguments, weights_ptrs and
    slice_ptrs, that store the pointers to the weight and slice_array array.
    This avoids accessing them through the C API.
    """

    def __init__(self,**params):
        super(CFDotProduct_CPointer,self).__init__(**params)

    def __call__(self, cfs, input_activity, activity, strength, **params):
        temp_act = activity
        rows,cols = activity.shape
        len, len2 = input_activity.shape
        X = input_activity.flat
        weight_ptrs = params['weight_ptrs']
        slice_ptrs = params['slice_ptrs']
        
    
        code = """
            double tot;
            float *wi, *wj;
            double *xi, *xj, *xjtmp;
            double *tact = temp_act;
            int *slice;
            int rr1, rr2, cc1, cc2;
            int oc2, cact, nonzero_act;
            int i, j, r, l, it;
            float **wip = (float **)weight_ptrs;
            int **sip = (int **)slice_ptrs;
            int slice_cols;
            int or2;
            int *prev_act = (int *)malloc(cols*sizeof(int));

            memset(prev_act, 0, cols*sizeof(int));
            rr2 = 0;

            for (r=0; r<rows; ++r) {
                nonzero_act = 1;
                cact = -1;
                or2 = rr2;
                for (l=0; l<cols; ++l) {
                    slice = *sip;
                    sip++;

                    rr1 = *slice++;
                    rr2 = *slice++;
                    cc1 = *slice++;
                    cc2 = *slice;

                    slice_cols = cc2-cc1;

                    // if the cf at column l in the previous row contains no
                    // activation, we can skip those that are already covered
                    // by that cf
                    if (prev_act[l] == 0)
                        rr1 = or2;

                    // check if previous cf contains any activity

                    if (nonzero_act==0) {
                        // if previous cf is not active, only need to start
                        // to check from the new column
                        cc1 = oc2-1;
                        oc2 = cc2;
                    } else {
                        // if there is activity at column cact, check if it is
                        // in the current cf, if so, jump to compute activity.
                        // NOTE: work for retangular cf only.
                        oc2 = cc2;
                        if (cc1<=cact && cact<cc2) {
                            it = rr1;
                            xj = X+len*rr1+cc1;
                            goto need_compute;
                        }
                    }

                    xj = X+len*rr1+cc1;
                    xjtmp = xj;


                    // parse through the cf to see if there is any activity
                    // If there isn't any, just don't bother to fetch the
                    // weight object and compute the result (which is 0).
                    for (it=rr1; it<rr2; ++it) {
                        xi = xjtmp;
                        nonzero_act = 0;
                        for (j=cc1; j<cc2; ++j) {
                            if (*xi != 0) {
                                cact = j;
                                nonzero_act = 1;
                                goto need_compute;
                            }
                            ++xi;
                        }
                        xjtmp += len;
                    }
                    // The input in the connection field is 0, so just set the
                    // activity to 0 and continue.
                    prev_act[l] = 0;
                    *tact = 0.0;
                    ++tact;
                    ++wip;
                    continue;

        need_compute:
                    prev_act[l] = 1;
                    tot = 0.0;
                    wj = *wip;
                    wip++;
                    wj += (it-rr1)*slice_cols - (cc2 - cc1);

                    // computes the dot product
                    xj += (it-rr1-1)*len;
                    int count = cc2-cc1;
                    const int m = (count+7)/8;

                    for (i=it; i<rr2; ++i) {
                        xj += len;
                        xi = xj;
                        wj += slice_cols;
                        wi = wj;
                        int n = m;

                        // manual loop unrolling using Duff's device
                        // does the same thing as
                        // for (j=cc1; j<cc2; ++j) {
                        //     tot += *wi * *xi; ++wi; ++xi; }
                        switch(count%8){
                            case 0: do{ tot += *xi * *wi; ++wi; ++xi;
                            case 7: tot += *xi * *wi; ++wi; ++xi;
                            case 6: tot += *xi * *wi; ++wi; ++xi;
                            case 5: tot += *xi * *wi; ++wi; ++xi;
                            case 4: tot += *xi * *wi; ++wi; ++xi;
                            case 3: tot += *xi * *wi; ++wi; ++xi;
                            case 2: tot += *xi * *wi; ++wi; ++xi;
                            case 1: tot += *xi * *wi; ++wi; ++xi;
                                    }while(--n>0);

                        }

                    }

                    *tact = tot*strength;
                    ++tact;
                }
            }
            free(prev_act);

        """

        inline(code, ['X', 'strength', 'len', 'temp_act','cols','rows','weight_ptrs','slice_ptrs'], local_dict=locals())

# Optimized version is overwritten by the unoptimized version if the
# code does not have optimized set.
if not optimized:
    CFDotProduct_CPointer = CFDotProduct_Py
    TopoObject().message('Inline-optimized components not available; using CFDotProduct_Py instead of CFDotProduct_CPointer.')
        
