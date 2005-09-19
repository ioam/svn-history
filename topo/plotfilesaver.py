"""
File saving routines for plots.

STATUS 6/18/05: Little more than a stub, with one class that calls a
subroutine depending on the type of plot requested.  Not yet clear if
this class should be desined with the command-line interface in mind
(IE: minimal typing, function parameters, etc.)  Additional: With the
new Plot Template mechanism the plot_keys are not as critical as they
used to be.

Note: Inspiration may be found from the ImageSaver class written for
models.cfsom and currently (9/2005) residing in topo.image


$Id$
"""
import topo
import topo.base
import topo.plotengine
import topo.registry
from topo.utils import *

class PlotFileSaver(topo.base.TopoObject):
    def __init__(self,**config):
        super(PlotFileSaver,self).__init__(**config)
        self.sim = topo.registry.active_sim()
        self.pe = topo.plotengine.PlotEngine(self.sim)
        self.bitmaps = []
        self.files = []
        self.name = {'base':self.sim.name, 'iteration':self.sim.time(), \
                    'presentation':'0', 'region':'', 'type':''}

    def create_bitmaps(self):
        pass

    def save_to_disk(self):
        if self.bitmaps:
            for i in range(len(self.bitmaps)):
                d = self.name
                filename = '%s.%06d.p%03d.%s_%s_%d.png' % \
                           (d['base'], int(d['iteration']), \
                           int(d['presentation']), d['region'], d['type'],i)
                           
                #self.message('Saving', filename)
                self.bitmaps[i].bitmap.save(filename)
                self.files.append(filename)



class ActivityFile(PlotFileSaver):
    def __init__(self,region,**config):
        super(ActivityFile,self).__init__(**config)
        self.region = region
        self.name['region'] = region
        self.name['type'] = 'Activity'
        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
        pg = self.pe.get_plot_group('Activity',
                                    topo.plotengine.plotgroup_templates['Activity'],
                                    self.region)
        self.bitmaps = pg.load_images()
        


class UnitWeightsFile(PlotFileSaver):
    def __init__(self,region,x,y,**config):
        super(UnitWeightsFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%01.03f_%01.03f' % (region, x, y)
        self.name['type'] = 'Weights'
        self.plot_key = ('Weights',self.region,x,y)

        pt = topo.plotengine.plotgroup_templates['Unit Weights'].plot_templates['Unit Weights']
        pt.channels['Sheet_name'] = region
        pt.channels['Location'] = (x, y)

        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
        pg = self.pe.get_plot_group(self.plot_key,
                                    topo.plotengine.plotgroup_templates['Unit Weights'],
                                    self.region)
        self.bitmaps = pg.load_images()



class ProjectionFile(PlotFileSaver):
    def __init__(self,region,projection,density,**config):
        super(ProjectionFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%s' % (region, projection)
        self.name['type'] = 'WeightsArray'
        self.plot_key = ('WeightsArray',projection,density)

        pt = topo.plotengine.plotgroup_templates['Projection'].plot_templates['Projection']
        pt.channels['Density'] = density
        pt.channels['Projection_name'] = region

        self.create_bitmaps()
        self.save_to_disk()


    def create_bitmaps(self):
        pg = self.pe.get_plot_group(self.plot_key,
                                    topo.plotengine.plotgroup_templates['Projection'],
                                    self.region)
        pg.do_plot_cmd()
        self.bitmaps = pg.load_images()





### JABHACKALERT!
### 
### The code from here to the end of ImageSaver needs to be
### reworked into a proper mechanism for saving images.

# The class ImageSaver was originally written by Jeff, but now it
# should be replaced by a PlotFileSaver that will save a plot.
# Currently (9/05) only used by cfsom.py and a couple of test files.
from Numeric import resize,array,zeros
from simulator import EventProcessor
from sheet import Sheet
from parameter import Parameter
from utils import NxN
from pprint import *
import Image, ImageOps
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



    def input_event(self,src,src_port,dest_port,data):

        self.verbose("Received %s  input from %s" % (NxN(data.shape),src))
        self.verbose("input max value = %d" % max(data.flat))

        # assemble the filename
        filename = self.file_prefix + self.name
        if dest_port:
            filename += "_" + str(dest_port)
        filename += "_" + (self.time_format % self.simulator.time())
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
        

