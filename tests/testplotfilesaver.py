import unittest
from pprint import pprint
from topo import plot
from topo.sheet import *
from topo.bitmap import RGBMap
from topo.image import ImageGenerator
from topo.inputsheet import *
import Numeric, random, os
from math import pi
from topo.kernelfactory import FuzzyLineFactory
import topo.base
import topo.cfsom
import topo.cfsheet
from topo.plotfilesaver import *
from PIL import *

class TestPlotFileSaver(unittest.TestCase):

    def test_file_saving(self):
        InputSheet.period = 1.0
        InputSheet.density = 400
        FuzzyLineFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        FuzzyLineFactory.width = 0.02
        FuzzyLineFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        topo.cfsom.CFSOM.density = 100
        topo.cfsom.CFSOM.learning_length = 10000
        topo.cfsom.CFSOM.radius_0 = 0.1
        topo.cfsheet.KernelProjection.weights_factory = UniformRandomFactory(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
        
        topo.base.min_print_level = topo.base.WARNING
        self.s = topo.simulator.Simulator()
        
        retina = InputSheet(input_generator=FuzzyLineFactory(),name='Retina')
        retina2 = InputSheet(input_generator=FuzzyLineFactory(),name='Retina2')
        V1 = topo.cfsom.CFSOM(name='V1')
        V2 = topo.cfsom.CFSOM(name='V2')
        retina.print_level = topo.base.WARNING
        retina2.print_level = topo.base.WARNING
        V1.print_level = topo.base.WARNING
        V2.print_level = topo.base.WARNING
        
        self.s.connect(retina,V1,delay=0.5,projection_params={'name':'R1toV1'})
        self.s.connect(retina,V2,delay=0.5,projection_params={'name':'R1toV2'})
        self.s.connect(retina2,V2,delay=0.5,projection_params={'name':'R2toV2'})
        self.pe = topo.plotengine.PlotEngine(self.s)
        self.s.run(2)

        af = ActivationFile('Retina')
        wf = WeightsFile('V1',0.0,0.0)
        waf = WeightsArrayFile('V1','R1toV1',10)
#        for each in af.files + wf.files + waf.files:
#            os.remove(each)
#


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotFileSaver))
