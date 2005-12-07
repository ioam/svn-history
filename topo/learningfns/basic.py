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
from topo.base.boundingregion import BoundingBox
from topo.patterns.basic import GaussianGenerator
from math import ceil


# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import IdentityCFLF,GenericCFLF

### JABHACKALERT! Most of these need move to a new file optimized.py,
### because they use weave.


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



class SOMLF(CFLearningFunction):
    """
    An abstract base class of learning functions for Self-Organizing Maps.
    
    These objects have a parameter learning_radius that is expected to
    be kept up to date, either by the Sheet to which they are
    connected or explicitly by the user.  The learning_radius
    specifies the radius of the neighborhood function used during
    learning.
    """
    learning_radius = Number(default=0.0)

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        raise NotImplementedError



class HebbianSOMLF(SOMLF):
    """
    Hebbian learning rule for CFProjections to Self-Organizing Maps.

    Only the winner unit and those surrounding it will learn. The
    radius of the surround is specified by the parameter
    learning_radius, which should be set before using __call__.  The
    shape of the surround is determined by the neighborhood_kernel_generator, 
    and can be any PatternGenerator instance, or any function accepting
    bounds, density, radius, and height to return a kernel matrix.
    """

    learning_radius = Number(default=0.0)
    output_fn = Parameter(default=Identity())
    # JABALERT: Should be a PatternGeneratorParameter eventually
    neighborhood_kernel_generator = Parameter(default=GaussianGenerator())
    
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):

        rows,cols = output_activity.shape
        radius = self.learning_radius
        output_fn = self.output_fn

        # find out the matrix coordinates of the winner
        #
	# NOTE: when there are multiple projections, it would be
        # slightly more efficient to calculate the winner coordinates
        # within the Sheet, e.g. by moving winner_coords() to CFSOM
        # and passing in the results here.  However, finding the
        # coordinates does not take much time, and requiring the
        # winner to be passed in would make it harder to mix and match
        # Projections and learning rules with different Sheets.
        wr,wc = self.winner_coords(output_activity,cols)

        ### JABHACKALERT!  Is updating only within this radius really
        ### valid?  E.g. a Gaussian is still quite strong one sigma
        ### away from the center; it's probably not near zero until at
        ### least two or three radii away.  But maybe that's what is
        ### usually done for a SOM, and it works ok?  In any case, it
        ### might be better to let the user decide which bounds to use.
        
        # find out the bounding box around the winner in which weights will
        # be changed. This is just to make the code run faster.
        cmin = int(max(0,wc-radius))
        cmax = int(min(wc+radius+1,cols)) # at least 1 between cmin and cmax
        rmin = int(max(0,wr-radius))
        rmax = int(min(wr+radius+1,rows))

        # generate the neighborhood kernel matrix so that the values
        # can be read off easily using matrix coordinates.
        nk_generator = self.neighborhood_kernel_generator
        radius_int = int(ceil(radius))
        rbound = radius_int + 0.5
        bb = BoundingBox(points=((-rbound,-rbound), (rbound,rbound)))
        neighborhood_matrix = nk_generator(bounds=bb,density=1,width=radius,height=radius)

        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                cwc = c - wc 
                rwr = r - wr 
                lattice_dist = L2norm((cwc,rwr))
		if lattice_dist <= radius:
                    cf = cfs[r][c]
                    rate = learning_rate * neighborhood_matrix[rwr+radius_int,cwc+radius_int]
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

