"""
Created to test the pattern input orientations.

$Id$
"""
__version__='$Revision$'

import unittest

from Numeric import array

from topo.base.patterngenerator import *
import topo.patterns.basic

from utils import assert_array_equal


# CEBHACKALERT: needs writing so that it tests PatternGenerator properly!

class TestPatternGenerator(unittest.TestCase):

    def test_orientation(self):
        """
        Create a pattern, and test the orientation.
        """
        target = array([[0, 0, 0, 0, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0]])

        bounds = BoundingBox(radius=0.3)
        density = 10
        width = 2.0/density
        height = 4.0/density
        
        rect = topo.patterns.basic.Rectangle(size=height,
                                             aspect_ratio=width/height,
                                             density=density,bounds=bounds)

        assert_array_equal(rect(),target)

        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternGenerator))
