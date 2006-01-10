"""
Unit test for TopoConsole
$Id$
"""
__version__='$Revision$'


# CEBHACKALERT: doesn't test topoconsole completely.

import unittest
from topo.tkgui import *
from topo.base.simulator import Simulator
import topo.base.topoobject
import topo.base.simulator

class TestTopoConsole(unittest.TestCase):
    def setUp(self):
        # CEBHACKALERT: do we need such a test now?
        # topo.base.registry.set_active_sim(None)
        self.s = Simulator(register=False)
        self.console = start()
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        self.s.print_level = topo.base.topoobject.WARNING

    def test_do_learning(self):
        run_time = 15.5
        topo.base.simulator.set_active_sim(self.s)
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

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
