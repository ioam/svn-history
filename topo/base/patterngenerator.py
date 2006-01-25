"""
PatternGenerator abstract class and sample Constant(PatternGenerator)
concrete class.

$Id$
"""


__version__='$Revision$'

from topoobject import TopoObject
from boundingregion import BoundingBox
from sheet import  matrixidx2sheet, bounds2slice
from Numeric import add,subtract,cos,sin,array
from parameter import Parameter,Number,ClassSelectorParameter
from math import pi


# CEBHACKALERT: doesn't work as you might expect for
# boundingregions. This code assumes the underlying pattern is
# centered at (0,0) in Sheet coordinates. Supplying bounds that are
# not centered results in a sample of the (0,0)-centered pattern in
# this off-center region, rather than having the pattern centered in
# the supplied region. Shouldn't the pattern be created in such a way
# that it's always centered in the supplied boundingregion?

 
class PatternGenerator(TopoObject):
    # CEBHACKALERT: update this documentation when finished reorganizing parametersframe.py
    """
    A class hierarchy for callable objects that can generate 2D patterns.

    Once initialized, PatternGenerators can be called to generate a
    value or a matrix of values from a 2D function, typically
    accepting at least x and y.
    
    A PatternGenerator's Parameters can make use of Parameter's
    precedence attribute to specify the order in which they should
    appear e.g. on a GUI. The precedence attribute is based on the
    range 0.0 to 1.0, with ordering going from 0.0 (first) to 1.0
    (last).

    The orientation of the pattern matrices have the same orientation
    maintained by the Sheet classes; see sheet.py for more details of
    the Topographica coordinate system.
    """

    bounds  = Parameter(default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))),hidden=True)
    density = Parameter(default=10,hidden=True)

    x       = Number(default=0.0,softbounds=(-1.0,1.0),precedence=0.20,
                     doc="x-coordinate location of pattern center")
    y       = Number(default=0.0,softbounds=(-1.0,1.0),precedence=0.21,
                     doc="y-coordinate location of pattern center")
    orientation = Number(default=0,softbounds=(0.0,2*pi),precedence=0.40,
                         doc="Polar angle of pattern, i.e. the orientation in Cartesian coordinate\nsystem, with zero at 3 o'clock and increasing counterclockwise")
    scale = Number(default=1.0,softbounds=(0.0,2.0),precedence=0.10,
                   doc="Multiplicative strength of input pattern, defaulting to 1.0")
    offset = Number(default=0.0,softbounds=(-1.0,1.0),precedence=0.11,
                    doc="Additive offset to input pattern, defaulting to 0.0")


    def __call__(self,**params):
        """
        # CEBHACKALERT: I still have documentation to write, including explaining
        params.get().

        Sometimes the slice is already known before PatternGenerator
	is called, so we can just provide this information without
	having the slice recomputed from the bounds.
        """
        self.verbose("params = ",params)
        self.__setup_xy(params.get('bounds',self.bounds),
                        params.get('density',self.density),
                        params.get('x', self.x),
                        params.get('y',self.y),
                        params.get('orientation',self.orientation),
                        params.get('slice_array',None))
        return self.scale*self.function(**params)+self.offset

    def __setup_xy(self,bounds,density,x,y,orientation,slice_array):
        """
        Produce the pattern matrices from the bounds and density (or
        rows and cols), and transform according to x, y, and
        orientation.
        """
        self.verbose("bounds = ",bounds,"density =",density,"x =",x,"y=",y)
        x_points,y_points = self.__produce_sampling_vectors(bounds,density,slice_array)
        self.pattern_x, self.pattern_y = self.__create_and_rotate_coordinates(x_points-x,y_points-y,orientation)

    def function(self,**params):
        """
        Subclasses will typically implement this function to draw a pattern.

        The pattern will then be scaled and rotated automatically by
        __call__.  Alternatively, this function may be omitted and
        __call__ reimplemented, e.g. if the automatic scaling and
        rotating is not appropriate.
        """
        raise NotImplementedError


    def __produce_sampling_vectors(self, bounds, density, slice_array):
        """
        Generate vectors representing coordinates at which the pattern will be sampled.

        x is a 1d-array of x-axis values at which to sample the pattern;
        y contains the y-axis values.
        """

        # CEBHACKALERT: only Sheet should have to know about xdensity etc.
        left,bottom,right,top = bounds.aarect().lbrt()
        xdensity = int(density*(right-left)) / float((right-left))
        ydensity = int(density*(top-bottom)) / float((top-bottom))

        # avoid calculating the slice if it's been done elsewhere        
        if slice_array==None:
            # a slice to get the matrix corresponding to the whole bounds
            r1,r2,c1,c2 = bounds2slice(bounds,bounds,xdensity,ydensity)
        else:
            r1,r2,c1,c2 = slice_array

        rows = array(range(r1,r2))
        cols = array(range(c1,c2))

        y = array([matrixidx2sheet(r,0,bounds,xdensity,ydensity) for r in rows])
        x = array([matrixidx2sheet(0,c,bounds,xdensity,ydensity) for c in cols])

        # x increases from left to right; y decreases from left to right.
        # For this function to make sense on its own, y should probably be
        # reversed, but y would then have to be reversed again in
        # __create_and_rotate_coordinates().
        y = y[:,1]
        x = x[:,0]

        return x, y


    def __create_and_rotate_coordinates(self, x, y, orientation):
        """
        Creates pattern matrices from x and y vectors, and rotates them to the specified orientation.
        """
        pattern_y = subtract.outer(cos(orientation)*y, sin(orientation)*x)
        pattern_x = add.outer(sin(orientation)*y, cos(orientation)*x)
        return pattern_x, pattern_y


# Trivial example of a PatternGenerator, provided for when a default is
# needed.  The other concrete PatternGenerator classes are stored in
# patterns/, to be imported as needed.
from Numeric import ones, Float

class Constant(PatternGenerator):
    """Constant pattern generator, i.e. a solid, uniform field of the same value."""

    # The standard x, y, and orientation variables are currently ignored,
    # so they aren't shown in auto-generated lists of parameters (e.g. in the GUI)
    x       = Number(hidden = True)
    y       = Number(hidden = True)
    orientation   = Number(hidden = True)

    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params):
        slice_array = params.get('slice_array',None)
        bounds = params.get('bounds',self.bounds)
        density = params.get('density',self.density)

        left,bottom,right,top = bounds.aarect().lbrt()
        xdensity = int(density*(right-left)) / float((right-left))
        ydensity = int(density*(top-bottom)) / float((top-bottom))

        # avoid calculating the slice if it's been done elsewhere        
        if slice_array==None:
            # a slice to get the matrix corresponding to the whole bounds
            r1,r2,c1,c2 = bounds2slice(bounds,bounds,xdensity,ydensity)
        else:
            r1,r2,c1,c2 = slice_array

        return self.scale*ones((r2-r1,c2-c1), Float)+self.offset


# CEBHACKALERT: don't need to pass through doc etc.
class PatternGeneratorParameter(ClassSelectorParameter):
    """
    """
    def __init__(self,default=Constant(),doc='',**params):
        """
        """
        super(PatternGeneratorParameter,self).__init__(PatternGenerator,default=default,doc=doc,**params)




