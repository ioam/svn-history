"""
Test for the PlotFileSaver class
$Id$
"""
__version__='$Revision$'

import unittest
from pprint import pprint
from topo.plotting import plot
from topo.base.sheet import *
from testsheetview import ImageGenerator
from topo.sheets.generatorsheet import *
import Numeric, random, os
from math import pi
import topo.patterns.basic
import topo.patterns.random
import topo.base.topoobject
from topo.sheets.cfsom import CFSOM
import topo.base.connectionfield
from topo.plotting.plotfilesaver import *
from PIL import *
from topo.base.connectionfield import CFProjection
from topo.learningfns.basic import HebbianSOMLF

class TestPlotFileSaver(unittest.TestCase):

    def test_file_saving(self):
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 20
        topo.patterns.basic.Line.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        topo.patterns.basic.Line.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        topo.patterns.basic.Line.orientation = Dynamic(lambda :random.uniform(-pi,pi))
        topo.patterns.basic.Line.thickness = 0.02
        topo.patterns.basic.Line.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        CFSOM.density = 10
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1
        CFProjection.weights_generator = topo.patterns.random.UniformRandom(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
	CFProjection.learning_fn=HebbianSOMLF()
        topo.base.topoobject.min_print_level = topo.base.topoobject.WARNING
        self.s = topo.base.simulator.Simulator()
        
        retina = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina')
        retina2 = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina2')
        V1 = CFSOM(name='V1')
        V2 = CFSOM(name='V2')
        retina.print_level = topo.base.topoobject.WARNING
        retina2.print_level = topo.base.topoobject.WARNING
        V1.print_level = topo.base.topoobject.WARNING
        V2.print_level = topo.base.topoobject.WARNING
        
        self.s.connect(retina,V1,delay=0.5,connection_type=CFProjection,connection_params={'name':'R1toV1'})
        self.s.connect(retina,V2,delay=0.5,connection_type=CFProjection,connection_params={'name':'R1toV2'})
        self.s.connect(retina2,V2,delay=0.5,connection_type=CFProjection,connection_params={'name':'R2toV2'})
        self.s.run(2)

        af = ActivityFile('Retina')
        wf = UnitWeightsFile('V1',0.0,0.0)
        waf = ProjectionFile('V1','R1toV1',10)
        for each in af.files + wf.files + waf.files:
            os.remove(each)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestPlotFileSaver))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
