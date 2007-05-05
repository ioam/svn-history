"""
Unit test for TopoConsole
$Id$
"""
__version__='$Revision$'


# CEBALERT: doesn't really test topoconsole.

import topo
import unittest
from topo.tkgui import *
from topo.base.simulation import Simulation
import topo.base.parameterizedobject
import topo.base.simulation

class TestTopoConsole(unittest.TestCase):
    def setUp(self):
        self.s = Simulation(register=False)
        self.console = start()
        topo.base.parameterizedobject.min_print_level = topo.base.parameterizedobject.WARNING
        self.s.print_level = topo.base.parameterizedobject.WARNING

    def tearDown(self):
        self.console.quit() # does quit() do anything without mainloop()? Why test a tkinter method?
                            # we can't really test the interactive quit dialog...
                            # should remove this, I think

suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
suite.requires_display = True
suite.addTest(unittest.makeSuite(TestTopoConsole))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
