"""
Response functions (see basic.py) and CFProjection response functions
(see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__='$Revision$'

from topo.base.connectionfield import CFProjectionResponseFn
from topo.base.parameterclasses import Parameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.inlinec import inline, optimized

from topo.responsefns.projfns import CFProjectionDotProduct, CFProjectionEuclideanDistance

class CFProjectionDotProduct_opt1(CFProjectionResponseFn):
    """
    Dot-product response function.

    Written in C for a several-hundred-times speedup; see
    CFProjectionDotProduct for an easier-to read (but otherwise equivalent)
    version in Python.
    """
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
    CFprojectionDotProduct_opt1 = CFProjectionDotProduct
    ParameterizedObject().message('Inline-optimized components not available; using CFProjectionDotProduct instead of CFProjectionDotProduct_opt1.')



class CFProjectionEuclideanDistance_opt1(CFProjectionResponseFn):
    """
    Euclidean-distance response function.

    Written in C for a several-hundred-times speedup; see
    CFProjectionEuclideanDistance for an easier-to read (but otherwise
    equivalent) version in Python.
    """
    def __init__(self,**params):
        super(CFProjectionEuclideanDistance_opt1,self).__init__(**params)

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
    CFProjectionEuclideanDistance_opt1 = CFProjectionEuclideanDistance
    ParameterizedObject().message('Inline-optimized components not available; using CFProjectionEuclideanDistance instead of CFProjectionEuclideanDistance_opt1.')


