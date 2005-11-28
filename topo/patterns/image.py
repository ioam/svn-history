"""
Contains two classes: TopoImage and ImageGenerator.


$Id$
"""

from topo.base.topoobject import TopoObject
from topo.base.sheet import bounds2shape
from topo.outputfns.basic import DivisiveMaxNormalize
from topo.base.patterngenerator import PatternGenerator
from topo.base.parameter import Parameter, Number
from Numeric import array, transpose, ones, floor, Float, divide, where
import Image, ImageOps


# CEBHACKALERT:
# The image is not scaled at all on loading.


from topo.base.sheet import sheet2matrix
def sheet2matrixidx_array(x,y,bounds,density):
    """
    """
    row, col = sheet2matrix(x,y,bounds,density)
    return row.astype(int),col.astype(int)


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


    ### JABHACKALERT!  Should be unified with sheet2matrix in sheet.py
    def __topo_coords_to_image(self,x,y,bounds,density,width,height):
        """
        Transform the given topographica abscissae/ordinates (x) to fit
        an image with num_pixels along that aspect.

        - translate center (Image has (0,0) as top-left corner)
        - scale x to match the size of the image, so e.g. x=3 corresponds
          to pixel 3, and x=4 to pixel 4

        An Image consists of discrete pixels, whereas the x values are floating-
        point numbers. The simplistic technique in this function uses floor() to
        map a range to a single number.

        Maybe it would be better to put image into Sheet and use BoundingBocol functions, etc.
        """
        # CEBHACKALERT:
        # offer alternatives (shortest dimension to area, etc.)
        # fit longest dimension to default retina area (1.0)

        x = x/width  
        y = y/height

        row, col = sheet2matrixidx_array(x,y,bounds,density)
        n_rows,n_cols = bounds2shape(bounds,density)

        col = col - n_cols/2.0 + self.w/2.0
        row = row - n_rows/2.0 + self.h/2.0
        
        col = where(col>=self.w, -col, col)
        row = where(row>=self.h, -row, row)

        return col.astype(int), row.astype(int)


    def __call__(self, x, y, bounds, density, width=1.0, height=1.0):
        """
        Return pixels from the image at the given Topographica (x,y) coordinates,
        with width/height multiplied as specified by the given width and height factors.

        The Topographica coordinates are mapped to the Image ones by assuming the longest
        dimension of the Image should fit the default retinal dimension of 1.0. The other
        dimension is scaled by the same factor.
        """
 
        x_scaled, y_scaled = self.__topo_coords_to_image(x, y, bounds, density, width, height)
        
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



# xsee PIL for documentation
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
        
        return image(x,y,bounds,density, width, height)


