"""
Basic learning functions for CFProjections.

$Id$
"""
__version__ = "$Revision$"

from topo.base.topoobject import TopoObject
from topo.base.parameter import Parameter,Number
from topo.base.projection import Identity
from topo.base.connectionfield import CFLearningFunction
from topo.base.arrayutils import L2norm
from Numeric import exp, argmax
from topo.base.boundingregion import BoundingBox
import topo.patterns.basic
from math import ceil


# Imported here so that all CFLearningFunctions will be in the same package
from topo.base.connectionfield import IdentityCFLF,GenericCFLF


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
    neighborhood_kernel_generator = Parameter(default=topo.patterns.basic.Gaussian())
    
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):

        rows,cols = output_activity.shape
	single_connection_learning_rate = self.single_connection_learning_rate(cfs,learning_rate,rows,cols)
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
        # CEBHACKALERT: specifying aspect_ratio and size here won't work
        # for all patterns.
        # CEBHACKALERT: warnings should be printed if a non-parameter attribute
        # is set this way (e.g. try adding height=4).
        neighborhood_matrix = nk_generator(bounds=bb,density=1,aspect_ratio=1.0,size=radius)
        output_fn = self.output_fn
        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                cwc = c - wc 
                rwr = r - wr 
                lattice_dist = L2norm((cwc,rwr))
		if lattice_dist <= radius:
                    cf = cfs[r][c]
                    rate = single_connection_learning_rate * neighborhood_matrix[rwr+radius_int,cwc+radius_int]
		    X = cf.get_input_matrix(input_activity)

                    # CEBHACKALERT:
                    # This is for pickling - the savespace for cf.weights does
                    # not appear to be pickled.
                    cf.weights.savespace(1)
                    cf.weights += rate * (X - cf.weights)

                    # CEBHACKALERT: see ConnectionField.__init__()
                    cf.weights *= cf.mask
                    if type(output_fn) is not Identity:
                        output_fn(cf.weights)



    def winner_coords(self, activity, cols):
        pos = argmax(activity.flat)
        r = pos/cols
        c = pos%cols
        return r,c

