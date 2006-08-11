"""
Learning functions (see basic.py) and projection-level learning
functions (see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__ = "$Revision$"

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Parameter
from topo.base.cf import CFPLearningFn,CFPLF_Plugin
from topo.base.functionfamilies import Hebbian

from topo.misc.inlinec import inline, optimized



class CFPLF_Hebbian_opt(CFPLearningFn):
    """
    CF-aware Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    CFPLF_Plugin(single_cf_fn=Hebbian), except faster.  

    As a side effect, sets the norm_total attribute on any cf whose
    weights are updated during learning, to speed up later operations
    that might depend on it.
    """
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
        len, len2 = input_activity.shape

        hebbian_code = """
            double *x = output_activity;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    double load = *x++;
                    if (load != 0) {
                        load *= single_connection_learning_rate;

                        PyObject *cf = PyList_GetItem(cfsr,l);
                        PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                        PyObject *slice_obj   = PyObject_GetAttrString(cf,"slice_array");
                        PyObject *mask_obj    = PyObject_GetAttrString(cf,"mask");

                        float *wi = (float *)(((PyArrayObject*)weights_obj)->data);
                        int *slice =  (int *)(((PyArrayObject*)slice_obj)->data);
                        float *m  = (float *)(((PyArrayObject*)mask_obj)->data);
                        
                        int rr1 = *slice++;
                        int rr2 = *slice++;
                        int cc1 = *slice++;
                        int cc2 = *slice;
                        
                        double total = 0.0;
                        
                        // modify non-masked weights
                        double *inpj = input_activity+len*rr1+cc1;
                        for (int i=rr1; i<rr2; ++i) {
                            double *inpi = inpj;
                            for (int j=cc1; j<cc2; ++j) {
                                // The mask is floating point, so we have to 
                                // use a robust comparison instead of testing 
                                // against exactly 0.0.
                                if (*(m++) >= 0.000001) {
                                    *wi += load * *inpi;
                                    total += fabs(*wi);
                                }
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }

                        // Anything obtained with PyObject_GetAttrString must be explicitly freed
                        Py_DECREF(weights_obj);
                        Py_DECREF(slice_obj);
                        Py_DECREF(mask_obj);
                        
                        // store the sum of the cf's weights
                        PyObject *total_obj = PyFloat_FromDouble(total);  //(new ref)
                        PyObject_SetAttrString(cf,"norm_total",total_obj);
                        Py_DECREF(total_obj);
                    }
                }
            }
        """

        inline(hebbian_code, ['input_activity', 'output_activity','rows', 'cols', 'len', 'cfs', 'single_connection_learning_rate'], local_dict=locals())
    
       

class CFPLF_Hebbian(CFPLF_Plugin):
    """
    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to CFPLF_Plugin(single_cf_fn=Hebbian()).
    """
    def __init__(self,**params):
        super(CFPLF_Hebbian,self).__init__(single_cf_fn=Hebbian(),**params)

if not optimized:
    CFPLF_Hebbian_opt = CFPLF_Hebbian
    ParameterizedObject().message('Inline-optimized components not available; using CFPLF_Hebbian instead of CFPLF_Hebbian_opt.')
