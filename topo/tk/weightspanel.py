"""
PMW WeightsPanel object for GUI visualization.

Subclasses RegionPlotPanel, which is basically a PlotPanel.

$Id$
"""
import __main__
from topo.tk.plotpanel import *
from topo.tk.regionplotpanel import *

class WeightsPanel(RegionPlotPanel):
    def __init__(self,parent,pengine,console=None,**config):
        super(WeightsPanel,self).__init__(parent,pengine,console,**config)

        # Receptive Fields are generally tiny.  Boost it up to 100 pixels.
        self.WEIGHT_PLOT_INITIAL_SIZE = 100

        self.x = 0
        self.x_str = StringVar()
        self.x_str.set(0.0)
        self.y = 0
        self.y_str = StringVar()
        self.y_str.set(0.0)

        self.panel_num = self.console.num_weights_windows

        self._add_xy_boxes()
        self.auto_refresh_checkbutton.invoke()

        self.refresh()


    def _add_xy_boxes(self):
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)

        Message(params_frame,text="X:",aspect=1000).pack(side=LEFT)
        Entry(params_frame,textvariable=self.x_str).pack(side=LEFT,expand=YES,fill=X)
        Message(params_frame,text="Y:",aspect=1000).pack(side=LEFT)
        Entry(params_frame,textvariable=self.y_str).pack(side=LEFT,expand=YES,fill=X,padx=5)


    def generate_plot_key(self):
        """
        The plot_key for the WeightsPanel will change depending on the
        input within the window widgets.  This means that the key
        needs to be regenerated at the appropriate times.

        Key Format:  Tuple: ('Weights', X_Number, Y_Number)
        """
        g = __main__.__dict__
        self.x = eval(self.x_str.get(),g)
        self.y = eval(self.y_str.get(),g)
        if isinstance(self.x,int): self.x = float(self.x)
        if isinstance(self.y,int): self.y = float(self.y)
        self.plot_key = ('Weights',self.x,self.y)


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotPanel's
        display_labels().
        """
        self.plot_group.configure(tag_text = 'Projection Plot')
        super(WeightsPanel,self).display_labels()
    
        
    def refresh_title(self):
        self.parent.title("Unit Weights %d. (x=%0.4f, y=%0.4f)" %
                          (self.panel_num,self.x, self.y))
