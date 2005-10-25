"""
Tests of featuremap.py

$Id$
"""

"""
TestFeatureMap

$Id$

"""

# CEB:
# This file is still being written

# To do:
# 


import unittest


from topo.outputfns.basic import PiecewiseLinear, DivisiveL1Normalize
from topo.outputfns.basic import DivisiveL2Normalize, DivisiveMaxNormalize
from topo.outputfns.basic import DivisiveLpNormalize

from Numeric import array
from math import sqrt


class TestPiecewiseLinear(unittest.TestCase):

    def setUp(self):

        self.a1 = array([[0.5,-1.0,0.99],
                        [1.001,-0.001,0.6]])

        self.a2 = array([[1,-1,7],
                        [4,3,11]])

        self.fn1 = PiecewiseLinear()
        print self.fn1
        self.fn2 = PiecewiseLinear(lower_bound = 0.1,upper_bound = 0.5)    
        self.fn3 = PiecewiseLinear(lower_bound = 0, upper_bound = 10)
        
    def test_piecewiselinear(self):

        fn1_a1 = array([[0.5,0.0,0.99],
                       [1.0,0.0,0.6]])

        fn2_a1 = array([[1.0, 0.0, 1.0],
                       [1.0,0.0, 1.0]])

        fn3_a2 = array([[0.1,0.0,0.7],
                       [0.4,0.3,1.0]])

        for item1,item2 in zip(self.fn1.__call__(self.a1).flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a1).flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn3.__call__(self.a2).flat,fn3_a2.flat):
            self.assertAlmostEqual(item1, item2)
 
            
## REMENBER: eventually, change the name of this function to DivisiveNormalizeSum     
class TestDivisiveL1Normalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]])

        self.fn1 = DivisiveL1Normalize()
        self.fn2 = DivisiveL1Normalize(norm_value=4.0)
               
    def test_divisive_l1_normalize(self):

        fn1_a1 = self.a1/3.0

        fn1_a2 = self.a2/25.0

        fn2_a1 = (self.a1/3.0)*4.0

        fn2_a2 = (self.a2/25.0)*4.0

        for item1,item2 in zip(self.fn1.__call__(self.a1).flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1.__call__(self.a2).flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a1).flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a2).flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)    

## REMENBER: eventually, change the name of this function to DivisiveNormalizeLentgh (..?)     
class TestDivisiveL2Normalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,11.0],
                         [2.0,5.0,9.0]])

        self.fn1 = DivisiveL2Normalize()        
        self.fn2 = DivisiveL2Normalize(norm_value=4.0)
               
    def test_divisive_l2_normalize(self):

        eucl_norm_a1 = sqrt(0.3**2+0.6**2+0.7**2+0.8**2+0.4**2+0.2**2)
        # eucl_norm_a2 = sqrt(307)
        
        fn1_a1 = self.a1/eucl_norm_a1
        fn1_a2 = self.a2/sqrt(307)
        fn2_a1 = (self.a1/eucl_norm_a1)*4.0
        fn2_a2 = (self.a2/sqrt(307))*4.0

        for item1,item2 in zip(self.fn1.__call__(self.a1).flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1.__call__(self.a2).flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a1).flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a2).flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)
            
class TestDivisiveMaxNormalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])

        self.fn1 = DivisiveMaxNormalize()        
        self.fn2 = DivisiveMaxNormalize(norm_value=3.0)
               
    def test_divisive_max_normalize(self):
        
        fn1_a1 = self.a1/0.8
        fn1_a2 = self.a2/11.0
        print fn1_a2
        fn2_a1 = (self.a1/0.8)*3.0
        fn2_a2 = (self.a2/11.0)*3.0

        for item1,item2 in zip(self.fn1.__call__(self.a1).flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1.__call__(self.a2).flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a1).flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a2).flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)

class TestDivisiveLpNormalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])

        # The default value of p is 2, so in this case, same as L2
        self.fn1 = DivisiveLpNormalize()        
        self.fn2 = DivisiveLpNormalize(p=3.0)
        self.fn3 = DivisiveLpNormalize(p=4.0,norm_value=2.0)
        
    def test_divisive_lp_normalize(self):
        eucl_norm_a1 = sqrt(0.3**2+0.6**2+0.7**2+0.8**2+0.4**2+0.2**2)

        fn1_a1 = self.a1/eucl_norm_a1
        fn1_a2 = self.a2/sqrt(307)

        l3norm_a1 = pow(0.3**3+0.6**3+0.7**3+0.8**3+0.4**3+0.2**3,1.0/3.0)
        l3norm_a2 = pow(2.0+7.0**3+4.0**3+3.0**3+11.0**3+2.0**3+5.0**3+9.0**3,1.0/3.0)
        fn2_a1 = self.a1/l3norm_a1
        fn2_a2 = self.a2/l3norm_a2

        for item1,item2 in zip(self.fn1.__call__(self.a1).flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1.__call__(self.a2).flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a1).flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2.__call__(self.a2).flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)  

        l4norm_a1 = pow(0.3**4+0.6**4+0.7**4+0.8**4+0.4**4+0.2**4,1.0/4.0)
        l4norm_a2 = pow(2.0+7.0**4+4.0**4+3.0**4+11.0**4+2.0**4+5.0**4+9.0**4,1.0/4.0)
        fn3_a1 = self.a1/l4norm_a1
        fn3_a2 = self.a2/l4norm_a2

        for item1,item2 in zip(self.fn3.__call__(self.a1).flat,fn3_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn3.__call__(self.a2).flat,fn3_a2.flat):
            self.assertAlmostEqual(item1, item2)  




cases = [TestPiecewiseLinear,
         TestDivisiveL1Normalize,
         TestDivisiveL2Normalize,
         TestDivisiveMaxNormalize,
         TestDivisiveLpNormalize]

suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(case) for case in cases)
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)


        
