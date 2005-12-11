"""
See test_cfsom(self) and ImagePoster for an example of how to use and call
the PlotEngine system from a simulation.

$Id$
"""
__version__='$Revision$'

import unittest
from topo.sheets.cfsom import CFSOM
from pprint import pprint
from topo.plotting import plot
from topo.base import topoobject
from topo.plotting.bitmap import *
from topo.base.sheet import Sheet
from topo.sheets.generatorsheet import *
from topo.base.simulator import *
from topo.plotting.plotfilesaver import ImageSaver
from topo.base import patterngenerator
from topo.patterns.basic import GaussianGenerator
from math import pi
from topo.base.parameter import Dynamic
import random
from topo.base.connectionfield import CFProjection
from topo.learningfns.basic import HebbianSOMLF
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
        from testsheetview import ImageGenerator
        from topo.plotting.plotfilesaver import ImageSaver
        
        s = Simulator(step_mode=True)
    
        input = ImageGenerator(filename='examples/main.ppm',density=100,
                               bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
    
    
        save = ImageSaver(pixel_scale=1.5)
        som = CFSOM()
        
        s.add(som,input,save)
        s.connect(input,som,connection_type=CFProjection,connection_params={'learning_fn':HebbianSOMLF()})
        s.connect(som,save)
        s.run(duration=10)
    


    def test_cfsom(self):
        """
        Cut and paste of current topographica/examples/cfsom_example.py
        """
        # input generation params
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 30
        GeneratorSheet.print_level = topo.base.topoobject.WARNING
        
        GaussianGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        GaussianGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))        
        GaussianGenerator.orientation = Dynamic(lambda :random.uniform(-pi,pi))
        
        gaussian_width = 0.02
        gaussian_height = 0.9
        GaussianGenerator.scale = gaussian_height
        GaussianGenerator.aspect_ratio = gaussian_width/gaussian_height
        GaussianGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        # cf som parameters
        CFSOM.density = 30
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1

        ###########################################
        # build simulation
        
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
      
        s = Simulator()
        s.verbose("Creating simulation objects...")
        retina = GeneratorSheet(input_generator=GaussianGenerator())
        
        # Old form
        #retina = GaussianSheet(name='Retina')
        V1 = CFSOM(name='V1')
        V1.print_level = topo.base.topoobject.WARNING

        s.connect(retina,V1,delay=1,connection_type=CFProjection,connection_params={'name':'RtoV1','learning_fn':HebbianSOMLF()})
        s.print_level = topo.base.topoobject.WARNING

        self.assertTrue(len(V1.get_in_projection_by_name('RtoV1')) == 1)
        self.assertTrue(len(V1.get_in_projection_by_name('R1toV1')) == 0)
        s.run(10)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestCFSom))
