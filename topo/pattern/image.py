"""
PatternGenerators based on bitmap images stored in files.

$Id$
"""

# PIL Image is imported as PIL because we have our own Image PatternGenerator
import Image as PIL
import ImageOps

from numpy.oldnumeric import array, Float, sum, ravel, ones

from .. import param
from topo.param.parameterized import ParamOverrides

from topo.base.boundingregion import BoundingBox
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.transferfn.basic import DivisiveNormalizeLinf,TransferFn
from topo.misc.filepath import Filename


class PatternSampler(param.Parameterized):
    """
    Stores a SheetCoordinateSystem whose activity represents the
    supplied pattern_array, and when called will resample that array
    at the supplied Sheet coordinates according to the supplied
    scaling parameters.

    (x,y) coordinates outside the pattern_array are returned as the
    background value.
    """

    whole_pattern_output_fns = param.List(class_=TransferFn,default=[],doc="""
    Functions to apply to the whole image before any sampling is done.""")

    background_value_fn = param.Callable(default=None,doc="""
    Function to compute an appropriate background value. Must accept
    an array and return a scalar.""")

    scaling = param.Enumeration(
        default='original',
        available=['original','stretch_to_fit','fit_shortest','fit_longest'],
        doc="""
    Determines how the pattern is scaled initially, relative to the
    default retinal dimension of 1.0 in sheet coordinates:
        
    'stretch_to_fit': scale both dimensions of the pattern so they
    would fill a Sheet with bounds=BoundingBox(radius=0.5) (disregards
    the original's aspect ratio).

    'fit_shortest': scale the pattern so that its shortest dimension
    is made to fill the corresponding dimension on a Sheet with
    bounds=BoundingBox(radius=0.5) (maintains the original's aspect
    ratio).

    'fit_longest': scale the pattern so that its longest dimension is
    made to fill the corresponding dimension on a Sheet with
    bounds=BoundingBox(radius=0.5) (maintains the original's aspect
    ratio).

    'original': no scaling is applied; one pixel of the pattern is put
    in one unit of the sheet on which the pattern being displayed.""")
                                

    def __init__(self, pattern_array=None, image=None, **params):
        """
        Create a SheetCoordinateSystem whose activity is pattern_array
        (where pattern_array is a NumPy array).
        """
        super(PatternSampler,self).__init__(**params)

        if pattern_array is not None and image is not None:
            raise ValueError("PatternSampler instances can have a pattern or an image, but not both.")    
        elif pattern_array is not None:
            pass
        elif image is not None:
            pattern_array = array(image,Float)
        else:
            raise ValueError("PatternSampler instances must have a pattern or an image.")

        rows,cols = pattern_array.shape

        self.scs = SheetCoordinateSystem(xdensity=1.0,ydensity=1.0,
            bounds=BoundingBox(points=((-cols/2.0,-rows/2.0),
                                       ( cols/2.0, rows/2.0))))

        for wpof in self.whole_pattern_output_fns:
            wpof(pattern_array)
            
        self.scs.activity = pattern_array

        if not self.background_value_fn:
            self.background_value = 0.0
        else:
            self.background_value = self.background_value_fn(self.scs.activity)
        

    def __call__(self, x, y, sheet_xdensity, sheet_ydensity, width=1.0, height=1.0, **params):
        """
        Return pixels from the pattern at the given Sheet (x,y) coordinates.

        sheet_density should be the density of the sheet on which the pattern
        is to be drawn.


        The pattern is further scaled according to the supplied width and height.
        """
        p=ParamOverrides(self,params)
        
        # create new pattern sample, filled initially with the background value
        pattern_sample = ones(x.shape, Float)*p.background_value

        # if the height or width is zero, there's no pattern to display...
        if width==0 or height==0:
            return pattern_sample

        # scale the supplied coordinates to match the pattern being at density=1
        x*=sheet_xdensity 
        y*=sheet_ydensity
      
        # scale according to initial pattern scaling selected (size_normalization)
        self.__apply_size_normalization(x,y,sheet_xdensity,sheet_ydensity,p.scaling)

        # scale according to user-specified width and height
        x/=width
        y/=height

        # convert the sheet (x,y) coordinates to matrixidx (r,c) ones
        r,c = self.scs.sheet2matrixidx(x,y)

        # now sample pattern at the (r,c) corresponding to the supplied (x,y)
        pattern_rows,pattern_cols = self.scs.activity.shape
        if pattern_rows==0 or pattern_cols==0:
            return pattern_sample
        else:
            # CEBALERT: is there a more NumPy way to do this that would be faster?
            rows,cols = pattern_sample.shape
            for i in xrange(rows):
                for j in xrange(cols):
                    # indexes outside the pattern are left with the background color
                    if self.scs.bounds.contains_exclusive(x[i,j],y[i,j]):
                        pattern_sample[i,j] = self.scs.activity[r[i,j],c[i,j]]

        return pattern_sample


    def __apply_size_normalization(self,x,y,sheet_xdensity,sheet_ydensity,scaling):
        pattern_rows,pattern_cols = self.scs.activity.shape

        # Instead of an if-test, could have a class of this type of
        # function (c.f. OutputFunctions, etc)...
        if scaling=='original':
            return
        
        elif scaling=='stretch_to_fit':
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



