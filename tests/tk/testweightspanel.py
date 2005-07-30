import unittest
import topo
import Numeric
import Tkinter
from PIL import Image
from topo.inputsheet import *
from topo.kernelfactory import *
from topo.simulator import *
from topo.sheetview import *
from topo.plotengine import *

class TestWeightsPanel(unittest.TestCase):


    def test_top_right_edge(self):
        self.left    = -0.1
        self.bottom  = -0.2
        self.right   =  0.3
        self.top     =  0.4
        self.lbrt = (self.left,self.bottom,self.right,self.top)
        self.region = BoundingBox(points = ((self.left,self.bottom),
                                            (self.right,self.top)))
        self.xc,self.yc = self.region.aarect().centroid()

        self.assertTrue(self.region.contains(0.3,0.4))




suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestWeightsPanel))
