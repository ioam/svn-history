"""
See test_cfsom(self) and ImagePoster for an example of how to use and call
the PlotEngine system from a simulation.

$Id$
"""
__version__='$Revision$'

import unittest
from topo.sheets.cfsom import CFSOM
from pprint import pprint
from topo.plotting import plot
from topo.base import parameterizedobject
from topo.plotting.bitmap import *
from topo.base.sheet import Sheet
from topo.sheets.generatorsheet import *
from topo.base.simulation import *
from topo.base import patterngenerator
import topo.patterns.basic
from math import pi
from topo.base.parameterclasses import Dynamic, Parameter
import random
import topo.base.parameterizedobject
from topo.base.cf import CFProjection
from topo.learningfns.som import HebbianSOMLF
import pdb #debugger


### Only for ImageSaver
from Numeric import resize,array,zeros
from topo.base.simulation import EventProcessor
from topo.misc.utils import NxN
from pprint import *
import Image, ImageOps


### JABALERT: The ImageSaver class should probably be deleted,
### but it is currently used in this test.
class ImageSaver(EventProcessor):
    """

    A Sheet that receives activity matrices and saves them as bitmaps.
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

    file_prefix = Parameter('')
    file_format = Parameter('ppm')
    time_format = Parameter('%f')
    pixel_scale = Parameter(255)
    pixel_offset = Parameter(0)



    def input_event(self,conn,data):

        self.verbose("Received %s  input from %s" % (NxN(data.shape),conn.src))
        self.verbose("input max value = %d" % max(data.flat))

        # assemble the filename
        filename = self.file_prefix + self.name
        if conn.dest_port:
            filename += "_" + str(conn.dest_port)
        filename += "_" + (self.time_format % self.simulation.time())
        filename += "." + self.file_format

        self.verbose("filename = '%s'" % filename)
        
        # make and populate the image
        im = Image.new('L',(data.shape[1],data.shape[0]))
        self.verbose("image size = %s" % NxN(im.size))
        im.putdata(data.flat,
                   scale=self.pixel_scale,
                   offset=self.pixel_offset)

        self.verbose("put image data.")

        #save the image
        f = open(filename,'w')
        im.save(f,self.file_format)
        f.close()



class TestCFSom(unittest.TestCase):

    def setUp(self):
        self.s = Simulation(step_mode = True)
        self.sheet1 = Sheet()
        self.sheet2 = Sheet()


# CEBHACKALERT: replace with an equivalent example that uses Image
##     def test_imagegenerator(self):
##         """
##         Code moved from __main__ block of cfsom.py.  Gives a tight example
##         of running a cfsom simulation.
##         """
##         from testsheetview import ImageGenerator
        
##         s = Simulation(step_mode=True)

##         ImageGenerator.density = 100
##         ImageGenerator.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))
##         input = ImageGenerator(filename='examples/ellen_arthur.pgm')
    
    
##         save = ImageSaver(pixel_scale=1.5)
##         som = CFSOM()
        
##         s.add(som,input,save)
##         s.connect(input,som,connection_type=CFProjection,learning_fn=HebbianSOMLF())
##         s.connect(som,save)
##         s.run(duration=10)
    


    def test_cfsom(self):
        """
        """
        # input generation params
        GeneratorSheet.period = 1.0
        GeneratorSheet.density = 5
        GeneratorSheet.print_level = topo.base.parameterizedobject.WARNING
        
        topo.patterns.basic.Gaussian.x = Dynamic(lambda : random.uniform(-0.5,0.5))
        topo.patterns.basic.Gaussian.y = Dynamic(lambda : random.uniform(-0.5,0.5))        
        topo.patterns.basic.Gaussian.orientation = Dynamic(lambda :random.uniform(-pi,pi))
        
        gaussian_width = 0.02
        gaussian_height = 0.9
        topo.patterns.basic.Gaussian.scale = gaussian_height
        topo.patterns.basic.Gaussian.aspect_ratio = gaussian_width/gaussian_height
        topo.patterns.basic.Gaussian.bounds = BoundingBox(points=((-0.8,-0.8),(0.8,0.8)))

        # cf som parameters
        CFSOM.density = 5
        CFSOM.learning_length = 10000
        CFSOM.radius_0 = 0.1

        ###########################################
        # build simulation
        
        topo.base.parameterizedobject.min_print_level = topo.base.parameterizedobject.WARNING
      
        s = Simulation()
        s.verbose("Creating simulation objects...")
        s['retina']=GeneratorSheet(input_generator=topo.patterns.basic.Gaussian())
        
        s['V1'] = CFSOM()
        s['V1'].print_level = topo.base.parameterizedobject.WARNING

        s.connect('retina','V1',delay=1,connection_type=CFProjection,
                  learning_fn=HebbianSOMLF())
        s.print_level = topo.base.parameterizedobject.WARNING

        self.assertTrue(topo.sim['V1'].projections().get('retinaToV1',None) != None)
        self.assertTrue(topo.sim['V1'].projections().get('retinaToV1',None) != None)
        s.run(10)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestCFSom))
