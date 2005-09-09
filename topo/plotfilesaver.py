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
                filename = '%s.%06d.p%03d.%s_%s_%d.png' % \
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
        pg = self.pe.get_plot_group('Activation',
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



