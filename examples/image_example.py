"""

A simple non-neural example of how to use sheets.  Uses the
ImageGenerator, ImageSaver, and Combiner classes.  Read the in-line
comments and code to see what it does. Run this script from the parent
directory as:

  ./topographica examples/image_example.py

Output will be in files name ImageSaver.*.

$Id$
"""

import sys
from topo import * 
from topo.patterngenerator import *
from topo.sheets.composer import Composer
from topo.plotfilesaver import ImageSaver

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

left_image = ImageGenerator(filename='examples/main.ppm')
right_image = ImageGenerator(filename='examples/test.ppm')
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
