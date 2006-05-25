"""
TestFeatureMap

$Id$

"""
__version__='$Revision$'


# To do:
# - Remove the commented line from when it was calling a function 
# - finish to transform the call to be to a procedure in the last test
# - Also clean up the original file to this purpose


import unittest


from topo.outputfns.basic import PiecewiseLinear, DivisiveSumNormalize
from topo.outputfns.basic import DivisiveNormalizeL2, DivisiveMaxNormalize
from topo.outputfns.basic import DivisiveNormalizeLp

from Numeric import array
from math import sqrt

### JCALERT! In the original outputfns/basic.py files, the return x line at the end has been kept
### to avoid changing all the call to outputfns in others topographica module
### This is why in the test, both way of calling the outputfns has been tested:
### as a procedure and as a function
### Note: that it does not work for the DivisiveNormalizeLp for reasons not yet clarified;
### (cf outputfns/basic.py, corresponding  JCALERT!)
### Therefore the test for this function has to be eventually re-written when the problem is solved


class TestPiecewiseLinear(unittest.TestCase):

    def setUp(self):

        self.a1 = array([[0.5,-1.0,0.99],
                        [1.001,-0.001,0.6]])

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]])

        self.fn1 = PiecewiseLinear()
        self.fn2 = PiecewiseLinear(lower_bound = 0.1,upper_bound = 0.5)    
        self.fn3 = PiecewiseLinear(lower_bound = 0, upper_bound = 10.0)
        
    def test_piecewiselinear(self):
        # Test as a procedure

        fn1_a1 = array([[0.5,0.0,0.99],
                       [1.0,0.0,0.6]])

        fn2_a1 = array([[1.0, 0.0, 1.0],
                       [1.0,0.0, 1.0]])

        fn3_a2 = array([[0.1,0.0,0.7],
                       [0.4,0.3,1.0]])


        self.fn1(self.a1)
        for item1,item2 in zip(self.a1.flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.a1 = array([[0.5,-1.0,0.99],
                        [1.001,-0.001,0.6]])
        self.fn2(self.a1)
        for item1,item2 in zip(self.a1.flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)

            
        self.fn3(self.a2)
        for item1,item2 in zip(self.a2.flat,fn3_a2.flat):
            self.assertAlmostEqual(item1, item2)
        
        # Test as a function:

        self.a1 = array([[0.5,-1.0,0.99],
                        [1.001,-0.001,0.6]])

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]])

        for item1,item2 in zip(self.fn1(self.a1).flat,fn1_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a1).flat,fn2_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn3(self.a2).flat,fn3_a2.flat):
           self.assertAlmostEqual(item1, item2)
 
            
class TestDivisiveSumNormalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]])

        self.fn1 = DivisiveSumNormalize()
        self.fn2 = DivisiveSumNormalize(norm_value=4.0)
               
    def test_divisive_sum_normalize(self):
        # Test as a procedure

        fn1_a1 = self.a1/3.0

        fn1_a2 = self.a2/25.0

        fn2_a1 = (self.a1/3.0)*4.0

        fn2_a2 = (self.a2/25.0)*4.0


        self.fn1(self.a1)
        for item1,item2 in zip(self.a1.flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn1(self.a2)
        for item1,item2 in zip(self.a2.flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
            
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]])
            
        self.fn2(self.a1)
        for item1,item2 in zip(self.a1.flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn2(self.a2)
        for item1,item2 in zip(self.a2.flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)


        # Test as a function:
        
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]])

        for item1,item2 in zip(self.fn1(self.a1).flat,fn1_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1(self.a2).flat,fn1_a2.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a1).flat,fn2_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a2).flat,fn2_a2.flat):
           self.assertAlmostEqual(item1, item2)    

class TestDivisiveLengthNormalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,11.0],
                         [2.0,5.0,9.0]])

        self.fn1 = DivisiveNormalizeL2()        
        self.fn2 = DivisiveNormalizeL2(norm_value=4.0)
               
    def test_divisive_length_normalize(self):
        # Test as a procedure
        
        eucl_norm_a1 = sqrt(0.3**2+0.6**2+0.7**2+0.8**2+0.4**2+0.2**2)
        # eucl_norm_a2 = sqrt(307)
        
        fn1_a1 = self.a1/eucl_norm_a1
        fn1_a2 = self.a2/sqrt(307)
        fn2_a1 = (self.a1/eucl_norm_a1)*4.0
        fn2_a2 = (self.a2/sqrt(307))*4.0


        self.fn1(self.a1)
        for item1,item2 in zip(self.a1.flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn1(self.a2)
        for item1,item2 in zip(self.a2.flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
            
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,11.0],
                         [2.0,5.0,9.0]])

            
        self.fn2(self.a1)
        for item1,item2 in zip(self.a1.flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn2(self.a2)
        for item1,item2 in zip(self.a2.flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)
            

        # Test as a function:

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,11.0],
                         [2.0,5.0,9.0]])


        for item1,item2 in zip(self.fn1(self.a1).flat,fn1_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1(self.a2).flat,fn1_a2.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a1).flat,fn2_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a2).flat,fn2_a2.flat):
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
        # Test as a procedure:
        
        fn1_a1 = self.a1/0.8
        fn1_a2 = self.a2/11.0
        fn2_a1 = (self.a1/0.8)*3.0
        fn2_a2 = (self.a2/11.0)*3.0


        self.fn1(self.a1)
        for item1,item2 in zip(self.a1.flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn1(self.a2)
        for item1,item2 in zip(self.a2.flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
                    
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])
    
        self.fn2(self.a1)
        for item1,item2 in zip(self.a1.flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn2(self.a2)
        for item1,item2 in zip(self.a2.flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)


        # Test as a function:
        
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])
            
        for item1,item2 in zip(self.fn1(self.a1).flat,fn1_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1(self.a2).flat,fn1_a2.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a1).flat,fn2_a1.flat):
           self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a2).flat,fn2_a2.flat):
           self.assertAlmostEqual(item1, item2)

class TestDivisiveLpNormalize(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])

        # The default value of p is 2, so in this case, same as L2
        self.fn1 = DivisiveNormalizeLp()        
        self.fn2 = DivisiveNormalizeLp(p=3.0)
        self.fn3 = DivisiveNormalizeLp(p=4.0,norm_value=2.0)
        
    def test_divisive_lp_normalize(self):

        ### JCALERT! As already said above; this method does not work as a procedure
        ### because of a problem when using x *= factor instead of x = x * factor
        ### it is not understood why because it does work fine in all others outputfns?
        ### Therefore it is only tested as a function

        # Test as a function
        
        eucl_norm_a1 = sqrt(0.3**2+0.6**2+0.7**2+0.8**2+0.4**2+0.2**2)

        fn1_a1 = self.a1/eucl_norm_a1
        fn1_a2 = self.a2/sqrt(307)

        l3norm_a1 = pow(0.3**3+0.6**3+0.7**3+0.8**3+0.4**3+0.2**3,1.0/3.0)
        l3norm_a2 = pow(2.0+7.0**3+4.0**3+3.0**3+11.0**3+2.0**3+5.0**3+9.0**3,1.0/3.0)
        fn2_a1 = self.a1/l3norm_a1
        fn2_a2 = self.a2/l3norm_a2

        for item1,item2 in zip(self.fn1(self.a1).flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn1(self.a2).flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)

	self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])

        for item1,item2 in zip(self.fn2(self.a1).flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn2(self.a2).flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)

	self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])

        l4norm_a1 = pow(0.3**4.0+0.6**4.0+0.7**4.0+0.8**4.0+0.4**4.0+0.2**4.0,1.0/4.0)
        l4norm_a2 = pow(1.0**4.0+1.0**4.0+7.0**4.0+4.0**4.0+3.0**4.0+11.0**4.0+2.0**4.0+5.0**4.0+9.0**4.0,1.0/4.0)
        fn3_a1 = (self.a1/l4norm_a1)*2.0
        fn3_a2 = (self.a2/l4norm_a2)*2.0


        for item1,item2 in zip(self.fn3(self.a1).flat,fn3_a1.flat):
            self.assertAlmostEqual(item1, item2)
        for item1,item2 in zip(self.fn3(self.a2).flat,fn3_a2.flat):
            self.assertAlmostEqual(item1, item2)

        # Test as a procedure to be fixed!

	self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])
        

        self.fn1(self.a1)
        for item1,item2 in zip(self.a1.flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)
        self.fn1(self.a2)    
        for item1,item2 in zip(self.a2.flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
            
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])
        
        self.fn2(self.a1)
        for item1,item2 in zip(self.a1.flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2)
        self.fn2(self.a2)    
        for item1,item2 in zip(self.a2.flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)      

       
        
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]])

        self.a2 = array([[1.0,-1.0,7.0],
                         [4.0,3.0,-11.0],
                         [2.0,5.0,9.0]])

        self.fn3(self.a1)
        for item1,item2 in zip(self.a1.flat,fn3_a1.flat):
            self.assertAlmostEqual(item1, item2)
        self.fn3(self.a2)    
        for item1,item2 in zip(self.a2.flat,fn3_a2.flat):
            self.assertAlmostEqual(item1, item2)      


cases = [TestPiecewiseLinear,
         TestDivisiveSumNormalize,
         TestDivisiveLengthNormalize,
         TestDivisiveMaxNormalize,
         TestDivisiveLpNormalize]

suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(case) for case in cases)
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)
    


        
