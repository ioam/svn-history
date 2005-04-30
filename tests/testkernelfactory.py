"""
Created to test the kernel input orientations.

$Id$
"""
import unittest
import topo.kernelfactory
from MLab import flipud, rot90

class TestKernelFactory(unittest.TestCase):

    def test_orientation(self):
        """
        Create a kernel, and test the orientation.
        """
        rect = topo.kernelfactory.RectangleFactory(x=-0.1,y=0.1,width=0.25,height=1.0,density=100)
        # print rect()
        # print 'rotated'
        # print flipud(rot90(rect()))
        # rb = rect.bounds.aarect()
        # print rb.lbrt()

suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestKernelFactory))
