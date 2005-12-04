"""
Basic learning functions for CFProjections.

$Id$
"""
__version__ = "$Revision$"

from topo.base.inlinec import inline
from topo.base.topoobject import TopoObject
from topo.base.parameter import Parameter,Constant,Number
from topo.base.projection import Identity
from topo.base.connectionfield import CFLearningFunction
from topo.outputfns.basic import DivisiveSumNormalize
from topo.base.arrayutils import L2norm
from Numeric import exp, argmax
from topo.base.patternfns import gaussian


# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import IdentityCFLF,GenericCFLF


### JABALERT!  Untested.
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

        # Apply output_fn to each CF
        # (skipped entirely for no-op case, as an optimization)
        output_fn = self.output_fn
        if type(output_fn) is not Identity:
            for r in range(rows):
                for c in range(cols):
                    cfs[r][c].weights = output_fn(cfs[r][c].weights)


### JABALERT!  Untested.
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
        len, len2 = input_activity.shape

        hebbian_div_norm_code = """
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




### JABALERT!  Untested.
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



class HebbianSOM(CFLearningFunction):
    """
    CF-aware Hebbian learning rule in Self-Organizing Maps. Only the winner
    unit its surrounds will learn. The radius of the 
    surround is specified by the named parameter radius in __call_.
    """
    output_fn = Parameter(default=Identity())
    learning_radius = Number(default=0.0)
    
    def __init__(self,**params):
        super(HebbianSOM,self).__init__(**params)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):

        rows,cols = output_activity.shape
        radius = self.learning_radius
        output_fn = self.output_fn

        # find out the matrix coordinates of the winner
	# NOTE: the coordinates could be calculated more efficiently within the 
        # Sheet, e.g. by CFSOM.winnder_coords(), and pass them in, but
	# that doesn't save much time and makes it harder to mix and match
	# Projections and learning rules.
        wr,wc = self.winner_coords(output_activity,cols)

        # find out the bounding box around the winner in which weights will
        # be changed. This is just to make the code run faster.
        cmin = int(max(0,wc-radius))
        cmax = int(min(wc+radius+1,cols)) # at least 1 between cmin and cmax
        rmin = int(max(0,wr-radius))
        rmax = int(min(wr+radius+1,rows))

        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                lattice_dist = L2norm((wc-c,wr-r))
		if lattice_dist <= radius:
                    cf = cfs[r][c]
                    #rate = learning_rate * exp(-lattice_dist/radius)
                    rate = learning_rate * gaussian(lattice_dist,lattice_dist,radius,radius)
		    X = cf.get_input_matrix(input_activity)

                    # CEBHACKALERT:
                    # This is for pickling - the savespace for cf.weights does
                    # not appear to be pickled.
                    cf.weights.savespace(1)
                    cf.weights += rate * (X - cf.weights)
                    if type(output_fn) is not Identity:
                        cf.weights=self.output_fn(cf.weights)


    def winner_coords(self, activity, cols):
        pos = argmax(activity.flat)
        r = pos/cols
        c = pos%cols
        return r,c
