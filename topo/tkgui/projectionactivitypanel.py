"""
ProjectionActivity object for GUI visualization.

Subclasses CFSheetPlotPanel, which is basically a PlotGroupPanel.


"""


import Pmw
import __main__

from Tkinter import StringVar, BooleanVar, Frame, TOP, LEFT, YES, X, Message
from Tkinter import Entry, Label, NSEW, Checkbutton, NORMAL, DISABLED

import topo

from topo.base.projection import ProjectionSheet
from topo.plotting.plotgroup import ProjectionActivityPlotGroup
from topo.base.sheet import Sheet

import topo.base.cf

from topo.commands.analysis import *
import topo.commands.analysis

from projectionpanel import SomethingPanel

### JABALERT: Should pull out common code from ProjectionActivityPanel,
### ProjectionPanel, and ConnectionFieldsPanel into a shared parent
### class.  Then those classes should probably all be in one file.
class ProjectionActivityPanel(SomethingPanel):
    def __init__(self,console=None,pgt_name=None,**params):       


        super(ProjectionActivityPanel,self).__init__(console,pgt_name,**params)

	self.plotgroup_key='ProjectionActivity'


	self.cmdname = update_projectionactivity()


	self.refresh()
	

    # CEBALERT! Dynamic info doesn't work on projection activity windows!
    # e.g. on hierarchical there is an error, on cfsom the dynamic info stops
    # half way across the plot...
    # So, dynamic info is disabled for now in proj. act. windows.
    # This will be easier to fix when the class hierarchy is cleaned up
    # (if it is still a problem then).
    def _update_dynamic_info(self,e):
        self.messageBar.message('state',"")






    @staticmethod
    def valid_context():
        """
        Only open if there are Projections defined.
        """
        projectionsheets=topo.sim.objects(ProjectionSheet).values()
        if not projectionsheets:
            return False

        projections=[proj_sheet.in_connections for proj_sheet in projectionsheets]
        return (not projections == [])


    ### JABALERT: This looks like too much intelligence to include in
    ### the GUI code; this function should probably just be calling a
    ### PlotGroup (or subclass) function to generate the key.  This
    ### file should have only GUI-specific stuff.
  
    def update_plotgroup_variables(self):

	self.plotgroup.sheet_name = self.sheet_var.get()



    def generate_plotgroup(self):
        """
        Create the right Plot Key that will define the needed
        information for a ProjectionActivityPlotGroup.  This is the key-word
        'ProjectionActivity'.  Once the
        PlotGroup is created, call its do_plot_cmd() to prepare
        the Plot objects.
        """

	plotgroup = ProjectionActivityPlotGroup([],self.pgt,self.sheet_var.get(),
                                              normalize=self.normalize.get(),
                                              sheetcoords=self.sheetcoords.get(),
                                              integerscaling=self.integerscaling.get())
	return plotgroup


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotGroupPanel's
        display_labels().
        """
        new_title = 'Projection Activity of ' + self.plotgroup.sheet_name + ' at time ' + str(self.plotgroup.time)
        self.plot_group_title.configure(tag_text = new_title)
        super(ProjectionActivityPanel,self).display_labels()

    



