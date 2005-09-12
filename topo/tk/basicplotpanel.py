"""
Activity Panel bitmap plot.  Inherits and extends PlotPanel, while
using a BasicPlotGroup.  Many defaults of the other class allows this
class to be small.

$Id$
"""
import plotpanel

class BasicPlotPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine=None,console=None,plot_key='Activity',**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console=console,plot_key=plot_key,**config)
        self.refresh()

