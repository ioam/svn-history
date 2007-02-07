"""
Basic learning functions for CFProjections.

$Id$
"""
__version__ = "$Revision$"


from math import ceil

from Numeric import exp, argmax

from topo.base.arrayutils import L2norm, array_argmax
from topo.base.boundingregion import BoundingBox
from topo.base.cf import CFPLearningFn
from topo.base.parameterclasses import Number
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.patterngenerator import PatternGeneratorParameter
    
from topo.patterns.basic import Gaussian
from topo.outputfns.basic import IdentityOF


class CFPLF_SOM(CFPLearningFn):
    """An abstract base class of learning functions for Self-Organizing Maps."""
    _abstract_class_name = "CFPLF_SOM"

    learning_radius = Number(default=0.0,doc=
        """
        The radius of the neighborhood function to be used for
        learning.  Typically, this value will be set by the Sheet or
        Projection owning this CFPLearningFn, but it can also be set
        explicitly by the user.
        """)
    
    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):
        raise NotImplementedError



class CFPLF_HebbianSOM(CFPLF_SOM):
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
    
    crop_radius_multiplier = Number(default=3.0,doc=
        """
        Factor by which the radius should be multiplied,
        when deciding how far from the winner to keep updating the weights.
        """)
    
    neighborhood_kernel_generator = PatternGeneratorParameter(
        default=Gaussian(x=0.0,y=0.0,aspect_ratio=1.0),
        doc="Neighborhood function")
    

    def __call__(self, cfs, input_activity, output_activity, learning_rate, **params):

        rows,cols = output_activity.shape

        # This learning function does not need to scale the learning
        # rate like some do, so it does not use constant_sum_connection_rate()
	single_connection_learning_rate = learning_rate

        ### JABALERT: The learning_radius is normally set by
        ### the learn() function of CFSOM, so it doesn't matter
        ### much that the value accepted here is in matrix and 
        ### not sheet coordinates.  It's confusing that anything
        ### would accept matrix coordinates, but the learning_fn
        ### doesn't have access to the sheet, so it can't easily
        ### convert from sheet coords.
        radius = self.learning_radius
        crop_radius = max(1.25,radius*self.crop_radius_multiplier)

        # find out the matrix coordinates of the winner
        #
	# NOTE: when there are multiple projections, it would be
        # slightly more efficient to calculate the winner coordinates
        # within the Sheet, e.g. by moving winner_coords() to CFSOM
        # and passing in the results here.  However, finding the
        # coordinates does not take much time, and requiring the
        # winner to be passed in would make it harder to mix and match
        # Projections and learning rules with different Sheets.
        wr,wc = array_argmax(output_activity)

        # Optimization: Calculate the bounding box around the winner
        # in which weights will be changed, to avoid considering those
        # units below.
        cmin = int(max(0,wc-crop_radius))
        cmax = int(min(wc+crop_radius+1,cols)) # at least 1 between cmin and cmax
        rmin = int(max(0,wr-crop_radius))
        rmax = int(min(wr+crop_radius+1,rows))

        # generate the neighborhood kernel matrix so that the values
        # can be read off easily using matrix coordinates.
        nk_generator = self.neighborhood_kernel_generator
        radius_int = int(ceil(crop_radius))
        rbound = radius_int + 0.5
        bb = BoundingBox(points=((-rbound,-rbound), (rbound,rbound)))

        # Print parameters designed to match fm2d's output
        #print "%d rad= %d std= %f alpha= %f" % (topo.sim._time, radius_int, radius, single_connection_learning_rate)

        neighborhood_matrix = nk_generator(bounds=bb,xdensity=1,ydensity=1,
                                           size=2*radius)
        for r in range(rmin,rmax):
            for c in range(cmin,cmax):
                cwc = c - wc 
                rwr = r - wr 
                lattice_dist = L2norm((cwc,rwr))
		if lattice_dist <= crop_radius:
                    cf = cfs[r][c]
                    rate = single_connection_learning_rate * neighborhood_matrix[rwr+radius_int,cwc+radius_int]
		    X = cf.get_input_matrix(input_activity)

                    # CEBALERT:
                    # This is for pickling - the savespace for cf.weights does
                    # not appear to be pickled.
                    cf.weights.savespace(1)
                    cf.weights += rate * (X - cf.weights)

                    # CEBHACKALERT: see ConnectionField.__init__()
                    cf.weights *= cf.mask

