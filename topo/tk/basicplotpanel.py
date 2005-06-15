"""
Activity Panel bitmap plot.  Inherits and extends PlotPanel, while
using a BasicPlotGroup.  Many defaults of the other class allows this
class to be small.

$Id$
"""
from topo.tk.plotpanel import *

class BasicPlotPanel(PlotPanel):
    def __init__(self,parent,pengine=None,console=None,**config):
        PlotPanel.__init__(self,parent,pengine,console=console,plot_key='Activation',**config)
        self.refresh()

