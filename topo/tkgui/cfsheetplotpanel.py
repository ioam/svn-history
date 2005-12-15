"""
CFSheetPlotPanel must be subclassed to be used.

Subclasses PlotGroupPanel with additional buttons for Sheet access.

The Sheet menu was not included in PlotGroupPanel itself, because it
depends on the CFSheet class.

$Id$
"""
__version__='$Revision$'

from Tkinter import StringVar, Frame, LEFT, RIGHT, TOP, BOTTOM, YES, X, Checkbutton, DISABLED
from topo.base.sheet import Sheet
import Pmw
import plotgrouppanel
import topo.base.connectionfield
import topoconsole

### JCALERT! It might be clearer to get rid of this class and just add its functionnality
### to both projectionpanel and unitweightpanel. Or it might need another name that
### make you understand what it does (i.e. take care of the sheet menu and enable to switch
### from what sheet to another by modifying the attribute region).

class CFSheetPlotPanel(plotgrouppanel.PlotGroupPanel):

    def __init__(self,parent,pengine,console,**config):
        plotgrouppanel.PlotGroupPanel.__init__(self,parent,pengine,console,**config)

        self.region = StringVar()
        self.region.set('None')

        self.__params_frame = Frame(master=self)
        self.__params_frame.pack(side=LEFT,expand=YES,fill=X)

        self._add_situate_button()
        self._add_region_menu()
        


    def _add_region_menu(self):
        """
        This function adds a Sheet: menu that queries the active
        simulation for the list of options.  When an update is made,
        _region_refresh() is called.  It can either call the refresh()
        funcion, or update another menu, and so on.
        """

        # Create the item list for CFSheet 'Sheet'  This will not change
        # since this window will only examine one Simulator.
        sim = topoconsole.active_sim()
        self._sim_eps = [ep for ep in sim.objects(Sheet).values()
                  if isinstance(ep,topo.base.connectionfield.CFSheet)]
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

    def _add_situate_button(self):
        
        self.situate = 0
        self.situate_checkbutton = Checkbutton(self.__params_frame,
                                                    text="Situate",
                                                    command=self.toggle_situate)
        self.situate_checkbutton.pack(side=LEFT)

    def toggle_situate(self):
        """Set the attribute situate"""
        self.situate = not self.situate
        if self.pe_group != None:
            self.pe_group.set_situate(self.situate)
        self.initial_plot = True
        self.zoom_factor = self.min_zoom_factor = 1
        self.refresh()

    def region_refresh(self, sheet_name):
        """
        Only called by PMW.OptionMenu when the Sheet changes.  Subclasses
        can either leave this the way it is, or redefine.
        """
        # When comfortable about the refresh behavior, remove this
        # commented code.
        #if self.auto_refresh: self.refresh()
        self.refresh()

    
