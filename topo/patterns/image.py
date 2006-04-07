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
from topo.base.projection import OutputFunctionParameter

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


