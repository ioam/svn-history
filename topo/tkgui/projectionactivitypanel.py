"""
ProjectionActivityPanel
"""


import topo
from topo.plotting.plotgroup import ProjectionActivityPlotGroup
from topo.commands.analysis import update_projectionactivity
from projectionpanel import ProjectionSheetPGPanel


### JABALERT: Should pull out common code from ProjectionActivityPanel,
### ProjectionPanel, and ConnectionFieldsPanel into a shared parent
### class.  Then those classes should probably all be in one file.
class ProjectionActivityPanel(ProjectionSheetPGPanel):

    plotgroup_type = ProjectionActivityPlotGroup
    
    
    def __init__(self,console,master,pgt,**params):       
        super(ProjectionActivityPanel,self).__init__(console,master,pgt,**params)
        self.auto_refresh = True
        # CB: why do we do this?
	self.plotgroup_label='ProjectionActivity'
	

    # CEBALERT! Dynamic info doesn't work on projection activity windows!
    # e.g. on hierarchical there is an error, on cfsom the dynamic info stops
    # half way across the plot...
    # So, dynamic info is disabled for now in proj. act. windows.
    # This will be easier to fix when the class hierarchy is cleaned up
    # (if it is still a problem then).
    def _update_dynamic_info(self,e):
        self.messageBar.message('state',"")


    def sheet_change(self):
        self.refresh() 


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotGroupPanel's
        display_labels().
        """
        new_title = 'Projection Activity of ' + self.plotgroup.sheet.name + ' at time ' + str(self.plotgroup.time)
        self.plot_group_title.configure(tag_text = new_title)
        super(ProjectionActivityPanel,self).display_labels()

    



