"""
Tests of featuremap.py

$Id$
"""

# CEB:
# This file is still being written

# To do:
# 


import unittest

from topo.base.featuremap import FeatureMap


from topo.base.utils import arg
from math import pi
from Numeric import array, exp
from topo.base.sheet import Sheet
from topo.base.boundingregion import BoundingBox

class TestFeatureMap(unittest.TestCase):

    def setUp(self):

        # sheet to test. As it is, its activity matrix dimension is (3,2) 
        test_sheet = Sheet(density= 1, bounds= BoundingBox(points=((-1,-2),(1,1))))

        # simple activity arrays use to update the feature maps
        self.a1 = array([[1,1], [1,1], [1,1]])
        self.a2 = array([[0,1], [0,1], [0,1]])
        
        # object to test for non-cyclic distributions
        self.fm1 = FeatureMap(sheet=test_sheet, axis_range=(0.0,1.0), cyclic=False)
        self.fm1.update(self.a1,0.5)

        # object to for cyclic distributions
        self.fm2 = FeatureMap(sheet=test_sheet, axis_range=(0.0,1.0), cyclic=True)
        self.fm2.update(self.a1,0.5)


    # need to add a test_update()    


    def test_map(self):
        
        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.5)
                self.assertAlmostEqual(self.fm2.preference()[i,j], 0.5)


             
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.6)
                self.assertAlmostEqual(self.fm2.preference()[i,j],
                                       1.0+(arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j)))/(2*pi)) 
                                       # CEB: 
                                       # added 1.0 because arg returns principal value (change here)

        
        # To test the keep_peak=True 
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm1.preference()[i,j], 0.6)
                self.assertAlmostEqual(self.fm2.preference()[i,j],
                                       1.0+(arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi)))
                                       # CEB: 
                                       # added 1.0 because arg returns principal value (change here)

        
        self.fm1.update(self.a2,0.9)
        self.fm2.update(self.a2,0.9)

        for i in range(3):
            self.assertAlmostEqual(self.fm1.preference()[i,0], 0.6)
            self.assertAlmostEqual(self.fm1.preference()[i,1], 0.7)
            self.assertAlmostEqual(self.fm2.preference()[i,0],
                                   1.0+(arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi)))
            self.assertAlmostEqual(self.fm2.preference()[i,1],
                                   1.0+(arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j)+exp(0.9*2*pi*1j))/(2*pi)))
          
         
        # need to add the test........def test_selectivity



suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(TestFeatureMap))
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)


        

        
        

                
        

   
