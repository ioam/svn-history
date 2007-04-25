"""
Created to test the pattern presentation.

$Id$
"""
__version__='$Revision$'

import unittest, random
from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.parameterclasses import DynamicNumber
import topo.patterns.basic
from topo.base.boundingregion import BoundingBox
import topo.patterns.random
from topo.base.cf import CFProjection, CFSheet
import topo.base.parameterizedobject
from math import pi
from topo.commands.basic import pattern_present
from topo.learningfns.optimized import CFPLF_Hebbian_opt
from topo.misc.numbergenerators import UniformRandom

class TestPatternPresent(unittest.TestCase):

    def test_pattern_present(self):
        GeneratorSheet.period = 1.0
        GeneratorSheet.nominal_density = 4


        input_pattern1 = topo.patterns.basic.Line(
            thickness=0.02,
            bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))),
            x=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=100)),
            y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=200)),
            orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=300)))

        input_pattern2 = topo.patterns.basic.Line(
            thickness=0.02,
            bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))),
            x=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=100)),
            y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=200)),
            orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=300)))

        CFSheet.nominal_density = 4
        CFProjection.weights_generator = topo.patterns.random.UniformRandom(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
	CFProjection.learning_fn=CFPLF_Hebbian_opt()
        topo.base.parameterizedobject.min_print_level = topo.base.parameterizedobject.MESSAGE
        s = topo.base.simulation.Simulation()
        s['Retina'] = GeneratorSheet(input_generator=input_pattern1)
        s['Retina2'] = GeneratorSheet(input_generator=input_pattern2)
        s['V1'] = CFSheet()
        s['V2'] = CFSheet()
        s.connect('Retina','V1',delay=0.5,connection_type=CFProjection,name='R1toV1')
        s.connect('Retina','V2',delay=0.5,connection_type=CFProjection,name='R1toV2')
        s.connect('Retina2','V2',delay=0.5,connection_type=CFProjection,name='R2toV2')
        s.run(2)

        # Want to temporarily replace this:
        #retina = GeneratorSheet(input_generator=topo.patterns.basic.Line(),name='Retina')
        pattern_present({'Retina':topo.patterns.basic.Line()},5.0)

        


suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternPresent))
