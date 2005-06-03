"""
File saving routines for plots.

STATUS 6/18/05: Little more than a stub, with one class that calls a
subroutine depending on the type of plot requested.  Not yet clear if
this class should be desined with the command-line interface in mind
(IE: minimal typing, function parameters, etc.)

$Id$
"""
import topo
import topo.base
import topo.plotengine
from topo.utils import *

class PlotFileSaver(topo.base.TopoObject):
    def __init__(self,**config):
        super(PlotFileSaver,self).__init__(**config)
        self.sim = topo.simulator.active_sim()
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
                filename = '%s.%06d.p%03d.%s_%s_%d.jpg' % \
                           (d['base'], int(d['iteration']), \
                           int(d['presentation']), d['region'], d['type'],i)
                           
                #self.message('Saving', filename)
                self.bitmaps[i].bitmap.save(filename)
                self.files.append(filename)



class ActivationFile(PlotFileSaver):
    def __init__(self,region,**config):
        super(ActivationFile,self).__init__(**config)
        self.region = region
        self.name['region'] = region
        self.name['type'] = 'Activity'
        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
        pg = self.pe.get_plot_group('Activation','ActivationPlotGroup',
                                    self.region)
        self.bitmaps = pg.load_images()
        


class WeightsFile(PlotFileSaver):
    def __init__(self,region,x,y,**config):
        super(WeightsFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%01.03f_%01.03f' % (region, x, y)
        self.name['type'] = 'Weights'
        self.plot_key = ('Weights',x,y)
        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
        pg = self.pe.get_plot_group(self.plot_key,
                                    'WeightsPlotGroup',
                                    self.region)
        self.bitmaps = pg.load_images()



class WeightsArrayFile(PlotFileSaver):
    def __init__(self,region,projection,density,**config):
        super(WeightsArrayFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%s' % (region, projection)
        self.name['type'] = 'WeightsArray'
        self.plot_key = ('WeightsArray',projection,density)
        self.create_bitmaps()
        self.save_to_disk()


    def create_bitmaps(self):
        pg = self.pe.get_plot_group(self.plot_key,
                                    'WeightsArrayPlotGroup',
                                    self.region)
        pg.do_plot_cmd()
        self.bitmaps = pg.load_images()



