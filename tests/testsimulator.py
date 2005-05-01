import unittest
import copy

from Numeric import array
from topo.simulator import *
from topo.scalarep import *

class TestSimulator(unittest.TestCase):
    def test_event_copy(self):
        """
        Test to make sure a copy of an Event works, which is pointers to
        all the sheets, but a deepcopy of the data.  The data is probably
        an array, but it's not required.
        """
        s = Simulator(step_mode = 1)
        data = array([4,3])
        se = Simulator.Event(1,2,3,4,5,data)
        se2 = copy(se)
        assert se != se2, 'Objects are the same'
        se2.data[0] = 5
        assert se.data[0] != se2.data[0], 'Matrices should be different'

    def test_state_stack(self):
        s = Simulator(step_mode = 1)
        pulse1 = PulseGenerator(period = 1)
        pulse2 = PulseGenerator(period = 3)
        sum = SumUnit()
        s.connect(pulse1,sum,delay=1)
        s.connect(pulse2,sum,delay=1)
        s.run(1.0)
        s.state_push()
        self.assertEqual(s.state_len(),1)
        s.state_pop()
        self.assertEqual(s.state_len(),0)
        

    def test_get_event_processors(self):
        s = Simulator(step_mode = 1)

        pulse1 = PulseGenerator(period = 1)
        pulse2 = PulseGenerator(period = 3)
        sum = SumUnit()
        n1 = pulse1.name
        n2 = pulse2.name

        s.connect(pulse1,sum,delay=1)
        s.connect(pulse2,sum,delay=1)
        t1 = s.get_event_processors()
        e1 = [ep for ep in t1 if isinstance(ep,PulseGenerator) and ep.name == n1]
        t2 = s.get_event_processors()
        e2 = [ep for ep in t2 if isinstance(ep,PulseGenerator) and ep.name == n2]
        assert e1.pop().name == n1, 'Object names do not match'
        assert e2.pop().name == n2, 'Object names do not match'
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimulator))
