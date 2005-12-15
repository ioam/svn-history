"""
Topographica Bitmap Class

Encapsulates the PIL Image class so that an input matrix can be displayed
as a bitmap image without needing to know about PIL proper.

There are three different base image Classes which inherit Bitmap:

ColorMap  - 1 2D Matrix, 1 1D Color Map
BWMap     - 1 2D Matrix.  Defaults to a Luminance palette.
HSVMap    - 3 2D Matrices, Color (H), Confidence (S), Strength (V)
RGBMap    - 3 2D Matrices, Red, Green, Blue Channels.

All maps are assumed to be normalized to 1.  Matrices are passed in as
part of the constructor and the image is generaed.

The encapsulated PIL Image is accessible through the .bitmap attribute.

---
Creating new Bitmaps:

bitmap1 = ColorMap(inArray,palette)
    inArray: 2D Array
    palette: 768 integers (3x256 of RGB ranged 0-255).

bitmap3 = RGBMap(rMapArray,gMapArray,bMapArray)
    Three matrices that are combined into one image, where each matrix
    represents a different color channel.
    3 matrices expected, each should have been normalized to 1.

bitmap4 = HSVMap(hMapArray,sMapArray,vMapArray)
    HSV Map inputs, converts to RGB image.
    3 matrices expected, each should have been normalized to 1.

The constructed Image is then in [BitmapObject].bitmap.

$Id$
"""
__version__='$Revision$'

### JABHACKALERT!
### 
### The code in this file has not yet been reviewed, and may need
### substantial changes.

from colorsys import hsv_to_rgb
import Numeric, Image, math
from Numeric import Float
from topo.base.parameter import Parameter
import topo.base.topoobject
import MLab

# Background type.  Decides to fill dead areas with 0s or with 1s
BLACK_BACKGROUND = 0
WHITE_BACKGROUND = 1
MONITOR_BASED_PLOTS = BLACK_BACKGROUND
PAPER_BASED_PLOTS = WHITE_BACKGROUND

class Bitmap(topo.base.topoobject.TopoObject):
    """
    Wrapper class for the PIL Image class.  Only slightly hides PILs extra
    functionality since the encapsulated Image (self.bitmap) can be accessed
    if desired.
    """
    normalize = Parameter(default=0)
    
    def __init__(self,newMap):
        self.bitmap = newMap
        self.view_info = {}


    def copy(self):
        """
        Return a copy of the encapsulated image so the original is
        preserved.
        """
        return self.bitmap.copy()
    

    def show(self):
        """
        Renaming of Image.show() for the Bitmap.bitmap attribute.
        """
        self.bitmap.show()

    def width(self): return self.bitmap.size[0]
    def height(self): return self.bitmap.size[1]

    def zoom(self, factor):
        """
        Return a resized Image object, given the input 'factor'
        parameter.  1.0 is the same size, 2.0 is doubling the height
        and width, 0.5 is 1/2 the original size.  The original Image
        is not changed.
        """
        x,y = self.bitmap.size
        zx, zy = x*factor, y*factor
        return self.bitmap.resize((zx,zy))

    def arrayToImage(self, inArray):
        """
        Take in a normalized 2D array, return a one-channel luminosity image.
        """
        if max(inArray.flat) > 1:
            self.warning('arrayToImage inputs > 1. Normalizing.  Max value: ', max(inArray.flat))
            inArray = Numeric.divide(inArray,max(inArray.flat))
        if not max(inArray.flat) <= 1:
            self.warning('arrayToImage failed to Normalize.  Possible NaN.  Using blank matrix.')
            shape = inArray.shape
            inArray = Numeric.zeros(shape)
            
            
        # PIL 'L' Images use 0 to 255.  Have to scale up.
        inArray = (Numeric.floor(inArray * 255)).astype(Numeric.Int)
        r,c = inArray.shape
        # size is (width,height)
        newImage = Image.new('L',(c,r),None)
        newImage.putdata(inArray.flat)
        return newImage
        

        
