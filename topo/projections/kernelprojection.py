"""
The module defines KernelProjection, a subclass of Projection
that defines projections of connection fields where each
ConnectionField's initial weight matrix is created by calling a
PatternGenerator.

$Id$
"""

### JABHACKALERT!
###
### Should eliminate import *.
from topo.projection import Projection
from topo.parameter import Parameter
from topo.patterns.random import UniformRandomGenerator
from topo.boundingregion import Intersection,BoundingBox
from topo.learningrules import *
from topo.utils import *

class KernelProjection(Projection):
    """
    Projection that is based on an array of weight patterns
    generated by a PatternGenerator.
    """
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = Parameter(default=UniformRandomGenerator())
#    normalize = Parameter(default=0.0)
#    normalize_fn = Parameter(divisive_normalization)
    learning_rate = Parameter(default=0.0)

    def __init__(self,**params):
        super(KernelProjection,self).__init__(**params)
        
        # set up array of ConnectionFields translated to each x,y in the src sheet
        cfs = []
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                row.append(self.cf_type(input_sheet=self.src,weight_bounds=self.weights_bounds,weights_generator=self.weights_generator,x=x,y=y))

            cfs.append(row)
        self.set_cfs(cfs)

        # Normalize the weights of each connection field as specified
        if self.normalize:
            norm = self.normalize
            rows,cols = self.get_shape()
            for r in xrange(rows):
                for c in xrange(cols):
                    self.normalize_fn(self.cfs[r][c].weights, norm)


    ### JABHACKALERT!
    ### 
    ### Instead of having this special case, need to make all activity 
    ### functions be array-based like compute_response_mdot_c, but with
    ### one simple and slow version provided that accepts a scalar
    ### activity function (for generality).        
    def compute_response(self,input_activity, rows, cols):
        self.input_buffer = input_activity
        if self.activation_fn.func_name == "compute_response_mdot_c":
            # compute_response_mdot_c computes the mdot for all the units
            compute_response_mdot_c(input_activity, rows, cols, self.temp_activity, self.cfs, self.strength)
	else:
            for r in xrange(rows):
                for c in xrange(cols):
                    cf = self.cfs[r][c]
                    r1,r2,c1,c2 = cf.slice
                    X = input_activity[r1:r2,c1:c2]

                    self.temp_activity[r,c] = self.activation_fn(X,cf.weights)
            self.temp_activity *= self.strength


    def reduce_cfsize(self, new_wt_bounds):
        """
        Reduce the sizes of the connection fields contained in this object to
        new_wt_bounds.
        """
        if not self.weights_bounds.containsbb_exclusive(new_wt_bounds):
            self.warning('reduce_cfsize: new weight bounds should be strictly smaller than the original weight bounds')
            return

        self.weights_bounds = new_wt_bounds
        rows,cols = self.get_shape()
        cfs = self.cfs
	norm = self.normalize
        for r in xrange(rows):
            for c in xrange(cols):
                cfs[r][c].reduce_radius(new_wt_bounds)
                # Normalize the weights of each connection field as specified
                if norm:
                    self.normalize_fn(cfs[r][c].weights, norm)


