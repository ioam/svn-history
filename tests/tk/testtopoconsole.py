import unittest
from topo.tk import *
from topo.simulator import Simulator
from topo.plotengine import PlotEngine
import topo.base

class TestTopoConsole(unittest.TestCase):
    def setUp(self):
        self.s = Simulator()
        self.pe = PlotEngine(self.s)
        self.console = start()
        topo.base.min_print_level = topo.base.WARNING
        self.s.print_level = topo.base.WARNING

    def test_plotengine_dict(self):
        self.assertEqual(self.console.active_simulator(),None)
        self.console.set_active_simulator(self.s)
        self.assertNotEqual(self.console.active_simulator(),None)
        self.assertNotEqual(self.console.active_plotengine(),None)
        self.assertNotEqual(self.console.active_plotengine(),self.pe)
        generated_pe = self.console.active_plotengine()
        self.console.set_active_simulator(None)
        self.assertEqual(self.console.active_simulator(),None)

    def test_do_training(self):
        run_time = 15.5
        self.console.set_active_simulator(self.s)
        start_time = self.s.time()
        self.console.do_training(str(run_time))
        end_time = self.s.time()
        self.assertEqual(start_time+run_time,end_time)

    def tearDown(self):
        self.console.quit()


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestTopoConsole))
