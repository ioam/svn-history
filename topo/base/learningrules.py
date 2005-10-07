"""
Functions and classes that implement different learning rules.

$Id$
"""
__version__ = "$Revision$"

import weave


def hebbian_div_norm_c(input_activity, self_activity, rows, cols, len, cfs, alpha):
    """
    An inline C implementation of Hebbian learning with divisive normalization
    for the whole sheet.
    """
        
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

        x = self_activity;
        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                load = *x++;
                if (load != 0) {
                    load *= alpha;

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
    
    weave.inline(hebbian_div_norm_code, ['input_activity', 'self_activity', 'rows', 'cols', 'len', 'cfs', 'alpha'])



def hebbian_c(input_activity, self_activity, rows, cols, len, cfs, alpha):
    """
    An inline C implementation of Hebbian learning for the whole sheet.
    """
        
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

        x = self_activity;
        for (r=0; r<rows; ++r) {
            cfsr = PyList_GetItem(cfs,r);
            for (l=0; l<cols; ++l) {
                load = *x++;
                if (load != 0) {
                    load *= alpha;

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
    
    weave.inline(hebbian_code, ['input_activity', 'self_activity', 'rows', 'cols', 'len', 'cfs', 'alpha'])



def hebbian(input_activity, unit_activity, weights, alpha):
    """
    Hebbian learning for one single unit.
    """
    weights += alpha * unit_activity * input_activity


################################################################
# Normalization methods

def divisive_normalization(weights):
    """
    Normalize the numpy array weights to sum to 1.0 by divisive
    normalization.
    """

    s = sum(weights.flat)
    if s != 0:
        factor = 1.0/s
        weights *= factor


################################################################
# Wrapper functions of the learning and normalization methods

def apply_learn_norm_fn(proj, inp, act, learn_fn, norm_fn):
    """
    Apply the specified learn_fn and then norm_fn to the connections fields
    in proj using input inp and output activity act.
    """

    rows,cols = act.shape
    alpha = proj.learning_rate

    if learn_fn.func_name == "hebbian_c":
        # hebbian_c is an function for the whole sheet
        cfs = proj.cfs
        len, len2 = inp.shape
        if proj.normalize:
            # Hebbian learning with divisive normalization per projection. 
            # It is much faster to do both of them in one function.
            if norm_fn.func_name == "divisive_normalization":
                hebbian_div_norm_c(inp, act, rows, cols, len, cfs, alpha)
            else:
                hebbian_c(inp, act, rows, cols, len, cfs, alpha)
                norm = proj.normalize
                for r in range(rows):
                    for c in range(cols):
                        norm_fn(cfs[r][c].weights)
        else:
            hebbian_c(inp, act, rows, cols, len, cfs, alpha)
    else:
        # apply learning rule and normalization to each unit
        norm = proj.normalize
        for r in range(rows):
            for c in range(cols):
                cf = proj.cf(r,c)
                learn_fn(cf.get_input_matrix(inp), act[r,c], cf.weights, alpha)
                if norm:
                    norm_fn(cf.weights)

