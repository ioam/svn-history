"""
CFSheetPlotPanel must be subclassed to be used.

Subclasses PlotPanel with additional buttons for Sheet access.

The Sheet menu was not included in PlotPanel itself, because it
depends on the CFSheet class.

$Id$
"""
from Tkinter import StringVar, Frame, LEFT, RIGHT, TOP, BOTTOM, YES, X
import Pmw
import plotpanel
import topo.cfsheet

### JABHACKALERT!
###
### This file should be renamed to cfsheetplotpanel.py.  I've already
### changed the class name from RegionPlotPanel to CFSheetPlotPanel,
### and the GUI label from Region to Sheet, because "Region" is too
### ambiguous, and is not a term that we have defined in Topographica.  

class CFSheetPlotPanel(plotpanel.PlotPanel):

    def __init__(self,parent,pengine,console=None,**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console,**config)

        self.region = StringVar()
        self.region.set('None')

        self._add_region_menu()


    def _add_region_menu(self):
        """
        This function adds a Sheet: menu that queries the active
        simulation for the list of options.  When an update is made,
        _region_refresh() is called.  It can either call the refresh()
        funcion, or update another menu, and so on.
        """
        self.__params_frame = Frame(master=self)
        self.__params_frame.pack(side=LEFT,expand=YES,fill=X)

        # Create the item list for CFSheet 'Sheet'  This will not change
        # since this window will only examine one Simulator.
        sim = self.console.active_simulator()
        self._sim_eps = [ep for ep in sim.get_event_processors()
                  if isinstance(ep,topo.cfsheet.CFSheet)]
        sim_ep_names = [ep.name for ep in self._sim_eps]
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

        # The GUI label says Sheet, not CFSheet, because users probably 
        # don't need to worry about the distinction.
        self.opt_menu = Pmw.OptionMenu(self.__params_frame,
                       command = self.region_refresh,
                       labelpos = 'w',
                       label_text = 'Sheet:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names)
        self.opt_menu.pack(side=LEFT)


    def region_refresh(self, sheet_name):
        """
        Only called by PMW.OptionMenu when the Sheet changes.  If
        auto_refresh is set, then refresh the plot.  Subclasses
        can either leave this the way it is, or redefine.
        """
        if self.auto_refresh:
            self.refresh()

