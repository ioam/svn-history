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

debug.print_level = debug.VERBOSE

Simulator.step_mode = step_mode

# There's just one image generator, so we can set it's input as a class param
ImageGenerator.filename = image_file

# An off-center edge-detector kernel
Convolver.kernel = array([[0, 1,0],
                          [1,-4,1],
                          [0, 1,0]])

# Image saver parameters
ImageSaver.file_format = 'jpeg'
ImageSaver.time_format = '%.2f'
ImageSaver.pixel_scale = 255

#
Composer.matrix_shape = (250,700)


#################################################
# Now make the objects

im_gen = ImageGenerator()
off_convolve = Convolver()
on_convolve = Convolver()
combine = Composer()
output = ImageSaver()


################################################
# Set instance-specific parameters
on_convolve.kernel = Convolver.kernel * -1.0

combine.port_configure('left', origin = (-5,-5))
combine.port_configure('right', origin = (5,5))

###############################################
# Make the simulator
s = Simulator()

###############################################
#  connect the objects
s.connect(im_gen,on_convolve, delay=1)
s.connect(im_gen,off_convolve,delay=1)

s.connect(im_gen,       output,      dest_port='unmodified',delay=2)
s.connect(on_convolve,  output,      dest_port='on_center', delay=1)
s.connect(off_convolve, output,      dest_port='off_center',delay=1)

# The on-center output goes to the left, off-center to the right
s.connect(on_convolve, combine, dest_port='left', delay=1)
s.connect(off_convolve,combine, dest_port='right',delay=1)

s.connect(combine, output, dest_port='combined',delay=1)


##############################################
#  run it!

s.run()
