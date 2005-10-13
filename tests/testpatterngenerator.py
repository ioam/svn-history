"""
Created to test the pattern input orientations.

$Id$
"""
import unittest
from topo.base.patterngenerator import *
from MLab import flipud, rot90
from Numeric import *
from topo.patterns.basic import RectangleGenerator

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
        bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        density = 16
        rect = RectangleGenerator(width=0.3,height=0.9,
                                density=4,bounds=bounds)
        self.assertEqual(rect(),target)
#        print rect()
        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternGenerator))
