"""
File saving routines for plots.

Currently unimplemented.  When implemented, will need to be able to save
the Plots in a PlotGroup into files on disk, choosing meaningful names
for each file.

$Id$
"""
__version__='$Revision$'


### JABHACKALERT!
### 
### Not yet properly implemented; all the code in this file needs to
### be either implemented or removed.  The class ImageSaver in
### topo/tests/testcfsom.py might be of some help for inspiration.

import topo
import topo.base.topoobject
import topo.base.simulator
from topo.base.utils import *
from topo.plotting.templates import plotgroup_templates

import plotengine
 
class PlotFileSaver(topo.base.topoobject.TopoObject):
    def __init__(self,**config):
        super(PlotFileSaver,self).__init__(**config)
        self.sim = topo.base.simulator.get_active_sim()
        self.pe = plotengine.PlotEngine(self.sim)
        self.bitmaps = []
        self.files = []
        self.name = {'base':self.sim.name, 'iteration':self.sim.time(), \
                    'presentation':'0', 'region':'', 'type':''}

    def create_bitmaps(self):
        raise NotImplementedError

    def save_to_disk(self):
        if self.bitmaps:
            for i in range(len(self.bitmaps)):
                d = self.name
                filename = '%s.%06d.p%03d.%s_%s_%d.png' % \
                           (d['base'], int(d['iteration']), \
                           int(d['presentation']), d['region'], d['type'],i)
                           
                #self.message('Saving', filename)
                self.bitmaps[i].image.save(filename)
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
                                    plotgroup_templates['Activity'],
                                    'BasicPlotGroup',self.region)
        self.bitmaps = pg.load_images()
        


class UnitWeightsFile(PlotFileSaver):
    def __init__(self,region,x,y,**config):
        super(UnitWeightsFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%01.03f_%01.03f' % (region, x, y)
        self.name['type'] = 'Weights'
        self.plot_group_key = ('Weights',self.region,x,y)

        pt = plotgroup_templates['Unit Weights'].plot_templates['Unit Weights']
        pt.channels['Sheet_name'] = region
        pt.channels['Location'] = (x, y)

        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
        pg = self.pe.get_plot_group(self.plot_group_key,
                                    plotgroup_templates['Unit Weights'],
                                    'UnitWeightsPlotGroup',self.region)
        self.bitmaps = pg.load_images()



class ProjectionFile(PlotFileSaver):
    def __init__(self,region,projection,density,**config):
        super(ProjectionFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%s' % (region, projection)
        self.name['type'] = 'WeightsArray'
        self.plot_group_key = ('WeightsArray',projection,density)

        pt = plotgroup_templates['Projection'].plot_templates['Projection']
        
        pt.channels['Density'] = density
        pt.channels['Projection_name'] = region

        self.create_bitmaps()
        self.save_to_disk()


    def create_bitmaps(self):
        pg = self.pe.get_plot_group(self.plot_group_key,
                                    plotgroup_templates['Projection'],
                                    'ProjectionPlotGroup', self.region)
        pg.do_plot_cmd()
        self.bitmaps = pg.load_images()
        

