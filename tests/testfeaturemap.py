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

class TestFeatureMap(unittest.TestCase):

    def setUp(self):

        self.a1 = array([[1,1], [1,1], [1,1]])
        
        # object to test for non-cyclic, non-keep_peak distributions
        
        self.fm0 = FeatureMap((0.0,1.0), False, False, (3,2) )
        self.fm0.update(self.a1,0.5)

        # object to test for non-cyclic, keep_peak distributions
        
        self.fm1 = FeatureMap((0.0,1.0), False, True, (3,2) )
        self.fm1.update(self.a1,0.5)

        # object to for cyclic, non-keep_peak distributions
        
        self.fm2 = FeatureMap((0.0,1.0), True, False, (3,2) )
        self.fm2.update(self.a1,0.5)

        # object to for cyclic, keep_peak distributions

        self.fm3 = FeatureMap((0.0,1.0), True, True, (3,2) )
        self.fm3.update(self.a1,0.5)




    # add a test_update()    


    def test_map(self):
        
        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm0.map()[i,j], 0.5)
                self.assertAlmostEqual(self.fm1.map()[i,j], 0.5)
                self.assertAlmostEqual(self.fm2.map()[i,j], 0.5)
                self.assertAlmostEqual(self.fm3.map()[i,j], 0.5)


             
        self.fm0.update(self.a1,0.7)
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)
        self.fm3.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm0.map()[i,j], 0.6)
                self.assertAlmostEqual(self.fm1.map()[i,j], 0.6)
                self.assertAlmostEqual(self.fm2.map()[i,j], (arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j)))/(2*pi)) 
                self.assertAlmostEqual(self.fm3.map()[i,j], (arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j)))/(2*pi))

       
        self.fm0.update(self.a1,0.7)
        self.fm1.update(self.a1,0.7)
        self.fm2.update(self.a1,0.7)
        self.fm3.update(self.a1,0.7)

        for i in range(3):
            for j in range(2):
                self.assertAlmostEqual(self.fm0.map()[i,j], (0.5+2*0.7)/3)
                self.assertAlmostEqual(self.fm1.map()[i,j], 0.6)
                self.assertAlmostEqual(self.fm2.map()[i,j], (arg(2*exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi)))
                self.assertAlmostEqual(self.fm3.map()[i,j], (arg(exp(0.7*2*pi*1j)+exp(0.5*2*pi*1j))/(2*pi)))

                
        self.a2 = array([[2,2], [2,2], [2,2]])

        
        self.fm0.update(self.a2,0.7)
        self.fm1.update(self.a2,0.7)
        self.fm2.update(self.a2,0.7)
        self.fm3.update(self.a2,0.7)

        # add the test........def test_selectivity



cases = [TestFeatureMap]

suite = unittest.TestSuite()

suite.addTests([unittest.makeSuite(case) for case in cases])
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)


        

        
        

                
        

   
