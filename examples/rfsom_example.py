

from topo.inputsheet import GaussianSheet
from topo.rfsom import RFSOM
from topo.image import ImageSaver
import random
import pdb #debugger


###########################################
# Set parameters

print "Setting parameters..."


# input generation params
GaussianSheet.density = 900
GaussianSheet.period = 1.0

GaussianSheet.x = lambda : random.uniform(-0.5,0.5)
GaussianSheet.y = lambda : random.uniform(-0.5,0.5)

GaussianSheet.theta = lambda :random.uniform(-3.1415926,3.1415926)
GaussianSheet.width = 0.02
GaussianSheet.height = 0.1
GaussianSheet.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

# rf som parameters
RFSOM.density = 900
RFSOM.rf_width = 0.1
RFSOM.training_length = 10000
RFSOM.radius_0 = 0.05

# image saver parameters
ImageSaver.file_format='png'
ImageSaver.time_format='%0.4d'

###########################################
# build simulation

base.min_print_level = base.MESSAGE

print "Creating simulation objects..."
s = Simulator()

retina = GaussianSheet(name='Retina')
V1 = RFSOM(name='V1')
save  = ImageSaver(name='RFSOM')

s.connect(retina,V1,delay=1)
#s.connect(retina,save,dest_port='retina',delay=1)
#s.connect(V1,save,dest_port='V1',delay=0)

print "Running..."
s.run(10001)

V1.projections['Retina'].plot_rfs()
