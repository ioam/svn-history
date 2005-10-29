import unittest
from pprint import pprint
from topo.plotting import plot
from topo.base.sheet import *
from topo.plotting.bitmap import RGBMap
from topo.base.patterngenerator import ImageGenerator
from topo.sheets.generatorsheet import *
import Numeric, random, os
from math import pi
from topo.patterns.basic import FuzzyLineGenerator
from topo.patterns.random import UniformRandomGenerator
import topo.base.topoobject
from topo.sheets.cfsom import CFSOM
import topo.base.connectionfield
from topo.plotting.plotfilesaver import *
from PIL import *
from topo.projections.kernelprojection import KernelProjection

class TestPlotFileSaver(unittest.TestCase):

    def test_file_saving(self):
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 20
        FuzzyLineGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        FuzzyLineGenerator.orientation = Dynamic(lambda :random.uniform(-pi,pi))
        FuzzyLineGenerator.width = 0.02
        FuzzyLineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        CFSOM.density = 10
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1
        topo.projections.kernelprojection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        self.s = topo.base.simulator.Simulator()
        
        retina = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina')
        retina2 = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina2')
        V1 = CFSOM(name='V1')
        V2 = CFSOM(name='V2')
        retina.print_level = topo.base.topoobject.WARNING
        retina2.print_level = topo.base.topoobject.WARNING
        V1.print_level = topo.base.topoobject.WARNING
        V2.print_level = topo.base.topoobject.WARNING
        
        self.s.connect(retina,V1,delay=0.5,connection_type=KernelProjection,connection_params={'name':'R1toV1'})
        self.s.connect(retina,V2,delay=0.5,connection_type=KernelProjection,connection_params={'name':'R1toV2'})
        self.s.connect(retina2,V2,delay=0.5,connection_type=KernelProjection,connection_params={'name':'R2toV2'})
        self.pe = topo.plotting.plotengine.PlotEngine(self.s)
        self.s.run(2)

        af = ActivityFile('Retina')
        wf = UnitWeightsFile('V1',0.0,0.0)
        waf = ProjectionFile('V1','R1toV1',10)
        for each in af.files + wf.files + waf.files:
            os.remove(each)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotFileSaver))
