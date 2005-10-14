"""
The module defines KernelProjection, a subclass of CFProjection
that defines projections of connection fields where each
ConnectionField's initial weight matrix is created by calling a
PatternGenerator.

$Id$
"""

### JABHACKALERT!
###
### Should eliminate import *.
from topo.base.connectionfield import CFProjection
from topo.base.parameter import Parameter
from topo.patterns.random import UniformRandomGenerator
from topo.base.boundingregion import Intersection,BoundingBox
from topo.base.learningrules import *
from topo.base.utils import *
from topo.base.projection import Identity

class KernelProjection(CFProjection):
    """
    Projection that is based on an array of weight patterns generated
    by a PatternGenerator.  The activity of the Projection is
    calculated by a specified activation_fn and output_fn (which is
    typically Identity).    
    """
    weights_bounds = Parameter(default=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
    weights_generator = Parameter(default=UniformRandomGenerator())
    learning_rate = Parameter(default=0.0)

    # Should be changed to a OutputFunctionParameter
    output_fn  = Parameter(default=Identity())

    def __init__(self,**params):
        super(KernelProjection,self).__init__(**params)
        
        # set up array of ConnectionFields translated to each x,y in the src sheet
        cfs = []
        for y in self.dest.sheet_rows()[::-1]:
            row = []
            for x in self.dest.sheet_cols():
                row.append(self.cf_type(input_sheet=self.src,weight_bounds=self.weights_bounds,weights_generator=self.weights_generator,weight_type=self.weight_type,normalize=self.normalize,normalize_fn=self.normalize_fn,x=x,y=y))

            cfs.append(row)
        self.set_cfs(cfs)


    ### JABHACKALERT!
    ### 
    ### Instead of having this special case, need to make all activity 
    ### functions be array-based like compute_response_mdot_c, but with
    ### one simple and slow version provided that accepts a scalar
    ### activity function (for generality).
    def activate(self,input_activity, rows, cols):
        """
        Activate using the specified activation_fn followed by the specified output_fn.
        """
        self.input_buffer = input_activity
        if self.activation_fn.func_name == "compute_response_mdot_c":
            # compute_response_mdot_c computes the mdot for all the units
            compute_response_mdot_c(input_activity, rows, cols, self.activity, self.cfs, self.strength)
	else:
            for r in xrange(rows):
                for c in xrange(cols):
                    cf = self.cfs[r][c]
                    r1,r2,c1,c2 = cf.slice
                    X = input_activity[r1:r2,c1:c2]

                    self.activity[r,c] = self.activation_fn(X,cf.weights)
            self.activity *= self.strength
        self.activity = self.output_fn(self.activity)


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


