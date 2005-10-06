import unittest
import topo
import Numeric
import Tkinter
import Pmw
import random
from PIL import Image
from topo.sheets.generatorsheet import *
from topo.base.patterngenerator import *
from topo.base.simulator import *
from topo.base.sheetview import *
from topo.plotting.plotengine import *
from topo.tk.preferencemappanel import *


class TestPreferenceMapPanel(unittest.TestCase):


    def test_preference_plot(self):
        pass

suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPreferenceMapPanel))
