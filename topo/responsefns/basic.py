"""
Basic response functions for CFProjections.

These function objects compute a response matrix when given an input
pattern and a set of ConnectionField objects.

$Id$
"""

from topo.base.connectionfield import CFResponseFunction
import weave

class CFDotProduct_Py(CFResponseFunction):
    """
    Dot-product response function.

    Written entirely in Python; see CFDotProduct for a much faster
    (but otherwise equivalent) version.
    """
    def __init__(self,**params):
        super(CFDotProduct_Py,self).__init__(**params)

    def __call__(self,input_activity, rows, cols, activity, cfs, strength):
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice
                X = input_activity[r1:r2,c1:c2]
        
                a = X*cf.weights
                activity[r,c] = sum(a.flat)
        activity *= strength


class CFDotProduct(CFResponseFunction):
    """
    Dot-product response function.

    Written in C for a several-hundred-times speedup; see
    CFDotProduct_Py for an easier-to read (but otherwise equivalent)
    version in Python.
    """
    def __init__(self,**params):
        super(CFDotProduct,self).__init__(**params)

    def __call__(self,input_activity, rows, cols, activity, cfs, strength):
        temp_act = activity
        len, len2 = input_activity.shape
        X = input_activity.flat
    
        code = """
            double tot;
            float *wi; 
            double *xi, *xj;
            double *tact = temp_act;
            int *slice;
            int rr1, rr2, cc1, cc2;
            int i, j, r, l;
            PyObject *cf, *cfsr;
            PyObject *sarray = PyString_FromString("slice_array");
            PyObject *weights = PyString_FromString("weights");
    
            for (r=0; r<rows; ++r) {
                cfsr = PyList_GetItem(cfs,r);
                for (l=0; l<cols; ++l) {
                    cf = PyList_GetItem(cfsr,l);
                    wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                    slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                    rr1 = *slice++;
                    rr2 = *slice++;
                    cc1 = *slice++;
                    cc2 = *slice;
    
                    tot = 0.0;
    
                    // computes the dot product
                    xj = X+len*rr1+cc1;
                    for (i=rr1; i<rr2; ++i) {
                        xi = xj;
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
        """
    
        weave.inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows'])

