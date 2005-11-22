"""
Contains three classes: BoundedImage, TopoImage, and ImageGenerator.


$Id$
"""

# CEB:
# this file is still being written.

# - bad image quality on rotate (only solution would be to use Image's own rotate)


from topo.base.patterngenerator import PatternGenerator
from topo.base.parameter import Parameter, Number
from Numeric import array, transpose, zeros, floor, remainder, Float, divide
import Image, ImageOps


# CEBHACKALERT:
# use normalization functions already available
from Numeric import ravel
def normalize(image_array):
    """
    Divide all values in the array by the maximum value.

    If the maximum value is zero, return the original values.
    """
    max_val = float(max(ravel(image_array)))
    
    if max_val > 0.0:
        return image_array/max_val
    else:
        return image_array



class TopoImage(object):
    """
    Stores a Numeric array representing a normalized Image. The Image is converted to and
    stored in grayscale. It is stored at its original size.
    """
    def __init__(self, filename):
        """
        """
        image = ImageOps.grayscale(Image.open(filename))
        self.w, self.h = image.size 

        image_array = array(image.getdata())
        image_array = normalize(image_array)
        image_array.shape = (self.h, self.w) # ** getdata() returns transposed image?

        self.image_array = transpose(image_array)
        

    def resample(self, x, y, bounds, density, width=1.0, height=1.0):
        """
        Return pixels from the image at the given Topographica (x,y) coordinates,
        with width/height multiplied as specified by the given width and height factors.

        The Topographica coordinates are mapped to the Image ones by assuming the longest
        dimension of the Image should fit the default retinal dimension of 1.0. The other
        dimension is scaled by the same factor.
        """
        # fit longest dimension to default retina area (1.0)
        if self.h > self.w:
            stretch_factor = float(self.h)/1.0
        else:
            stretch_factor = float(self.w)/1.0

        x_scaled = self.__topo_coords_to_image(x, divide(stretch_factor,width), self.w)
        y_scaled = self.__topo_coords_to_image(y, divide(stretch_factor,height), self.h)

        assert x_scaled.shape == x.shape
        assert y_scaled.shape == y.shape 

        image_sample = zeros(x_scaled.shape, Float)
        
        if self.h==0 or self.w==0 or width==0 or height==0:
            # we either had a zero-sized image originally, or height/width is zero
            # either case gets zero activity
            return image_sample
        else:
            # sample image at the scaled (x,y) coordinates
            for i in range(len(image_sample)):
                for j in range(len(image_sample[i,:])):
                    # CEBHACKALERT:
                    # Instead of replacing areas where there's no image with 0, it should be
                    # with the edge average. I have to think about how is best to do that;
                    # certainly a try/except statement is not the way!
                    try:
                        image_sample[i,j] = self.image_array[ x_scaled[i,j] , y_scaled[i,j] ]
                    except IndexError:
                        image_sample[i,j] = 0.0

        # CEBALERT:
        # It might make more sense for normalization to occur here rather than
        # in for the whole image. 
        # "That could be a useful option, i.e. to support both local and global
        # normalization."
        
        return image_sample


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
        return x_scaled.astype(int)  # no rounding is done here


            
class ImageGenerator(PatternGenerator):
    """2D image generator."""

    width  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0))
    height  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0))

    # CEBHACKALERT:
    # Until parametersframe is changed to allow non-number parameters, etc,
    # this has to be hidden. Eventually could be 'default="a_file_name"' or
    # 'default=TopoImage_name', or whatever.
    image = Parameter(default=TopoImage(filename='examples/ellen_arthur_square.pgm'), hidden=True)
    
    def function(self,**params):
        bounds  = params.get('bounds', self.bounds)
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        width   = params.get('width',self.width)
        height  = params.get('height',self.height)
        image   = params.get('image',self.image)
        
        return image.resample(x,y,bounds,density, width, height)


