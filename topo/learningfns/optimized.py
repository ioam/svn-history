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


class Hebbian(CFLearningFunction):
    """
    CF-aware Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    GenericCFLF(single_cf_fn=hebbian), except faster.  
    """
    def __init__(self,**params):
        super(Hebbian,self).__init__(**params)

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
                        PyObject_SetAttrString(cf,"sum",PyFloat_FromDouble(total));
                    }
                }
            }
        """

        inline(hebbian_code, ['input_activity', 'output_activity','rows', 'cols', 'len', 'cfs', 'single_connection_learning_rate'], local_dict=locals())
    
       

class Hebbian_Py(GenericCFLF):
    """
    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to GenericCFLF(single_cf_fn=topo.base.connectionfield.Hebbian())
    """
    def __init__(self,**params):
        super(Hebbian_Py,self).__init__(single_cf_fn=topo.base.connectionfield.Hebbian(),**params)

if not optimized:
    Hebbian = Hebbian_Py
    ParameterizedObject().message('Inline-optimized components not available; using Hebbian_Py instead of Hebbian.')






# CEBHACKALERT: this code has not been developed along with the other C code.
# I think we need to pick one type, either use pointer versions or not as
# our "_opt" version. 
## # this code applies the mask wrongly - needs to be made
## # more like code above
## class DivisiveHebbian_CPointer(CFLearningFunction):
##     """
##     CF-aware Hebbian learning rule with built-in divisive normalization.

##     Same as DivisiveHebbian except it takes 2 extra arguments, weights_ptrs
##     and slice_ptrs, in __call__. These 2 argument store the pointers to the
##     weight and slice_array, respectively, of each ConnectionField in
##     CFProjection_CPointer. This class should only be used by a sheet that
##     only has CFProjection_CPointers connected to it. 
##     """
##     output_fn = OutputFunctionParameter(DivisiveSumNormalize())

##     def __init__(self,**params):
##         super(DivisiveHebbian_CPointer,self).__init__(**params)

##     def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
##         weight_ptrs = params['weight_ptrs']
##         slice_ptrs = params['slice_ptrs']
##         mask_ptrs = params['mask_ptrs']
##         rows,cols = output_activity.shape
## 	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
##         len, len2 = input_activity.shape

##         hebbian_div_norm_code = """
##             float *wi, *wj, *wk, *m;
##             double *x, *inpi, *inpj;
##             int *slice;
##             int rr1, rr2, cc1, cc2;
##             int i, j, r, l;
##             double load, delta;
##             double totald;
##             float **wip = (float **)weight_ptrs;
##             int **sip = (int **)slice_ptrs;
            
##             float **mip = (float **)mask_ptrs;
    
##             x = output_activity;
##             for (r=0; r<rows; ++r) {
##                 for (l=0; l<cols; ++l) {
##                     load = *x++;
##                     if (load != 0) {
##                         load *= single_connection_learning_rate;
    
##                         wi = *wip;
##                         wj = wi;
##                         wk = wi;

##                         slice = *sip;
##                         rr1 = *slice++;
##                         rr2 = *slice++;
##                         cc1 = *slice++;
##                         cc2 = *slice;
    
##                         totald = 0.0;
    
##                         inpj = input_activity+len*rr1+cc1;

##                         const int rr1c = rr1;
##                         const int rr2c = rr2;
##                         const int cc1c = cc1;
##                         const int cc2c = cc2;

##                         for (i=rr1c; i<rr2c; ++i) {
##                             inpi = inpj;
##                             for (j=cc1c; j<cc2c; ++j) {
##                                 delta = load * *(inpi++);
##                                 *(wi++) += delta;
##                                 totald += delta;
##                             }
##                             inpj += len;
##                         }

##                         // apply the mask
##                         m = *mip;
##                         for (i=rr1c; i<rr2c; ++i) {
##                             for (j=cc1c; j<cc2c; ++j) {
##                                *(wk++) *= *(m++);
##                                }
##                         }
    
##                         // normalize the weights
##                         totald += 1.0; 
##                         totald = 1.0/totald;
##                         const int rc = (rr2-rr1)*(cc2-cc1);
    
##                         for (i=0; i<rc; ++i) {
##                             *(wj++) *= totald;
##                         }
##                     }
##                     ++mip;
##                     ++wip;
##                     ++sip;
##                 }
##             }
##         """
        
##         inline(hebbian_div_norm_code, ['input_activity', 'output_activity', 'rows', 'cols', 'len', 'single_connection_learning_rate','weight_ptrs','slice_ptrs','mask_ptrs'], local_dict=locals())


## if not optimized:
##     DivisiveHebbian_CPointer = DivisiveHebbian_Py
##     ParameterizedObject().message('Inline-optimized components not available; using DivisiveHebbian_Py instead of DivisiveHebbian_CPointer.')
    


