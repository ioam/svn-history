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

bitmap2 = BWMap(inArray)
    Calls ColorMap with the default Luminosity palette.

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

from colorsys import rgb_to_hsv, hsv_to_rgb
import Numeric, Image, math
from Numeric import Float
import topo.base
import MLab

# Background type.  Decides to fill dead areas with 0s or with 1s
BLACK_BACKGROUND = 0
WHITE_BACKGROUND = 1
MONITOR_BASED_PLOTS = BLACK_BACKGROUND
PAPER_BASED_PLOTS = WHITE_BACKGROUND


def matrix_hsv_to_rgb(hMapArray,sMapArray,vMapArray):
    """
    First matrix sets the Hue (Color).
    Second marix sets the Sauration (How much color)
    Third matrix sets the Value (How bright the pixel will be)

    The three input matrices should all be the same size, and have
    been normalized to 1.  There should be no side-effects on the
    original input matrices.
    """
    
    shape = hMapArray.shape
    rmat = Numeric.array(hMapArray,Float)
    gmat = Numeric.array(sMapArray,Float)
    bmat = Numeric.array(vMapArray,Float)

    if max(rmat.flat) > 1 or max(gmat.flat) > 1 or max(bmat.flat) > 1:
        print 'Warning: HSVMap inputs exceed 1. Clipping to 1.0'
        #print 'Old max h:', max(rmat.flat), 'max s:', max(gmat.flat), \
        #      'max v:', max(bmat.flat)
        if max(rmat.flat) > 0: rmat = MLab.clip(rmat,0.0,1.0)
        if max(gmat.flat) > 0: gmat = MLab.clip(gmat,0.0,1.0)
        if max(bmat.flat) > 0: bmat = MLab.clip(bmat,0.0,1.0)
        #print 'New max h:', max(rmat.flat), 'max s:', max(gmat.flat), 'max v:', max(bmat.flat)


    ### JABHACKALERT!
    ###
    ### The PreferenceMap panel currently prints the warning below.
    ### Dividing automatically by 255 is not appropriate, because
    ### there is no way to know what the appropriate value might be.
    ### It should be entirely legal to plot something with a range
    ### higher than 1.0.  E.g. very often we deliberately plot
    ### selectivity with the brightness turned up so high that many of
    ### the brighter pixels get cropped off, to accentuate the shape
    ### of the few remaining areas that are poorly selective.  It's 
    ### very important to have some way to warn the user of such cropping,
    ### but not ok to simply rescale everything (unless the user has 
    ### explictly turned on such autoscaling.
    ### 
    ### In any case, there must be a bug in the current code, because there's no 
    ### reason this routine should get called with values ranging 0..255 if
    ### they are intended to plot in the logical range 0..1.

    # List comprehensions were not used because it was slower.
    for j in range(shape[0]):
        for i in range(shape[1]):
            rgb = hsv_to_rgb(rmat[j,i],gmat[j,i],bmat[j,i])
            rmat[j,i] = rgb[0]
            gmat[j,i] = rgb[1]
            bmat[j,i] = rgb[2]
                
    return (rmat, gmat, bmat)
    

    


class Bitmap(object):
    """
    Wrapper class for the PIL Image class.  Only slightly hides PILs extra
    functionality since the encapsulated Image (self.bitmap) can be accessed
    if desired.
    """
    
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
            print 'Warning: arrayToImage inputs not normalized. Normalizing to 1.  Max value: ', max(inArray.flat)
            inArray = Numeric.divide(inArray,max(inArray.flat))
        assert max(inArray.flat) <= 1, 'arrayToImage failed to Normalize'
            
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
            topo.base.TopoObject().warning('ColorMap inArray not normalized to 1.  Normalizing')
            inArray = Numeric.divide(inArray,max(inArray.flat))

        newImage = self.arrayToImage(inArray)
        if palette == None:
            palette = [i for i in range(256) for j in range(3)]
        newImage.putpalette(palette)
        newImage = newImage.convert('P')
        super(ColorMap,self).__init__(newImage)



class BWMap(ColorMap):
    """
    The name has been changed to make the code more intuitive to read
    when wishing to use B/W maps.  Just calls ColorMap with the default
    palette.
    """
    def __init__(self,inArray):
        super(BWMap,self).__init__(inArray)
        

        
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
        if max(hFlat) > 1 or max(sFlat) > 1 or max(vFlat) > 1:
            print 'Warning: HSVMap inputs not normalized to 1. Dividing by 255'
            print 'Max of each channel is: ', max(hflat), max(sFlat), max(vFlat)
            hFlat = hFlat / 255.0
            sFlat = sFlat / 255.0
            vFlat = vFlat / 255.0

        buffer = []
        for i in range(len(hFlat)):
            (r, g, b) = hsv_to_rgb(hFlat[i],sFlat[i],vFlat[i])
            pixel = (int(math.floor(r * 255)),
                     int(math.floor(g * 255)),
                     int(math.floor(b * 255)))
            buffer.append(pixel)

        # Equivalent to the above code, but this uses list
        # comprehensions instead.  Slower than the for loop.
        # rgbFlat = [hsv_to_rgb(h,s,v) for h,s,v in zip(hFlat, sFlat, vFlat)]
        # buffer = [(int(math.floor(r * 255)),
        #            int(math.floor(g * 255)),
        #            int(math.floor(b * 255)))
        #           for r,g,b in rgbFlat]

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
            topo.base.TopoObject().warning('RGBMap rMapArray not normalized to 1.  Normalizing.  Max:' + str(max(rMapArray.flat)))
            rMapArray = Numeric.divide(rMapArray,max(rMapArray.flat))
        if max(max(gMapArray)) > 1.0:
            topo.base.TopoObject().warning('RGBMap gMapArray not normalized to 1.  Normalizing.  Max:' + str(max(gMapArray.flat)))
            gMapArray = Numeric.divide(gMapArray,max(gMapArray.flat))
        if max(max(bMapArray)) > 1.0:
            topo.base.TopoObject().warning('RGBMap bMapArray not normalized to 1.  Normalizing.  Max:' + str(max(bMapArray.flat)))
            bMapArray = Numeric.divide(bMapArray,max(bMapArray.flat))
        rImage = self.arrayToImage(rMapArray)
        gImage = self.arrayToImage(gMapArray)
        bImage = self.arrayToImage(bMapArray)

        super(RGBMap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))



#  All testing code has been moved to the unit testing module found at
#  topographica/tests/testbitmap.py
