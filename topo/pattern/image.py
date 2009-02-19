"""
PatternGenerators based on bitmap images stored in files.

$Id$
"""

# PIL Image is imported as PIL because we have our own Image PatternGenerator
import Image as PIL
import ImageOps
import numpy
import copy

from numpy.oldnumeric import array, Float, sum, ravel, ones

from .. import param
from topo.param.parameterized import ParamOverrides

from topo.base.boundingregion import BoundingBox
from topo.base.patterngenerator import PatternGenerator
from topo.base.sheetcoords import SheetCoordinateSystem
from topo.transferfn.basic import DivisiveNormalizeLinf,TransferFn
from topo.misc.filepath import Filename


# CEBALERT: Isn't it an image sampler? should at least make all
# variable and parameter names be consistent.
class PatternSampler(param.Parameterized):
    """
    When called, resamples - according to the size_normalization
    parameter - an image at the supplied (x,y) sheet coordinates.
    
    (x,y) coordinates outside the image are returned as the background
    value.
    """
    # Stores a SheetCoordinateSystem with an activity matrix
    # representing the image

    whole_pattern_output_fns = param.HookList(class_=TransferFn,default=[],doc="""
        Functions to apply to the whole image before any sampling is done.""")

    background_value_fn = param.Callable(default=None,doc="""
        Function to compute an appropriate background value. Must accept
        an array and return a scalar.""")

    size_normalization = param.Enumeration(default='original',
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
        ratio, filling the entire bounding box).
    
        'fit_longest': scale the pattern so that its longest dimension is
        made to fill the corresponding dimension on a Sheet with
        bounds=BoundingBox(radius=0.5) (maintains the original's
        aspect ratio, fitting the image into the bounding box but not
        necessarily filling it).
    
        'original': no scaling is applied; each pixel of the pattern 
        corresponds to one matrix unit of the Sheet on which the
        pattern being displayed.""")

    # CEBALERT: would have to call _set_image() whenever this
    # parameter is changed.
    # image = param.Parameter(default=None)

    def _set_image(self,image):
        # store the supplied image
        if not isinstance(image,numpy.ndarray):
            image = array(image,Float)

        rows,cols = image.shape
        self.scs = SheetCoordinateSystem(xdensity=1.0,ydensity=1.0,
                                         bounds=BoundingBox(points=((-cols/2.0,-rows/2.0),
                                                                    ( cols/2.0, rows/2.0))))
        self.scs.activity=image
        self._image_initialized=False

    def _initialize_image(self):
        # apply the whole_pattern_output_fns and set a background_value.
        for wpof in self.whole_pattern_output_fns:
            wpof(self.scs.activity)
        if not self.background_value_fn:
            self.background_value = 0.0
        else:
            self.background_value = self.background_value_fn(self.scs.activity)
        self._image_initialized=True


    def __call__(self, x, y, sheet_xdensity, sheet_ydensity, width=1.0, height=1.0, image=None, **params):
        """
        Return pixels from the supplied image at the given Sheet (x,y)
        coordinates.

        If no image is supplied, the last image that was supplied is
        used.

        If an image is supplied, the whole_image_output_fns are
        applied, a background value is calculated, and the image is
        stored for future calls. The image is assumed to be a NumPy
        array or other object that exports the NumPy buffer interface
        (i.e. can be converted to a NumPy array by passing it to
        numpy.array(), e.g. PIL.Image).

        To calculate the sample, the image is scaled according to the
        size_normalization parameter, and any supplied width and
        height. sheet_xdensity and sheet_ydensity are the xdensity and
        ydensity of the sheet on which the pattern is to be drawn.
        """
        p=ParamOverrides(self,params)
        
        if image is not None:
            self._set_image(image)

        if self._image_initialized is False:
            self._initialize_image()
                    
        # create new pattern sample, filled initially with the background value
        pattern_sample = ones(x.shape, Float)*self.background_value

        # if the height or width is zero, there's no pattern to display...
        if width==0 or height==0:
            return pattern_sample

        # scale the supplied coordinates to match the pattern being at density=1
        x=x*sheet_xdensity # deliberately don't operate in place (so as not to change supplied x & y)
        y=y*sheet_ydensity
      
        # scale according to initial pattern size_normalization selected (size_normalization)
        self.__apply_size_normalization(x,y,sheet_xdensity,sheet_ydensity,p.size_normalization)

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


    def __apply_size_normalization(self,x,y,sheet_xdensity,sheet_ydensity,size_normalization):
        pattern_rows,pattern_cols = self.scs.activity.shape

        # Instead of an if-test, could have a class of this type of
        # function (c.f. OutputFunctions, etc)...
        if size_normalization=='original':
            return
        
        elif size_normalization=='stretch_to_fit':
            x_sf,y_sf = pattern_cols/sheet_xdensity, pattern_rows/sheet_ydensity
            x*=x_sf; y*=y_sf

        elif size_normalization=='fit_shortest':
            if pattern_rows<pattern_cols:
                sf = pattern_rows/sheet_ydensity
            else:
                sf = pattern_cols/sheet_xdensity
            x*=sf;y*=sf
            
        elif size_normalization=='fit_longest':
            if pattern_rows<pattern_cols:
                sf = pattern_cols/sheet_xdensity
            else:
                sf = pattern_rows/sheet_ydensity
            x*=sf;y*=sf




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
    size_normalization or cropping but rather simply scales and crops the image
    to fit the given matrix size without distorting the aspect ratio
    of the original picture.
    """
    
    sampling_method = param.Integer(default=PIL.NEAREST,doc="""
       Python Imaging Library sampling method for resampling an image.
       Defaults to Image.NEAREST.""")


    def _set_image(self,image):
        if not isinstance(image,PIL.Image):
            self.image = PIL.new('L',image.shape)
            self.image.putdata(image.ravel())
        else:
            self.image = image


    def __call__(self, x, y, sheet_xdensity, sheet_ydensity, width=1.0, height=1.0, image=None,**params):

        if image is not None:
            self._set_image(image)

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

    At present, rotation, size_normalization, etc. just resample; it would be nice
    to support some interpolation options as well.
    """

    __abstract = True
    
    aspect_ratio  = param.Number(default=1.0,bounds=(0.0,None),
        softbounds=(0.0,2.0),precedence=0.31,doc="""
        Ratio of width to height; size*aspect_ratio gives the width.""")

    size  = param.Number(default=1.0,bounds=(0.0,None),softbounds=(0.0,2.0),
                   precedence=0.30,doc="Height of the image.")

    pattern_sampler = param.Parameter(instantiate=True,
        default=PatternSampler(background_value_fn=edge_average,
                               size_normalization='fit_shortest',
                               whole_pattern_output_fns=[DivisiveNormalizeLinf()]),doc="""
        The PatternSampler to use to resample/resize the image.""")

    cache_image = param.Boolean(default=True,doc="""
        If False, discards the image and pattern_sampler after drawing the pattern each time,
        to make it possible to use very large databases of images without
        running out of memory.""")
        
    def function(self,params):
        xdensity = params['xdensity']
        ydensity = params['ydensity']
        x        = params['pattern_x']
        y        = params['pattern_y']
        height   = params['size']
        width    = params['aspect_ratio']*height
        cache_image = params['cache_image']

        # if pattern_sampler could be lazily created, we wouldn't need this
        if params['pattern_sampler'] is None:
            self.pattern_sampler = copy.deepcopy(GenericImage.pattern_sampler)
                    
        pattern_sampler_params = {}

        if self._get_image(params): 
            pattern_sampler_params['image']=self._image
            
        result = params['pattern_sampler'](x,y,float(xdensity),float(ydensity),float(width),float(height),
                                           **pattern_sampler_params)

        if cache_image is False:
            self.pattern_sampler = self._image = None

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

    # CEBALERT: almost identical code to that in topo.plotting.bitmap.Bitmap.
    # Can we instead patch PIL? (Note that we can't use copy_reg as we do for
    # e.g. numpy ufuncs because PIL's Image is not a new-style class. So patching
    # PIL is probably the only option to handle this problem in one place.)
    
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
        Create the last_filename attribute, used to hold the last
        filename. This allows reloading an existing image to be
        avoided.
        """
        super(FileImage,self).__init__(**params)
        self.last_filename = None


    def _get_image(self,p):
        if p.filename!=self.last_filename or self._image is None:
            self.last_filename=p.filename
            self._image = ImageOps.grayscale(PIL.open(p.filename))
            return True
        else:
            return False

# PICKLEHACK (move to legacy)
# Temporary as of 12/2007, for backwards compatibility
Image=FileImage


