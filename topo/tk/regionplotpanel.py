"""
VIRTUAL RegionPlotPanel class that subclasses PlotPanel with
additional buttons for Region access.

Not included in PlotPanel, because this class knows about, and
requires, the RFSheet class.

$Id$
"""
from topo.tk.plotpanel import *
import topo.rfsheet

class RegionPlotPanel(PlotPanel):

    def __init__(self,parent,pengine,console=None,**config):
        PlotPanel.__init__(self,parent,pengine,console,**config)

        self.region = StringVar()
        self.region.set('None')

        self._add_region_menu()


    def _add_region_menu(self):
        """
        This function adds a Region: menu that queries the active
        simulation for the list of options.  When an update is made,
        _region_refresh() is called.  It can either call the refresh()
        funcion, or update another menu, and so on.
        """
        self.params_frame2 = Frame(master=self)
        self.params_frame2.pack(side=BOTTOM,expand=YES,fill=X)

        # Create the item list for RFSheet 'Region'  This will not change
        # since this window will only examine one Simulator.
        sim = self.console.active_simulator()
        self._sim_eps = [ep for ep in sim.get_event_processors()
                  if isinstance(ep,topo.rfsheet.RFSheet)]
        sim_ep_names = [ep.name for ep in self._sim_eps]
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

        self.opt_menu = Pmw.OptionMenu(self.params_frame2,
                       command = self.region_refresh,
                       labelpos = 'w',
                       label_text = 'Region:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names)
        self.opt_menu.pack(side=LEFT)


    def region_refresh(self, sheet_name):
        """
        Only called by PMW.OptionMenu when the Region changes.  If
        auto_refresh is set, then refresh the plot.  Subclasses
        can either leave this the way it is, or redefine.
        """
        if self.auto_refresh:
            self.refresh()
