"""

A simple example of how to use sheets.  Uses the ImageGenerator,
ImageSaver,  and Combiner classes.  Read the
in-line comments and code to see what it does.

This differs from image_example.py in how it sets up the simulation
parameters and objects.  It shows how to set parameters for classes of objects.

'python image_example.py -h' for usage.

$Id$
"""


import sys
from topo import * 
from topo.image import *
from topo.composer import Composer

#################################################
# Set class parameter defaults

base.print_level = base.DEBUG

Simulator.step_mode = True

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



###############################################
# Make the simulator
s = Simulator()

###############################################
#  connect the objects

# The left image gets pasted at x = -0.25
s.connect(left_image,combine, delay=1,origin = (-0.25,0.0))

# The right image gets pasted at x = 0.25
s.connect(right_image,combine,delay=1,origin = (0.25,0.0))

s.connect(left_image,       output,      dest_port='left_input',delay=2)
s.connect(right_image,      output,      dest_port='right_input',delay=2)

s.connect(combine, output, dest_port='combined',delay=1)


##############################################
#  run it!
s.run(until=10)
