"""

$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: other test files set ParameterizedObject class
# attributes to unpickleable things such as a lambdas (in various
# out-of-date ways!).  This test file therefore fails when run with
# the others, but runs fine on its own.
# So, we need to eliminate such things as
# "topo.patterns.basic.Gaussian.x=lambda..." from the test files.
#
# Meanwhile, run as:
#./topographica -c 'import topo.tests.testsnapshots; topo.tests.run(test_modules=[topo.tests.testsnapshots])'    
import unittest, copy

import topo
import __main__

from topo.base.sheet import Sheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.commands.basic import save_snapshot,load_snapshot
from topo.patterns.basic import Gaussian, Line

from utils import assert_array_equal


class TestSnapshots(unittest.TestCase):

    def test_basic_save_load_snapshot(self):
        """
        Very basic test to check the activity matrix of a GeneratorSheet
        comes back ok, and that class attributes are pickled.
        """
        Sheet.nominal_density = 2.0

        topo.sim['R']=GeneratorSheet(input_generator=Gaussian())
        topo.sim.run(1)

        R_act = copy.deepcopy(topo.sim['R'].activity)
        Line.x = 12.0
        topo.sim.startup_commands.append("z=99")

        save_snapshot("testsnapshot.typ") # CEBALERT: should delete at end of test

        Line.x = 9.0
        exec "z=88" in __main__.__dict__
        
        topo.sim['R'].set_input_generator(Line())
        topo.sim.run(1)

        load_snapshot("testsnapshot.typ")

        # CEBALERT: should also test that unpickling order is correct
        # (i.e. startup_commands, class attributes, simulation)
        assert_array_equal(R_act,topo.sim['R'].activity)
        self.assertEqual(Line.x,12.0)
        self.assertEqual(__main__.__dict__['z'],99)

        # CB: add xml pickling test. Certainly seems like
        # gnosis.xml.pickle is not the drop-in replacement
        # for pickle that it is supposed to be
        # (e.g. on unpickling, startup commands are not
        # executed: so gnosis.xml.pickle.load() does
        # things differently from pickle.load() ).
        # Need to investigate this.
        

# CB: longer to run test should additionally quit the simulation
# and start again. Should also test scheduled actions.
   
        
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSnapshots))
