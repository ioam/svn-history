"""
Learning functions written in C to optimize performance. 

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__ = "$Revision$"

from topo.misc.inlinec import inline, optimized
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Parameter,Number
from topo.base.projection import Identity
from topo.base.connectionfield import CFLearningFunction,OutputFunctionParameter
from topo.outputfns.basic import DivisiveSumNormalize


# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import IdentityCFLF,GenericCFLF


class Hebbian(CFLearningFunction):
    """
    CF-aware Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    GenericCFLF(single_cf_fn=hebbian), except faster.  Callers can set
    the output_fn to perform normalization if desired.
    """
    
    def __init__(self,**params):
        super(Hebbian,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
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
                        load *= single_connection_learning_rate;
    
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
        
        inline(hebbian_code, ['input_activity', 'output_activity', 'rows', 'cols', 'len', 'cfs', 'single_connection_learning_rate'],local_dict=locals())

        # Apply output_fn to each CF, followed by mask
        # (output_fn skipped for no-op case, as an optimization) 
        output_fn = self.output_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                # CEBHACKALERT: see ConnectionField.__init__()
                cf.weights *= cf.mask
                if type(output_fn) is not Identity:
                    cf.weights = output_fn(cf.weights)

class Hebbian_Py(GenericCFLF):
    """
    CF-aware Hebbian learning rule.

    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to GenericCFLF(single_cf_fn=hebbian)
    """
    def __init__(self,**params):
        super(Hebbian_Py,self).__init__(single_cf_fn=hebbian,**params)

if not optimized:
    Hebbian = Hebbian_Py
    ParameterizedObject().message('Inline-optimized components not available; using Hebbian_Py instead of Hebbian.')



# CEBHACKALERT: ought to be DivisiveL1Hebbian (assuming DivisiveSumNormalize
# is changed to DivisiveL1Normalize). Same for similarly named functions.
class DivisiveHebbian(CFLearningFunction):
    """
    CF-aware Hebbian learning rule with built-in divisive normalization.

    Implemented in C for speed.  Should be equivalent to
    GenericCFLF(single_cf_fn=hebbian,output_fn=DivisiveSumNormalize()),
    except faster.  The output_fn cannot be modified, because the
    divisive normalization is performed in C while doing the weight
    modification; the output_fn is not actually called from within
    this function.
    """
    output_fn = OutputFunctionParameter(DivisiveSumNormalize())

    def __init__(self,**params):
        super(DivisiveHebbian,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
	single_connection_learning_rate = self.constant_sum_connection_rate(cfs,learning_rate)
        len, len2 = input_activity.shape

        hebbian_div_norm_code = """
            float *wi, *wj, *m;
            double *x, *inpi, *inpj;
            int *slice;
            int rr1, rr2, cc1, cc2, rc;
            int i, j, r, l;
            PyObject *cf, *cfsr;
            PyObject *sarray = PyString_FromString("slice_array");
            PyObject *weights = PyString_FromString("weights");
            PyObject *mask = PyString_FromString("mask");
            double load, delta;
            double totald;

            x = output_activity;
            for (r=0; r<rows; ++r) {
                cfsr = PyList_GetItem(cfs,r);
                for (l=0; l<cols; ++l) {
                    load = *x++;
                    if (load != 0) {
                        load *= single_connection_learning_rate;

                        cf = PyList_GetItem(cfsr,l);
                        wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                        wj = wi;
                        slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                        rr1 = *slice++;
                        rr2 = *slice++;
                        cc1 = *slice++;
                        cc2 = *slice;
                        m = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,mask))->data);

                        totald = 0.0;

                        // modify non-masked weights
                        inpj = input_activity+len*rr1+cc1;
                        for (i=rr1; i<rr2; ++i) {
                            inpi = inpj;
                            for (j=cc1; j<cc2; ++j) {
                                // CEBHACKALERT: the mask is an array of
                                // Numeric.Float32 values. 0 does not appear to transfer
                                // as 0.
                                if (*(m++) >= 0.000001) {
                                    delta = load * *inpi;
                                    *wi += delta;
                                    totald += delta;
                                }
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }

                        // CEBHACKALERT: it might be better just to sum the current weights
                        // in the loop above and use this in the normalization. It would be
                        // clearer and would probably behave better numerically (maybe
                        // it's not currently summing to 1 exactly). But then it wouldn't
                        // match C++ LISSOM so clearly.

                        // normalize the weights
                        totald += 1.0;
                        totald = 1.0/totald;
                        rc = (rr2-rr1)*(cc2-cc1);

                        for (i=0; i<rc; ++i) {
                            *(wj++) *= totald;
                        }
                    }
                }
            }
        """
        
        inline(hebbian_div_norm_code, ['input_activity', 'output_activity','rows', 'cols', 'len', 'cfs', 'single_connection_learning_rate'], local_dict=locals())
       

class DivisiveHebbian_Py(GenericCFLF):
    """
    Same as GenericCFLF, but with a default output_fn of DivisiveSumNormalize.

    Acts as a an exact (but much, much slower) replacement for
    DivisiveHebbian, to declare what DivisiveHebbian implements and to
    allow fallback when inline-optimized components are not available.
    """
    def __init__(self,**params):
        super(DivisiveHebbian_Py,self).__init__(**params)
        self.output_fn = DivisiveSumNormalize()

if not optimized:
    DivisiveHebbian = DivisiveHebbian_Py
    ParameterizedObject().message('Inline-optimized components not available; using DivisiveHebbian_Py instead of DivisiveHebbian.')


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
    

