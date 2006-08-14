"""
Output functions (see basic.py) and projection-level output functions
(see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.
"""

from topo.base.cf import CFPOutputFn,CFPOF_Plugin
from topo.base.functionfamilies import OutputFn, OutputFnParameter, IdentityOF
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject

from topo.misc.inlinec import inline, optimized

from basic import DivisiveNormalizeL1

from Numeric import sum

# For backwards compatibility when loading pickled files; can be deleted
DivisiveNormalizeL1_opt=DivisiveNormalizeL1

class CFPOF_DivisiveNormalizeL1_opt(CFPOutputFn):
    """
    Performs divisive normalization of the weights of all cfs.

    Intended to be equivalent to, but faster than,
    CFPOF_DivisiveNormalizeL1.
    """
    single_cf_fn = OutputFnParameter(DivisiveNormalizeL1(norm_value=1.0),
                                     constant=True)

    def __call__(self, cfs, mask, **params):
        rows,cols = mask.shape

        # The original code normalized only the CFs for units that were
        # activated; it might be possible to restore that extra optimization
        # if some way is found to override that for the first iteration.
        code = """
            double *x = mask;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    double load = *x++;
                    if (load != 0)
                    {
                        PyObject *cf = PyList_GetItem(cfsr,l);
                        PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                        PyObject *slice_obj   = PyObject_GetAttrString(cf,"slice_array");
                        PyObject *sum_obj     = PyObject_GetAttrString(cf,"norm_total");
                        
                        float *wi = (float *)(((PyArrayObject*)weights_obj)->data);
                        int *slice =  (int *)(((PyArrayObject*)slice_obj)->data);
                        double total = PyFloat_AsDouble(sum_obj); // sum of the cf's weights

                        int rr1 = *slice++;
                        int rr2 = *slice++;
                        int cc1 = *slice++;
                        int cc2 = *slice;

                        // normalize the weights
                        double factor = 1.0/total;
                        int rc = (rr2-rr1)*(cc2-cc1);
                        for (int i=0; i<rc; ++i) {
                            *(wi++) *= factor;
                        }

                        // Anything obtained with PyObject_GetAttrString must be explicitly freed
                        Py_DECREF(weights_obj);
                        Py_DECREF(slice_obj);
                        Py_DECREF(sum_obj);

                        // Delete the stale norm_total
                        PyObject_DelAttrString(cf,"norm_total");
                    }
                }
            }
        """    
        inline(code, ['mask','rows','cols','cfs'], local_dict=locals())


class CFPOF_DivisiveNormalizeL1(CFPOutputFn):
    """
    Non-optimized version of CFOF_DivisiveNormalizeL1_opt1.

    Same as CFPOF_Plugin(single_cf_fn=DivisiveNormalizeL1), except
    that it supports joint normalization using the norm_total
    property of ConnectionField.
    """

    single_cf_fn = OutputFnParameter(DivisiveNormalizeL1(norm_value=1.0),
                                     constant=True)

    def __call__(self, cfs, mask, **params):
        """
        Uses the cf.norm_total attribute to allow optimization
        by computing the sum separately, and to allow joint
        normalization.  After use, cf.norm_total is deleted because
        the value it would have has been changed.
        """
        if type(self.single_cf_fn) is not IdentityOF:
            rows,cols = mask.shape
            single_cf_fn = self.single_cf_fn
            norm_value = self.single_cf_fn.norm_value                

            for r in xrange(rows):
                for c in xrange(cols):
                    if (mask[r][c] != 0):
                        cf = cfs[r][c]
    		        current_sum=cf.norm_total
    	                factor = norm_value/current_sum
    	                cf.weights *= factor
                        del cf.norm_total


if not optimized:
    CFPOF_DivisiveNormalizeL1_opt = CFPOF_DivisiveNormalizeL1
    ParameterizedObject().message('Inline-optimized components not available; using CFPOF_DivisiveNormalizeL1 instead of CFPOF_DivisiveNormalizeL1_opt.')
