"""
PatternGenerator abstract class and basic example concrete class.

$Id$
"""
__version__='$Revision$'


from math import pi

from numpy.oldnumeric import add,subtract,cos,sin

from boundingregion import BoundingBox, BoundingRegionParameter
from functionfamilies import OutputFnParameter, IdentityOF
from parameterclasses import Parameter,Number,ClassSelectorParameter,CompositeParameter
from parameterizedobject import ParameterizedObject,ParamOverrides
from sheetcoords import SheetCoordinateSystem


# CEBALERT: PatternGenerator has become a bit of a monster abstract
# class.  Can it be split into the minimum required to specify the
# interface, with a subclass implementing the rest (this subclass
# still being above the rest of the PatternGenerators)?  We want to
# make it easy to add new types of PatternGenerator that don't match
# the assumptions of the current ones (OneDPowerSpectrum is an example
# of a PG that doesn't match the current assumptions), but still lets
# them be used like the current ones.
# (PatternGenerator-->TwoDPatternGenerator?)
class PatternGenerator(ParameterizedObject):
    """
    A class hierarchy for callable objects that can generate 2D patterns.

    Once initialized, PatternGenerators can be called to generate a
    value or a matrix of values from a 2D function, typically
    accepting at least x and y.
    
    A PatternGenerator's Parameters can make use of Parameter's
    precedence attribute to specify the order in which they should
    appear, e.g. in a GUI. The precedence attribute has a nominal
    range of 0.0 to 1.0, with ordering going from 0.0 (first) to 1.0
    (last), but any value is allowed.

    The orientation and layout of the pattern matrices is defined by
    the SheetCoordinateSystem class, which see.

    Note that not every parameter defined for a PatternGenerator will
    be used by every subclass.  For instance, a Constant pattern will
    ignore the x, y, orientation, and size parameters, because the
    pattern does not vary with any of those parameters.  However,
    those parameters are still defined for all PatternGenerators, even
    Constant patterns, to allow PatternGenerators to be scaled, rotated,
    translated, etc. uniformly.
    """
    __abstract = True
    
    bounds  = BoundingRegionParameter(
        default=BoundingBox(points=((-0.5,-0.5), (0.5,0.5))),precedence=-1,
        doc="BoundingBox of the area in which the pattern is generated.")
    
    xdensity = Number(default=10,bounds=(0,None),precedence=-1,doc="""
        Density (number of samples per 1.0 length) in the x direction.""")

    ydensity = Number(default=10,bounds=(0,None),precedence=-1,doc="""
        Density (number of samples per 1.0 length) in the y direction.
        Typically the same as the xdensity.""")

    x = Number(default=0.0,softbounds=(-1.0,1.0),precedence=0.20,doc="""
        X-coordinate location of pattern center.""")

    y = Number(default=0.0,softbounds=(-1.0,1.0),precedence=0.21,doc="""
        Y-coordinate location of pattern center.""")


    position = CompositeParameter(attribs=['x','y'],precedence=-1,doc="""
        Coordinates of location of pattern center.
        Provides a convenient way to set the x and y parameters together
        as a tuple (x,y), but shares the same actual storage as x and y
        (and thus only position OR x and y need to be specified).""")
    
    orientation = Number(default=0.0,softbounds=(0.0,2*pi),precedence=0.40,doc="""
        Polar angle of pattern, i.e., the orientation in the Cartesian coordinate
        system, with zero at 3 o'clock and increasing counterclockwise.""")
    
    size = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.30,doc="""Determines the overall size of the pattern.""")

    scale = Number(default=1.0,softbounds=(0.0,2.0),precedence=0.10,doc="""
        Multiplicative strength of input pattern, defaulting to 1.0""")
    
    offset = Number(default=0.0,softbounds=(-1.0,1.0),precedence=0.11,doc="""
        Additive offset to input pattern, defaulting to 0.0""")

    mask = Parameter(default=None,precedence=0.06,doc="""
        Optional object (expected to be an array) with which to multiply the
        pattern array after it has been created, before any output_fn is
        applied. This can be used to shape the pattern.""")
    
    output_fn = OutputFnParameter(default=IdentityOF(),precedence=0.08,doc="""
        Optional function to apply to the pattern array after it has been created.
        This function can be used for normalization, thresholding, etc.""")

    def __call__(self,**params_to_override):
        """
        Call the subclasses 'function' method on a rotated and scaled coordinate system.

        Creates and fills an array with the requested pattern.  If
        called without any params, uses the values for the Parameters
        as currently set on the object. Otherwise, any params
        specified override those currently set on the object.
        """
        self._check_params(params_to_override)                
        self.debug("params = ",params_to_override)
        params = ParamOverrides(self,params_to_override)

        bounds=params['bounds']
        xdensity=params['xdensity']
        ydensity=params['ydensity']
        x=params['x']
        y=params['y']
        orientation=params['orientation']
        position=params_to_override.get('position',None)

        if position is not None:
            x,y = position

        self.__setup_xy(bounds,xdensity,ydensity,x,y,orientation)
            
        result = params['scale']*self.function(params)+params['offset']

        mask = params['mask']
        if mask is not None:
            result*=mask

        output_fn = params['output_fn']
        if output_fn is not IdentityOF: # Optimization (but may not actually help)
            output_fn(result)           # CEBHACKALERT: particularly since everything but
                                        # the IdentityOF *class* will pass this if-test!
        return result                   # Should be: "if not instance(output_fn,IdentityOF):".
                                        # I guess this needs fixing in several places.

    def __setup_xy(self,bounds,xdensity,ydensity,x,y,orientation):
        """
        Produce pattern coordinate matrices from the bounds and
        density (or rows and cols), and transforms them according to
        x, y, and orientation.
        """
        self.debug("bounds = ",bounds,"xdensity =",xdensity,"x =",x,"y=",y)
        # Generate vectors representing coordinates at which the pattern
        # will be sampled.

        x_points,y_points = SheetCoordinateSystem(bounds,xdensity,ydensity).sheetcoordinates_of_matrixidx()
            
        # Generate matrices of x and y sheet coordinates at which to
        # sample pattern, at the correct orientation
        self.pattern_x, self.pattern_y = self.__create_and_rotate_coordinate_arrays(x_points-x,y_points-y,orientation)


    def function(self,params):
        """
        Function to draw a pattern that will then be scaled and rotated.

        Instead of implementing __call__ directly, PatternGenerator
        subclasses will typically implement this helper function used
        by __call__, because that way they can let __call__ handle the
        scaling and rotation for them.  Alternatively, __call__ itself
        can be reimplemented entirely by a subclass (e.g. if it does
        not need to do any scaling or rotation), in which case this
        function will be ignored.
        """
        raise NotImplementedError

        
    def __create_and_rotate_coordinate_arrays(self, x, y, orientation):
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
from numpy.oldnumeric import ones, Float

