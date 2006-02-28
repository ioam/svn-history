"""
Contains two classes: TopoImage and Image.


$Id$
"""

# CEBHACKALERT: I have to go over this file. It should be considered
# untested. Needs to be updated following changes to Sheet and
# pattern generator.

# CEBHACKALERT: We already have 'Image' for the image generator.
import Image as pImage
import ImageOps
from Numeric import array, transpose, ones, floor, Float, divide, where

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import bounds2slice, sheet2matrix
from topo.base.patterngenerator import PatternGenerator
from topo.base.parameterclasses import Filename, Number, Parameter, Enumeration
from topo.base.projection import OutputFunctionParameter

from topo.outputfns.basic import DivisiveMaxNormalize


# CEBHACKALERT: this is sheet's, but for arrays
def sheet2matrixidx_array(x,y,bounds,density):
    """
    Convert a point (x,y) in sheet coordinates to the integer row and
    column index of the matrix cell in which that point falls, given a
    bounds and density.  Returns (row,column).

    Note that if coordinates along the right or bottom boundary are
    passed into this function, the returned matrix coordinate of the
    boundary will be just outside the matrix, because the right and
    bottom boundaries are exclusive.
    """
    # CEBHACKALERT: see Sheet.__init__
    if type(density)!=tuple:
        left,bottom,right,top = bounds.aarect().lbrt()
        xdensity = int(density*(right-left)) / float((right-left))
        ydensity = int(density*(top-bottom)) / float((top-bottom))
    else:
        xdensity,ydensity = density

    r,c = sheet2matrix(x,y,bounds,xdensity,ydensity)
    r = floor(r)
    c = floor(c)
    return r, c


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


def stretch_to_fit(x,y,n_rows,n_cols,height,width):
    """
    """
    y_sf = divide(float(n_rows),height)
    x_sf = divide(float(n_cols),width)
    return x/x_sf, y/y_sf        


# CEBHACKALERT:
# instead of fitting to this particular retina,
# should fit to 1.0 ?
def fit_shortest(x,y,n_rows,n_cols,height,width):
    """
    """
    longest_r_dim = max(n_rows,n_cols)
    shortest_i_dim = min(height,width)
    sf = divide(float(longest_r_dim),shortest_i_dim)
    return x/sf, y/sf

def fit_longest(x,y,n_rows,n_cols,height,width):
    """
    """
    shortest_r_dim = min(n_rows,n_cols)
    longest_i_dim = max(height,width)
    sf = divide(float(shortest_r_dim),longest_i_dim)
    return x/sf, y/sf


