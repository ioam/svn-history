"""
Created to test the pattern presentation.

$Id$
"""
__version__='$Revision$'

import unittest, random
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.parameter import Dynamic
import topo.patterns.basic
from topo.base.boundingregion import BoundingBox
from topo.sheets.cfsom import CFSOM
import topo.patterns.random
from topo.base.connectionfield import CFProjection
import topo.base.topoobject
from math import pi
from topo.commands.basic import pattern_present
from topo.learningfns.basic import HebbianSOMLF

class TestPatternPresent(unittest.TestCase):

    def test_pattern_present(self):
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
        topo.base.topoobject.min_print_level = topo.base.topoobject.MESSAGE
        s = topo.base.simulator.Simulator()
        retina = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina')
        retina2 = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina2')
        V1 = CFSOM(name='V1')
        V2 = CFSOM(name='V2')
        s.connect(retina,V1,delay=0.5,connection_type=CFProjection,name='R1toV1')
        s.connect(retina,V2,delay=0.5,connection_type=CFProjection,name='R1toV2')
        s.connect(retina2,V2,delay=0.5,connection_type=CFProjection,name='R2toV2')
        s.run(2)

        # Want to temporarily replace this:
        #retina = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina')
        pattern_present({'Retina':topo.patterns.basic.Line()},5.0)

        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternPresent))
