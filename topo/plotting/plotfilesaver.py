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
import topo.base.parameterizedobject
from topo.misc.utils import *

from topo.commands.analysis import *

from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import plotgroup_dict, TemplatePlotGroup, ConnectionFieldsPlotGroup,ProjectionPlotGroup 

 
class PlotFileSaver(topo.base.parameterizedobject.ParameterizedObject):
    def __init__(self,**config):
        super(PlotFileSaver,self).__init__(**config)
        self.bitmaps = []
        self.files = []
        self.name = {'base':topo.sim.name, 'iteration':topo.sim.time(), \
                    'presentation':'0', 'region':'', 'type':''}

    def create_bitmaps(self):
        raise NotImplementedError


    def save_to_disk(self):
        if self.bitmaps:
	    d = self.name
	  
            for bitmap in self.bitmaps:               
                #self.message('Saving', filename)
		d['title']=bitmap.name
		filename = '%s.%06d.p%03d.%s_%s_%s.png' % \
                           (d['base'], int(d['iteration']), \
                           int(d['presentation']), d['region'], d['type'],d['title'])
		f = open(filename,'w')                           
                bitmap.image.save(f,"png")
	    f.close()
	    self.files.append(filename)




class TemplateFile(PlotFileSaver):
    def __init__(self,pgt_name,**config):

        super(TemplateFile,self).__init__(**config)
        self.pgt = plotgroup_templates.get(pgt_name,None)
        self.name['region'] = 'All_region'
        self.name['type'] = self.pgt.name
        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
		
	pg = plotgroup_dict.get(self.pgt.name,None)
	exec(self.pgt.command)
	if pg == None:
	    pg = TemplatePlotGroup(self.pgt.name,[],self.pgt.normalize,
				   self.pgt,None)
        self.bitmaps = pg.load_images()
        



class ActivityFile(PlotFileSaver):
    def __init__(self,region=None,**config):
        super(ActivityFile,self).__init__(**config)
        self.region = region
        self.name['region'] = region
        self.name['type'] = 'Activity'
        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):
	
	pgt = plotgroup_templates['Activity']
	pg = plotgroup_dict.get('Activity',None)
	
	if pg == None:
	    pgt = plotgroup_templates['Activity']
	    pg = TemplatePlotGroup('Activity',[],pgt.normalize,
				   pgt,None)
	    
        self.bitmaps = pg.load_images()
	
        


class UnitWeightsFile(PlotFileSaver):
    def __init__(self,region,x,y,**config):
        super(UnitWeightsFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%01.03f_%01.03f' % (region, x, y)
        self.name['type'] = 'Weights'
        self.plotgroup_key = ('Weights',self.region,x,y)

        self.create_bitmaps()
        self.save_to_disk()

    def create_bitmaps(self):

	pg = plotgroup_dict.get(self.plotgroup_key,None)	
	if pg == None:
	    pgt = plotgroup_templates['Connection Fields']
	    pg = ConnectionFieldsPlotGroup(self.plotgroup_key,[],pgt.normalize,
					   pgt,self.region)
			
	
        self.bitmaps = pg.load_images()



class ProjectionFile(PlotFileSaver):
    def __init__(self,region,projection,density,**config):
        super(ProjectionFile,self).__init__(**config)
        self.region = region
        self.name['region'] = '%s_%s' % (region, projection)
        self.name['type'] = 'Projection'
        self.plotgroup_key = ('Projection',projection,density,self.region)

        self.create_bitmaps()
        self.save_to_disk()


    def create_bitmaps(self):

	pg = plotgroup_dict.get(self.plotgroup_key,None)	
	if pg == None:
	    pgt = plotgroup_templates['Projection']
	    pg = ProjectionPlotGroup(self.plotgroup_key,[],pgt.normalize,
				     pgt,self.region)

        self.bitmaps = pg.load_images()
        

