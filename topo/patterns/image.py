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
from topo.base.sheet import Sheet, bounds2slice
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


class TopoImage(ParameterizedObject):
    """
    Stores a Sheet whose activity represents the image found at
    filename.

    The image is converted to grayscale if it is not already a
    grayscale image. See PIL's Image class for details of supported
    image file formats.

    When called, returns an array which is a sampling of this image at
    the given array of (x,y) coordinates. (x,y) coordinates outside
    the image are returned as the background value (calculated as an
    edge average: see edge_average()).

    (Black-bordered images therefore have a black background, and
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
        image_array = whole_image_output_fn(array(image.getdata(),Float))
        image_array.shape = (image.size[::-1]) # getdata() returns transposed image?
        
        rows,cols=image_array.shape
        self.image_sheet = Sheet(density=1,
                                 bounds=BoundingBox(points=((-cols/2.0,-rows/2.0),
                                                            ( cols/2.0, rows/2.0))))

        self.image_sheet.activity = image_array
        self.background_value = edge_average(image_array)


    def __call__(self, x, y, sheet_bounds, sheet_density, scaling, width=1.0, height=1.0):
        """
        Return pixels from the Image at the given Sheet (x,y) coordinates.

        sheet_bounds, sheet_density, and scaling determine how the image is scaled
        initially (see __apply_size_normalization).

        The image is also scaled according to the supplied width and height.
        """
        # create new image sample, filled initially with the background value
        image_sample = ones(x.shape, Float)*self.background_value

        # if the height or width is zero, there's no image to display...
        if width==0 or height==0:
            return image_sample

        # scale the supplied coordinates to match the image
        x*=sheet_density 
        y*=sheet_density
      
        # scale according to initial image scaling selected (size_normalization)
        if not scaling=='original':
            self.__apply_size_normalization(x,y,sheet_bounds,sheet_density,scaling)

        # scale according to user-specified width and height
        x/=width
        y/=height

        # convert the sheet (x,y) coordinates to matrixidx (r,c) ones
        r,c = self.image_sheet.sheet2matrixidx_array(x,y)

        # now sample image at the (r,c) corresponding to the supplied (x,y)
        image_rows,image_cols = self.image_sheet.activity.shape
        if image_rows==0 or image_cols==0:
            return image_sample
        else:
            # CEBALERT: is there a more Numeric way to do this?
            rows,cols = image_sample.shape
            for i in xrange(rows):
                for j in xrange(cols):
                    # indexes outside the image are left with the background color
                    if self.image_sheet.bounds.contains_exclusive(x[i,j],y[i,j]):
                        image_sample[i,j] = self.image_sheet.activity[r[i,j],c[i,j]]

        return image_sample


    def __apply_size_normalization(self,x,y,sheet_bounds,sheet_density,scaling):
        """
        Initial image scaling (size_normalization).

        scaling can be:
          'stretch_to_fit'
        scale both dimensions of the image so they fill the sheet
        on which the image is being displayed
        (disregards the original's aspect ratio)

          'fit_shortest'
        scale the image so that its shortest dimension is made to fit
        the longest dimension of the sheet on which it is being displayed
        (maintains the original's aspect ratio)

          'fit_longest'
        scale the image so that its longest dimension is made to fit
        the shortest dimension of the sheet on which it is being displayed
        (maintains the original's aspect ratio)

          'original'
        no scaling is applied; one pixel of the image is put in one unit
        of the sheet on which the image being displayed
        """
        # CEBHACKALERT: temporary, sheet_density will become one again soon...
        if type(sheet_density)!=tuple:
            xdensity=sheet_density
            ydensity=sheet_density
        else:
            xdensity,ydensity = sheet_density


        r1,r2,c1,c2 = bounds2slice(sheet_bounds,sheet_bounds,xdensity,ydensity)        
        sheet_rows,sheet_cols = float(r2-r1),float(c2-c1)  # (float for later divisions)
        image_rows,image_cols = self.image_sheet.activity.shape

        # CEBALERT: instead of an if-test, could have a class of this
        # type of function (c.f. OutputFunctions, etc).


        # CEBHACKALERT: scaling should be done relative to the default
        # retinal area (i.e. 1.0) rather than to the current sheet.
        if scaling=='stretch_to_fit':
            x_sf,y_sf = image_cols/sheet_cols, image_rows/sheet_rows
            x*=x_sf; y*=y_sf

        elif scaling=='fit_shortest':
            if image_rows<image_cols:
                sf = image_rows/sheet_rows
            else:
                sf = image_cols/sheet_cols
            x*=sf;y*=sf
            
        elif scaling=='fit_longest':
            if image_rows<image_cols:
                sf = image_cols/sheet_cols
            else:
                sf = image_rows/sheet_rows
            x*=sf;y*=sf

        else:
            raise ValueError("Unknown scaling option",scaling)



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
        bounds  = params.get('bounds', self.bounds)
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        filename = params.get('filename',self.filename)
        size_normalization = params.get('scaling',self.size_normalization)
        whole_image_output_fn = params.get('whole_image_output_fn',self.whole_image_output_fn)

        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        image = TopoImage(filename, whole_image_output_fn)
        return image(x,y,bounds,density, size_normalization,width, height)


