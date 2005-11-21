"""
Contains three classes: BoundedImage, TopoImage, and ImageGenerator.


$Id$
"""

# CEB:
# this file is still being written.


# ? doesn't resize image correctly to bounds e.g. border missing on not_square
#   (or is that just from resize...seems likely: try image at full size)
#
# - bad image quality on rotate (only solution would be to use Image's own rotate)


from topo.base.patterngenerator import PatternGenerator
from topo.base.parameter import Parameter, Number
from Numeric import array, transpose, zeros, floor, where, remainder, zeros, Float
from topo.base.sheet import bounds2shape
import Image, ImageOps


# CEBALERT:
# BoundedImage and TopoImage could be one class, except then it wouldn't be possible
# to cache some results. Whenever ImageGenerator is called, it creates a new
# TopoImage, but the BoundedImage remains the same unless the image Parameter is changed.


class BoundedImage(object):
    """
    Stores a Numeric array representing a normalized Image, resized to fit the given bounds and density.
    The Image is converted to and stored in grayscale.

    The Image is resized so that its longest aspect (dimension) fills the range specified by the
    bounds and density. The other aspect is scaled by the same factor, maintaining the
    aspect ratio: non-square Images remain so. This Image is stored in a Numeric array, image_array,
    in which the pixel values are normalized (each pixel's value is divided by the largest pixel value).

    New bounds and density can be supplied after creation without loss of image quality because the
    original Image itself is resized in this case.

    A method, resize(), is provided to resize the image_array. (This uses Image.resize() to resize the
    bounded version of the original Image.)
    """
    def __init__(self, filename, bounds=None, density=None):
        """
        If bounds and density are supplied, create image_array and other variables.

        Otherwise, no image_array exists.
        """
        self.__original_image = ImageOps.grayscale(Image.open(filename)) 

        self.bounds, self.density = bounds, density
        self.__image_array_rows, self.__image_array_cols = None, None
        self.width, self.height = None, None
        self.install_bounds(bounds,density)


    def install_bounds(self, bounds, density):
        """
        Create image_array from the original image resized to given the bounds and density.
        """
        if bounds==None or density==None:
            return
            
        rows,cols = bounds2shape(bounds,density)

        if self.__image_array_rows != rows or self.__image_array_cols != cols:
            self.__image_array_rows, self.__image_array_cols = rows, cols
            
            original_width, original_height = self.__original_image.size
            if original_height > original_width:
                stretch_factor = float(rows)/float(original_height)
            else:
                stretch_factor = float(cols)/float(original_width)

            self.bounded_height = int(stretch_factor * original_height)
            self.bounded_width  = int(stretch_factor * original_width)
            self.__bounded_image = self.__original_image.resize((self.bounded_width, self.bounded_height))
            self.bounds, self.density = bounds,density
            self.resize( (self.bounded_width, self.bounded_height) )
            return
        
        
    def resize(self, xy):
        """
        Resize image_array to the width (x) and height (y) specified by the 2-tuple xy.
        """
        if self.bounds == None or self.density == None:
            raise ValueError("Bounds must be installed before resizing.")
        
        x, y = xy
        if self.width != x or self.height != y:
            self.width, self.height = x, y
            resized_image = self.__bounded_image.resize((self.width,self.height))

            if self.width==0 or self.height==0:
                self.image_array = array([0.0])
            else:
                self.image_array = array(resized_image.getdata())
                self.image_array.shape = (self.height,self.width) # ** getdata() returns transposed image?
                self.image_array = transpose(self.image_array)
                self.image_array = normalize(self.image_array)

            return 


        
class TopoImage(object):
    """
    Stores a BoundedImage and provides a method to sample it at Topographica coordinates, and
    with the width and height scaled by separate factors.
    
    If the specified coordinates, when transformed to Image coordinates, fall outside the image,
    they are wrapped: see resample().
    
    Where a
    dimension is shorter than the range specified by the bounds and density, the
    Image is 'wrapped': 
    """

    def __init__(self, bounded_image, bounds, density):
        """
        """
        self.bounded_image = bounded_image        
        self.bounded_image.install_bounds(bounds,density)


    def resample(self,x,y,width=1.0, height=1.0):
        """
        Return pixels from the BoundedImage at the given Topographica (x,y) coordinates,
        and with its width/height multiplied as specified by the given width and height factors.

        (This is where Topographica meets Image. So width,height,x,y mean different things.)
        
        Any required resizing is done with Image.resize().

        Asking for coodinates outsides the Image causes the coordinates to be wrapped, giving an
        image that is also wrapped (so, along x: left edge -> image -> right edge -> left edge -> image ...)
        """
        new_width = int(self.bounded_image.bounded_width*width)
        new_height = int(self.bounded_image.bounded_height*height)
        
        self.bounded_image.resize( (new_width,new_height) )
        image = self.bounded_image.image_array

        # rescale topo coordinates to Image ones
        max_dim = max(self.bounded_image.bounded_width,self.bounded_image.bounded_height)
        x_scaled = self.__topo_coords_to_image(x, max_dim, new_width)
        y_scaled = self.__topo_coords_to_image(y, max_dim, new_height)        

        assert x_scaled.shape == y_scaled.shape

        image_sample = zeros(x_scaled.shape, Float)
        
        if new_height==0 or new_width==0:
            return image_sample
        else:
            # sample image at the scaled (x,y) coordinates
            for i in range(len(image_sample)):
                for j in range(len(image_sample[i,:])):
                    image_sample[i,j] = image[ x_scaled[i,j] , y_scaled[i,j] ]

        # CEBALERT:
        # It might make more sense for normalization to occur here rather than
        # in BoundedImage. But this would not normalize the whole image -
        # just the section being returned.
        
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
        # one way of scaling & wrapping:
        x_scaled = (x+0.5) * scale_factor
        x_scaled = floor(x_scaled)
        x_scaled = x_scaled % num_pixels
        return x_scaled.astype(int)  # no rounding is done here


class ImageGenerator(PatternGenerator):
    """2D image generator."""

    width  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0))
    height  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0))

    # CEBHACKALERT:
    # Until parametersframe is changed to allow non-number parameters, etc,
    # this has to be hidden. Eventually could be 'default="a_file_name"' or
    # 'default=BoundedImage_name', or whatever.
    image = Parameter(default=BoundedImage(filename='examples/ellen_arthur_square.pgm'), hidden=True)
    
    def function(self,**params):
        bounds  = params.get('bounds', self.bounds)
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        width   = params.get('width',self.width)
        height  = params.get('height',self.height)
        image   = params.get('image',self.image)
        
        topo_image = TopoImage(image, bounds, density)
        return topo_image.resample(x,y,width,height)


# CEBHACKALERT:
# make more general and put in utils?
# there's a similar use in plot.py
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
