"""
File saving routines for plots.

Currently unimplemented.  When implemented, will need to be able to save
the Plots in a PlotGroup into files on disk, choosing meaningful names
for each file.

$Id$
"""
__version__='$Revision$'



# * Incomplete & untested *



# you can use this to save images, though

# e.g.
#from topo.plotting.plotfilesaver import TemplatePlotGroupSaver; t = TemplatePlotGroupSaver('Orientation Preference'); t.save_images()
#from topo.plotting.plotfilesaver import TemplatePlotGroupSaver; t = TemplatePlotGroupSaver('Activity'); t.save_images()


# probably does all kinds of things you don't want, like updating the plots (re-measuring maps, etc)...

# The implementation and names of things will change, so if you use these classes you will have to update
# your code in the future...


import topo
from topo.base.parameterizedobject import ParameterizedObject,Parameter

from plotgroup import PlotGroup,TemplatePlotGroup
from templates import plotgroup_templates

class PlotGroupSaver(ParameterizedObject):

    file_format = Parameter(default="PNG")


# filename_format:
#  "topo.sim.name+'.'+topo.sim.time()+'.'+current_sheet+'.'+current_plot+'.'+current_unit'"
# (Eventually we could customize this to allow each template in topo/commands/analysis.py
# to have a nice short filename format.)

    #filename_format = Parameter

    def __init__(self,plotgroup_label,**params):
        super(PlotGroupSaver,self).__init__(**params)
        self.plotgroup_label = plotgroup_label
        self.plotgroup = self.generate_plotgroup()
        self.plotgroup.update_plots(True)

    def generate_plotgroup(self):
	return PlotGroup([])
 
    def save_to_disk(self):
        n = topo.sim.name
        t = topo.sim.time()
        for p,l in zip(self.plotgroup.plots,self.plotgroup.labels):
            name = "%s.%s.%s"%(n,t,l.replace('\n','.'))
            #print "outfile",name
            p.bitmap.image.save(name+".%s"%self.file_format,self.file_format)



class TemplatePlotGroupSaver(PlotGroupSaver):

    def __init__(self,pgt_name,**params):
        self.pgt = plotgroup_templates.get(pgt_name,None)
        super(TemplatePlotGroupSaver,self).__init__(pgt_name,**params)

    def generate_plotgroup(self):
	plotgroup = TemplatePlotGroup([],self.pgt,None)
	return plotgroup




### JABHACKALERT!
### 
### Not yet properly implemented; all the code in this file needs to
### be either implemented or removed.  The class ImageSaver in
### topo/tests/testcfsom.py might be of some help for inspiration.

## import topo
## import topo.base.parameterizedobject
## from topo.misc.utils import *

## from topo.commands.analysis import *

## from topo.plotting.templates import plotgroup_templates
## from topo.plotting.plotgroup import TemplatePlotGroup, ConnectionFieldsPlotGroup,ProjectionPlotGroup 



 
## class PlotFileSaver(topo.base.parameterizedobject.ParameterizedObject):
##     def __init__(self,**params):
##         super(PlotFileSaver,self).__init__(**params)
##         self.bitmaps = []
##         self.files = []
##         self.name = {'base':topo.sim.name, 'iteration':topo.sim.time(), \
##                     'presentation':'0', 'region':'', 'type':''}

##     def create_bitmaps(self):
##         raise NotImplementedError


##     def save_to_disk(self):
##         if self.bitmaps:
## 	    d = self.name
	  
##             for bitmap in self.bitmaps:               
##                 #self.message('Saving', filename)
## 		d['title']=bitmap.name
## 		filename = '%s.%06d.p%03d.%s_%s_%s.png' % \
##                            (d['base'], int(d['iteration']), \
##                            int(d['presentation']), d['region'], d['type'],d['title'])
## 		f = open(filename,'w')                           
##                 bitmap.image.save(f,"png")
## 	    f.close()
## 	    self.files.append(filename)




## class TemplateFile(PlotFileSaver):
##     def __init__(self,pgt_name,**params):

##         super(TemplateFile,self).__init__(**params)
##         self.pgt = plotgroup_templates.get(pgt_name,None)
##         self.name['region'] = 'All_region'
##         self.name['type'] = self.pgt.name
##         self.create_bitmaps()
##         self.save_to_disk()

##     def create_bitmaps(self):
		
## 	pg = plotgroup_dict.get(self.pgt.name,None)
## 	exec(self.pgt.command)
## 	if pg == None:
## 	    pg = TemplatePlotGroup(self.pgt.name,[],self.pgt.normalize,
## 				   self.pgt,None)
##         self.bitmaps = pg.load_images()
        



## class ActivityFile(PlotFileSaver):
##     def __init__(self,region=None,**params):
##         super(ActivityFile,self).__init__(**params)
##         self.region = region
##         self.name['region'] = region
##         self.name['type'] = 'Activity'
##         self.create_bitmaps()
##         self.save_to_disk()

##     def create_bitmaps(self):
	
## 	pgt = plotgroup_templates['Activity']
## 	pg = plotgroup_dict.get('Activity',None)
	
## 	if pg == None:
## 	    pgt = plotgroup_templates['Activity']
## 	    pg = TemplatePlotGroup('Activity',[],pgt.normalize,
## 				   pgt,None)
	    
##         self.bitmaps = pg.load_images()
	
        


## class UnitWeightsFile(PlotFileSaver):
##     def __init__(self,region,x,y,**params):
##         super(UnitWeightsFile,self).__init__(**params)
##         self.region = region
##         self.name['region'] = '%s_%01.03f_%01.03f' % (region, x, y)
##         self.name['type'] = 'Weights'
##         self.plotgroup_key = ('Weights',self.region,x,y)

##         self.create_bitmaps()
##         self.save_to_disk()

##     def create_bitmaps(self):

## 	pg = plotgroup_dict.get(self.plotgroup_key,None)	
## 	if pg == None:
## 	    pgt = plotgroup_templates['Connection Fields']
## 	    pg = ConnectionFieldsPlotGroup(self.plotgroup_key,[],pgt.normalize,
## 					   pgt,self.region)
			
	
##         self.bitmaps = pg.load_images()



## class ProjectionFile(PlotFileSaver):
##     def __init__(self,region,projection,density,**params):
##         super(ProjectionFile,self).__init__(**params)
##         self.region = region
##         self.name['region'] = '%s_%s' % (region, projection)
##         self.name['type'] = 'Projection'
##         self.plotgroup_key = ('Projection',projection,density,self.region)

##         self.create_bitmaps()
##         self.save_to_disk()


##     def create_bitmaps(self):

## 	pg = plotgroup_dict.get(self.plotgroup_key,None)	
## 	if pg == None:
## 	    pgt = plotgroup_templates['Projection']
## 	    pg = ProjectionPlotGroup(self.plotgroup_key,[],pgt.normalize,
## 				     pgt,self.region)

##         self.bitmaps = pg.load_images()
        

