"""
See test_rfsom(self) and ImagePoster for an example of how to use and call
the PlotEngine system from a simulation.

$Id$
"""
import unittest
from pprint import pprint
from topo import plot
from topo import base
from topo.bitmap import *
from topo.sheet import Sheet
from topo.inputsheet import *
from topo.simulator import *
from topo.rfsom import RFSOM
from topo.image import ImageSaver
from topo import kernelfactory
from topo.kernelfactory import GaussianFactory
from math import pi
from topo.params import Dynamic
import random
import pdb #debugger


class TestRFSom(unittest.TestCase):

    def setUp(self):
        self.s = Simulator(step_mode = 1)
        self.sheet1 = Sheet()
        self.sheet2 = Sheet()

        pulse1 = PulseGenerator(period = 1)
        pulse2 = PulseGenerator(period = 3)
        sum = SumUnit()
        self.s.connect(pulse1,sum,delay=1)
        self.s.connect(pulse2,sum,delay=1)
        

    def test_rfsom(self):
        """
        Cut and paste of current topographica/examples/rfsom_example.py
        """
        # input generation params
        InputSheet.period = 1.0
        InputSheet.density = 900
        
        GaussianFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        
        GaussianFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        GaussianFactory.width = 0.02
        GaussianFactory.height = 0.9
        GaussianFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        # rf som parameters
        RFSOM.density = 900
        RFSOM.rf_width = 0.2
        RFSOM.training_length = 10000
        RFSOM.radius_0 = 0.1

        ###########################################
        # build simulation
        
        base.min_print_level = base.NORMAL
      
        s = Simulator()
        s.verbose("Creating simulation objects...")
        retina = InputSheet(input_generator=GaussianFactory())
        
        # Old form
        #retina = GaussianSheet(name='Retina')
        V1 = RFSOM(name='V1')

        s.connect(retina,V1,delay=1)

        s.run(10)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestRFSom))