class ColorMap(Bitmap):
    """
    Inputs:
    1 2D Array, and a palette of 768 integers (3x256 of RGB ranged 0-255).
    """

    def __init__(self,inArray,palette=None):
        """
        inArray should be normalized so all values are between 0 and 1
        Palette can be any color scale depending on the type of ColorMap
        desired.
        [0,0,0 ... 255,255,255] = Grayscale
        [0,0,0 ... 255,0,0] = Grayscale but through a Red filter.

        If palette is not passed as parameter, Grayscale is default.
        """
        if max(inArray.flat) > 1.0:
            self.warning('ColorMap inArray > 1.  Normalizing')
            inArray = Numeric.divide(inArray,max(inArray.flat))

        newImage = self.arrayToImage(inArray)
        if palette == None:
            palette = [i for i in range(256) for j in range(3)]
        newImage.putpalette(palette)
        newImage = newImage.convert('P')
        super(ColorMap,self).__init__(newImage)



class HSVMap(Bitmap):
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
        newImage = Image.new('RGB',hMapArray.shape,None)
        hFlat = hMapArray.flat
        sFlat = sMapArray.flat
        vFlat = vMapArray.flat

        ## This code should never be seen.  It means that calling code did
        ## not take the precaution of clipping the input matrices.
        if max(hFlat) > 1 or max(sFlat) > 1 or max(vFlat) > 1:
            topo.base.topoobject.TopoObject().warning('HSVMap inputs exceed 1. Clipping to 1.0')
            if max(hFlat) > 0: hFlat = MLab.clip(hFlat,0.0,1.0)
            if max(sFlat) > 0: sFlat = MLab.clip(sFlat,0.0,1.0)
            if max(vFlat) > 0: vFlat = MLab.clip(vFlat,0.0,1.0)

        # List comprehensions not used for speed.
        buffer = []
        for i in range(len(hFlat)):
            (r, g, b) = hsv_to_rgb(hFlat[i],sFlat[i],vFlat[i])
            pixel = (int(math.floor(r * 255)),
                     int(math.floor(g * 255)),
                     int(math.floor(b * 255)))
            buffer.append(pixel)

        newImage.putdata(buffer)
        super(HSVMap,self).__init__(newImage)



class RGBMap(Bitmap):
    """
    Three matrices that are combined into one image, where each matrix
    represents a different color channel.
    """

    def __init__(self,rMapArray,gMapArray,bMapArray):
        """
        Each matrix must be the same size and normalized to 1.
        """
        if max(rMapArray.flat) > 1.0:
            self.warning('RGBMap rMapArray not normalized to 1.  Normalizing.  Max:' + str(max(rMapArray.flat)))
            rMapArray = Numeric.divide(rMapArray,max(rMapArray.flat))
        if max(gMapArray.flat) > 1.0:
            self.warning('RGBMap gMapArray not normalized to 1.  Normalizing.  Max:' + str(max(gMapArray.flat)))
            gMapArray = Numeric.divide(gMapArray,max(gMapArray.flat))
        if max(bMapArray.flat) > 1.0:
            self.warning('RGBMap bMapArray not normalized to 1.  Normalizing.  Max:' + str(max(bMapArray.flat)))
            bMapArray = Numeric.divide(bMapArray,max(bMapArray.flat))

        ## This code should never be seen.  It means that calling code did
        ## not take the precaution of clipping the input matrices.
        if max(rMapArray.flat) > 1 or max(gMapArray.flat) > 1 or max(bMapArray.flat) > 1:
            topo.base.topoobject.TopoObject().warning('RGBMap inputs exceed 1. Clipping to 1.0')
            rMapArray = MLab.clip(rMapArray,0.0,1.0)
            gMapArray = MLab.clip(gMapArray,0.0,1.0)
            bMapArray = MLab.clip(bMapArray,0.0,1.0)

        rImage = self.arrayToImage(rMapArray)
        gImage = self.arrayToImage(gMapArray)
        bImage = self.arrayToImage(bMapArray)

        super(RGBMap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))
