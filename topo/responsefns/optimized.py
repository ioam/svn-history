"""
Response functions for CFProjections written in C to optimize performance. 

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__='$Revision$'

from topo.base.connectionfield import CFResponseFunction
from topo.base.parameterclasses import Parameter
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.inlinec import inline, optimized

from topo.responsefns.basic import CFDotProduct, CFEuclideanDistance

class CFDotProduct_opt1(CFResponseFunction):
    """
    Dot-product response function.

    Written in C for a several-hundred-times speedup; see
    CFDotProduct_Py for an easier-to read (but otherwise equivalent)
    version in Python.
    """
    def __init__(self,**params):
        super(CFDotProduct_opt1,self).__init__(**params)

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
    CFDotProduct_opt1 = CFDotProduct
    ParameterizedObject().message('Inline-optimized components not available; using CFDotProduct instead of CFDotProduct_opt1.')



class CFEuclideanDistance_opt1(CFResponseFunction):
    """
    Euclidean-distance response function.

    Written in C for a several-hundred-times speedup; see
    CFDotProduct_Py for an easier-to read (but otherwise equivalent)
    version in Python.
    """
    def __init__(self,**params):
        super(CFEuclideanDistance_opt1,self).__init__(**params)

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
    CFEuclideanDistance_opt1 = CFEuclideanDistance
    ParameterizedObject().message('Inline-optimized components not available; using CFEuclideanDistance instead of CFEuclideanDistance_opt1.')


