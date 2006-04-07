"""
Image is a PatternGenerator that displays grayscale images.

$Id$
"""

# CEBHACKALERT: Needs to be updated following changes to Sheet and
# pattern generator.

# CEBALERT: We already have 'Image' for the image generator.
import Image as pImage
import ImageOps
from Numeric import array, ones, Float

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import Sheet
from topo.base.boundingregion import BoundingBox
from topo.base.patterngenerator import PatternGenerator
from topo.base.parameterclasses import Filename, Number, Parameter, Enumeration
from topo.base.projection import OutputFunctionParameter

from topo.outputfns.basic import DivisiveMaxNormalize,Identity


from Numeric import sum,ravel
def edge_average(a):
    """
    Return the mean value around the edge of an array.
    """
    if len(ravel(a)) < 2:
        return float(a[0])
    else:
        top_edge = a[0]
        bottom_edge = a[-1]
        left_edge = a[1:-1,0]
        right_edge = a[1:-1,-1]

        edge_sum = sum(top_edge) + sum(bottom_edge) + sum(left_edge) + sum(right_edge)
        num_values = len(top_edge)+len(bottom_edge)+len(left_edge)+len(right_edge)

        return float(edge_sum)/num_values


class PatternSampler(ParameterizedObject):
    """
    Stores a Sheet whose activity represents the supplied pattern_array,
    and when called will resample that array at the supplied Sheet coordinates
    according to the supplied scaling parameters.

    (x,y) coordinates outside the pattern_array are returned as the
    background value.
    """

    def __init__(self, pattern_array, whole_pattern_output_fn=Identity(), background_value=0.0):
        """
        Create a Sheet whose activity is pattern_array (where pattern_array
        is a Numeric array) after application of whole_pattern_output_fn.
        """
        super(PatternSampler,self).__init__()
        
        rows,cols=pattern_array.shape
        self.pattern_sheet = Sheet(density=1.0,
                                 bounds=BoundingBox(points=((-cols/2.0,-rows/2.0),
                                                            ( cols/2.0, rows/2.0))))
        self.pattern_sheet.activity = whole_pattern_output_fn(pattern_array)
        self.background_value = background_value
        

    def __call__(self, x, y, sheet_density, scaling, width=1.0, height=1.0):
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
        x*=sheet_density 
        y*=sheet_density
      
        # scale according to initial pattern scaling selected (size_normalization)
        if not scaling=='original':
            self.__apply_size_normalization(x,y,sheet_density,scaling)

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
                    if self.pattern_sheet.bounds.contains_exclusive(x[i,j],y[i,j]):
                        pattern_sample[i,j] = self.pattern_sheet.activity[r[i,j],c[i,j]]

        return pattern_sample


    def __apply_size_normalization(self,x,y,sheet_density,scaling):
        """
        Initial pattern scaling (size_normalization), relative to the
        default retinal dimension of 1.0 in sheet coordinates.

        See __call__ for a description of the various scaling options.
        """
        pattern_rows,pattern_cols = self.pattern_sheet.activity.shape

        # CEBALERT: instead of an if-test, could have a class of this
        # type of function (c.f. OutputFunctions, etc).
        if scaling=='stretch_to_fit':
            x_sf,y_sf = pattern_cols/sheet_density, pattern_rows/sheet_density
            x*=x_sf; y*=y_sf

        elif scaling=='fit_shortest':
            if pattern_rows<pattern_cols:
                sf = pattern_rows/sheet_density
            else:
                sf = pattern_cols/sheet_density
            x*=sf;y*=sf
            
        elif scaling=='fit_longest':
            if pattern_rows<pattern_cols:
                sf = pattern_cols/sheet_density
            else:
                sf = pattern_rows/sheet_density
            x*=sf;y*=sf

        else:
            raise ValueError("Unknown scaling option",scaling)
    



class TopoImage(PatternSampler):
    """
    A PatternSampler based on the image found at filename.

    The image is converted to grayscale if it is not already a
    grayscale image. See PIL's Image class for details of supported
    image file formats.

    The background value is calculated as an edge average: see edge_average().
    Black-bordered images therefore have a black background, and
    white-bordered images have a white background. Images with no
    border have a background that is less of a contrast than a white
    or black one.
    """    
    def __init__(self, filename, whole_image_output_fn=Identity()):
        """
        Create a Sheet whose activity represents the original image,
        after having whole_image_output_fn applied.
        """
        image = ImageOps.grayscale(pImage.open(filename))
        image_array = array(image.getdata(),Float)
        image_array.shape = (image.size[::-1]) # getdata() returns transposed image?
        super(TopoImage,self).__init__(image_array,whole_image_output_fn,edge_average(image_array))



# CEBHACKALERT: rotation,scaling etc. just resample - there's no interpolation.
class Image(PatternGenerator):
    """2D image generator."""

    output_fn = OutputFunctionParameter(default=Identity())
    
    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.31,doc="Ratio of width to height; size*aspect_ratio gives the width.")
    size  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.30,doc="Height of the image.")
    filename = Filename(default='examples/ellen_arthur.pgm',precedence=0.9,doc="Path (can be relative to Topographica's base path) to an image in e.g. PNG, JPG, TIFF, or PGM format.")
    size_normalization = Enumeration(default='fit_shortest',
                                     available=['fit_shortest','fit_longest','stretch_to_fit','original'],
                                     precedence=0.95,
                                     doc='How to scale the initial image size relative to the default area of 1.0.')

    whole_image_output_fn = OutputFunctionParameter(default=DivisiveMaxNormalize(),
                              precedence=0.96,
                              doc='Function applied to the whole, original image array (before any cropping).')

    
    def function(self,**params):
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        filename = params.get('filename',self.filename)
        size_normalization = params.get('scaling',self.size_normalization)
        whole_image_output_fn = params.get('whole_image_output_fn',self.whole_image_output_fn)

        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        image = TopoImage(filename, whole_image_output_fn)
        return image(x,y,float(density),size_normalization,float(width),float(height))


