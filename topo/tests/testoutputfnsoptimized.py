"""

$Id$
"""
__version__='$Revision$'


import unittest

from Numeric import array, Float32

from topo.outputfns.optimized import DivisiveNormalizeL1_opt



class TestDivisiveNormalizeL1_opt1(unittest.TestCase):
    
    def setUp(self):

        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]]).astype(Float32)

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]]).astype(Float32)

        self.fn1 = DivisiveNormalizeL1_opt()
        self.fn2 = DivisiveNormalizeL1_opt(norm_value=4.0)
               
    def test_divisive_sum_normalize(self):
        # Test as a procedure

        fn1_a1 = self.a1/3.0

        fn1_a2 = self.a2/27.0

        fn2_a1 = (self.a1/3.0)*4.0

        fn2_a2 = (self.a2/27.0)*4.0


        self.fn1(self.a1)
        for item1,item2 in zip(self.a1.flat,fn1_a1.flat):
            self.assertAlmostEqual(item1, item2)

        self.fn1(self.a2)
        for item1,item2 in zip(self.a2.flat,fn1_a2.flat):
            self.assertAlmostEqual(item1, item2)
            
        self.a1 = array([[0.3,0.6,0.7],
                        [0.8,0.4,0.2]]).astype(Float32)

        self.a2 = array([[1.0,-1.0,7.0],
                        [4.0,3.0,11.0]]).astype(Float32)
            
        self.fn2(self.a1)
        # Numeric does the sum with Float32s; the comparison
        # value comes from Python doing the sum (in Float64s)
        # so we round to 6 d.p.
        for item1,item2 in zip(self.a1.flat,fn2_a1.flat):
            self.assertAlmostEqual(item1, item2, 6)

        self.fn2(self.a2)
        for item1,item2 in zip(self.a2.flat,fn2_a2.flat):
            self.assertAlmostEqual(item1, item2)



cases = [TestDivisiveNormalizeL1_opt1]

suite = unittest.TestSuite()
suite.addTests(unittest.makeSuite(case) for case in cases)
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)
    


        
