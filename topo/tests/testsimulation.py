"""
Unit test for Simulation
$Id$
"""
__version__='$Revision$'

import unittest
import copy

from Numeric import array
from topo.base.simulation import *
from topo.eps.basic import *


# CEBHACKALERT: not a complete test of Simulation

class TestSimulation(unittest.TestCase):
    def test_event_copy(self):
        """
        Test to make sure that EPConnectionEvent copies the underlying data
        on construction.
        """
        s = Simulation(step_mode = True)
        data = array([4,3])
        se = EPConnectionEvent(1,2,data)
        se.data[0] = 5
        assert data[0] != se.data[0], 'Matrices should be different'
        se2 = copy(se)
        assert se != se2, 'Objects are the same'

    def test_state_stack(self):
        s = Simulation(step_mode = True)
        s['pulse1'] = PulseGenerator(period = 1)
        s['pulse2'] = PulseGenerator(period = 3)
        s['sum_unit'] = SumUnit()
        s.connect('pulse1','sum_unit',delay=1)
        s.connect('pulse2','sum_unit',delay=1)
        s.run(1.0)
        s.state_push()
        self.assertEqual(s.state_len(),1)
        s.state_pop()
        self.assertEqual(s.state_len(),0)
        

    def test_get_objects(self):
        s = Simulation(step_mode = True)

        s['pulse1'] = PulseGenerator(period = 1)
        s['pulse2'] = PulseGenerator(period = 3)
        s['sum_unit'] = SumUnit()
        n1 = s['pulse1'].name
        n2 = s['pulse2'].name

        s.connect('pulse1','sum_unit',delay=1)
        s.connect('pulse2','sum_unit',delay=1)
        t1 = s.objects()
        e1 = [ep for ep in t1.values() if isinstance(ep,PulseGenerator) and ep.name == n1]
        t2 = s.objects()
        e2 = [ep for ep in t2.values() if isinstance(ep,PulseGenerator) and ep.name == n2]
        assert e1.pop().name == n1, 'Object names do not match'
        assert e2.pop().name == n2, 'Object names do not match'
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimulation))
