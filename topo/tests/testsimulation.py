"""
Unit test for Simulation
$Id$
"""
__version__='$Revision$'

import unittest
import copy

from numpy.oldnumeric import array
from topo.base.simulation import *
from topo.eps.basic import *


# CEBALERT: not a complete test of Simulation

class TestSimulation(unittest.TestCase):
    def test_event_copy(self):
        """
        Test to make sure that EPConnectionEvent copies the underlying data
        on construction.
        """
        s = Simulation()
        data = array([4,3])
        epc = EPConnection()
        se = EPConnectionEvent(1,epc,data)
        se.data[0] = 5
        assert data[0] != se.data[0], 'Matrices should be different'
        se2 = copy(se)
        assert se is not se2, 'Objects are the same'

    def test_state_stack(self):
        s = Simulation()
        s['pulse1'] = PulseGenerator(period = 1)
        s['pulse2'] = PulseGenerator(period = 3)
        s['sum_unit'] = SumUnit()
        s.connect('pulse1','sum_unit',delay=1)
        s.connect('pulse2','sum_unit',delay=1)
        s.run(1.0)
        s.state_push()
        self.assertEqual(len(s._events_stack),1)
        s.state_pop()
        self.assertEqual(len(s._events_stack),0)
        

    def test_event_cmp(self):

        e1 = Event(1)
        e1a = Event(1)
        e2 = Event(2)

        assert e1 is not e1a
        assert e1 ==  e1a
        assert e1 < e2
        assert e1 == e1
        assert e2 > e1
        assert e2 == e2
        assert e1 != e2
        assert e2 != e1
        
    def test_event_insert(self):
        s = Simulation()

        e1 = Event(1)
        e1a = Event(1)
        e2 = Event(2)
        e2a = Event(2)

        s.enqueue_event(e1)
        s.enqueue_event(e2)
        s.enqueue_event(e2a)
        s.enqueue_event(e1a)

        s.enqueue_event(Event(0))

        assert len(s.events) == 5, 'Event queue has %d events, should have 5.' % len(s.events)

        assert s.events[1] == e1
        assert s.events[2] == e1a
        assert s.events[3] == e2
        assert s.events[4] == e2a

        
    def test_get_objects(self):
        s = Simulation()

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