from numpy.oldnumeric import sum,ravel
def edge_average(a):
    "Return the mean value around the edge of an array."
    
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


class FastPatternSampler(param.Parameterized):
    """
    A fast-n-dirty pattern sampler using Python Imaging Library
    routines.  Currently this sampler doesn't support user-specified
    scaling or cropping but rather simply scales and crops the image
    to fit the given matrix size without distorting the aspect ratio
    of the original picture.
    """
    
    sampling_method = param.Integer(default=PIL.NEAREST,doc="""
       Python Imaging Library sampling method for resampling an image.
       Defaults to Image.NEAREST.""")

       
    def __init__(self, pattern=None, image=None, **params):
        super(FastPatternSampler,self).__init__(**params)

        if pattern and image:
            raise ValueError("PatternSampler instances can have a pattern or an image, but not both.")    
        elif pattern is not None:
            self.image = PIL.new('L',pattern.shape)
            self.image.putdata(pattern.ravel())
        elif image is not None:
            self.image = image
        else:
            raise ValueError("PatternSampler instances must have a pattern or an image.")


    def __call__(self, x, y, sheet_xdensity, sheet_ydensity, width=1.0, height=1.0, **params):

        # JPALERT: Right now this ignores all options and just fits the image into given array.
        # It needs to be fleshed out to properly size and crop the
        # image given the options. (maybe this class needs to be
        # redesigned?  The interface to this function is pretty inscrutable.)

        im = ImageOps.fit(self.image,x.shape,self.sampling_method)
        return array(im,dtype=Float)

        
