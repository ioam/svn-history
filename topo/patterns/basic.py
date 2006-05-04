"""
Simple two-dimensional mathematical or geometrical pattern generators.

$Id$
"""
__version__='$Revision$'

from math import pi
from Numeric import around,bitwise_and,sin,add,Float

from topo.base.parameterclasses import Number, Parameter, Enumeration
from topo.base.functionfamilies import OutputFnParameter
from topo.base.patterngenerator import PatternGenerator
# Imported here so that all PatternGenerators will be in the same package
from topo.base.patterngenerator import Constant

from topo.misc.patternfns import gaussian,gabor,line,disk,ring
 

class Gaussian(PatternGenerator):
    """
    2D Gaussian pattern generator.

    The sigmas of the Gaussian are calculated from the size and
    aspect_ratio parameters:

      ysigma=size/2
      xsigma=ysigma*aspect_ratio

    The Gaussian is then computed for the given (x,y) values as:
    
      exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)
    """
    
    aspect_ratio   = Number(default=0.3,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of the width to the height.  Specifically, xsigma=ysigma*aspect_ratio (see size).")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Gaussian is defined by:\n  exp(-x^2/(2*xsigma^2) - y^2/(2*ysigma^2)\nwhere ysigma=size/2.")

    def function(self,**params):
        ysigma = params.get('size',self.size)/2.0
        xsigma = params.get('aspect_ratio',self.aspect_ratio)*ysigma

        return gaussian(self.pattern_x,self.pattern_y,xsigma,ysigma)


class SineGrating(PatternGenerator):
    """2D sine grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
                       precedence=0.50,
                       doc="Frequency of the sine grating.")
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=0.51,doc="phase of the sine grating")

    def function(self,**params):
        """
        Return a sine grating pattern (two-dimensional sine wave).
        """
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return 0.5 + 0.5*sin(frequency*2*pi*self.pattern_y + phase)        



class Gabor(PatternGenerator):
    """2D Gabor pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),
                       precedence=0.50,
                       doc="Frequency of the sine grating component.")
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),
                       precedence=0.51,
                       doc="Phase of the sine grating component.")
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of width to height; size*aspect_ratio gives the width of Gaussian component (see Gaussian)")
    size  = Number(default=0.25,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Determines the height of the Gaussian component (see Gaussian).")

    def function(self,**params):
        height = params.get('size',self.size)/2.0
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return gabor( self.pattern_x,
                      self.pattern_y,
                      width,
                      height,
                      params.get('frequency',self.frequency),
                      params.get('phase',self.phase))  


class Line(PatternGenerator):
    """2D line pattern generator."""

    # CEBHACKALERT:
    # Set smoothing to zero for the cfsom_example and you can
    # see a problem with lines. The problem is either in
    # the line() function, the generation of the matrices
    # used to draw it, or just in the display; I have to look to
    # see which.

    thickness   = Number(default=0.006,bounds=(0.0,None),softbounds=(0.0,1.0),
                         precedence=0.60,
                         doc="Thickness (width) of the solid central part of the line.")
    smoothing = Number(default=0.05,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off.")

    # CEBHACKALERT:
    # scale does not need to be here. For the tutorial, having this scale
    # allows users to see patchy responses to a line without needing to
    # adjust it themselves.
    scale = Number(default=0.7,softbounds=(0.0,2.0))
    
    def function(self,**params):
        return line(self.pattern_y, 
                    params.get('thickness',self.thickness),
                    params.get('smoothing',self.smoothing))


class Disk(PatternGenerator):
    """2D disk pattern generator."""

    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                           precedence=0.31,
                           doc="Ratio of width to height; size*aspect_ratio gives the width of the disk.")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Height of the disk")
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off")
    
    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        return disk( self.pattern_x, 
                     self.pattern_y, 
                     width,
                     height,
                     params.get('smoothing',self.smoothing))  


class Ring(PatternGenerator):
    """2D ring pattern generator."""

    thickness   = Number(default=0.015,bounds=(0.0,None),softbounds=(0.0,0.5),
                         precedence=0.60,
                         doc="Thickness (line width) of the ring.")
    smoothing = Number(default=0.1,bounds=(0.0,None),softbounds=(0.0,0.5),
                       precedence=0.61,
                       doc="Width of the Gaussian fall-off inside and outside the ring.")
    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                           precedence=0.31,
                           doc="Ratio of width to height; size*aspect_ratio gives the overall width.")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.30)

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return ring(self.pattern_x, 
                    self.pattern_y,
                    width,
                    height,
                    params.get('thickness',self.thickness),
                    params.get('smoothing',self.smoothing))  
    

