"""
Unit tests for bitmap.py

Constructs a few bitmap objects but does not display them or compare them
to a base image.  Primary purpose of testing is to verify that the interface
to the PIL imaging library does all the expected operations such as loading
jpg.

Should be extended as more functionality is added to the Bitmap
classes.

$Id$
"""
import topo
from topo.bitmap import *
import Image, Numeric
import unittest

class TestBitmap(unittest.TestCase):


    def setUp(self):
        """
        Uses testbitmap.jpg in the topographica/tests directory
        """
        miata = Image.open('tests/testbitmap.jpg')
        miata = miata.resize((miata.size[0]/2,miata.size[1]/2))
        self.rIm, self.gIm, self.bIm = miata.split()
        self.rseq = self.rIm.getdata()
        self.gseq = self.gIm.getdata()
        self.bseq = self.bIm.getdata()
        self.rar = Numeric.array(self.rseq)
        self.gar = Numeric.array(self.gseq)
        self.bar = Numeric.array(self.bseq)
        self.ra = Numeric.reshape(self.rar,miata.size) / 255.0
        self.ga = Numeric.reshape(self.gar,miata.size) / 255.0
        self.ba = Numeric.reshape(self.bar,miata.size) / 255.0


    def test_ColorMap(self):
        p = [j and i for i in range(256) for j in (1,0,0)]
        cmap = ColorMap(self.ra,p)
        # cmap.show()


    def test_BWMap(self):
        bwmap = BWMap(self.ra)
        # bwmap.show()

    
    def test_HSVMap(self):
        a = [j for i in range(256) for j in range(256)]
        b = [i for i in range(256) for j in range(256)]
        c = [max(i,j) for i in range(256) for j in range(256)]
        a = Numeric.reshape(a,(256,256)) / 255.0
        b = Numeric.reshape(b,(256,256)) / 255.0
        c = Numeric.reshape(c,(256,256)) / 255.0
        hsv = HSVMap(a,b,c)
        # hsv.show()


    def test_RGBMap(self):
        rgb = RGBMap(self.ra,self.ga,self.ba)
        # rgb.show()


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestBitmap))
