"""
Topographica Bitmap Class

Encapsulates the PIL Image class so that an input matrix can be displayed
as a bitmap image.

There are three different base image Classes which inherit Bitmap:

ColorMap  - 1 2D Matrix, 1 1D Color Map
HSVMap    - 3 2D Matrices, Color (H), Confidence (S), Strength (V)
RGBMap    - 3 2D Matrices, Red, Green, Blue Channels.

All maps are assumed to be normalized to 1.  Matrices are passed in as
part of the constructor and the image is generaed.

The encapsulated Image is accessible through the .bitmap attribute if you're
too lazy to extend the base Bitmap object.
"""

from colorsys import rgb_to_hsv, hsv_to_rgb
import Numeric, Image, math


class Bitmap(object):
    """
    Wrapper class for the PIL Image class.  Only slightly hides PILs extra
    functionality since the encapsulated Image (self.bitmap) can be accessed
    if desired.
    """
    
    def __init__(self,newMap):
        self.bitmap = newMap


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


    def arrayToImage(self, inArray):
        """
        Take in a normalized 2D array, return a one-channel luminosity image.
        """
        if max(inArray) > 1:
            print 'Warning: arrayToImage inputs not normalized. Dividing by 255'
            inArray = inArray / 255.0

        # PIL 'L' Images use 0 to 255.  Have to scale up.
        inArray = (Numeric.floor(inArray * 255)).astype(Numeric.Int)
        newImage = Image.new('L',inArray.shape,None)
        newImage.putdata(inArray.flat)
        return newImage
        

        
class ColorMap(Bitmap):
    """
    Inputs:
    1 2D Array, and a palette of 768 integers (3x256 of RGB ranged 0-255).
    """

    def __init__(self,inArray,palette=None):
        """
        Palette can be any color scale depending on the type of ColorMap
        desired.
        [0,0,0 ... 255,255,255] = Grayscale
        [0,0,0 ... 255,0,0] = Grayscale but through a Red filter.

        If palette is not passed as parameter, Grayscale is default.
        """
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

        # Equivalent to the above commented code, but this uses
        # list comprehensions instead.  Slower than the for loop.
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
        rImage = self.arrayToImage(rMapArray)
        gImage = self.arrayToImage(gMapArray)
        bImage = self.arrayToImage(bMapArray)

        super(RGBMap,self).__init__(Image.merge('RGB',(rImage,gImage,bImage)))



if __name__ == '__main__':
    print 'Test Module'
    miata = Image.open('miata.jpg')
    miata = miata.resize((miata.size[0]/2,miata.size[1]/2))
    rIm, gIm, bIm = miata.split()
    rseq, gseq, bseq = rIm.getdata(), gIm.getdata(), bIm.getdata()
    rar,gar,bar = Numeric.array(rseq),Numeric.array(gseq),Numeric.array(bseq)
    ra = Numeric.reshape(rar,miata.size) / 255.0
    ga = Numeric.reshape(gar,miata.size) / 255.0
    ba = Numeric.reshape(bar,miata.size) / 255.0

    # Test RGBMap
    rgb = RGBMap(ra,ga,ba)
    rgb.show()

    # Test ColorMap
    p = [j and i for i in range(256) for j in (1,0,0)]
    cmap = ColorMap(ra,p)
    cmap.show()

    # Test HSVMap
    a = [j for i in range(256) for j in range(256)]
    b = [i for i in range(256) for j in range(256)]
    c = [max(i,j) for i in range(256) for j in range(256)]
    a = Numeric.reshape(a,(256,256)) / 255.0
    b = Numeric.reshape(b,(256,256)) / 255.0
    c = Numeric.reshape(c,(256,256)) / 255.0
    hsv = HSVMap(a,b,c)
    hsv.show()
    #cmap = ColorMap(c)
    #cmap.show()

    # Test BWMap
    bwmap = BWMap(ra)
    bwmap.show()