class Rectangle(PatternGenerator):
    """2D rectangle pattern generator."""
    
    aspect_ratio   = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                            precedence=0.31,
                            doc="Ratio of width to height; size*aspect_ratio gives the width of the rectangle.")
    size  = Number(default=0.5,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Height of the rectangle.")

    # We will probably want to add Fuzzy-style anti-aliasing to this.

    def function(self,**params):
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height
        
        return bitwise_and(abs(self.pattern_x)<=width/2.0,
                           abs(self.pattern_y)<=height/2.0)


class SquareGrating(PatternGenerator):
    """2D squarewave grating pattern generator."""
    
    frequency = Number(default=2.4,bounds=(0.0,None),softbounds=(0.0,10.0),precedence=0.50,doc="Frequency of the square grating.")
    phase     = Number(default=0.0,bounds=(0.0,None),softbounds=(0.0,2*pi),precedence=0.51,doc="Phase of the square grating.")

    # We will probably want to add anti-aliasing to this,
    # and there might be an easier way to do it than by
    # cropping a sine grating.

    def function(self,**params):
        """
        Return a square-wave grating (alternating black and white bars).
        """
        frequency  = params.get('frequency',self.frequency)
        phase      = params.get('phase',self.phase)
        
        return around(0.5 + 0.5*sin(frequency*2*pi*self.pattern_y + phase))






# CEBHACKALERT: not sure where this class should go.  Maybe it could
# be generalized further and moved elsewhere.
# Also, will need updating when Sheet is cleaned up.
from Numeric import ones

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.base.boundingregion import BoundingBox
from topo.outputfns.basic import IdentityOF
class PatternSampler(ParameterizedObject):
    """
    Stores a Sheet whose activity represents the supplied pattern_array,
    and when called will resample that array at the supplied Sheet coordinates
    according to the supplied scaling parameters.

    (x,y) coordinates outside the pattern_array are returned as the
    background value.
    """

    def __init__(self, pattern_array, whole_pattern_output_fn=IdentityOF(), background_value_fn=None):
        """
        Create a Sheet whose activity is pattern_array (where pattern_array
        is a Numeric array) after application of whole_pattern_output_fn.

        If supplied, background_value_fn must accept an array and return a scalar.
        """
        super(PatternSampler,self).__init__()
        
        rows,cols=pattern_array.shape

        self.pattern_sheet = SheetCoordinateSystem(
            xdensity=1.0,
            ydensity=1.0,
            bounds=BoundingBox(points=((-cols/2.0,-rows/2.0),
                                       ( cols/2.0, rows/2.0))))
        
        self.pattern_sheet.activity = whole_pattern_output_fn(pattern_array)

        if not background_value_fn:
            self.background_value = 0.0
        else:
            self.background_value = background_value_fn(self.pattern_sheet.activity)
        

    def __call__(self, x, y, sheet_xdensity, sheet_ydensity, scaling, width=1.0, height=1.0):
        """
        Return pixels from the pattern at the given Sheet (x,y) coordinates.

        sheet_density should be the density of the sheet on which the pattern
        is to be drawn.

        scaling determines how the pattern is scaled initially; it can be:
          'stretch_to_fit'
        scale both dimensions of the pattern so they would fill a Sheet
        with bounds=BoundingBox(radius=0.5)
        (disregards the original's aspect ratio)

          'fit_shortest'
        scale the pattern so that its shortest dimension is made to fill
        the corresponding dimension on a Sheet with
        bounds=BoundingBox(radius=0.5)
        (maintains the original's aspect ratio)

          'fit_longest'
        scale the pattern so that its longest dimension is made to fill
        the corresponding dimension on a Sheet with
        bounds=BoundingBox(radius=0.5)
        (maintains the original's aspect ratio)

          'original'
        no scaling is applied; one pixel of the pattern is put in one
        unit of the sheet on which the pattern being displayed


        The pattern is further scaled according to the supplied width and height.
        """
        # create new pattern sample, filled initially with the background value
        pattern_sample = ones(x.shape, Float)*self.background_value

        # if the height or width is zero, there's no pattern to display...
        if width==0 or height==0:
            return pattern_sample

        # scale the supplied coordinates to match the pattern being at density=1
        x*=sheet_xdensity 
        y*=sheet_ydensity
      
        # scale according to initial pattern scaling selected (size_normalization)
        if not scaling=='original':
            self.__apply_size_normalization(x,y,sheet_xdensity,sheet_ydensity,scaling)

        # scale according to user-specified width and height
        x/=width
        y/=height

        # convert the sheet (x,y) coordinates to matrixidx (r,c) ones
        r,c = self.pattern_sheet.sheet2matrixidx_array(x,y)

        # now sample pattern at the (r,c) corresponding to the supplied (x,y)
        pattern_rows,pattern_cols = self.pattern_sheet.activity.shape
        if pattern_rows==0 or pattern_cols==0:
            return pattern_sample
        else:
            # CEBALERT: is there a more Numeric way to do this?
            rows,cols = pattern_sample.shape
            for i in xrange(rows):
                for j in xrange(cols):
                    # indexes outside the pattern are left with the background color
                    if self.pattern_sheet.true_bounds.contains_exclusive(x[i,j],y[i,j]):
                        pattern_sample[i,j] = self.pattern_sheet.activity[r[i,j],c[i,j]]

        return pattern_sample


    def __apply_size_normalization(self,x,y,sheet_xdensity,sheet_ydensity,scaling):
        """
        Initial pattern scaling (size_normalization), relative to the
        default retinal dimension of 1.0 in sheet coordinates.

        See __call__ for a description of the various scaling options.
        """
        pattern_rows,pattern_cols = self.pattern_sheet.activity.shape

        # CEBALERT: instead of an if-test, could have a class of this
        # type of function (c.f. OutputFunctions, etc).
        if scaling=='stretch_to_fit':
            x_sf,y_sf = pattern_cols/sheet_xdensity, pattern_rows/sheet_ydensity
            x*=x_sf; y*=y_sf

        elif scaling=='fit_shortest':
            if pattern_rows<pattern_cols:
                sf = pattern_rows/sheet_ydensity
            else:
                sf = pattern_cols/sheet_xdensity
            x*=sf;y*=sf
            
        elif scaling=='fit_longest':
            if pattern_rows<pattern_cols:
                sf = pattern_cols/sheet_xdensity
            else:
                sf = pattern_rows/sheet_ydensity
            x*=sf;y*=sf

        else:
            raise ValueError("Unknown scaling option",scaling)


# CEBHACKALERT: this new version is untested (as was the old one...)
from topo.base.parameterclasses import Wrapper
class CompositePatternGenerator(PatternGenerator):
    """
    PatternGenerator that accepts a list of other PatternGenerators.
    To create a new pattern, asks each of the PatternGenerators in the
    list to create a pattern, then it combines the patterns to create a 
    single pattern that it returns.
    """

    # CEBHACKALERT: size_normalization and whole_image_output_fn are
    # hidden temporarily.

    output_fn = OutputFnParameter(default=IdentityOF())

    operator = Parameter(
        default=Wrapper("Numeric.add"),
        doc="Numeric function used to combine the individual patterns.",
        precedence=0.98)
    
    generators = Parameter(
        default=[],
        doc="List of patterns to use in the composite pattern.",
        precedence=0.97)

    aspect_ratio   = Number(
        default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
        precedence=0.31,
        doc="Ratio of width to height of the composite pattern.")
    
    size  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,
                   doc="Height of the composite pattern.")

    size_normalization = Enumeration(
        hidden='True',
        default='original',
        available=['fit_shortest','fit_longest','stretch_to_fit','original'],
        precedence=0.95,
        doc='How to scale the initial image size relative to the default area of 1.0.')

    whole_image_output_fn = OutputFnParameter(
        hidden='True',
        default=IdentityOF(),
        precedence=0.96,
        doc='Function applied to the whole composite array (before any cropping).')


    def __init__(self,generators=[Disk(x=-0.3),Disk(x=0.3)],**params):
        super(CompositePatternGenerator,self).__init__(**params)
        self.generators = generators
        self.image_array = None


    def function(self,**params):
        size_normalization = params.get('scaling',self.size_normalization)
        whole_image_output_fn = params.get('whole_image_output_fn',
                                           self.whole_image_output_fn)
        bounds = params.get('bounds',self.bounds)
        xdensity=params.get('density',self.xdensity)
        ydensity=params.get('density',self.ydensity)
        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height


        assert hasattr(self.operator,'reduce'),repr(self.operator)+" does not support 'reduce'."


        # CEBHACKALERT: could skip re-generation if nothing has
        # changed.  But that involves checking the component
        # PatternGenerators haven't also changed (e.g. had a parameter
        # altered), which I'm not sure how to do in a reasonable
        # way. Alternatively, we could just say that if the list
        # doesn't change, we don't change the Composite - even though
        # a component PatternGenerator might have changed.


        patterns = []
        
        for pg in self.generators:
            assert isinstance(pg,PatternGenerator),repr(pg)+" is not a PatternGenerator."
            # just call the PG because it should already have been
            # setup as desired.
            patterns.append(pg())
        
        image_array = self.operator.reduce(patterns)

        ps = PatternSampler(image_array,whole_image_output_fn)


        return ps(self.pattern_x,self.pattern_y,
                  float(xdensity),
                  float(ydensity),
                  size_normalization,
                  float(width),float(height))










        
