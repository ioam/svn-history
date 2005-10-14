"""
$Id$
"""

import random

from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.patterngenerator import BoundingBox
from topo.projections.kernelprojection import KernelProjection
from topo.base.parameter import Dynamic
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomGenerator
from topo.patterns.basic import FuzzyLineGenerator
from topo.base.simulator import Simulator


###########################################
# Set parameters

# input patterns
GeneratorSheet.period = 1.0
GeneratorSheet.density = 20

FuzzyLineGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
FuzzyLineGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))

FuzzyLineGenerator.theta = Dynamic(lambda :random.uniform(-pi,pi))
FuzzyLineGenerator.width = 0.02
FuzzyLineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

# cortical sheet
CFSOM.density = 10
CFSOM.learning_length = 10000
CFSOM.radius_0 = 0.1

KernelProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))

#topo.base.object.min_print_level = topo.base.object.MESSAGE


###########################################
# build simulation

s = Simulator()

retina = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina')
retina2 = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina2')
V1 = CFSOM(name='V1')
V2 = CFSOM(name='V2')

s.connect(retina,V1,delay=0.5,projection_type=KernelProjection,projection_params={'name':'R1toV1'})
s.connect(retina,V2,delay=0.5,projection_type=KernelProjection,projection_params={'name':'R1toV2'})
s.connect(retina2,V2,delay=0.5,projection_type=KernelProjection,projection_params={'name':'R2toV2'})

s.run(1)
