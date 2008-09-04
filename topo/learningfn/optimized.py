"""
Learning functions (see basic.py) and projection-level learning
functions (see projfn.py) written in C to optimize performance.

Requires the weave package; without it unoptimized versions are used.

$Id$
"""
__version__ = "$Revision$"

from numpy import zeros

from .. import param

from topo.base.sheet import activity_type
from topo.base.cf import CFPLearningFn,CFPLF_Plugin,CFPLF_PluginScaled
from topo.base.functionfamily import Hebbian,LearningFn
from topo.misc.inlinec import inline, provide_unoptimized_equivalent

from projfn import CFPLF_Trace



class CFPLF_Hebbian_opt(CFPLearningFn):
    """
    CF-aware Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    CFPLF_Plugin(single_cf_fn=Hebbian), except faster.  

    As a side effect, sets the norm_total attribute on any cf whose
    weights are updated during learning, to speed up later operations
    that might depend on it.
    """
    single_cf_fn = param.ClassSelector(LearningFn,default=Hebbian(),readonly=True)
    
    def __call__(self, iterator, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
        cfs = iterator.proj._cfs
        single_connection_learning_rate = self.constant_sum_connection_rate(iterator.proj,learning_rate)
        if(single_connection_learning_rate==0): return
        irows,icols = input_activity.shape
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
                        PyObject *slice_obj   = PyObject_GetAttrString(cf,"input_sheet_slice");
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
                        double *inpj = input_activity+icols*rr1+cc1;
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
                            inpj += icols;
                        }

                        // Anything obtained with PyObject_GetAttrString must be explicitly freed
                        Py_DECREF(weights_obj);
                        Py_DECREF(slice_obj);
                        Py_DECREF(mask_obj);
                        
                        // store the sum of the cf's weights
                        PyObject *total_obj = PyFloat_FromDouble(total);  //(new ref)
                        PyObject_SetAttrString(cf,"_norm_total",total_obj);
                        PyObject_SetAttrString(cf,"_has_norm_total",Py_True);
                        Py_DECREF(total_obj);
                    }
                }
            }
        """

        inline(hebbian_code, ['input_activity', 'output_activity','rows', 'cols', 'icols', 'cfs', 'single_connection_learning_rate'], local_dict=locals())

class CFPLF_Scaled_opt(CFPLF_PluginScaled):
    """
    CF-aware Scaled Hebbian learning rule.

    Implemented in C for speed.  Should be equivalent to
    CFPLF_PluginScaled(single_cf_fn=Hebbian), except faster.  

    As a side effect, sets the norm_total attribute on any cf whose
    weights are updated during learning, to speed up later operations
    that might depend on it.
    """
    single_cf_fn = param.ClassSelector(LearningFn,default=Hebbian(),readonly=True)
    
    def __call__(self, iterator, input_activity, output_activity, learning_rate, **params):
        
        if self.learning_rate_scaling_factor is None:
            self.learning_rate_scaling_factor = ones(output_activity.shape)*1.0

        learning_rate_scaling_factor = self.learning_rate_scaling_factor

        rows,cols = output_activity.shape
        cfs = iterator.proj._cfs
        single_connection_learning_rate = self.constant_sum_connection_rate(iterator.proj,learning_rate)
        if(single_connection_learning_rate==0): return
        irows,icols = input_activity.shape
        hebbian_code = """
            double *x = output_activity;
            double *sclr = learning_rate_scaling_factor;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    double load = *x++;
                    double  a= *sclr++;
                    load = load * a;
                    if (load != 0) {
                        load *= single_connection_learning_rate;

                        PyObject *cf = PyList_GetItem(cfsr,l);
                        PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                        PyObject *slice_obj   = PyObject_GetAttrString(cf,"input_sheet_slice");
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
                        double *inpj = input_activity+icols*rr1+cc1;
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
                            inpj += icols;
                        }

                        // Anything obtained with PyObject_GetAttrString must be explicitly freed
                        Py_DECREF(weights_obj);
                        Py_DECREF(slice_obj);
                        Py_DECREF(mask_obj);
                        
                        // store the sum of the cf's weights
                        PyObject *total_obj = PyFloat_FromDouble(total);  //(new ref)
                        PyObject_SetAttrString(cf,"_norm_total",total_obj);
                        PyObject_SetAttrString(cf,"_has_norm_total",Py_True);
                        Py_DECREF(total_obj);
                    }
                }
            }
            
        """

        inline(hebbian_code, ['input_activity','learning_rate_scaling_factor', 'output_activity','rows', 'cols', 'icols', 'cfs', 'single_connection_learning_rate'], compiler='gcc',local_dict=locals())

class CFPLF_Hebbian(CFPLF_Plugin):
    """
    Wrapper written to allow transparent non-optimized fallback; 
    equivalent to CFPLF_Plugin(single_cf_fn=Hebbian()).
    """
    # CB: single_cf_fn should probably be declared here (as readonly)
    def __init__(self,**params):
        super(CFPLF_Hebbian,self).__init__(single_cf_fn=Hebbian(),**params)


provide_unoptimized_equivalent("CFPLF_Hebbian_opt","CFPLF_Hebbian",locals())




class CFPLF_Trace_opt(CFPLearningFn):
    """
    Optimized version of CFPLF_Trace; see projfn.py for more info 
    """

    trace_strength=param.Number(default=0.5,bounds=(0.0,1.0),doc="""
       How much the learning is dominated by the activity trace, relative to the current value.""")

    single_cf_fn = param.ClassSelector(LearningFn,default=Hebbian(),readonly=True,
        doc="LearningFn that will be applied to each CF individually.")              

    def __call__(self, iterator, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
        cfs = iterator.proj._cfs
        single_connection_learning_rate = self.constant_sum_connection_rate(iterator.proj,learning_rate)
        irows,icols = input_activity.shape
        if(single_connection_learning_rate==0): return
        ##Initialise traces to zero if they don't already exist
        if not hasattr(self,'traces'):
            self.traces=zeros(output_activity.shape,activity_type)
        
        self.traces = (self.trace_strength*output_activity)+((1-self.trace_strength)*self.traces)
        traces = self.traces
        
        trace_code = """
            double *x = traces;
            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    double load = *x++;
                    if (load != 0) {
                        load *= single_connection_learning_rate;

                        PyObject *cf = PyList_GetItem(cfsr,l);
                        PyObject *weights_obj = PyObject_GetAttrString(cf,"weights");
                        PyObject *slice_obj   = PyObject_GetAttrString(cf,"input_sheet_slice");
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
                        double *inpj = input_activity+icols*rr1+cc1;
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
                            inpj += icols;
                        }

                        // Anything obtained with PyObject_GetAttrString must be explicitly freed
                        Py_DECREF(weights_obj);
                        Py_DECREF(slice_obj);
                        Py_DECREF(mask_obj);
                        
                        // store the sum of the cf's weights
                        PyObject *total_obj = PyFloat_FromDouble(total);  //(new ref)
                        PyObject_SetAttrString(cf,"norm_total",total_obj);
                        PyObject_SetAttrString(cf,"_has_norm_total",Py_True);
                        Py_DECREF(total_obj);
                    }
                }
            }
        """

        inline(trace_code, ['input_activity', 'traces','rows', 'cols', 'icols', 'cfs', 'single_connection_learning_rate'], local_dict=locals())


provide_unoptimized_equivalent("CFPLF_Trace_opt","CFPLF_Trace",locals())
