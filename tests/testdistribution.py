
"""
Tests of distribution.py

$Id$
"""

# CEB:
# This file is still being written

# No test for relative_selectivity(), vector_selectivity()


import unittest

from topo.base.distribution import Distribution

import copy 

# for testing the statistics
from math import pi, atan2, cos
from topo.base.utils import arg


class TestHistogram(unittest.TestCase):

    def setUp(self):
        self.h = Distribution((0.0,5.0))
        self.h.add({0:0.0})
        self.h.add({1:0.1})
        self.h.add({2:0.2})
        self.h.add({2:0.2})
        self.h.add({3:0.3})
        self.h.add({3:0.3})
        self.h.add({3:0.3})
        self.h.add({4:0.4})
        self.h.add({4:0.4})
        self.h.add({4:0.4})
        self.h.add({4:0.4})
        self.h.add({5:0.5})
        self.h.add({5:0.5})
        self.h.add({5:0.5})
        self.h.add({5:0.5})
        self.h.add({5:0.5})

        

        
        self.g = copy.deepcopy(self.h)
        self.g.add({0:0.0})
        self.g.add({1:0.1})
        self.g.add({2:0.2})
        self.g.add({3:0.3})
        self.g.add({4:0.4})
        self.g.add({5:0.5})


    def test_raise_error(self):
        self.assertRaises(ValueError, self.h.add, {6:1.0})


    def test_lissom_values(self):
        self.assertAlmostEqual(self.h.get_value(0), 0.0)
        self.assertAlmostEqual(self.h.get_value(1), 0.1)
        self.assertAlmostEqual(self.h.get_value(2), 0.4)
        self.assertAlmostEqual(self.h.get_value(3), 0.9)
        self.assertAlmostEqual(self.h.get_value(4), 1.6)
        self.assertAlmostEqual(self.h.get_value(5), 2.5)

        self.assertEqual(self.h.get_count(0), 1)
        self.assertEqual(self.h.get_count(1), 1)
        self.assertEqual(self.h.get_count(2), 2)
        self.assertEqual(self.h.get_count(3), 3)
        self.assertEqual(self.h.get_count(4), 4)
        self.assertEqual(self.h.get_count(5), 5)

        self.assertAlmostEqual(self.g.get_value(0), 0.0)
        self.assertAlmostEqual(self.g.get_value(1), 0.2)
        self.assertAlmostEqual(self.g.get_value(2), 0.6)
        self.assertAlmostEqual(self.g.get_value(3), 1.2)
        self.assertAlmostEqual(self.g.get_value(4), 2.0)
        self.assertAlmostEqual(self.g.get_value(5), 3.0)
        

    def test_lissom_mags(self):
        self.assertAlmostEqual(self.h.value_mag(0), 0.0/5.5)
        self.assertAlmostEqual(self.h.value_mag(1), 0.1/5.5)
        self.assertAlmostEqual(self.h.value_mag(2), 0.4/5.5)
        self.assertAlmostEqual(self.h.value_mag(3), 0.9/5.5)
        self.assertAlmostEqual(self.h.value_mag(4), 1.6/5.5)
        self.assertAlmostEqual(self.h.value_mag(5), 2.5/5.5)

        self.assertAlmostEqual(self.h.count_mag(0), 1.0/16)
        self.assertAlmostEqual(self.h.count_mag(1), 1.0/16)
        self.assertAlmostEqual(self.h.count_mag(2), 2.0/16)
        self.assertAlmostEqual(self.h.count_mag(3), 3.0/16)
        self.assertAlmostEqual(self.h.count_mag(4), 4.0/16)
        self.assertAlmostEqual(self.h.count_mag(5), 5.0/16)

   
    def test_lissom_statistics(self):
        self.assertEqual(self.h.num_bins(), 6)
        self.assertAlmostEqual(self.h.total_value, 5.5)
        self.assertEqual(self.h.total_count, 16)
        
        values = [value for bin,value in self.h.values()]
        self.assertAlmostEqual(max(values), 2.5)
        self.assertAlmostEqual(min(values), 0.0)
        counts = [count for bin,count in self.h.counts()]
        self.assertEqual(max(counts), 5)
        self.assertEqual(min(counts), 1)

        
        self.assertAlmostEqual(self.g.total_value, 7.0)         
        self.assertEqual(self.g.total_count, 22)
        self.assertAlmostEqual(sum([value for bin,value in self.g.values()]), 7.0)
        self.assertAlmostEqual(self.g.weighted_sum(), 28.0)
        self.assertAlmostEqual(self.g.weighted_average(), 28.0/sum([value for bin,value in self.g.values()]))
        # Different from lissom's g because this is 0 to 5 where 0 and 5 are the same
        self.assertAlmostEqual(self.g.vector_sum()[1], -0.59550095717251439) 
        self.assertAlmostEqual(self.g.vector_average(), self.g.vector_sum()[0]/self.g.num_bins()) 


        self.q = Distribution((0,4), cyclic=True)
        self.q.add({3:1})
        self.q.add({0:0, 1:0, 2:0, 4:0})                
        self.assertAlmostEqual(self.q.vector_sum()[0], 1.0)
        self.assertAlmostEqual(self.q.vector_average(), 1.0/5.0) 
        self.assertAlmostEqual(self.q.vector_sum()[1], -1.0)  # what do i do about that? (expect 3/4 but cyclic)

        # Example where this matches LISSOM by using an empty bin at 5.
        self.rr = Distribution((0,5))  # 5 because in the L. test example 0 and 4 are distinct
        self.rr.add({0:1, 1:1, 2:1, 3:1, 4:1})
        
        self.assertAlmostEqual(self.rr.vector_sum()[0], 0.0)
        self.assertAlmostEqual(self.rr.vector_average(), self.rr.vector_sum()[0]/5.0)
        self.rr.add({1:2})
        self.assertAlmostEqual(self.rr.vector_sum()[0], 2.0) 
        self.assertAlmostEqual(self.rr.vector_average(), self.rr.vector_sum()[0]/5.0)
        self.assertAlmostEqual(self.rr.vector_sum()[1], 1.0)  
        self.rr.add({3:2})
        self.assertAlmostEqual(self.rr.vector_sum()[0], 2*2*cos(2*pi/5)) 
        self.assertAlmostEqual(self.rr.vector_average(), self.rr.vector_sum()[0]/5.0)
        self.assertAlmostEqual(self.rr.vector_sum()[1], 2.0)  



    def test_lissom_peak_histogram(self):
        self.p = Distribution((0,2),keep_peak=True)

        self.p.add({0:1.0})
        self.p.add({2:9.9})
        self.p.add({2:3.3})
        self.p.add({0:1.0})
        self.p.add({1:0.3})
        self.p.add({1:84.0})
        self.p.add({1:36.0})

        self.assertAlmostEqual(self.p.get_value(0), 1.0)
        self.assertAlmostEqual(self.p.get_value(1), 84.0)
        self.assertAlmostEqual(self.p.get_value(2), 9.9)

        self.assertEqual(self.p.get_count(0), 2)
        self.assertEqual(self.p.get_count(1), 3)
        self.assertEqual(self.p.get_count(2), 2)



    def test_statistics(self):

        self.a = Distribution(cyclic=True)
        self.a.add({0.0:0.0, pi/2:1.0})
        self.assertAlmostEqual(self.a.vector_sum()[0], 1.0)
        self.assertAlmostEqual(self.a.vector_average(), 1.0/2.0)
        self.assertAlmostEqual(self.a.vector_sum()[1], pi/2)

        self.a.add({-pi/2:1.0}) # (should be like 3pi/2)
        self.assertAlmostEqual(self.a.vector_sum()[0], 0.0)
        self.assertAlmostEqual(self.a.vector_average(), 0.0)

        self.a.add({3*pi/8:0.3})
        self.assertAlmostEqual(self.a.vector_sum()[0], 0.3)
        self.assertAlmostEqual(self.a.vector_average(), 0.3/4.0)
        self.assertAlmostEqual(self.a.vector_sum()[1], 3*pi/8)


        self.c = Distribution((0.0,1.0), cyclic=True)
        self.c.add({0.0:1.0, 0.25:1.0})
        self.assertAlmostEqual(self.c.vector_sum()[0], (1.0+1.0)**0.5) 
        self.assertAlmostEqual(self.c.vector_average(), self.c.vector_sum()[0]/self.c.num_bins())
        self.assertEqual(self.c.vector_sum()[1], atan2(1.0,1.0)/(2*pi))

        self.c.add({1.75:1.0})  # added beyond bounds
        self.assertAlmostEqual(self.c.vector_sum()[0], 1.0) 
        self.assertAlmostEqual(self.c.vector_average(), self.c.vector_sum()[0]/self.c.num_bins())
        self.assertEqual(self.c.vector_sum()[1], 0.0)
        


        
cases = [TestHistogram]

suite = unittest.TestSuite()

suite.addTests([unittest.makeSuite(case) for case in cases])
              
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=1).run(suite)

