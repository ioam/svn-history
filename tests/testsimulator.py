import unittest

from topo.simulator import *
from topo.scalarep import *

class TestSimulator(unittest.TestCase):
    def test_get_event_processors(self,):
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
