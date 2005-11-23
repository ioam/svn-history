"""
Contains two classes: TopoImage and ImageGenerator.


$Id$
"""

# CEB:
# this file is still being written.

# - when resizing, image should remain centered


from topo.base.topoobject import TopoObject
from topo.outputfns.basic import DivisiveMaxNormalize
from topo.base.patterngenerator import PatternGenerator
from topo.base.parameter import Parameter, Number
from Numeric import array, transpose, ones, floor, Float, divide, where
import Image, ImageOps


from Numeric import sum, ravel
def edge_average(a):
    """
    Return the mean value around the edge of an array.
    """
    flat_a = ravel(a)
    if len(flat_a) <= 4:
        edge_sum = sum(flat_a)
        num_values = len(flat_a)
    else:
        edge_sum = sum(a[0]) + sum(a[-1]) + sum(a[:,0]) + sum(a[:,-1]) - a[0,0] - a[0,-1] - a[-1,0] - a[-1,-1]
        num_values = 2*len(a[0])+2*len(a[:,0]) - 4

    return edge_sum/num_values


class TopoImage(TopoObject):
    """
    Stores a Numeric array representing a normalized Image. The Image is converted to and
    stored in grayscale. It is stored at its original size.

    There is also a background value, displayed at any point on the retina not covered by the
    image. This background value is calculated by calculating the mean of the pixels around
    the edge of the image. Black-bordered images therefore have a black background, and white-
    bordered images have a white background, for example. Images with no border have a background
    that is less of a contrast than a white or black one.
    """
    ### JABALERT: Should eventually make this an OutputFunctionParameter
    output_fn = Parameter(default=DivisiveMaxNormalize())
    
    def __init__(self, filename):
        """
        """
        image = ImageOps.grayscale(Image.open(filename))
        self.w, self.h = image.size 

        image_array = array(image.getdata(),Float)
        image_array = self.output_fn(image_array)
        
        image_array.shape = (self.h, self.w) # ** getdata() returns transposed image?
        self.image_array = transpose(image_array)
        
        self.background_value = edge_average(self.image_array)


    def resample(self, x, y, bounds, density, width=1.0, height=1.0):
        """
        Return pixels from the image at the given Topographica (x,y) coordinates,
        with width/height multiplied as specified by the given width and height factors.

        The Topographica coordinates are mapped to the Image ones by assuming the longest
        dimension of the Image should fit the default retinal dimension of 1.0. The other
        dimension is scaled by the same factor.
        """
        # CEBHACKALERT:
        # offer alternatives (shortest dimension to area, etc.)
        # fit longest dimension to default retina area (1.0)
        if self.h > self.w:
            stretch_factor = float(self.h)/1.0
        else:
            stretch_factor = float(self.w)/1.0

        x_scaled = self.__topo_coords_to_image(x, divide(stretch_factor,width), self.w)
        y_scaled = self.__topo_coords_to_image(y, divide(stretch_factor,height), self.h)

        assert x_scaled.shape == x.shape
        assert y_scaled.shape == y.shape
        
        image_sample = ones(x_scaled.shape, Float)*self.background_value
        
        if self.h==0 or self.w==0 or width==0 or height==0:
            return image_sample
        else:
            # sample image at the scaled (x,y) coordinates
            for i in xrange(len(image_sample)):
                for j in xrange(len(image_sample[i,:])):
                    if x_scaled[i,j] >= 0 and y_scaled[i,j] >= 0:
                        image_sample[i,j] = self.image_array[ x_scaled[i,j], y_scaled[i,j] ]

        # CEBALERT:
        # Could be useful to allow local normalization here instead of global.             
        return image_sample

    ### JABHACKALERT!  Should be unified with sheet2matrix in sheet.py
    def __topo_coords_to_image(self,x,scale_factor,num_pixels):
        """
        Transform the given topographica abscissae/ordinates (x) to fit
        an image with num_pixels along that aspect.

        - translate center (Image has (0,0) as top-left corner)
        - scale x to match the size of the image, so e.g. x=3 corresponds
          to pixel 3, and x=4 to pixel 4

        An Image consists of discrete pixels, whereas the x values are floating-
        point numbers. The simplistic technique in this function uses floor() to
        map a range to a single number.
        """
        x_scaled = (x+0.5) * scale_factor
        x_scaled = floor(x_scaled)
        x_scaled = where(x_scaled>=num_pixels, -1, x_scaled)  
        return x_scaled.astype(int)  # no rounding is done here


# see PIL for documentation
# color to grayscale, etc
# rotation, resize just resample no interpolation
class ImageGenerator(PatternGenerator):
    """2D image generator."""

    width  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0))
    height  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0))

    # CEBHACKALERT:
    # Until parametersframe is changed to allow non-number parameters, etc,
    # this has to be hidden. Eventually could be 'default="a_file_name"' or
    # 'default=TopoImage_name', or whatever.
    image = Parameter(default=TopoImage(filename='examples/ellen_arthur.pgm'), hidden=True)
    
    def function(self,**params):
        bounds  = params.get('bounds', self.bounds)
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        width   = params.get('width',self.width)
        height  = params.get('height',self.height)
        image   = params.get('image',self.image)
        
        return image.resample(x,y,bounds,density, width, height)