class Constant(PatternGenerator):
    """Constant pattern generator, i.e., a solid, uniform field of the same value."""

    # The standard position and orientation variables are ignored for this special case,
    # so we hide them from auto-generated lists of parameters (e.g. in the GUI)
    x = Number(precedence=-1)
    y = Number(precedence=-1)
    orientation   = Number(precedence=-1)
    size = Number(precedence=-1)
    

    # Optimization: We use a simpler __call__ method here to skip the
    # coordinate transformations (which would have no effect anyway)
    def __call__(self,**params_to_override):
        self._check_params(params_to_override)
        params = ParamOverrides(self,params_to_override)
        
        shape = SheetCoordinateSystem(params['bounds'],params['xdensity'],params['ydensity']).shape

        result = params['scale']*ones(shape, Float)+params['offset']

        mask = params['mask']
        if mask is not None:
            result*=mask

        output_fn = params['output_fn']
        if output_fn is not IdentityOF: # Optimization (but may not actually help)
            output_fn(result)

        return result


class PatternGeneratorParameter(ClassSelectorParameter):
    """Parameter whose value can be any instance of a PatternGenerator class."""
    
    __slots__ = []
    __doc__ = property((lambda self: self.doc))

    def __init__(self,default=Constant(),**params):
        super(PatternGeneratorParameter,self).__init__(PatternGenerator,default=default,suffix_to_lose='Generator',**params)