class TopoImage(ParameterizedObject):
    """

    Stores a Numeric array representing a normalized Image. The Image
    is converted to and stored in grayscale. It is stored at its
    original size.

    There is also a background value, displayed at any point on the
    retina not covered by the image. This background value is
    calculated by calculating the mean of the pixels around the edge
    of the image. Black-bordered images therefore have a black
    background, and white- bordered images have a white background,
    for example. Images with no border have a background that is less
    of a contrast than a white or black one.

    """    
    def __init__(self, filename, output_fn):
        """
        """
        image = ImageOps.grayscale(pImage.open(filename))
        self.n_image_cols, self.n_image_rows = image.size

        image_array = array(image.getdata(),Float)
        image_array = output_fn(image_array)
        
        image_array.shape = (self.n_image_rows, self.n_image_cols) # ** getdata() returns transposed image?
        self.image_array = transpose(image_array)
        
        self.background_value = edge_average(self.image_array)


    # CEBHACKALERT: the name and documentation have to be changed.
    def __sheet_to_image(self,x,y,bounds,density,width,height,scaling):
        """
        Transform the given topographica abscissae/ordinates (x) to fit
        an image with num_pixels along that aspect.

        - translate center (Image has (0,0) as top-left corner, whereas Sheet has
        (0,0) in the center).

        An Image consists of discrete pixels, whereas the x values are floating-
        point numbers. The simplistic technique in this function uses floor() to
        map a range to a single number.

        Maybe it would be better to put image into Sheet and use BoundingBocol functions, etc.
        """

        # CEBHACKALERT: temporary, density will become one again soon...
        if type(density)!=tuple:
            xdensity=density
            ydensity=density
        else:
            xdensity,ydensity = density


        # CEBHACKALERT: just made it work - this needs to be changed now
        # that sheet and patterngenerator are different.
        #n_sheet_rows,n_sheet_cols = bounds2shape(bounds,xdensity,ydensity)
        r1,r2,c1,c2 = bounds2slice(bounds,bounds,xdensity,ydensity)
        n_sheet_rows,n_sheet_cols = r2-r1,c2-c1

        
        # Initial image scaling (size_normalization)
        
        # CEBALERT: instead of an if-test, could have a class of this
        # type of function and generate the list from that
        # (c.f. PatternGeneratorParameter).
        if scaling=='fit_shortest':
            x,y = fit_shortest(x,y,n_sheet_rows,n_sheet_cols,self.n_image_rows,self.n_image_cols)
        elif scaling=='fit_longest':
            x,y = fit_longest(x,y,n_sheet_rows,n_sheet_cols,self.n_image_rows,self.n_image_cols)
        elif scaling=='stretch_to_fit':
            x,y = stretch_to_fit(x,y,n_sheet_rows,n_sheet_cols,self.n_image_rows,self.n_image_cols)
        elif scaling=='original':
            pass
        
        x = x/width
        y = y/height

        row, col = sheet2matrixidx_array(x,y,bounds,density)

        # CEBALERT:
        # Instead of doing this kind of thing, could make TopoImage a
        # Sheet and then do this with BoundingBoxes.
        col = col - n_sheet_cols/2.0 + self.n_image_cols/2.0
        row = row - n_sheet_rows/2.0 + self.n_image_rows/2.0

        # document what this is...
        col = where(col>=self.n_image_cols, -col, col)
        row = where(row>=self.n_image_rows, -row, row)

        # ...and don't do this
        return col.astype(int), row.astype(int)


    def __call__(self, x, y, bounds, density, scaling, width=1.0, height=1.0):
        """
        Return pixels from the image (size-normalized according to scaling) at the given Sheet (x,y) coordinates, with width/height multiplied as specified
        by the given width and height factors.

        
        """
 
        x_scaled, y_scaled = self.__sheet_to_image(x, y, bounds, density, width, height, scaling)
        
        image_sample = ones(x_scaled.shape, Float)*self.background_value

        if self.n_image_rows==0 or self.n_image_cols==0 or width==0 or height==0:
            return image_sample
        else:
            # CEBALERT: Sample image at the scaled (x,y)
            # coordinates. You'd think there'd be a Numeric way to do
            # this.
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
class Image(PatternGenerator):
    """2D image generator."""

    aspect_ratio  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.31,doc="Ratio of width to height; size*aspect_ratio gives the width.")
    size  = Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),precedence=0.30,doc="Height of the image.")
    filename = Filename(default='examples/ellen_arthur.pgm',search_paths=['/home/chris'],precedence=0.9,doc="Path (relative to the Topographica base path) to an image in e.g. PNG, JPG, TIFF, or PGM format.")

    size_normalization = Enumeration(default='fit_shortest',
                                     available=['fit_shortest','fit_longest','stretch_to_fit','original'],
                                     precedence=0.95,
                                     doc='How to scale the initial image size relative to the default area of 1.0.')

    output_fn = OutputFunctionParameter(default=DivisiveMaxNormalize(),
                                        precedence=0.96,
                                        doc='How to normalize the value of each image pixel.')
    
    def function(self,**params):
        bounds  = params.get('bounds', self.bounds)
        density = params.get('density', self.density)
        x       = params.get('pattern_x',self.pattern_x)
        y       = params.get('pattern_y',self.pattern_y)
        filename = params.get('filename',self.filename)
        size_normalization = params.get('scaling',self.size_normalization)
        output_fn = params.get('output_fn',self.output_fn)

        height = params.get('size',self.size)
        width = (params.get('aspect_ratio',self.aspect_ratio))*height

        image = TopoImage(filename, output_fn)
        return image(x,y,bounds,density, size_normalization,width, height)


