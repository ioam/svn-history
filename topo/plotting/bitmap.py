"""
Topographica Bitmap Class.

Encapsulates the PIL Image class so that an input matrix can be displayed
as a bitmap image without needing to know about PIL proper.

There are three different base image Classes which inherit Bitmap:

PaletteBitmap  - 1 2D Matrix, 1 1D Color Map
HSVBitmap    - 3 2D Matrices, Color (H), Confidence (S), Strength (V)
RGBBitmap    - 3 2D Matrices, Red, Green, Blue Channels.

All maps are assumed to be normalized to 1.  Matrices are passed in as
part of the constructor and the image is generaed.  For more information,
see the documentation for each of the Bitmap classes.

The encapsulated PIL Image is accessible through the .bitmap attribute.

$Id$
"""
__version__='$Revision$'


from colorsys import hsv_to_rgb

import Numeric, Image, math
from topo.base.parameterclasses import Parameter
from topo.base.parameterizedobject import ParameterizedObject

### JCALERT: To do:
###        - Update the test file.
###        - Write PaletteBitmap when the Palette class is fixed
###        - Get rid of accessing function (copy, show...) (should we really?)

class Bitmap(ParameterizedObject):
    """
    Wrapper class for the PIL Image class.

    The main purpose for this base class is to provide a consistent
    interface for defining bitmaps constructed in various different
    ways.  The resulting bitmap is a PIL Image object that can be
    accessed using the normal PIL interface.

    If subclasses use the _arrayToImage() function provided, any
    pixels larger than the maximum that can be displayed will
    be counted before they are clipped; these are stored in the
    clipped_pixels attribute.
    """
    clipped_pixels = 0
    
    def __init__(self,image):
        self.image = image


    def copy(self):
        """
        Return a copy of the encapsulated image so the original is
        preserved.
        """
        return self.image.copy()
    

    def show(self):
        """
        Renaming of Image.show() for the Bitmap.bitmap attribute.
        """
        self.image.show()

    def width(self): return self.image.size[0]
    def height(self): return self.image.size[1]

    def zoom(self, factor):
        """
        Return a resized Image object, given the input 'factor'
        parameter.  1.0 is the same size, 2.0 is doubling the height
        and width, 0.5 is 1/2 the original size.  The original Image
        is not changed.
        """
        x,y = self.image.size
        zx, zy = int(x*factor), int(y*factor)
        return self.image.resize((zx,zy))

    def _arrayToImage(self, inArray):
        """
        Generate a 1-channel PIL Image from an array of values from 0 to 1.0.

        Values larger than 1.0 are clipped, after adding them to the total
        clipped_pixels.  Returns a one-channel (monochrome) Image.
        """
        
        # PIL 'L' Images use a range of 0 to 255, so we scale the
        # input array to match.  The pixels are scaled by 255, not
        # 256, so that 1.0 maps to fully white.
        max_pixel_value=255
        inArray = (Numeric.floor(inArray * max_pixel_value)).astype(Numeric.Int)

        # Clip any values that are still larger than max_pixel_value
        to_clip = sum(Numeric.greater(inArray.flat,max_pixel_value))
	if (to_clip>0):
            self.clipped_pixels = self.clipped_pixels + to_clip
	    inArray = Numeric.clip(inArray,0,max_pixel_value)
	    self.verbose("Bitmap: clipped",to_clip,"image pixels that were out of range")

        r,c = inArray.shape
        # The size is (width,height), so we swap r and c:
        newImage = Image.new('L',(c,r),None)
        newImage.putdata(inArray.flat)
        return newImage
        

class PaletteBitmap(Bitmap):
    """
    Bitmap constructed using a single 2D array.
 
    The image is monochrome by default, but more colorful images can
    be constructed by specifying a Palette.
    """

    def __init__(self,inArray,palette=None):
        """
        inArray should have values in the range from 0.0 to 1.0.
        
        Palette can be any color scale depending on the type of ColorMap
        desired.  Examples:
        
        [0,0,0 ... 255,255,255] = grayscale
        [0,0,0 ... 255,0,0] = grayscale but through a Red filter.

        The default palette is grayscale, with 0.0 mapping to black
        and 1.0 mapping to white.
        """
        ### JABALERT: Should accept a Palette class, not a data
        ### structure, unless for some reason we want to get rid of
        ### the Palette classes and always use data structures
        ### instead.
	### JC: not yet properly implemented anyway.
        max_pixel_value=255

        newImage = self._arrayToImage(inArray)
        if palette == None:
            palette = [i for i in range(max_pixel_value+1) for j in range(3)]
        newImage.putpalette(palette)
        newImage = newImage.convert('P')
        super(PaletteBitmap,self).__init__(newImage)



class HSVBitmap(Bitmap):
    """
    Bitmap constructed from 3 2D arrays, for hue, saturation, and value.

    The hue matrix determines the pixel colors.  The saturation matrix
    determines how strongly the pixels are saturated for each hue,
    i.e. how colorful the pixels appear.  The value matrix determines
    how bright each pixel is.

    An RGB image is constructed from the HSV matrices using
    hsv_to_rgb; the resulting image is of the same type that is
    constructed by RGBBitmap, and can be used in the same way.
    """

    def __init__(self,hue,sat,val):
        """Each matrix must be the same size, with values in the range 0.0 to 1.0."""
        shape = hue.shape # Assumed same as sat.shape and val.shape
        rmat = Numeric.zeros(shape,Numeric.Float)
        gmat = Numeric.zeros(shape,Numeric.Float)
        bmat = Numeric.zeros(shape,Numeric.Float)

        # Note: should someday file a feature request for PIL for them
        # to accept an image of type 'HSV', so that they will do this
        # conversion themselves, without us needing an explicit loop
        # here.  That should speed this up.
        ch = Numeric.clip(hue,0.0,1.0)
        cs = Numeric.clip(sat,0.0,1.0)
        cv = Numeric.clip(val,0.0,1.0)
        
        for i in range(shape[0]):
            for j in range(shape[1]):
                r,g,b = hsv_to_rgb(ch[i,j],cs[i,j],cv[i,j])
                rmat[i,j] = r
                gmat[i,j] = g
                bmat[i,j] = b
        
        rImage = self._arrayToImage(rmat)
        gImage = self._arrayToImage(gmat)
        bImage = self._arrayToImage(bmat)

        super(HSVBitmap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))



class RGBBitmap(Bitmap):
    """
    Bitmap constructed from three 2D arrays, for red, green, and blue.

    Each matrix is used as the corresponding channel of an RGB image.
    """

    def __init__(self,rMapArray,gMapArray,bMapArray):
        """Each matrix must be the same size, with values in the range 0.0 to 1.0."""
        rImage = self._arrayToImage(rMapArray)
        gImage = self._arrayToImage(gMapArray)
        bImage = self._arrayToImage(bMapArray)

        super(RGBBitmap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))



	
