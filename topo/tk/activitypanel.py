"""
ActivityPanel bitmap plot.  Inherits and extends PlotPanel, while
using an ActivationPlotGroup.  Many defaults of the other classes
allows this class to be small.

$Id$
"""
from topo.tk.plotpanel import *

class ActivityPanel(PlotPanel):
    def __init__(self,parent,pengine=None,console=None,**config):
        PlotPanel.__init__(self,parent,pengine,console=console,**config)
        self.INITIAL_PLOT_WIDTH = 60
        self.plot_key = 'Activation'
        self.plotgroup_type = 'ActivationPlotGroup'
        self.plot_group.configure(tag_text = str(self.plot_key))
        self.panel_num = self.console.num_activity_windows
        self.refresh()

