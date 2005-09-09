"""
Activity Panel bitmap plot.  Inherits and extends PlotPanel, while
using a BasicPlotGroup.  Many defaults of the other class allows this
class to be small.

$Id$
"""
import plotpanel

### JABHACKALERT!
###
### The word "Activation" should henceforth not be used anywhere in
### the code.  We need to change all instances of "Activation" to
### "Activity" instead, to avoid confusing the user.  (Right now the
### main plot is called Activity in the menu, but shows up in a window
### labeled Activation, and so on.)  I think Activity is better than
### Activation, because Activation implies that something in
### particular activated the neurons, which is only usually (and not
### always) the case for such a plot.
class BasicPlotPanel(plotpanel.PlotPanel):
    def __init__(self,parent,pengine=None,console=None,plot_key='Activity',**config):
        plotpanel.PlotPanel.__init__(self,parent,pengine,console=console,plot_key=plot_key,**config)
        self.refresh()

