

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
SineGratingSin.density = 10000
InputSheet.period = 1.0

GaussianSheet.x = Dynamic(lambda : random.uniform(-0.5,0.5))
GaussianSheet.y = Dynamic(lambda : random.uniform(-0.5,0.5))

GaussianSheet.theta = Dynamic(lambda :random.uniform(-pi,pi))
GaussianSheet.width = 0.02
GaussianSheet.height = 0.9
GaussianSheet.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))


# rf som parameters
RFSOM.density = 900
RFSOM.rf_width = 0.2
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

#retina = GaussianSheet(name='Retina')
retina = SineGratingSheet(name='Retina')
V1 = RFSOM(name='V1')
save  = ImageSaver(name='RFSOM')

s.connect(retina,V1,delay=1)

# Uncomment the connections to the image saver, to save all the activation
# images to disk.
# s.connect(retina,save,dest_port='retina',delay=1)
# s.connect(V1,save,dest_port='V1',delay=0)

s.run(10000)

V1.projections['Retina'].plot_rfs()

# import profile,pstats
#
# p = profile.Profile()
# p.runctx('s.run(10)',locals(),globals())
