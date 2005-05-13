"""
PMW WeightsPanel object for GUI visualization.

Subclasses RegionPlotPanel, which is basically a PlotPanel.

$Id$
"""
import __main__
import Tkinter
from topo.tk.plotpanel import *
from topo.tk.regionplotpanel import *

class WeightsPanel(RegionPlotPanel):
    def __init__(self,parent,pengine,console=None,**config):
        super(WeightsPanel,self).__init__(parent,pengine,console,**config)

        # Receptive Fields are generally tiny.  Boost it up to make it visible.
        self.WEIGHT_PLOT_INITIAL_SIZE = 30

        self.x = 0
        self.x_str = StringVar()
        self.x_str.set(0.0)
        self.y = 0
        self.y_str = StringVar()
        self.y_str.set(0.0)
        self.displayed_x, self.displayed_y = 0, 0

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

        ep = [ep for ep in self.console.active_simulator().get_event_processors()
              if ep.name == self.region.get()][0]
        # This assumes that displaying the rectangle information is enough.
        l,b,r,t = ep.bounds.aarect().lbrt()

        # BUG WORKAROUND.  Bounding regions are currently (5/2005) consistent
        # with reporting edge conditions.  getting a unit at 0.5 when the
        # bounds ends at 0.5, will return an error, but bounds.contains(0.5,0.5)
        # will return true.

        if ep.bounds.contains(self.x,self.y):
            self.plot_key = ('Weights',self.x,self.y)
            self.displayed_x, self.displayed_y = self.x, self.y
        else:
            self.dialog = Pmw.Dialog(self.parent,title = 'Error')
            message = 'The x/y coordinates are outside the bounding region.\n' \
                    + '  ' + str(l) + ' < X < ' + str(r) + '\n' \
                    + '  ' + str(b) + ' < Y < ' + str(t)
            w = Tkinter.Label(self.dialog.interior(),
                              text = message,
                              background = 'black',
                              foreground = 'white',
                              pady = 20)
            w.pack(expand = 1, fill = 'both', padx = 4, pady = 4)
        


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotPanel's
        display_labels().
        """
        self.plot_group.configure(tag_text = 'Connection Field Plot')
        super(WeightsPanel,self).display_labels()
    
        
    def refresh_title(self):
        self.parent.title("Unit Weights %d. (x=%0.3f, y=%0.3f)" %
                          (self.panel_num,self.displayed_x, self.displayed_y))
