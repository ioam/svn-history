"""
$Id$
"""

import random

from topo.sheets.generatorsheet import GeneratorSheet
from topo.base.patterngenerator import BoundingBox
from topo.projections.kernelprojection import KernelProjection
from topo.base.parameter import DynamicNumber
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomGenerator
from topo.patterns.basic import FuzzyLineGenerator
from topo.base.simulator import Simulator


###########################################
# Set parameters

# input patterns
GeneratorSheet.period = 1.0
GeneratorSheet.density = 30

FuzzyLineGenerator.x = DynamicNumber(lambda : random.uniform(-0.5,0.5),softbounds=(-1.0,1.0))
FuzzyLineGenerator.y = DynamicNumber(lambda : random.uniform(-0.5,0.5),softbounds=(-1.0,1.0))

FuzzyLineGenerator.theta = DynamicNumber(lambda :random.uniform(-pi,pi),softbounds=(0,2*pi))
FuzzyLineGenerator.width = 0.02
FuzzyLineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

# cortical sheet
CFSOM.density = 50
CFSOM.learning_length = 10000
CFSOM.radius_0 = 0.1

KernelProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))


###########################################
# build simulation

s = Simulator()

retina = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina')
V1 = CFSOM(name='V1')
s.connect(retina,V1,delay=1,connection_type=KernelProjection,connection_params={'name':'RtoV1'})

s.run(1)
#s.run(10000)

# import profile,pstats
#
# p = profile.Profile()
# p.runctx('s.run(10)',locals(),globals())
