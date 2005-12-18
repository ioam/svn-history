"""
Topographica Bitmap Class

Encapsulates the PIL Image class so that an input matrix can be displayed
as a bitmap image without needing to know about PIL proper.

There are three different base image Classes which inherit Bitmap:

PaletteBitmap  - 1 2D Matrix, 1 1D Color Map
HSVBitmap    - 3 2D Matrices, Color (H), Confidence (S), Strength (V)
RGBBitmap    - 3 2D Matrices, Red, Green, Blue Channels.

All maps are assumed to be normalized to 1.  Matrices are passed in as
part of the constructor and the image is generaed.

The encapsulated PIL Image is accessible through the .bitmap attribute.

---
Creating new Bitmaps:

bitmap1 = PaletteBitmap(inArray,palette)
    inArray: 2D Array
    palette: 768 integers (3x256 of RGB ranged 0-255).

bitmap3 = RGBBitmap(rMapArray,gMapArray,bMapArray)
    Three matrices that are combined into one image, where each matrix
    represents a different color channel.
    3 matrices expected, each should have been normalized to 1.

bitmap4 = HSVBitmap(hMapArray,sMapArray,vMapArray)
    HSV Map inputs, converts to RGB image.
    3 matrices expected, each should have been normalized to 1.

The constructed Image is then in [BitmapObject].bitmap.

$Id$
"""
__version__='$Revision$'


from colorsys import hsv_to_rgb

import Numeric, Image, math

from topo.base.parameter import Parameter
from topo.base.topoobject import TopoObject

### TO DO: - Update the test file.
###        - Write PaletteBitmap when the Palette class is fixed
###        - Get rid of view_info
###        - Get rid of accessing function (copy, show...), though it is not crucial.

class Bitmap(TopoObject):
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
    normalize = Parameter(default=0)
    clipped_pixels = 0
    
    def __init__(self,image):
        self.image = image

        ### JABALERT: Should presumably be deleted; seems to be an
        ### extra copy of the Plot's view_info
        self.view_info = {}


    ### JABALERT: Should presumably be deleted, if bitmap stays public.
    def copy(self):
        """
        Return a copy of the encapsulated image so the original is
        preserved.
        """
        return self.image.copy()
    

    ### JABALERT: Should presumably be deleted, if bitmap stays public.
    def show(self):
        """
        Renaming of Image.show() for the Bitmap.bitmap attribute.
        """
        self.image.show()

    ### JABALERT: Should presumably be deleted, if bitmap stays public.
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
        zx, zy = x*factor, y*factor
        return self.image.resize((zx,zy))

    def _arrayToImage(self, inArray):
        """
        Generate a 1-channel PIL Image from an array of values from 0 to 1.0.

        Values larger than 1.0 are clipped, after adding them to the total
        clipped_pixels.  Returns a one-channel (monochrome) Image.
        """
        
        # PIL 'L' Images use a range of 0 to 255, so we scale the
        # input array to match
        max_pixel_value=255
        ### JABALERT: Shouldn't this scale by max_pixel_value+1 (256), not max_pixel_value (255)?
        inArray = (Numeric.floor(inArray * max_pixel_value)).astype(Numeric.Int)

        # Clip any values that are still larger than max_pixel_value
        to_clip = sum(Numeric.greater(inArray.flat,max_pixel_value))
	if (to_clip>0):
            self.clipped_pixels = self.clipped_pixels + to_clip
	    inArray = Numeric.clip(inArray,0,max_pixel_value)
	    self.verbose("Bitmap: clipped",to_clip,"image pixels that were out of range")

        r,c = inArray.shape
        # size is (width,height), so we swap r and c:
        newImage = Image.new('L',(c,r),None)
        newImage.putdata(inArray.flat)
        return newImage
        

class PaletteBitmap(Bitmap):
    """
    A Bitmap constructed using a single 2D array.

    By default, the Image constructed will be monochrome.  More
    colorful Images can be constructed by specifying a Palette.
    """

    def __init__(self,inArray,palette=None):
        """
        inArray should have values in the range from 0 and 1.
        
        Palette can be any color scale depending on the type of ColorMap
        desired.
        [0,0,0 ... 255,255,255] = Grayscale
        [0,0,0 ... 255,0,0] = Grayscale but through a Red filter.

        If palette is not passed as parameter, Grayscale is default.
        """
        ### JABALERT: Should accept a Palette class, not a data structure,
        ### or we should get rid of the Palette classes.

        newImage = self._arrayToImage(inArray)
        if palette == None:
            palette = [i for i in range(256) for j in range(3)]
        newImage.putpalette(palette)
        newImage = newImage.convert('P')
        super(PaletteBitmap,self).__init__(newImage)



class HSVBitmap(Bitmap):
    """
    HSV Map inputs, converts to RGB image.  3 matrices expected, each should
    have been normalized to 1.
    """

    def __init__(self,hMapArray,sMapArray,vMapArray):
        """
        First matrix sets the Hue (Color).
        Second marix sets the Sauration (How much color)
        Third matrix sets the Value (How bright the pixel will be)
        """
        shape = hMapArray.shape
        rmat = Numeric.array(hMapArray,Numeric.Float)
        gmat = Numeric.array(sMapArray,Numeric.Float)
        bmat = Numeric.array(vMapArray,Numeric.Float)
        
        # List comprehensions were not used because they were slower.
        for j in range(shape[0]):
            for i in range(shape[1]):
                rgb = hsv_to_rgb(rmat[j,i],gmat[j,i],bmat[j,i])
                rmat[j,i] = rgb[0]
                gmat[j,i] = rgb[1]
                bmat[j,i] = rgb[2]
                   
        rImage = self._arrayToImage(rmat)
        gImage = self._arrayToImage(gmat)
        bImage = self._arrayToImage(bmat)

        super(HSVBitmap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))



class RGBBitmap(Bitmap):
    """A Bitmap constructed using three 2D arrays, for Red, Green, and Blue."""

    def __init__(self,rMapArray,gMapArray,bMapArray):
        """Each matrix must be the same size, with values in the range 0.0 to 1.0."""

        rImage = self._arrayToImage(rMapArray)
        gImage = self._arrayToImage(gMapArray)
        bImage = self._arrayToImage(bMapArray)

        super(RGBBitmap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))
