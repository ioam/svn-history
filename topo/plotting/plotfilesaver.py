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
from topo.plotting.plotgroup import plotgroup_dict, BasicPlotGroup, UnitWeightsPlotGroup,ProjectionPlotGroup 

 
class PlotFileSaver(topo.base.topoobject.TopoObject):
    def __init__(self,**config):
        super(PlotFileSaver,self).__init__(**config)
        self.sim = topo.base.simulator.get_active_sim()
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
	
	pg = plotgroup_dict.get('Activity',None)
	
	if pg == None:
	    pgt = plotgroup_templates['Activity']
	    pg = BasicPlotGroup(self.sim,pgt,'Activity',
				None,[])

        self.bitmaps = pg.load_images()
        


class UnitWeightsFile(PlotFileSaver):
    def __init__(self,region,x,y,**config):
        super(UnitWeightsFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%01.03f_%01.03f' % (region, x, y)
        self.name['type'] = 'Weights'
        self.plot_group_key = ('Weights',self.region,x,y)

        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):

	pg = plotgroup_dict.get(self.plot_group_key,None)	
	if pg == None:
	    pgt = plotgroup_templates['Unit Weights']
	    pg = UnitWeightsPlotGroup(self.sim,pgt,self.plot_group_key,
				      self.region,[])
	
        self.bitmaps = pg.load_images()



class ProjectionFile(PlotFileSaver):
    def __init__(self,region,projection,density,**config):
        super(ProjectionFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%s' % (region, projection)
        self.name['type'] = 'Projection'
        self.plot_group_key = ('Projection',projection,density,self.region)

        pt = plotgroup_templates['Projection'].plot_templates['Projection']
        
        pt['Density'] = density
        pt['Projection_name'] = region

        self.create_bitmaps()
        self.save_to_disk()


    def create_bitmaps(self):

	pg = plotgroup_dict.get(self.plot_group_key,None)	
	if pg == None:
	    pgt = plotgroup_templates['Projection']
	    pg = ProjectionPlotGroup(self.sim,pgt,self.plot_group_key,
				self.region,[])

        pg.do_plot_cmd()
        self.bitmaps = pg.load_images()
        

