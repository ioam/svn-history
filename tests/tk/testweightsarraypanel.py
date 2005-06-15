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

class TestWeightsArrayPanel(unittest.TestCase):

    def setUp(self):
        pass


suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestWeightsArrayPanel))
