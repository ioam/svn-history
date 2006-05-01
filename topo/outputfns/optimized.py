"""
Output functions (see basic.py) and projection-level output functions
(see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.
"""
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import Number
from topo.base.cf import CFProjectionOutputFn,CFProjectionGenericOutputFn
from topo.base.functionfamilies import OutputFn, OutputFnParameter

from topo.misc.inlinec import inline, optimized

from basic import DivisiveSumNormalize


# CB: will be DivisiveL1Normalize (i.e. will use the
# absolute values - see basic.py).
class DivisiveSumNormalize_opt1(OutputFn):
    """
    OutputFn that divides an array by its sum.

    See the equivalent version in outputfns.basic for a
    description.

    The given array must be of type Numeric.Float32.
    """
    norm_value = Number(default=1.0)    

    def __init__(self,**params):
        super(DivisiveSumNormalize_opt1,self).__init__(**params)

    def __call__(self, x, current_norm_value=None):
        """
        Normalize the input array.

        If the array's current norm_value is already equal to the required
        norm_value, the operation is skipped.
        """
        # Doesn't seem like it would be much faster to do this bit in C
        if current_norm_value==None:
            current_norm_value = sum(x.flat)
        
        if current_norm_value==self.norm_value:
            return x

        target_norm_value = self.norm_value

        if current_norm_value != 0:
            rows,cols=x.shape
            
            div_sum_norm_code = """
            float *xi = x;

            double factor = target_norm_value/current_norm_value;

            for (int i=0; i<rows*cols; ++i) {
                *(xi++) *= factor;
            }
            """
            inline(div_sum_norm_code, ['x','current_norm_value','target_norm_value','rows','cols'], local_dict=locals())

        return x


if not optimized:
    DivisiveSumNormalize_opt1 = DivisiveSumNormalize
    ParameterizedObject().message('Inline-optimized components not available; using DivisiveSumNormalize instead of DivisiveSumNormalize_opt1.')



## class PiecewiseLinear(OutputFn):
##     """ 
##     Piecewise-linear output function with lower and upper thresholds
##     as constructor parameters.
##     """
##     lower_bound = Number(default=0.0,softbounds=(0.0,1.0))
##     upper_bound = Number(default=1.0,softbounds=(0.0,1.0))
    
##     def __call__(self,x):
        
##         fact = 1.0/(self.upper_bound-self.lower_bound)        
##         rows,cols = x.shape
##         lower_bound = self.lower_bound
        
##         clip_code = """
##         double *xi = x;
        
##         for (int i=0; i<rows*cols; ++i) {
##             *xi -= lower_bound;
##             *xi *= fact;
        
##             if (*xi < 0.0) {
##                 *xi = 0.0;
##             }
##             else {
##                 if (*xi > 1.0) {
##                    *xi = 1.0;
##                 }
##             }
##             xi++;
##         }
##         """
##         inline(clip_code, ['x','lower_bound','fact','rows','cols'], local_dict=locals())

##         return x


class CFProjectionDivisiveSumNormalize_opt1(CFProjectionOutputFn):
    """
    Performs divisive normalization of the weights of all cfs.

    Equivalent to
    GenericCFProjectionOutputFn(single_cf_fn=DivisiveSumNormalize(norm_value=1.0)),
    except this assumes the presence of the _sum attribute on any
    activated unit's CFs.
    """
    single_cf_fn = OutputFnParameter(DivisiveSumNormalize_opt1(norm_value=1.0),
                                     constant=True)

    def __init__(self,**params):
        super(CFProjectionDivisiveSumNormalize_opt1,self).__init__(**params)

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
                        float *wi = (float *)(((PyArrayObject*)PyObject_GetAttrString(cf,"weights"))->data);
                        int *slice = (int *)(((PyArrayObject*)PyObject_GetAttrString(cf,"slice_array"))->data);
                        int rr1 = *slice++;
                        int rr2 = *slice++;
                        int cc1 = *slice++;
                        int cc2 = *slice;

                        // get the sum of the cf's weights
                        double total = PyFloat_AsDouble(PyObject_GetAttrString(cf,"_sum"));

                        // normalize the weights
                        total = 1.0/total;
                        int rc = (rr2-rr1)*(cc2-cc1);
                        for (int i=0; i<rc; ++i) {
                            *(wi++) *= total;
                        }

                        // store the new sum (unlikely to be accessed before
                        // learning, but makes things consistent)
                        PyObject_SetAttrString(cf,"_sum",PyFloat_FromDouble(1.0));
                    }
                }
            }
        """    
        inline(code, ['output_activity','rows','cols','cfs'], local_dict=locals())


class CFProjectionDivisiveSumNormalize(CFProjectionGenericOutputFn):
    """
    Wraps
    CFProjectionGenericOutputFn(single_cf_fn=DivisiveSumNormalize),
    the non-optimized equivalent of DivisiveSumNormalizeCFOF_opt1.
    """
    def __init__(self,**params):
        super(CFProjectionDivisiveSumNormalize,self).__init__(single_cf_fn=DivisiveSumNormalize(norm_value=1.0),**params)


if not optimized:
    CFProjectionDivisiveSumNormalize_opt1 = CFProjectionDivisiveSumNormalize
    ParameterizedObject().message('Inline-optimized components not available; using CFProjectionDivisiveSumNormalize instead of CFProjectionDivisiveSumNormalize_opt1.')
