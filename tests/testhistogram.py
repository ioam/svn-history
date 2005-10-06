import unittest

import Numeric
from topo.plotting.histogram import *

class TestHistogram(unittest.TestCase):
    def test_calculate(self):
        h1 = Histogram(Numeric.ones((20,20)))
        h1.histogram()



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestHistogram))
