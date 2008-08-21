"""

$Id$
"""
__version__='$Revision$'

import unittest, copy
from numpy.testing import assert_array_equal

import topo
import __main__

from topo.base.sheet import Sheet
from topo.sheet.generator import GeneratorSheet
from topo.commands.basic import save_snapshot,load_snapshot
from topo.pattern.basic import Gaussian, Line
from topo.base.simulation import Simulation,SomeTimer


# CEBHACKALERT: this test must depend on something that happens in
# another one, (or there is some other problem) because when run on
# its own it fails with a strange error.
# ./topographica -c 'import topo.tests.testsnapshots; topo.tests.run(test_modules=[topo.tests.testsnapshots])'


SNAPSHOT_LOCATION = "topo/tests/testsnapshot.typ"
SIM_NAME = "testsnapshots"

class TestSnapshots(unittest.TestCase):

    # CB: all tests that use topo.sim ought to do make a new topo.sim
    def setUp(self):
        """
        Create a new Simulation as topo.sim (so this test isn't affected by changes
        to topo.sim by other tests).
        """
        Simulation(register=True,name=SIM_NAME)


    def basic_save_load_snapshot(self,xml=False):
        """
        Very basic test to check the activity matrix of a GeneratorSheet
        comes back ok, and that class attributes are pickled.
        """
        assert topo.sim.name==SIM_NAME
         
        topo.sim['R']=GeneratorSheet(input_generator=Gaussian(),nominal_density=2)

        topo.sim.run(1)

        R_act = copy.deepcopy(topo.sim['R'].activity)
        Line.x = 12.0
        topo.sim.startup_commands.append("z=99")

        save_snapshot(SNAPSHOT_LOCATION,xml)


        Line.x = 9.0
        exec "z=88" in __main__.__dict__
        
        topo.sim['R'].set_input_generator(Line())
        topo.sim.run(1)

        load_snapshot(SNAPSHOT_LOCATION)

        
        # CEBALERT: should also test that unpickling order is correct
        # (i.e. startup_commands, class attributes, simulation)
        assert_array_equal(R_act,topo.sim['R'].activity)
        self.assertEqual(Line.x,12.0)
        self.assertEqual(__main__.__dict__['z'],99)

        

    def test_basic_save_load_snapshot(self):
        self.basic_save_load_snapshot()


# CB: all the subsequent tests fail if this runs!!
# I'm working on it...
#    def test_xml_basic_save_load_snapshot(self):
#        self.basic_save_load_snapshot(xml=True)


    def test_new_simulation_still_works(self):

        #  Test to make sure the above tests haven't screwed up
        # the ability to construct new simulation objects
        topo.base.simulation.Simulation()






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
