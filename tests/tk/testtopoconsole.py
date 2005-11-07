"""
Unit test for TopoConsole
$Id$
"""
__version__='$Revision$'


import unittest
from topo.tk import *
from topo.base.simulator import Simulator
from topo.plotting.plotengine import PlotEngine
import topo.base.topoobject
import topo.base.registry

class TestTopoConsole(unittest.TestCase):
    def setUp(self):
        topo.base.registry.set_active_sim(None)
        self.s = Simulator(register=False)
        self.pe = PlotEngine(self.s)
        self.console = start()
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        self.s.print_level = topo.base.topoobject.WARNING

    def test_plotengine_dict(self):
        self.assertEqual(self.console.active_simulator(),None)
        topo.base.registry.set_active_sim(self.s)
        self.assertNotEqual(self.console.active_simulator(),None)
        self.assertNotEqual(self.console.active_plotengine(),None)
        self.assertNotEqual(self.console.active_plotengine(),self.pe)
        generated_pe = self.console.active_plotengine()
        topo.base.registry.set_active_sim(None)
        self.assertEqual(self.console.active_simulator(),None)

    def test_do_learning(self):
        run_time = 15.5
        topo.base.registry.set_active_sim(self.s)
        start_time = self.s.time()
        self.console.do_learning(str(run_time))
        end_time = self.s.time()
        self.assertEqual(start_time+run_time,end_time)

    def tearDown(self):
        self.console.quit()


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestTopoConsole))
