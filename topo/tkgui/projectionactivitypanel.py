"""
ProjectionActivity object for GUI visualization.

Subclasses CFSheetPlotPanel, which is basically a PlotGroupPanel.


"""


import Pmw
import __main__

from Tkinter import StringVar, BooleanVar, Frame, TOP, LEFT, YES, X, Message
from Tkinter import Entry, Label, NSEW, Checkbutton, NORMAL, DISABLED

import topo

from templateplotgrouppanel import TemplatePlotGroupPanel
from topo.base.projection import ProjectionSheet
from topo.plotting.plotgroup import ProjectionActivityPlotGroup
from topo.base.sheet import Sheet
import topoconsole
import topo.base.cf

from topo.commands.analysis import *
import topo.commands.analysis

### JABALERT: Should pull out common code from ProjectionActivityPanel,
### ProjectionPanel, and ConnectionFieldsPanel into a shared parent
### class.  Then those classes should probably all be in one file.
class ProjectionActivityPanel(TemplatePlotGroupPanel):
    def __init__(self,parent,console=None,pgt_name=None,**config):       

        self.region = StringVar()
	TemplatePlotGroupPanel.__init__(self,parent,console,pgt_name,**config)

	self.plotgroup_key='ProjectionActivity'
        self.__params_frame = Frame(master=self)
        self.__params_frame.pack(side=LEFT,expand=YES,fill=X)


	self._add_region_menu()
	self.cmdname = update_projectionactivity()

        self.auto_refresh.set(True)
        self.set_auto_refresh()

	self.refresh()
	

    def _add_region_menu(self):
        """
        This function adds a Sheet: menu that queries the active
        simulation for the list of options.  When an update is made,
        _region_refresh() is called.  It can either call the refresh()
        funcion, or update another menu, and so on.
        """
        # Create the item list for CFSheet 'Sheet'  This will not change
        # since this window will only examine one Simulation.
        self._sim_eps = [ep for ep in topo.sim.objects(Sheet).values()
                  if isinstance(ep,topo.base.cf.CFSheet)]
	self._sim_eps.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        sim_ep_names = [ep.name for ep in self._sim_eps]
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

        # The GUI label says Sheet, not CFSheet, because users probably 
        # don't need to worry about the distinction.
        self.opt_menu = Pmw.OptionMenu(self.__params_frame,
                       command = self.refresh,
                       labelpos = 'w',
                       label_text = 'Sheet:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names)
        self.opt_menu.pack(side=LEFT)
        # Should be shared with projectionpanel
        self.balloon.bind(self.opt_menu,"""CFSheet whose unit(s) will be plotted.""")






    @staticmethod
    def valid_context():
        """
        Only open if there are Projections defined.
        """
        projectionsheets=topo.sim.objects(ProjectionSheet).values()
        if not projectionsheets:
            return False

        projections=[i.projections().values() for i in projectionsheets]
        return (not projections == [])


    ### JABALERT: This looks like too much intelligence to include in
    ### the GUI code; this function should probably just be calling a
    ### PlotGroup (or subclass) function to generate the key.  This
    ### file should have only GUI-specific stuff.
  
    def update_plotgroup_variables(self):

	self.plotgroup.sheet_name = self.region.get()



    def generate_plotgroup(self):
        """
        Create the right Plot Key that will define the needed
        information for a ProjectionActivityPlotGroup.  This is the key-word
        'ProjectionActivity'.  Once the
        PlotGroup is created, call its do_plot_cmd() to prepare
        the Plot objects.
        """

	plotgroup = ProjectionActivityPlotGroup([],self.pgt,self.region.get(),
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

    