# Would be best called Image, but that causes confusion with PIL's Image
class GenericImage(PatternGenerator):
    """
    Generic 2D image generator.

    Generates a pattern from a Python Imaging Library image object.
    Subclasses should override the _get_image method to produce the
    image object.

    The background value is calculated as an edge average: see edge_average().
    Black-bordered images therefore have a black background, and
    white-bordered images have a white background. Images with no
    border have a background that is less of a contrast than a white
    or black one.

    At present, rotation, scaling, etc. just resample; it would be nice
    to support some interpolation options as well.
    """

    __abstract = True
    
    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),
        softbounds=(0.0,2.0),precedence=0.31,doc="""
        Ratio of width to height; size*aspect_ratio gives the width.""")

    size  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,doc="Height of the image.")
        
    size_normalization = param.Enumeration(default='fit_shortest',
        available=['fit_shortest','fit_longest','stretch_to_fit','original'],
        precedence=0.95,doc="""
        How to scale the initial image size relative to the default area of 1.0.""")

    whole_image_output_fns = param.HookList(default=[DivisiveNormalizeLinf()],
        class_=TransferFn,precedence=0.96,doc="""
        Function(s) applied to the whole, original image array (before any cropping).""")

    # CB: I guess it's a type rather than an instance because of the
    # way PatternSampler is written (requiring values of many
    # parameters on initialization).
    pattern_sampler_type = param.Parameter(default=PatternSampler, doc="""
        The type of PatternSampler to use to resample/resize the image.""")

    cache_image = param.Boolean(default=True,doc="""
        If False, discards the image after drawing the pattern each time,
        to make it possible to use very large databases of images without
        running out of memory.""")
        

    def function(self,params):
        xdensity = params['xdensity']
        ydensity = params['ydensity']
        x        = params['pattern_x']
        y        = params['pattern_y']
        # CEBALERT: what's going on here? Where does scaling come
        # from? Why aren't params checked for size_normalization?
        size_normalization = params.get('scaling') or self.size_normalization  #params.get('scaling',self.size_normalization)

        height = params['size']
        width = params['aspect_ratio']*height

        whole_image_output_fns = params['whole_image_output_fns']

        if self._get_image(params) or whole_image_output_fns != self.last_wiofs:
            self.last_wiofs = whole_image_output_fns

            self.ps=self.pattern_sampler_type(image=self._image,
                                              whole_pattern_output_fns=whole_image_output_fns,
                                              background_value_fn=edge_average)
            
        result = self.ps(x,y,float(xdensity),float(ydensity),float(width),float(height),scaling=size_normalization)

        if not self.cache_image:
            del self.ps     ; self.ps=None
            del self._image ; self._image=None

        return result


    def _get_image(self,params):
        """
        Get a new image, if necessary.

        If necessary as indicated by the parameters, get a new image,
        assign it to self._image and return True.  If no new image is
        needed, return False.
        """
        
        raise NotImplementedError


    ### support pickling of PIL.Image

    # CEBALERT: almost identical code to that in topo.plotting.bitmap.Bitmap...
    # CEB: by converting to string and back, we probably incur some speed
    # penalty on copy()ing GenericImages (since __getstate__ and __setstate__ are
    # used for copying, unless __copy__ and __deepcopy__ are defined instead).
    def __getstate__(self):
        """
        Return the object's state (as in the superclass), but replace
        the '_image' attribute's Image with a string representation.
        """
        state = super(GenericImage,self).__getstate__()

        if '_image' in state and state['_image'] is not None:
            import StringIO
            f = StringIO.StringIO()
            image = state['_image']
            image.save(f,format=image.format or 'TIFF') # format could be None (we should probably just not save in that case)
            state['_image'] = f.getvalue()
            f.close()

        return state

    def __setstate__(self,state):
        """
        Load the object's state (as in the superclass), but replace
        the '_image' string with an actual Image object.
        """
        # CEBALERT: Need to figure out how state['_image'] could ever
        # actually be None; apparently it is sometimes (see SF
        # #2276819).
        if '_image' in state and state['_image'] is not None:
            import StringIO
            state['_image'] = PIL.open(StringIO.StringIO(state['_image']))
        super(GenericImage,self).__setstate__(state)



class FileImage(GenericImage):
    """
    2D Image generator that reads the image from a file.
    
    The image at the supplied filename is converted to grayscale if it
    is not already a grayscale image. See PIL's Image class for
    details of supported image file formats.
    """

    filename = Filename(default='images/ellen_arthur.pgm',precedence=0.9,doc="""
        File path (can be relative to Topographica's base path) to a bitmap image.
        The image can be in any format accepted by PIL, e.g. PNG, JPG, TIFF, or PGM.
        """)


    def __init__(self, **params):
        """
        Create the last_filename and last_wiof attributes, used to hold
        the last filename and last whole_image_output_function.

        This allows reloading an existing image to be avoided.
        """
        super(FileImage,self).__init__(**params)
        self.last_filename = None
        self.last_wiofs = None


    def _get_image(self,params):
        filename = params['filename']

        if filename!=self.last_filename or self._image is None:
            self.last_filename=filename
            self._image = ImageOps.grayscale(PIL.open(self.filename))
            return True
        else:
            return False

# PICKLEHACK (move to legacy)
# Temporary as of 12/2007, for backwards compatibility
Image=FileImage


