

from topo.inputsheet import *
from topo.kernelfactory import *
from topo.simulator import *
from topo.rfsheet import KernelProjection
from topo.cfsom import CFSOM
from topo.image import ImageSaver
from math import pi
from topo.params import Dynamic
import random
import pdb #debugger


###########################################
# Set parameters

print "Setting parameters..."

# input generation params
InputSheet.period = 1.0
InputSheet.density = 900

FuzzyLineFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
FuzzyLineFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))

FuzzyLineFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
FuzzyLineFactory.width = 0.02
FuzzyLineFactory.height = 0.9
FuzzyLineFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))


# rf som parameters
CFSOM.density = 2500
CFSOM.training_length = 10000
CFSOM.radius_0 = 0.1

# Projection Parameters
KernelProjection.weights_factory = UniformRandomFactory(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))

# image saver parameters
ImageSaver.file_format='png'
ImageSaver.time_format='%0.4d'

###########################################
# build simulation

base.min_print_level = base.MESSAGE

print "Creating simulation objects..."
s = SimpleSimulator()

retina = InputSheet(input_generator=FuzzyLineFactory(),name='Retina')
V1 = CFSOM(name='V1')
save  = ImageSaver(name='CFSOM')

s.connect(retina,V1,delay=1)

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
