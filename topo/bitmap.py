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

    def __init__(self,inArray,palette):
        """
        Palette can be any color scale depending on the type of ColorMap
        desired.  [0,0,0 ... 255,255,255] = Grayscale, [0,0,0 ... 255,0,0] =
        Grayscale but through a Red filter.
        """
        newImage = self.arrayToImage(inArray)
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
    a = Numeric.reshape(Numeric.arrayrange(10000) % 256,(100,100)) / 255.0
    b = Numeric.reshape(Numeric.arrayrange(10000) % 200,(100,100)) / 255.0
    c = Numeric.reshape(Numeric.arrayrange(10000) % 100,(100,100)) / 255.0

    # Test RGBMap
    rgb = RGBMap(a,b,c)
    rgb.show()

    # Test ColorMap
    import random
    p = range(256)
    p = p + p + p
    random.shuffle(p)
    cmap = ColorMap(a,p)
    cmap.show()

    # Test HSVMap
    hsv = HSVMap(a,b,c)
    hsv.show()
    hsv = HSVMap(a,a,a)
    hsv.show()
