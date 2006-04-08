"""
Image is a PatternGenerator that displays grayscale images.

$Id$
"""

# CEBALERT: We already have 'Image' for the image generator.
import Image as pImage
import ImageOps
from Numeric import array, Float, sum, ravel

from topo.base.patterngenerator import PatternGenerator
from topo.base.parameterclasses import Filename, Number, Parameter, Enumeration
from topo.base.projection import OutputFnParameter

from topo.outputfns.basic import DivisiveMaxNormalize,Identity

from basic import PatternSampler


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



# CEBHACKALERT: rotation,scaling etc. just resample - there's no interpolation.
class Image(PatternGenerator):
    """
    2D image generator.

    The image at the supplied filename is converted to grayscale if it
    is not already a grayscale image. See PIL's Image class for
    details of supported image file formats.

    The background value is calculated as an edge average: see edge_average().
    Black-bordered images therefore have a black background, and
    white-bordered images have a white background. Images with no
    border have a background that is less of a contrast than a white
    or black one.
    """

    output_fn = OutputFnParameter(default=Identity())
    
    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.31,doc="Ratio of width to height; size*aspect_ratio gives the width.")
    size  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.30,doc="Height of the image.")
    filename = Filename(default='examples/ellen_arthur.pgm',precedence=0.9,doc="Path (can be relative to Topographica's base path) to an image in e.g. PNG, JPG, TIFF, or PGM format.")
    size_normalization = Enumeration(default='fit_shortest',
                                     available=['fit_shortest','fit_longest','stretch_to_fit','original'],
                                     precedence=0.95,
                                     doc='How to scale the initial image size relative to the default area of 1.0.')

    whole_image_output_fn = OutputFnParameter(default=DivisiveMaxNormalize(),
                              precedence=0.96,
                              doc='Function applied to the whole, original image array (before any cropping).')


    def __init__(self, **params):
        """
        Create the last_filename and last_wiof attributes, used to hold
        the last filename and last whole_image_output_function.

        This allows reloading an existing image to be avoided.
        """
        super(Image,self).__init__(**params)
        self.last_filename = None
        self.last_wiof = None


    def __setup_pattern_sampler(self, filename, whole_image_output_fn):
        """
        If a new filename or whole_image_output_fn is supplied, create a
        PatternSampler based on the image found at filename.        

        The PatternSampler is given the whole image array after it has
        been converted to grayscale.
        """
        if filename!=self.last_filename or whole_image_output_fn!=self.last_wiof:
            self.last_filename=filename
            self.last_wiof=whole_image_output_fn
            image = ImageOps.grayscale(pImage.open(self.filename))
            image_array = array(image.getdata(),Float)
            image_array.shape = (image.size[::-1]) # getdata() returns transposed image?
            self.ps = PatternSampler(image_array,whole_image_output_fn,edge_average)


    def function(self,**params):
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        filename = params.get('filename',self.filename)
        size_normalization = params.get('scaling',self.size_normalization)
        whole_image_output_fn = params.get('whole_image_output_fn',self.whole_image_output_fn)

        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        self.__setup_pattern_sampler(filename,whole_image_output_fn)
        return self.ps(x,y,float(density),size_normalization,float(width),float(height))


