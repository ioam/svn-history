"""
WeightsPanel object for GUI visualization.

Subclasses CFSheetPlotPanel, which is basically a PlotGroupPanel.

Uses a WeightsPlotGroup to generate the plots displayed in the main
widget.

$Id$
"""
__version__='$Revision$'

import __main__
from Tkinter import StringVar, Frame, TOP, LEFT, YES, X, Message, Entry
from plotgrouppanel import PlotGroupPanel
from cfsheetplotpanel import CFSheetPlotPanel
from topo.base.projection import ProjectionSheet
from topo.plotting.templates import plotgroup_templates
from topo.base.sheet import Sheet
import topoconsole

class UnitWeightsPanel(CFSheetPlotPanel):
    def __init__(self,parent,pengine,console=None,**config):
        super(UnitWeightsPanel,self).__init__(parent,pengine,console,**config)

        # Receptive Fields are generally tiny.  Boost it up to make it visible.
        self.WEIGHT_PLOT_INITIAL_SIZE = 30

        self.x = 0
        self.x_str = StringVar()
        self.x_str.set(0.0)
        self.y = 0
        self.y_str = StringVar()
        self.y_str.set(0.0)
        self.displayed_x, self.displayed_y = 0, 0

        self._add_xy_boxes()
        self.auto_refresh_checkbutton.invoke()

        self.refresh()


    def _add_xy_boxes(self):
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)

        Message(params_frame,text="Unit  X:",aspect=1000).pack(side=LEFT)
        self.xe = Entry(params_frame,textvariable=self.x_str)
        self.xe.bind('<FocusOut>', self.refresh)
        self.xe.bind('<Return>', self.refresh)
        self.xe.pack(side=LEFT,expand=YES,fill=X)

        #self.tag.bind('<KeyRelease>', self.tag_keypress)

        Message(params_frame,text="Y:",aspect=1000).pack(side=LEFT)
        self.ye = Entry(params_frame,textvariable=self.y_str)
        self.ye.bind('<FocusOut>', self.refresh)
        self.ye.bind('<Return>', self.refresh)
        self.ye.pack(side=LEFT,expand=YES,fill=X,padx=5)

    @staticmethod
    def valid_context():
        """
        Only open if ProjectionSheets are in the Simulator.
        """
        if topoconsole.active_sim().objects(ProjectionSheet).items():
            return True
        else:
            return False


    def generate_plot_group_key(self):
        """
        The plot_group_key for the UnitWeightsPanel will change depending on the
        input within the window widgets.  This means that the key
        needs to be regenerated at the appropriate times.

        Key Format:  Tuple: ('Weights', Sheet_Name, X_Number, Y_Number)
        """
        g = __main__.__dict__
        self.x = eval(self.x_str.get(),g)
        self.y = eval(self.y_str.get(),g)
        if isinstance(self.x,int): self.x = float(self.x)
        if isinstance(self.y,int): self.y = float(self.y)

        ep = [ep for ep in topoconsole.active_sim().objects(Sheet).values()
              if ep.name == self.region.get()][0]
        # This assumes that displaying the rectangle information is enough.
        l,b,r,t = ep.bounds.aarect().lbrt()

        if ep.bounds.contains(self.x,self.y):
            self.plot_group_key = ('Weights',self.region.get(),self.x,self.y)
            self.displayed_x, self.displayed_y = self.x, self.y
        else:
            self.dialog = Pmw.Dialog(self.parent,title = 'Error')
            message = 'The x/y coordinates are outside the bounding region.\n'\
                    + '  ' + str(l) + ' < X < ' + str(r) + '\n' \
                    + '  ' + str(b) + ' < Y < ' + str(t)
            w = Tkinter.Label(self.dialog.interior(),
                              text = message,
                              background = 'black',
                              foreground = 'white',
                              pady = 20)
            w.pack(expand = 1, fill = 'both', padx = 4, pady = 4)
        


    def do_plot_cmd(self):
        """
        Create the right Plot Key that will define the needed
        information for a WeightsPlotGroup.  This is the key-word
        'Weights', and the necessary x,y coordinate.  Once the
        PlotGroup is created, call its do_plot_cmd() to prepare
        the Plot objects.
        """


        self.generate_plot_group_key()
        self.pe_group = self.pe.get_plot_group(self.plot_group_key,
                                               plotgroup_templates['Unit Weights'],
                                               'UnitWeightsPlotGroup',self.region.get())
        self.pe_group.do_plot_cmd()

        # self.situate is defined in the super class CFSheetPlotPanel
        self.pe_group.situate = self.situate
        
        ### JCALERT: Hack temporary
	self.pe_group.plot_list=self.pe_group.initialize_plot_list(plot_list=[])
       


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotGroupPanel's
        display_labels().
        """
        new_title = 'Connection Fields of ' + self.region.get() + \
                    ' unit (' + str(self.x) + ',' + str(self.y) + ') at time '\
                    + str(self.pe.simulation.time())
        self.plot_group.configure(tag_text = new_title)
        super(UnitWeightsPanel,self).display_labels()
    
        
    def refresh_title(self):
        self.parent.title("Unit Weights  %s (%0.3f,%0.3f) time:%s" %
                          (self.region.get(),self.displayed_x,self.displayed_y,self.pe.simulation.time()))
