

from topo.inputsheet import *
from topo.rfsom import RFSOM
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

FuzzyLineSheet.x = Dynamic(lambda : random.uniform(-0.5,0.5))
FuzzyLineSheet.y = Dynamic(lambda : random.uniform(-0.5,0.5))

FuzzyLineSheet.theta = Dynamic(lambda :random.uniform(-pi,pi))
FuzzyLineSheet.width = 0.02
FuzzyLineSheet.height = 0.9
FuzzyLineSheet.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))


# rf som parameters
RFSOM.density = 2500
RFSOM.weights_factory = UniformRandomSheet(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))
RFSOM.training_length = 10000
RFSOM.radius_0 = 0.1

# image saver parameters
ImageSaver.file_format='png'
ImageSaver.time_format='%0.4d'

###########################################
# build simulation

base.min_print_level = base.MESSAGE

print "Creating simulation objects..."
s = Simulator()

retina = FuzzyLineSheet(name='Retina')
V1 = RFSOM(name='V1')
save  = ImageSaver(name='RFSOM')

s.connect(retina,V1,delay=1)

# Uncomment the connections to the image saver, to save all the activation
# images to disk.
#s.connect(retina,save,dest_port='retina',delay=2)
#s.connect(V1,save,dest_port='V1',delay=1)

s.run(10000)

V1.projections['Retina'][0].plot_rfs()

# import profile,pstats
#
# p = profile.Profile()
# p.runctx('s.run(10)',locals(),globals())
