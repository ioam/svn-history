"""
Learning functions written with C code to optimize performance. Needs the
package weave to run.

$Id$
"""
__version__ = "$Revision$"

from topo.misc.inlinec import inline, optimized
from topo.base.topoobject import TopoObject
from topo.base.parameter import Parameter,Constant,Number
from topo.base.projection import Identity
from topo.base.connectionfield import CFLearningFunction
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
    output_fn = Parameter(default=Identity())
    
    def __init__(self,**params):
        super(Hebbian,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
	### JCALERT! Maybe change the name to single_connection_learning_rate 
	### and change the variable name in the C code. (same in DivisiveHebbian)
	learning_rate = self.set_learning_rate(cfs,learning_rate,rows,cols)
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
                        load *= learning_rate;
    
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
        
        inline(hebbian_code, ['input_activity', 'output_activity', 'rows', 'cols', 'len', 'cfs', 'learning_rate'],local_dict=locals())

        # Apply output_fn to each CF, followed by mask
        # (output_fn skipped for no-op case, as an optimization) 
        output_fn = self.output_fn
        # CEBHACKALERT: can this be done in the c?
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                if type(output_fn) is not Identity:
                    cf.weights = output_fn(cf.weights)
                cf.weights *= cf.mask


class Hebbian_Py(GenericCFLF):
    """
    CF-aware Hebbian learning rule.

    Equivalent to GenericCFLF(single_cf_fn=hebbian)
    Wrapper written to allow transparent non-optimized fallback.
    """
    def __init__(self,**params):
        super(Hebbian_Py,self).__init__(single_cf_fn=hebbian,**params)
        
# Optimized version is overwritten by the unoptimized version if the
# code does not have optimized set.
if not optimized:
    Hebbian = Hebbian_Py
    TopoObject().message('Inline-optimized components not available; using Hebbian_Py instead of Hebbian.')


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
    output_fn = Constant(DivisiveSumNormalize())

    def __init__(self,**params):
        super(DivisiveHebbian,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        rows,cols = output_activity.shape
	learning_rate = self.set_learning_rate(cfs,learning_rate,rows,cols)
        len, len2 = input_activity.shape

        hebbian_div_norm_code = """
            float *wi, *wj, *m, *wk;
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
                        load *= learning_rate;

                        cf = PyList_GetItem(cfsr,l);
                        wi = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,weights))->data);
                        wj = wi;
                        wk = wi;
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

                        // apply the mask
                        m = (float *)(((PyArrayObject*)PyObject_GetAttr(cf,mask))->data);
                        for (i=rr1; i<rr2; ++i) {
                            for (j=cc1; j<cc2; ++j) {
                               *wk *= *m;
                               ++wk;
                               ++m;
                               }
                        }

                        // normalize the weights
                        totald += 1.0;
                        totald = 1.0/totald;
                        rc = (rr2-rr1)*(cc2-cc1);

                        for (i=0; i<rc; ++i) {
                            *wj *= totald;
                            ++wj;
                        }
                    }
                }
            }
        """
        
        inline(hebbian_div_norm_code, ['input_activity', 'output_activity','rows', 'cols', 'len', 'cfs', 'learning_rate'], local_dict=locals())
       


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
    TopoObject().message('Inline-optimized components not available; using DivisiveHebbian_Py instead of DivisiveHebbian.')




class DivisiveHebbian_CPointer(CFLearningFunction):
    """
    CF-aware Hebbian learning rule with built-in divisive normalization.

    Same as DivisiveHebbian except it takes 2 extra arguments, weights_ptrs
    and slice_ptrs, in __call__. These 2 argument store the pointers to the
    weight and slice_array, respectively, of each ConnectionField in
    CFProjection_CPointer. This class should only be used by a sheet that
    only has CFProjection_CPointers connected to it. 
    """
    output_fn = Constant(DivisiveSumNormalize())

    def __init__(self,**params):
        super(DivisiveHebbian_CPointer,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        weight_ptrs = params['weight_ptrs']
        slice_ptrs = params['slice_ptrs']
        rows,cols = output_activity.shape
	single_cf_learning_rate = self.set_learning_rate(cfs,learning_rate,rows,cols)
        len, len2 = input_activity.shape

        hebbian_div_norm_code = """
            float *wi, *wj;
            double *x, *inpi, *inpj;
            int *slice;
            int rr1, rr2, cc1, cc2;
            int i, j, r, l;
            double load, delta;
            double totald;
            float **wip = (float **)weight_ptrs;
            int **sip = (int **)slice_ptrs;
    
            x = output_activity;
            for (r=0; r<rows; ++r) {
                for (l=0; l<cols; ++l) {
                    load = *x++;
                    if (load != 0) {
                        load *= learning_rate;
    
                        wi = *wip;
                        wj = wi;

                        slice = *sip;
                        rr1 = *slice++;
                        rr2 = *slice++;
                        cc1 = *slice++;
                        cc2 = *slice;
    
                        totald = 0.0;
    
                        inpj = input_activity+len*rr1+cc1;

                        const int rr1c = rr1;
                        const int rr2c = rr2;
                        const int cc1c = cc1;
                        const int cc2c = cc2;

                        for (i=rr1c; i<rr2c; ++i) {
                            inpi = inpj;
                            for (j=cc1c; j<cc2c; ++j) {
                                delta = load * *inpi;
                                *wi += delta;
                                totald += delta;
                                ++wi;
                                ++inpi;
                            }
                            inpj += len;
                        }
    
                        // normalize the weights
                        totald += 1.0; 
                        totald = 1.0/totald;
                        const int rc = (rr2-rr1)*(cc2-cc1);
    
                        for (i=0; i<rc; ++i) {
                            *wj *= totald;
                            ++wj;
                        }
                    }
                    ++wip;
                    ++sip;
                }
            }
        """
        
        inline(hebbian_div_norm_code, ['input_activity', 'output_activity', 'rows', 'cols', 'len', 'learning_rate','weight_ptrs','slice_ptrs'], local_dict=locals())

        # CEBHACKALERT: can this be done in the c?
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                cf.weights *= cf.mask


if not optimized:
    DivisiveHebbian_CPointer = DivisiveHebbian_Py
    TopoObject().message('Inline-optimized components not available; using DivisiveHebbian_Py instead of DivisiveHebbian_CPointer.')
    

