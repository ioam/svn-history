import unittest
from topo.tk import *
from topo.simulator import Simulator
from topo.plotengine import PlotEngine

class TestTopoConsole(unittest.TestCase):
    def test_plotengine_dict(self):
        s = Simulator()
        pe = PlotEngine(s)
        console = start()
        self.assertEqual(console.active_simulator(),None)
        console.set_active_simulator(s)
        self.assertNotEqual(console.active_simulator(),None)
        self.assertNotEqual(console.active_plotengine(),None)
        self.assertNotEqual(console.active_plotengine(),pe)
        generated_pe = console.active_plotengine()
        console.set_active_simulator(None)
        self.assertEqual(console.active_simulator(),None)
        console.quit()

suite = unittest.TestSuite()
#  Uncomment the following line of code, to not run the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestTopoConsole))
