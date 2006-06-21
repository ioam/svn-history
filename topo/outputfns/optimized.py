"""
Output functions (see basic.py) and projection-level output functions
(see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.
"""

from topo.base.cf import CFPOutputFn,CFPOF_Plugin
from topo.base.functionfamilies import OutputFn, OutputFnParameter
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject

from topo.misc.inlinec import inline, optimized

from basic import DivisiveNormalizeL1

from Numeric import sum


class DivisiveNormalizeL1_opt(OutputFn):
    """
    OutputFn that divides an array by the sum of the absolute value of each element.

    See the equivalent version outputfns.basic.DivisiveNormalizeL1 for
    a description. When used as the single_cf_fn in CFP learning
    functions, provides a performance improvement over the python
    DivisiveNormalizeL1 output function.  The all-C++ CFP learning
    function CFPOF_DivisiveNormalizeL1_opt is still much faster
    though.

    The given array must be of type Numeric.Float32.
    """
    norm_value = Number(default=1.0)    

    def __call__(self, x, current_norm_value=None):
        """
        Normalize the input array.

        If the array's current norm_value is already equal to the required
        norm_value, the operation is skipped.
        """
        # Doesn't seem like it would be much faster to do this bit in C
        if current_norm_value==None:
            current_norm_value = sum(abs(x.flat))
        
        if current_norm_value==self.norm_value:
            return x

        if current_norm_value != 0:
            factor = self.norm_value/current_norm_value
            rows,cols=x.shape
            
            div_sum_norm_code = """
            float *xi = x;

            for (int i=0; i<rows*cols; ++i) {
                *(xi++) *= factor;
            }
            """
            inline(div_sum_norm_code, ['x','rows','cols','factor'], local_dict=locals())


if not optimized:
    DivisiveNormalizeL1_opt = DivisiveNormalizeL1
    ParameterizedObject().message('Inline-optimized components not available; using DivisiveNormalizeL1 instead of DivisiveNormalizeL1_opt.')



class CFPOF_DivisiveNormalizeL1_opt(CFPOutputFn):
    """
    Performs divisive normalization of the weights of all cfs.

    Equivalent to
    CFPOF_Plugin(single_cf_fn=DivisiveNormalizeL1(norm_value=1.0)),
    except this assumes the presence of the _sum attribute on any
    activated unit's CFs, to be set by (e.g.) the learning_fn.
    """
    single_cf_fn = OutputFnParameter(DivisiveNormalizeL1_opt(norm_value=1.0),
                                     constant=True)

    def __call__(self, cfs, output_activity, **params):
        rows,cols = output_activity.shape

        code = """
            double *x = output_activity;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    double load = *x++;
                    if (load != 0) {

                        PyObject *cf = PyList_GetItem(cfsr,l);
                        PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                        PyObject *slice_obj   = PyObject_GetAttrString(cf,"slice_array");
                        PyObject *sum_obj     = PyObject_GetAttrString(cf,"_sum");
                        
                        float *wi = (float *)(((PyArrayObject*)weights_obj)->data);
                        int *slice =  (int *)(((PyArrayObject*)slice_obj)->data);
                        double total = PyFloat_AsDouble(sum_obj); // sum of the cf's weights

                        int rr1 = *slice++;
                        int rr2 = *slice++;
                        int cc1 = *slice++;
                        int cc2 = *slice;

                        // normalize the weights
                        total = 1.0/total;
                        int rc = (rr2-rr1)*(cc2-cc1);
                        for (int i=0; i<rc; ++i) {
                            *(wi++) *= total;
                        }

                        // Anything obtained with PyObject_GetAttrString must be explicitly freed
                        Py_DECREF(weights_obj);
                        Py_DECREF(slice_obj);
                        Py_DECREF(sum_obj);

                        // store the new sum (unlikely to be accessed before
                        // learning, but makes things consistent)
                        PyObject *total_obj = PyFloat_FromDouble(1.0);  //(new ref)
                        PyObject_SetAttrString(cf,"_sum",total_obj);
                        Py_DECREF(total_obj);
                    }
                }
            }
        """    
        inline(code, ['output_activity','rows','cols','cfs'], local_dict=locals())


class CFPOF_DivisiveNormalizeL1(CFPOF_Plugin):
    """
    Non-optimized version of CFOF_DivisiveNormalizeL1_opt1
    (which is just CFPOF_Plugin(single_cf_fn=DivisiveNormalizeL1)).
    """
    def __init__(self,**params):
        super(CFPOF_DivisiveNormalizeL1,self).__init__(single_cf_fn=DivisiveNormalizeL1(norm_value=1.0),**params)


if not optimized:
    CFPOF_DivisiveNormalizeL1_opt = CFPOF_DivisiveNormalizeL1
    ParameterizedObject().message('Inline-optimized components not available; using CFPOF_DivisiveNormalizeL1 instead of CFPOF_DivisiveNormalizeL1_opt.')
