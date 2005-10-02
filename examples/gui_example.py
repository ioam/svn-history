"""
$Id$
"""

import random
from math import pi
import pdb #debugger
from topo.inputsheet import *
from topo.kernelfactory import *
from topo.simulator import *
from topo.cfsheet import KernelProjection
from topo.plotfilesaver import ImageSaver
from topo.parameter import Dynamic
from topo.sheets.cfsom import CFSOM
from topo.patterns.random import UniformRandomFactory
from topo.patterns.basic import FuzzyLineFactory


###########################################
# Set parameters

print "Setting parameters..."

# input generation params
InputSheet.period = 1.0
InputSheet.density = 20*20

FuzzyLineFactory.x = Dynamic(lambda : random.uniform(-0.5,0.5))
FuzzyLineFactory.y = Dynamic(lambda : random.uniform(-0.5,0.5))

FuzzyLineFactory.theta = Dynamic(lambda :random.uniform(-pi,pi))
FuzzyLineFactory.width = 0.02
FuzzyLineFactory.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))


# rf som parameters
CFSOM.density = 10*10
CFSOM.learning_length = 10000
CFSOM.radius_0 = 0.1

KernelProjection.weights_factory = UniformRandomFactory(bounds=BoundingBox(points=((-0.1,-0.1),(0.1,0.1))))


# image saver parameters
ImageSaver.file_format='png'
ImageSaver.time_format='%0.4d'

###########################################
# build simulation

base.min_print_level = base.MESSAGE

print "Creating simulation objects..."
s = topo.simulator.Simulator()

retina = InputSheet(input_generator=FuzzyLineFactory(),name='Retina')
retina2 = InputSheet(input_generator=FuzzyLineFactory(),name='Retina2')
V1 = CFSOM(name='V1')
V2 = CFSOM(name='V2')
save  = ImageSaver(name='CFSOM')

s.connect(retina,V1,delay=0.5,projection_params={'name':'R1toV1'})
s.connect(retina,V2,delay=0.5,projection_params={'name':'R1toV2'})
s.connect(retina2,V2,delay=0.5,projection_params={'name':'R2toV2'})

# Uncomment the connections to the image saver, to save all the activation
# images to disk.
#s.connect(retina,save,dest_port='retina',delay=2)
#s.connect(V1,save,dest_port='V1',delay=1)

#topo.gui.link_to_sim(s)

s.run(2)

#V1.projections['Retina'][0].plot_cfs()

# import profile,pstats
#
# p = profile.Profile()
# p.runctx('s.run(10)',locals(),globals())

#topo.gui.start(s)
