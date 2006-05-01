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


# To do:
# - test saving scheduled actions


import unittest, copy

import topo

from topo.base.sheet import Sheet
from topo.base.simulator import Simulator
from topo.base.connectionfield import CFSheet,CFProjection
from topo.sheets.generatorsheet import GeneratorSheet
from topo.commands.basic import save_snapshot,load_snapshot

from utils import assert_array_equal


class TestSnapshots(unittest.TestCase):

    def test_basic_save_load_snapshot(self):
        """
        Simple test to check the activity matrix of a Sheet
        comes back ok.
        """
        test_sim_name = "testing_sim"
        Sheet.density = 2.0
        topo.sim.name = test_sim_name
        topo.sim['Retina'] = GeneratorSheet()
        topo.sim['V1'] = CFSheet()
        topo.sim.connect('Retina','V1',delay=0.5,connection_type=CFProjection,name='Afferent')
        topo.sim.run(1)
        v1_activity = copy.deepcopy(topo.sim['V1'].activity)
    
        save_snapshot("temp_test")

        Simulator()
        self.assertNotEqual(topo.sim.name,test_sim_name)

        load_snapshot("temp_test")

        self.assertEqual(topo.sim.name,test_sim_name)
        assert_array_equal(v1_activity,topo.sim['V1'].activity)
        

        
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSnapshots))
