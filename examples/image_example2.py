"""

A simple example of how to use sheets.  Uses the ImageGenerator,
ImageSaver, Convolver, and ActivityCombiner classes.  Read the
in-line comments and code to see what it does.

This differs from image_example.py in how it sets up the simulation
parameters and objects.  It shows how to set parameters for classes of objects.

'python image_example2.py -h' for usage.

$Id$
"""


import sys
from topo.convolve2d import *
from topo.image import *
from topo.sheet import Composer

from getopt import getopt

USAGE = """

usage: image_example.py [--step] image-file

image-file = an image file to be convolved, etc.

--step puts the simulator in step mode.

"""
##################################################
# read and process command line arguments
try:    
    opts,args = getopt(sys.argv[1:],'',['step'])
except:
    print USAGE
    sys.exit()

opts = dict(opts)

#
# whether to run in step mode
#
step_mode = '--step' in opts

if not args or len(args) > 1:
    print USAGE
    sys.exit()

image_file = args[0]


#################################################
# Set class parameter defaults

base.print_level = base.DEBUG

Simulator.step_mode = step_mode

# We want 100x100 images
ImageGenerator.density = 10000

# Image saver parameters
ImageSaver.file_format = 'jpeg'
ImageSaver.time_format = '%.2f'
ImageSaver.pixel_scale = 255

#
Composer.density = 25600


#################################################
# Now make the objects

left_image = ImageGenerator(filename='main.ppm')
right_image = ImageGenerator(filename='test.ppm')
combine = Composer()
output = ImageSaver()


################################################
# Set instance-specific parameters
combine.port_configure('left', origin = (-0.25,0.0))
combine.port_configure('right', origin = (0.25,0.0))

###############################################
# Make the simulator
s = Simulator()

###############################################
#  connect the objects
s.connect(left_image,combine, dest_port='left', delay=1)
s.connect(right_image,combine,dest_port='right',delay=1)

s.connect(left_image,       output,      dest_port='left_input',delay=2)
s.connect(right_image,      output,      dest_port='right_input',delay=2)

s.connect(combine, output, dest_port='combined',delay=1)


##############################################
#  run it!


s.run(until=10)
