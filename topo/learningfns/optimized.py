"""
Learning functions written in C to optimize performance. 

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__ = "$Revision$"

import topo.base.connectionfield
from topo.misc.inlinec import inline, optimized
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Parameter
from topo.base.connectionfield import CFLearningFunction


# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import IdentityCFLF,GenericCFLF


class Hebbian_opt1(CFLearningFunction):
    """
    CF-aware Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    GenericCFLF(single_cf_fn=hebbian), except faster.  

    Sets the _sum attribute on any cf whose weights are
    updated during learning.
    """
    def __init__(self,**params):
        super(Hebbian_opt1,self).__init__(**params)

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
                        float *wi = (float *)(((PyArrayObject*)PyObject_GetAttrString(cf,"weights"))->data);
                        int *slice = (int *)(((PyArrayObject*)PyObject_GetAttrString(cf,"slice_array"))->data);
                        int rr1 = *slice++;
                        int rr2 = *slice++;
                        int cc1 = *slice++;
                        int cc2 = *slice;
                        float *m = (float *)(((PyArrayObject*)PyObject_GetAttrString(cf,"mask"))->data);
                        double total = 0.0;
                        
                        // modify non-masked weights
                        double *inpj = input_activity+len*rr1+cc1;
                        for (int i=rr1; i<rr2; ++i) {
                            double *inpi = inpj;
                            for (int j=cc1; j<cc2; ++j) {
                                // CEBHACKALERT: the mask is an array of
                                // Numeric.Float32 values. 0 does not appear to transfer
                                // as 0.
                                if (*(m++) >= 0.000001) {
                                    *wi += load * *inpi;
                                    total += *wi;
                                }
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }

                        // store the sum of the cf's weights
                        PyObject_SetAttrString(cf,"_sum",PyFloat_FromDouble(total));
                    }
                }
            }
        """

        inline(hebbian_code, ['input_activity', 'output_activity','rows', 'cols', 'len', 'cfs', 'single_connection_learning_rate'], local_dict=locals())
    
       

class Hebbian(GenericCFLF):
    """
    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to GenericCFLF(single_cf_fn=topo.base.connectionfield.Hebbian())
    """
    def __init__(self,**params):
        super(Hebbian,self).__init__(single_cf_fn=topo.base.connectionfield.Hebbian(),**params)

if not optimized:
    Hebbian_opt1 = Hebbian
    ParameterizedObject().message('Inline-optimized components not available; using Hebbian instead of Hebbian_opt1.')
