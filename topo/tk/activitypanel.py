"""
ActivityPanel bitmap plot.  Inherits and extends PlotPanel.

$Id$
"""
from topo.tk.plotpanel import *

class ActivityPanel(PlotPanel):
    def __init__(self,parent,pengine=None,console=None,**config):
        PlotPanel.__init__(self,parent,pengine,console=console,**config)
        self.INITIAL_PLOT_WIDTH = 60
        self.panel_num = self.console.num_activity_windows
        self.generate_plot_key()
        self.refresh()


    def refresh_title(self):
        self.parent.title("Activity %d" % self.panel_num)


    def generate_plot_key(self):
        self.plot_key = 'Activation'
    

    def do_plot_cmd(self):
        """
        This instantiation asks the PlotEngine for the plotgroup
        linked to self.plot_key.  Since get_plot_group() is being
        called, it may update the plots, or it may use a cached
        version, depending on the type of PlotGroup being requested.
        """ 
        self.pe_group = self.pe.get_plot_group(self.plot_key)
        self.plots = self.pe_group.plots()


    def display_labels(self):
        """
        Change the grid group label, then call PlotPanel's display_labels()
        """
        self.plot_group.configure(tag_text = 'Activation')
        super(ActivityPanel,self).display_labels()

