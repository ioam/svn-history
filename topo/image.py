"""
Sheets for generating, manipulating, and saving pixmap images.

This module defines Sheets for reading pixmap images from files and
converting them to activity matrices, and receiving activity matrices
and storing them as bitmap files.  The sheets use the Python Imaging
Library (PIL) to handle the pixmaps.

$Id$
"""

from Numeric import resize,array,zeros
from simulator import PulseGenerator,EventProcessor
from sheet import Sheet
from debug import Debuggable,VERBOSE
from params import setup_params
from utils import NxN

from pprint import *

import Image, ImageOps

class ImageGenerator(Sheet):
    """

    parameters:

      filename = The path to the image file.

    A sheet that reads a pixel map and uses it to generate an activity
    matrix.  The image is converted to grayscale and scaled to match
    the bounds and density of the sheet.

    ImageGenerator sheets are PulseGenerators, and hence can be set up to
    repeatedly generate output.  The pulse amplitude scales the
    output. See simulator.PulseGenerator for more details.

    """
    filename = None
    
    def __init__(self,**config):

        Sheet.__init__(self,**config)

        setup_params(self,ImageGenerator,**config)

        self.db_print("filename = " + self.filename)

        image = Image.open(self.filename)
        image = ImageOps.grayscale(image)
        image = image.resize(self.activation.shape)
        self.activation = resize(array([x for x in image.getdata()]),
                                 (image.size[1],image.size[0]))

	self.db_print("Initialized %s activation from %s" % (NxN(self.activation.shape),self.filename),
                      VERBOSE)
        max_val = float(max(max(self.activation)))
        self.activation = self.activation / max_val


    def start(self):

        self.send_output(data=self.activation)

    def input_event(self,src,src_port,dest_port,data):

        self.send_output(data=self.activation)


class ImageSaver(EventProcessor):
    """

    A Sheet that receives activity matrices and saves them as bitmaps.

    [should this really be a sheet?? it doesn't generate activity. -jp]

    Each time an ImageSaver sheet receives an input event on any input
    port, it saves it to a file.  The file name is determined by:

      <file_prefix><name>_<port>_<time>.<file_format>

    Where <name> is the name of the ImageSaver object, <port> is the
    name of the input port used, and <time> is the current simulation time.

    Parameters:
      file_prefix = (default '') A path or other prefix for the
                    filename.
      file_format = (default 'ppm') The file type to use when saving
                    the image. (can be any image format understood by PIL)
      time_format = (default '%f') The format string for the time.
      pixel_scale = (default 255) The amount to scale the
                     activity. Used as parameter to PIL's Image.putdata().
      pixel_offset = (default 0) The zero-offset for each pixel. Used as
                     parameter to PIL's Image.putdata()
                     
    """

    file_prefix = ''
    file_format = 'ppm'
    time_format = '%f'
    pixel_scale = 255
    pixel_offset = 0

    """
    Receives 2D activation matrices from other sheets, and saves them
    as image files.  This component can receive input on any arbitrary
    string-named port, and save that matrix as an image file of the
    given type.  The image file is named using the following
    convention:
 
         <file-prefix><component-name>_<port-name>_<sim-time>.<type>

    where <file-prefix> is an arbitrary prefix or path,
    <component-name> is the name of the image saver, <port-name> is
    the name of the port on which the input was received, <sim-time>
    is the simulation time at which the event was received, and <type>
    is the image file type

    Parameters:

    file_format = (string) The image file format (e.g. 'ppm', 'gif').  Can be
                  format understood by PIL. (default ppm)
    file_prefix = (string) The prefix or path for the
                  filename. (default "")
    time_format = (string) The format string for the simulation time
                  in the file name.  (default ('%f')
    pixel_scale = (number) The amount by which the activity values will
                  be scaled when converted to pixels.  Same as the
                  scale parameter of PIL.Image.putdata().  (default 255)
    pixel_offset = (number) The offset added to the activations when
                  converting to pixel values.  Same as the offset
                  paramter of PIL.Image.putdata().  (default 0)
    
    """

    file_prefix = ''
    file_format = 'ppm'
    time_format = '%f'
    pixel_scale = 255
    pixel_offset = 0

    def __init__(self,**config):

        EventProcessor.__init__(self,**config)

        setup_params(self,ImageSaver,**config)
            

    def input_event(self,src,src_port,dest_port,data):

        self.db_print("Received %s  input from %s" % (NxN(data.shape),src),VERBOSE)
        self.db_print("input max value = %d" % max(data.flat),VERBOSE)

        # assemble the filename
        filename = self.file_prefix + self.name
        if dest_port:
            filename += "_" + str(dest_port)
        filename += "_" + (self.time_format % self.simulator.time())
        filename += "." + self.file_format

        self.db_print("filename = '%s'" % filename, VERBOSE)
        
        # make and populate the image
        im = Image.new('L',(data.shape[1],data.shape[0]))
        self.db_print("image size = %s" % NxN(im.size), VERBOSE)
        im.putdata(data.flat,
                   scale=self.pixel_scale,
                   offset=self.pixel_offset)

        self.db_print("put image data.",VERBOSE)

        #save the image
        f = open(filename,'w')
        im.save(f,self.file_format)
        f.close()
        


        
        

    
