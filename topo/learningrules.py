"""
Functions and classes that implement different learning rules.

$Id$
"""
__version__ = "$Revision$"

import weave


def hebbian_div_norm_c(input_activation, self_activation, rows, cols, len, cfs, alpha, normalize):
    """
    An inline C implementation of Hebbian learning with divisive normalization
    for the whole sheet.
    """
        
    hebbian_div_norm_code = """
        double *wi, *wj, *x, *inpi, *inpj;
        int *slice;
        int rr1, rr2, cc1, cc2, rc;
        int i, j, r, l;
        PyObject *cf, *cfsr;
        PyObject *sarray = PyString_FromString("slice_array");
        PyObject *weights = PyString_FromString("weights");
        double load, delta;
        double totald;

        x = self_activation;
        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                load = *x++;
                if (load != 0) {
                    load *= alpha;

                    cf = PyList_GetItem(cfsr,l);
                    wi = (double *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                    wj = wi;
                    slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                    rr1 = *slice++;
                    rr2 = *slice++;
                    cc1 = *slice++;
                    cc2 = *slice;

                    totald = 0.0;

                    inpj = input_activation+len*rr1+cc1;
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
                    if (normalize) {
                        totald += normalize; 
                        totald = normalize/totald;
                        rc = (rr2-rr1)*(cc2-cc1);

                        for (i=0; i<rc; ++i) {
                            *wj *= totald;
                            ++wj;
                        }
                    }
                }
            }
        }
    """
    
    weave.inline(hebbian_div_norm_code, ['input_activation', 'self_activation', 'rows', 'cols', 'len', 'cfs', 'alpha', 'normalize'])



def hebbian_c(input_activation, self_activation, rows, cols, len, cfs, alpha):
    """
    An inline C implementation of Hebbian learning for the whole sheet.
    """
        
    hebbian_code = """
        double *wi, *wj, *x, *inpi, *inpj;
        int *slice;
        int rr1, rr2, cc1, cc2, rc;
        int i, j, r, l;
        PyObject *cf, *cfsr;
        PyObject *sarray = PyString_FromString("slice_array");
        PyObject *weights = PyString_FromString("weights");
        double load, delta;
        double totald;

        x = self_activation;
        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                load = *x++;
                if (load != 0) {
                    load *= alpha;

                    cf = PyList_GetItem(cfsr,l);
                    wi = (double *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                    wj = wi;
                    slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                    rr1 = *slice++;
                    rr2 = *slice++;
                    cc1 = *slice++;
                    cc2 = *slice;

                    totald = 0.0;

                    inpj = input_activation+len*rr1+cc1;
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
    
    weave.inline(hebbian_code, ['input_activation', 'self_activation', 'rows', 'cols', 'len', 'cfs', 'alpha'])



def hebbian(input_activation, unit_activation, weights, alpha):
    """
    Hebbian learning for one single unit.
    """
    weights += alpha * unit_activation * input_activation

