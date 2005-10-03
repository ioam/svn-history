"""
See test_cfsom(self) and ImagePoster for an example of how to use and call
the PlotEngine system from a simulation.

$Id$
"""
import unittest
from topo.sheets.cfsom import CFSOM
from pprint import pprint
from topo import plot
from topo import base
from topo.bitmap import *
from topo.sheet import Sheet
from topo.sheets.generatorsheet import *
from topo.simulator import *
from topo.plotfilesaver import ImageSaver
from topo import patterngenerator
from topo.patterns.basic import GaussianGenerator
from math import pi
from topo.parameter import Dynamic
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
        from topo.patterngenerator import ImageGenerator
        from topo.plotfilesaver import ImageSaver
        
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
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 900
        GeneratorSheet.print_level = base.WARNING
        
        GaussianGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))        
        GaussianGenerator.theta = Dynamic(lambda :random.uniform(-pi,pi))
        
        GaussianGenerator.width = 0.02
        GaussianGenerator.height = 0.9
        GaussianGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        # cf som parameters
        CFSOM.density = 900
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1

        ###########################################
        # build simulation
        
        base.min_print_level = base.WARNING
      
        s = Simulator()
        s.verbose("Creating simulation objects...")
        retina = GeneratorSheet(input_generator=GaussianGenerator())
        
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
