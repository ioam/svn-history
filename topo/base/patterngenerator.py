"""
PatternGenerator abstract class and sample Constant(PatternGenerator)
concrete class.

$Id$
"""


__version__='$Revision$'

from math import pi
from Numeric import add,subtract,cos,sin,array

from parameterizedobject import ParameterizedObject
from boundingregion import BoundingBox, BoundingRegionParameter
from sheet import CoordinateTransformer
from parameterclasses import Parameter,Number,ClassSelectorParameter
from functionfamilies import OutputFnParameter, IdentityOF


class PatternGenerator(ParameterizedObject):
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


    CEBHACKALERT: might want to say something like, users of PG
    might like to consider what xdensity and ydensity they want...
    #width=self.right-self.left; height=self.top-self.bottom
    #self.xdensity = int(density*(width))/float((width))
    #self.ydensity = int(density*(height))/float((height))
    # etc

    """

    # PatternGenerator is abstract
    _abstract_class_name = "PatternGenerator"
    
    bounds  = BoundingRegionParameter(
        default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))),hidden=True,
        doc = "BoundingBox of the area in which the pattern is generated.")
    
    xdensity = Number(
        default=10,bounds=(0,None),hidden=True,
        doc="Density (number of samples per 1.0 length) in the x direction.")

    ydensity = Number(
        default=10,bounds=(0,None),hidden=True,
        doc="Density (number of samples per 1.0 length) in the y direction.")

    x = Number(
        default=0.0,softbounds=(-1.0,1.0),precedence=0.20,
        doc="x-coordinate location of pattern center")

    y = Number(
        default=0.0,softbounds=(-1.0,1.0),precedence=0.21,
        doc="y-coordinate location of pattern center")

    orientation = Number(
        default=0,softbounds=(0.0,2*pi),precedence=0.40,
        doc="""
        Polar angle of pattern, i.e. the orientation in Cartesian coordinate
        system, with zero at 3 o'clock and increasing counterclockwise.""")
    
    scale = Number(
        default=1.0,softbounds=(0.0,2.0),precedence=0.10,
        doc="Multiplicative strength of input pattern, defaulting to 1.0")
    
    offset = Number(
        default=0.0,softbounds=(-1.0,1.0),precedence=0.11,
        doc="Additive offset to input pattern, defaulting to 0.0")
    
    output_fn = OutputFnParameter(
        default=IdentityOF(),
        precedence=0.08,
        doc='Function applied to the pattern array after it has been created.')


    def __call__(self,**params):
        """
        Create the pattern array.
        
        If called without any params, uses the values for the Parameters as
        currently set on the object. Otherwise, any params specified override
        those currently set on the object.
        """
        # CEBHACKALERT: put in a method and add to the other __call__ methods.
        for item in params:
            if item not in self.params():
                self.warning("'%s' was ignored (not a Parameter)."%item)
                
        self.verbose("params = ",params)
        self.__setup_xy(params.get('bounds',self.bounds),
                        params.get('xdensity',self.xdensity),
                        params.get('ydensity',self.ydensity),                        
                        params.get('x',self.x),
                        params.get('y',self.y),
                        params.get('orientation',self.orientation))

        scale = params.get('scale',self.scale)
        offset = params.get('offset',self.offset)
        output_fn = params.get('output_fn',self.output_fn)

        if output_fn is IdentityOF:
            return scale*self.function(**params)+offset
        else:
            return output_fn(scale*self.function(**params)+offset)


    def __setup_xy(self,bounds,xdensity,ydensity,x,y,orientation):
        """
        Produce the pattern matrices from the bounds and density (or
        rows and cols), and transform according to x, y, and
        orientation.
        """
        self.verbose("bounds = ",bounds,"xdensity =",xdensity,"x =",x,"y=",y)
        x_points,y_points = self.__produce_sampling_vectors(bounds,xdensity,ydensity)
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


    def __produce_sampling_vectors(self, bounds, xdensity, ydensity):
        """
        Generate vectors representing coordinates at which the pattern
        will be sampled.

        Returns two vectors x and y, where x is a 1d-array of x-axis
        values at which to sample the pattern and y contains the y-axis
        values.
        """
        # CEBHACKALERT: this will become a method of the Slice object.
        pattern_sheet = CoordinateTransformer(bounds,xdensity,ydensity)
        n_rows,n_cols = pattern_sheet.shape

        rows = array(range(n_rows)); cols = array(range(n_cols))


        # returns x,y; x increases from left to right; y decreases
        # from left to right (because the row index increases as y
        # decreases).
        #
        # For this function to make sense on its own, y should probably be
        # reversed, but y would then have to be reversed again in
        # __create_and_rotate_coordinates().
        return pattern_sheet.matrixidx2sheet_array(rows,cols)

        
    def __create_and_rotate_coordinates(self, x, y, orientation):
        """
        Create pattern matrices from x and y vectors, and rotate
        them to the specified orientation.
        """
        # Using this two-liner requires that x increase from left to
        # right and y decrease from left to right; I don't think it
        # can be rewritten in so little code otherwise - but please
        # prove me wrong.
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
        bounds = params.get('bounds',self.bounds)
        xdensity = params.get('xdensity',self.xdensity)
        ydensity = params.get('ydensity',self.ydensity)
        scale = params.get('scale',self.scale)
        offset = params.get('offset',self.offset)
        output_fn = params.get('output_fn',self.output_fn)

        shape = CoordinateTransformer(bounds,xdensity,ydensity).shape

        if output_fn is IdentityOF:
            return scale*ones(shape, Float)+offset
        else:
            return output_fn(scale*ones(shape, Float)+offset)



class PatternGeneratorParameter(ClassSelectorParameter):
    """
    """
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    packages = []

    def __init__(self,default=Constant(),**params):
        """
        """
        super(PatternGeneratorParameter,self).__init__(PatternGenerator,default=default,suffix_to_lose='Generator',**params)




