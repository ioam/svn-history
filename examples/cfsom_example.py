"""
$Id$
"""

from math import pi
import random
import pdb #debugger
from topo.sheets.generatorsheet import *
from topo.patterngenerator import *
from topo.simulator import *
from topo.projections.kernelprojection import KernelProjection
from topo.plotfilesaver import ImageSaver
from topo.parameter import Dynamic
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomGenerator
from topo.patterns.basic import FuzzyLineGenerator


###########################################
# Set parameters

print "Setting parameters..."

# input generation params
GeneratorSheet.period = 1.0
GeneratorSheet.density = 900

FuzzyLineGenerator.x = Dynamic(lambda : random.uniform(-0.5,0.5))
FuzzyLineGenerator.y = Dynamic(lambda : random.uniform(-0.5,0.5))

FuzzyLineGenerator.theta = Dynamic(lambda :random.uniform(-pi,pi))
FuzzyLineGenerator.width = 0.02
#FuzzyLineGenerator.height = 0.9
FuzzyLineGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))


# rf som parameters
CFSOM.density = 2500
CFSOM.learning_length = 10000
CFSOM.radius_0 = 0.1

# Projection Parameters
KernelProjection.weights_generator = UniformRandomGenerator(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))

# image saver parameters
ImageSaver.file_format='png'
ImageSaver.time_format='%0.4d'

###########################################
# build simulation

base.min_print_level = base.MESSAGE

print "Creating simulation objects..."
# Used to be SimpleSimulator
s = Simulator()

retina = GeneratorSheet(input_generator=FuzzyLineGenerator(),name='Retina')
V1 = CFSOM(name='V1')
save  = ImageSaver(name='CFSOM')

s.connect(retina,V1,delay=1,projection_type=KernelProjection,projection_params={'name':'RtoV1'})


# Uncomment the connections to the image saver, to save all the activation
# images to disk.
#s.connect(retina,save,dest_port='retina',delay=2)
#s.connect(V1,save,dest_port='V1',delay=1)

#s.run(100)

#V1.projections['Retina'][0].plot_cfs()

# import profile,pstats
#
# p = profile.Profile()
# p.runctx('s.run(10)',locals(),globals())
