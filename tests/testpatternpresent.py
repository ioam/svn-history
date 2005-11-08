"""
Created to test the pattern presentation.

$Id$
"""
__version__='$Revision$'

import unittest, random
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.parameter import Dynamic
from topo.patterns.basic import LineGenerator
from topo.base.boundingregion import BoundingBox
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomGenerator
from topo.base.connectionfield import CFProjection
import topo.base.topoobject
from math import pi
from topo.commands.basic import pattern_present

class TestPatternPresent(unittest.TestCase):

    def test_pattern_present(self):
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 20
        LineGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        LineGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))
        LineGenerator.orientation = Dynamic(lambda :random.uniform(-pi,pi))
        LineGenerator.thickness = 0.02
        LineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
        CFSOM.density = 10
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1
        CFProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
        topo.base.topoobject.min_print_level = topo.base.topoobject.MESSAGE
        s = topo.base.simulator.Simulator()
        retina = GeneratorSheet(input_generator=LineGenerator(),name='Retina')
        retina2 = GeneratorSheet(input_generator=LineGenerator(),name='Retina2')
        V1 = CFSOM(name='V1')
        V2 = CFSOM(name='V2')
        s.connect(retina,V1,delay=0.5,connection_type=CFProjection,
                  connection_params={'name':'R1toV1'})
        s.connect(retina,V2,delay=0.5,connection_type=CFProjection,
                  connection_params={'name':'R1toV2'})
        s.connect(retina2,V2,delay=0.5,connection_type=CFProjection,
                  connection_params={'name':'R2toV2'})
        s.run(2)

        # Want to temporarily replace this:
        #retina = GeneratorSheet(input_generator=LineGenerator(),name='Retina')
        pattern_present({'Retina':LineGenerator()},5.0)

        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternPresent))
