#!/usr/bin/env python
"""

A simple example of how to use sheets.  Uses the ImageGenerator,
ImageSaver, Convolver, and ActivityCombiner classes.  Read the
in-line comments and code to see what it does.

'python image_example.py -h' for usage.

$Id$
"""

import sys
import debug
from convolve2d import Convolver
from image import ImageSaver,ImageGenerator
from simulator import Simulator
from sheet import Composer

from getopt import getopt
from Numeric import array

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
# set up the simulation
debug.print_level = debug.VERBOSE

s = Simulator(step_mode = step_mode)

#
# Make an image generator that gets its image from the command line
#
im_gen = ImageGenerator(filename = image_file)

#
# make a center-surround edge-detector kernel
#
off_center = array([[0, 1,0],
                    [1,-4,1],
                    [0, 1,0]])

#
#  two edge-detection sheets, one on-center, one off-center
#
on_convolve = Convolver( kernel = off_center * -1.0,  name="on_convolve")
off_convolve = Convolver( kernel = off_center,        name="off_convolve")

#
# an image saver, named 'output' which saves ppm files. we only need
# one -- inputs on different ports get saved with different names. 
#
output = ImageSaver(name = "output",
                    time_format = '%.3f',
                    file_format = 'jpeg',
                    pixel_scale = 255)    

#
# an activity combiner, with a 250 row x 700 column activity matrix
# The left port input  is placed at (-5,-5), the right port input at (5,5), in
# sheet coordinates
#
combine = Composer(matrix_shape = (250,700))
combine.port_configure('left', origin = (-5,-5))
combine.port_configure('right', origin = (5,5))

#
# Now add all the components to the simulator
#
s.add(im_gen, on_convolve, off_convolve, combine, output )

# make the connections
im_gen.connect_to(on_convolve, delay=1)
im_gen.connect_to(off_convolve,delay=1)

im_gen.connect_to(output,      dest_port='unmodified',delay=2)
on_convolve.connect_to(output, dest_port='on_center', delay=1)
off_convolve.connect_to(output,dest_port='off_center',delay=1)

# The on-center output goes to the left, off-center to the right
on_convolve.connect_to( combine, dest_port='left', delay=1)
off_convolve.connect_to(combine, dest_port='right',delay=1)

combine.connect_to(output,dest_port='combined',delay=1)

s.run()
