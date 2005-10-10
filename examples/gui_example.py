"""
$Id$
"""

import random
from math import pi
import pdb #debugger
from topo.sheets.generatorsheet import *
from topo.base.patterngenerator import *
from topo.base.simulator import *
from topo.projections.kernelprojection import KernelProjection
from topo.plotting.plotfilesaver import ImageSaver
from topo.base.parameter import Dynamic
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomGenerator
from topo.patterns.basic import FuzzyLineGenerator


###########################################
# Set parameters

# input generation params
GeneratorSheet.period = 1.0
GeneratorSheet.density = 20*20

FuzzyLineGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
FuzzyLineGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))

FuzzyLineGenerator.theta = Dynamic(lambda :random.uniform(-pi,pi))
FuzzyLineGenerator.width = 0.02
FuzzyLineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))


# rf som parameters
CFSOM.density = 10*10
CFSOM.learning_length = 10000
CFSOM.radius_0 = 0.1

KernelProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))


# image saver parameters
ImageSaver.file_format='png'
ImageSaver.time_format='%0.4d'

###########################################
# build simulation

topo.base.object.min_print_level = topo.base.object.MESSAGE

s = topo.base.simulator.Simulator()

retina = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina')
retina2 = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina2')
V1 = CFSOM(name='V1')
V2 = CFSOM(name='V2')
save  = ImageSaver(name='CFSOM')

s.connect(retina,V1,delay=0.5,projection_type=KernelProjection,projection_params={'name':'R1toV1'})
s.connect(retina,V2,delay=0.5,projection_type=KernelProjection,projection_params={'name':'R1toV2'})
s.connect(retina2,V2,delay=0.5,projection_type=KernelProjection,projection_params={'name':'R2toV2'})

s.run(2)
