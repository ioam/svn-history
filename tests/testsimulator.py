import unittest

from topo.simulator import *

class TestSimulator(unittest.TestCase):
    def test_find_EP(self,):
        s = Simulator(step_mode = 1)

        pulse1 = PulseGenerator(period = 1)
        pulse2 = PulseGenerator(period = 3)
        sum = SumUnit()
        n1 = pulse1.name
        n2 = pulse2.name

        s.connect(pulse1,sum,delay=1)
        s.connect(pulse2,sum,delay=1)
        t1 = s.find_EP(PulseGenerator,n1)
        t2 = s.find_EP(PulseGenerator,n2)
        assert t1.name == n1, 'Object names do not match'
        assert t2.name == n2, 'Object names do not match'
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSimulator))
