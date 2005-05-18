import unittest
from pprint import pprint
from topo import plot
from topo.sheet import *
from topo.bitmap import RGBMap
from topo.image import ImageGenerator
from topo.inputsheet import *
import Numeric
import topo.kernelfactory
import topo.base
from topo.plotfilesaver import *
from PIL import *

class TestPlotFileSaver(unittest.TestCase):

    def setup(self):
        InputSheet.period = 1.0
        InputSheet.density = 400
        FuzzyLineFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
        FuzzyLineFactory.width = 0.02
        FuzzyLineFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        CFSOM.density = 100
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1
        KernelProjection.weights_factory = UniformRandomFactory(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
        
        base.min_print_level = base.MESSAGE
        s = topo.simulator.Simulator()
        
        retina = InputSheet(input_generator=FuzzyLineFactory(),name='Retina')
        retina2 = InputSheet(input_generator=FuzzyLineFactory(),name='Retina2')
        V1 = CFSOM(name='V1')
        V2 = CFSOM(name='V2')
        save  = ImageSaver(name='CFSOM')
        
        s.connect(retina,V1,delay=0.5,projection_params={'name':'R1toV1'})
        s.connect(retina,V2,delay=0.5,projection_params={'name':'R1toV2'})
        s.connect(retina2,V2,delay=0.5,projection_params={'name':'R2toV2'})
        self.pe = topo.plotengine.PlotEngine(self.s)
        s.run(2)
        

    def test_activity_file(self):
        af = PlotFileSaver('Activation')


#    def test_weights_file(self):
#        wf = PlotFileSaver('Weights',x=0.0,y=0.0,


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotFileSaver))
