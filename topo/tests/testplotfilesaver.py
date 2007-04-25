"""
Test for the PlotFileSaver class
$Id$
"""
__version__='$Revision$'

import unittest
from pprint import pprint
from topo.plotting import plot
from topo.base.sheet import *
from topo.sheets.generatorsheet import *
import numpy.oldnumeric as Numeric, random, os
from math import pi
import topo.patterns.basic
import topo.patterns.random
import topo.base.parameterizedobject
from topo.plotting.plotfilesaver import *
from PIL import *
from topo.base.cf import CFProjection, CFSheet
from topo.learningfns.som import CFPLF_HebbianSOM

class TestPlotFileSaver(unittest.TestCase):

    def test_file_saving(self):
        pass
# 	  GeneratorSheet.period = 1.0
#         GeneratorSheet.xdensity = 4
#         topo.patterns.basic.Line.x = Dynamic(lambda : random.uniform(-0.5,0.5))
#         topo.patterns.basic.Line.y = Dynamic(lambda : random.uniform(-0.5,0.5))
#         topo.patterns.basic.Line.orientation = Dynamic(lambda :random.uniform(-pi,pi))
#         topo.patterns.basic.Line.thickness = 0.02
#         topo.patterns.basic.Line.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
#         CFSheet.nominal_density = 4
#         CFProjection.weights_generator = topo.patterns.random.UniformRandom(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
# 	CFProjection.learning_fn=CFPLF_HebbianSOM()
#         topo.base.parameterizedobject.min_print_level = topo.base.parameterizedobject.WARNING
#         self.s = topo.base.simulation.Simulation()
        
#         retina = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina')
#         retina2 = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina2')
#         V1 = CFSheet(name='V1')
#         V2 = CFSheet(name='V2')
#         retina.print_level = topo.base.parameterizedobject.WARNING
#         retina2.print_level = topo.base.parameterizedobject.WARNING
#         V1.print_level = topo.base.parameterizedobject.WARNING
#         V2.print_level = topo.base.parameterizedobject.WARNING
        
#         self.s.connect(retina,V1,delay=0.5,connection_type=CFProjection,name='R1toV1')
#         self.s.connect(retina,V2,delay=0.5,connection_type=CFProjection,name='R1toV2')
#         self.s.connect(retina2,V2,delay=0.5,connection_type=CFProjection,name='R2toV2')
#         self.s.run(2)

#         af = ActivityFile('Retina')
#         wf = UnitWeightsFile('V1',0.0,0.0)
#         waf = ProjectionFile('V1','R1toV1',10)
#         for each in af.files + wf.files + waf.files:
#             os.remove(each)



# suite = unittest.TestSuite()
# suite.addTest(unittest.makeSuite(TestPlotFileSaver))

# if __name__ == '__main__':
#     unittest.TextTestRunner(verbosity=2).run(suite)
