"""
See test_cfsom(self) and ImagePoster for an example of how to use and call
the PlotEngine system from a simulation.

$Id$
"""
import unittest
from models.cfsom import CFSOM
from pprint import pprint
from topo import plot
from topo import base
from topo.bitmap import *
from topo.sheet import Sheet
from topo.inputsheet import *
from topo.simulator import *
from topo.image import ImageSaver
from topo import kernelfactory
from topo.kernelfactory import GaussianFactory
from math import pi
from topo.params import Dynamic
import random
import pdb #debugger


class TestCFSom(unittest.TestCase):

    def setUp(self):
        self.s = Simulator(step_mode = 1)
        self.sheet1 = Sheet()
        self.sheet2 = Sheet()


    def test_imagegenerator(self):
        """
        Code moved from __main__ block of cfsom.py.  Gives a tight example
        of running a cfsom simulation.
        """
        from topo.image import ImageGenerator,ImageSaver
        
        s = Simulator(step_mode=True)
    
        input = ImageGenerator(filename='examples/main.ppm',density=10000,
                               bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
    
    
        save = ImageSaver(pixel_scale=1.5)
        som = CFSOM()
        
        s.add(som,input,save)
        s.connect(input,som)
        s.connect(som,save)
        s.run(duration=10)
    


    def test_cfsom(self):
        """
        Cut and paste of current topographica/examples/cfsom_example.py
        """
        # input generation params
        InputSheet.period = 1.0
        InputSheet.density = 900
        InputSheet.print_level = base.WARNING
        
        GaussianFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))        
        GaussianFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        
        GaussianFactory.width = 0.02
        GaussianFactory.height = 0.9
        GaussianFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        # cf som parameters
        CFSOM.density = 900
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1

        ###########################################
        # build simulation
        
        base.min_print_level = base.WARNING
      
        s = Simulator()
        s.verbose("Creating simulation objects...")
        retina = InputSheet(input_generator=GaussianFactory())
        
        # Old form
        #retina = GaussianSheet(name='Retina')
        V1 = CFSOM(name='V1')
        V1.print_level = base.WARNING

        s.connect(retina,V1,delay=1,projection_params={'name':'RtoV1'})
        s.print_level = base.WARNING

        self.assertTrue(len(V1.get_projection_by_name('RtoV1')) == 1)
        self.assertTrue(len(V1.get_projection_by_name('R1toV1')) == 0)
        s.run(10)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestCFSom))
