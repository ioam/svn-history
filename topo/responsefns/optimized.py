"""
Response functions (see basic.py) and CFProjection response functions
(see projfns.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__='$Revision$'

from topo.base.functionfamilies import ResponseFnParameter,DotProduct,ResponseFn
from topo.base.cf import CFPResponseFn, CFPRF_Plugin
from topo.base.parameterizedobject import ParameterizedObject
from topo.misc.inlinec import inline, provide_unoptimized_equivalent

from topo.responsefns.projfns import CFPRF_EuclideanDistance

class CFPRF_DotProduct_opt(CFPResponseFn):
    """
    Dot-product response function.

    Written in C for a several-hundred-times speedup; see
    CFPRF_DotProduct for an easier-to-read (but otherwise equivalent*)
    version in Python.

    * The unoptimized Python version works for 1D arrays, whereas this
    function assumes 2D arrays.
    """

    single_cf_fn = ResponseFnParameter(DotProduct(),constant=True)    

    def __call__(self, cfs, input_activity, activity, strength, **params):
	
        temp_act = activity
        rows,cols = activity.shape
        len, len2 = input_activity.shape
        X = input_activity.ravel()
    
        code = """
            double *tact = temp_act;
	    float *wj;
	    PyArrayObject *array;
	    
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
		for (int l=0; l<cols; ++l) {
                    PyObject *cf = PyList_GetItem(cfsr,l);
                    PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                    PyObject *slice_obj   = PyObject_GetAttrString(cf,"slice_array");

		    // This code is optimized for contiguous arrays, which are typical,
                    // but we make it work for noncontiguous arrays (e.g. views) by
                    // creating a contiguous copy if necessary.
                    array=0;
		    if(PyArray_ISCONTIGUOUS((PyArrayObject*)weights_obj))
                        wj = (float *)(((PyArrayObject*)weights_obj)->data);
                    else {
		    	array = (PyArrayObject*) PyArray_ContiguousFromObject(weights_obj,PyArray_FLOAT,2,2);
		    	wj = (float *) array->data;
		    }
                    
                    int *slice = (int *)(((PyArrayObject*)slice_obj)->data);
                    
                    int rr1 = *slice++;
                    int rr2 = *slice++;
                    int cc1 = *slice++;
                    int cc2 = *slice;
		    double tot = 0.0;
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

                    // Anything obtained with PyObject_GetAttrString must be explicitly freed
                    Py_DECREF(weights_obj);
                    Py_DECREF(slice_obj);
		    
                    if(array != 0)
		    	Py_DECREF(array);
                }
            }
        """
	inline(code, ['X', 'strength', 'len', 'temp_act','cfs','cols','rows'], local_dict=locals())

class CFPRF_DotProduct(CFPRF_Plugin):
    """
    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to CFPRF_Plugin(single_cf_fn=DotProduct()).
    """
    def __init__(self,**params):
        super(CFPRF_DotProduct,self).__init__(single_cf_fn=DotProduct(),**params)

provide_unoptimized_equivalent("CFPRF_DotProduct_opt","CFPRF_DotProduct",locals())


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
        X = input_activity.ravel()

        code = """
	    #include <math.h>
            double *tact = temp_act;
 	    double max_dist=0.0;
    
            for (int r=0; r<rows; ++r) {
                PyObject* cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    PyObject *cf = PyList_GetItem(cfsr,l);
                    PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                    PyObject *slice_obj   = PyObject_GetAttrString(cf,"slice_array");
                    
		    float *wj = (float *)(((PyArrayObject*)weights_obj)->data);
                    int *slice =  (int *)(((PyArrayObject*)slice_obj)->data);
                    
                    int rr1 = *slice++;
                    int rr2 = *slice++;
                    int cc1 = *slice++;
                    int cc2 = *slice;

                    double *xj = X+len*rr1+cc1;
    
                    // computes the dot product
		    double tot = 0.0;
                    for (int i=rr1; i<rr2; ++i) {
                        double *xi = xj;                        
                        float *wi = wj;
                        for (int j=cc1; j<cc2; ++j) {
                            double diff = *wi - *xi;
			    tot += diff*diff;
                            ++wi;
                            ++xi;
                        }
                        xj += len;
			wj += cc2-cc1;
                    }
		    
		    double euclidean_distance = sqrt(tot); 
		    if (euclidean_distance>max_dist)
		        max_dist = euclidean_distance;
		    
                    *tact = euclidean_distance;
                    ++tact;
                    
                    // Anything obtained with PyObject_GetAttrString must be explicitly freed
                    Py_DECREF(weights_obj);
                    Py_DECREF(slice_obj);
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
provide_unoptimized_equivalent("CFPRF_EuclideanDistance_opt","CFPRF_EuclideanDistance",locals())
