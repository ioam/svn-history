"""
Response functions (see basic.py) and CFProjection response functions
(see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__='$Revision$'

from topo.base.functionfamilies import ResponseFnParameter,DotProduct,ResponseFn
from topo.base.cf import CFPResponseFn
from topo.base.parameterizedobject import ParameterizedObject

from topo.misc.inlinec import inline, optimized

from topo.responsefns.projfns import CFPRF_DotProduct, CFPRF_EuclideanDistance

from topo.projections.basic import CFPRF_SharedWeight


class CFPRF_DotProduct_opt(CFPResponseFn):
    """
    Dot-product response function.

    Written in C for a several-hundred-times speedup; see
    CFPRF_DotProduct for an easier-to-read (but otherwise equivalent)
    version in Python.
    """

    single_cf_fn = ResponseFnParameter(DotProduct(),constant=True)    

    def __call__(self, cfs, input_activity, activity, strength, **params):
        temp_act = activity
        rows,cols = activity.shape
        len, len2 = input_activity.shape
        X = input_activity.flat
    
        code = """
            double *tact = temp_act;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
		for (int l=0; l<cols; ++l) {
                    PyObject *cf = PyList_GetItem(cfsr,l);
                    int *slice = (int *)(((PyArrayObject*)PyObject_GetAttrString(cf,"slice_array"))->data);
                    int rr1 = *slice++;
                    int rr2 = *slice++;
                    int cc1 = *slice++;
                    int cc2 = *slice;
		    double tot = 0.0;
                    float *wj = (float *)(((PyArrayObject*)PyObject_GetAttrString(cf,"weights"))->data);
		    double *xj = X+len*rr1+cc1;

                    // computes the dot product
		    for (int i=rr1; i<rr2; ++i) {
                        double *xi = xj;
			float *wi = wj;                       
			for (int j=cc1; j<cc2; ++j) {
                            tot += *wi * *xi;
                            ++wi;
                            ++xi;
                        }
                        xj += len;
			wj += cc2-cc1;
                    }  
                    *tact = tot*strength;
                    ++tact;
                }
            }
        """
    
        inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows'], local_dict=locals())

if not optimized:
    CFPRF_DotProduct_opt = CFPRF_DotProduct
    ParameterizedObject().message('Inline-optimized components not available; using CFPRF_DotProduct instead of CFPRF_DotProduct_opt.')



class CFPRF_EuclideanDistance_opt(CFPResponseFn):
    """
    Euclidean-distance response function.

    Written in C for a several-hundred-times speedup; see
    CFPRF_EuclideanDistance for an easier-to-read (but otherwise
    equivalent) version in Python.
    """
    def __call__(self, cfs, input_activity, activity, strength, **params):
        temp_act = activity
        rows,cols = activity.shape
        len, len2 = input_activity.shape
        X = input_activity.flat

        code = """
	    #include <math.h>
            float  *wi, *wj; 
            double *xi, *xj;
            double *tact = temp_act;
            int *slice;
            int rr1, rr2, cc1, cc2;
	    PyObject *cf, *cfsr;
            PyObject *sarray = PyString_FromString("slice_array");
            PyObject *weights = PyString_FromString("weights");
	    double euclidean_distance, tot;
 	    double max_dist=0.0;
    
            for (int r=0; r<rows; ++r) {
                cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    cf = PyList_GetItem(cfsr,l);
                    slice = (int *)(((PyArrayObject*)PyObject_GetAttr(cf,sarray))->data);
                    rr1 = *slice++;
                    rr2 = *slice++;
                    cc1 = *slice++;
                    cc2 = *slice;

                    xj = X+len*rr1+cc1;
		    wj = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
    
                    // computes the dot product
		    tot = 0.0;
                    for (int i=rr1; i<rr2; ++i) {
                        xi = xj;                        
                        wi = wj;
                        for (int j=cc1; j<cc2; ++j) {
			    // JCALERT! find power notation in C.
                            tot += (*wi - *xi) * (*wi - *xi);
                            ++wi;
                            ++xi;
                        }
                        xj += len;
			wj += cc2-cc1;
                    }
		    euclidean_distance = sqrt(tot); 
		    if (euclidean_distance>max_dist) {
		        max_dist = euclidean_distance;
                    }	    
                    *tact = euclidean_distance;
                    ++tact;
                }
            }
	    tact = temp_act;
	    for (int r=0; r<rows; ++r) {
	        for (int l=0; l<cols; ++l) {
    		    *tact = strength*(max_dist - *tact);
		    ++tact;
                }
            }	
        """

	
    
        inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows'], local_dict=locals())

if not optimized:
    CFPRF_EuclideanDistance_opt = CFPRF_EuclideanDistance
    ParameterizedObject().message('Inline-optimized components not available; using CFPRF_EuclideanDistance instead of CFPRF_EuclideanDistance_opt.')



class DotProduct_opt1(ResponseFn):
    """
    Dot-product response function. Equivalent to DotProduct.

    When used as the single_cf_fn for CFPRF_Plugin,
    improves the performance (compared with using DotProduct).
    However, the entirely C++ CFPRF_DotProduct_opt is still
    much faster.
    """
    def __call__(self, m1, m2):
        rows,cols = m1.shape
        tot = 0.0

        code = """
               for (int i=0; i<rows; ++i) {
                   for (int j=0; j<cols; ++j) {
                       tot += *m1 * *m2;
                       ++m1;
                       ++m2;
                   }
               }  
               """    
        inline(code, ['m1', 'm2', 'cols','rows','tot'], local_dict=locals())
        return tot


if not optimized:
    DotProduct_opt1 = DotProduct
    ParameterizedObject().message('Inline-optimized components not available; using DotProduct instead of DotProduct_opt1.')



# See the hackalert in projections/basic.py; this wouldn't be
# required if SharedWeightProjection wrapped the list of cfs
# better.
class CFPRF_SharedWeightDotProduct_opt(CFPResponseFn):
    """
    Dot-product response function for SharedWeightCFProjection.

    The same as CFPRF_DotProduct, but where there is only one set of weights.
    """
    single_cf_fn = ResponseFnParameter(DotProduct(),constant=True)    

    def __call__(self, cfs, input_activity, activity, strength, **params):
        temp_act = activity
        rows,cols = activity.shape
        len, len2 = input_activity.shape
        X = input_activity.flat
        sw = cfs[0][0].weights

        code = """
            double *tact = temp_act;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
		for (int l=0; l<cols; ++l) {
                    PyObject *cf = PyList_GetItem(cfsr,l);
                    int *slice = (int *)(((PyArrayObject*)PyObject_GetAttrString(cf,"slice_array"))->data);
                    int rr1 = *slice++;
                    int rr2 = *slice++;
                    int cc1 = *slice++;
                    int cc2 = *slice;
		    double tot = 0.0;
                    float *wj = sw;
		    double *xj = X+len*rr1+cc1;

                    // computes the dot product
		    for (int i=rr1; i<rr2; ++i) {
                        double *xi = xj;
			float *wi = wj;                       
			for (int j=cc1; j<cc2; ++j) {
                            tot += *wi * *xi;
                            ++wi;
                            ++xi;
                        }
                        xj += len;
			wj += cc2-cc1;
                    }  
                    *tact = tot*strength;
                    ++tact;
                }
            }
        """
    
        inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows','sw'], local_dict=locals())


class CFPRF_SharedWeightDotProduct(CFPRF_SharedWeight):
    """
    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to
    CFPRF_SharedWeight(single_cf_fn=DotProduct())
    """
    def __init__(self,**params):
        super(CFPRF_SharedWeightDotProduct,self).__init__(single_cf_fn=DotProduct(),**params)


if not optimized:
    CFPRF_SharedWeightDotProduct_opt = CFPRF_SharedWeightDotProduct
    ParameterizedObject().message('Inline-optimized components not available; using CFPRF_SharedWeightDotProduct instead of CFPRF_SharedWeightDotProduct_opt.')
