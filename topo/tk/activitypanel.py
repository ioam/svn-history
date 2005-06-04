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
        self.panel_num = self.console.num_activity_windows
        self.refresh()

    def refresh_title(self):
        self.parent.title("Activity %d" % self.panel_num)

    def do_plot_cmd(self):
        self.pe_group = self.pe.get_plot_group('Activation','ActivationPlotGroup')
        # This is a pass, so commented out: self.pe_group.do_plot_cmd()
        self.plots = self.pe_group.plots()

    def display_labels(self):
        """
        Change the grid group label, then call PlotPanel's display_labels()
        """
        self.plot_group.configure(tag_text = 'Activation')
        super(ActivityPanel,self).display_labels()

