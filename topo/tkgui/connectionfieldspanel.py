"""
WeightsPanel object for GUI visualization.

Subclasses CFSheetPlotPanel, which is basically a PlotGroupPanel.

Uses a WeightsPlotGroup to generate the plots displayed in the main
widget.

$Id$
"""
__version__='$Revision$'

import Pmw


from Tkinter import StringVar, Frame, TOP, LEFT, YES, X, Message
from Tkinter import Entry, Label, NSEW, Checkbutton, NORMAL, DISABLED

import topo

from topo.base.projection import ProjectionSheet
from topo.plotting.plotgroup import ConnectionFieldsPlotGroup
from topo.base.sheet import Sheet

from projectionpanel import SomethingPanel


# CEBHACKALERT: various parts of the dynamic info/right-click menu stuff
# don't make sense at the moment when things like 'situate' are clicked.

class ConnectionFieldsPanel(SomethingPanel):
    def __init__(self,console=None,pgt_name=None,x=0.0,y=0.0,**params):       

        # Receptive Fields are generally tiny.  Boost it up to make it visible.
        self.WEIGHT_PLOT_INITIAL_SIZE = 30

        self.x_var = StringVar()
        self.x_var.set(x) 
        self.y_var = StringVar()
        self.y_var.set(y) 


        super(ConnectionFieldsPanel,self).__init__(console,pgt_name,**params)

        # CEBALERT: I'm not sure what the various definitions of x and y
        # are for - I wonder if they can be cleaned up? I haven't looked,
        # and when adding the x any y args above with their defaults, I've
        # left a note of the previous values in case they're needed while
        # cleaning up.
 
	
        self._add_xy_boxes()


	self.refresh()


    def _add_xy_boxes(self):
        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)
        
        Message(params_frame,text="Unit  X:",aspect=1000).pack(side=LEFT)
        self.xe = Entry(params_frame,textvariable=self.x_var)
        self.xe.bind('<Return>',self.refresh)
        self.xe.pack(side=LEFT,expand=YES,fill=X)
        self.balloon.bind(self.xe,
"""Sheet coordinate location desired.  The unit nearest this location will be returned.
It is an error to request a unit outside the area of the Sheet.""")
        
        Message(params_frame,text="Y:",aspect=1000).pack(side=LEFT)
        self.ye = Entry(params_frame,textvariable=self.y_var)
	self.ye.bind('<Return>', self.refresh)
        self.ye.pack(side=LEFT,expand=YES,fill=X,padx=5)
        self.balloon.bind(self.ye,
"""Sheet coordinate location desired.  The unit nearest this location will be returned.
It is an error to request a unit outside the area of the Sheet.""")


    @staticmethod
    def valid_context():
        """
        Only open if there are Projections defined.
        """
        projectionsheets=topo.sim.objects(ProjectionSheet).values()
        if not projectionsheets:
            return False

        projections=[proj_sheet.in_connections for proj_sheet in projectionsheets]
        return (not projections == [])


    ### JABALERT: This looks like too much intelligence to include in
    ### the GUI code; this function should probably just be calling a
    ### PlotGroup (or subclass) function to generate the key.  This
    ### file should have only GUI-specific stuff.
    def update_plotgroup_variables(self):
        """
        The plotgroup_key for the ConnectionFieldsPanel will change depending on the
        input within the window widgets.  This means that the key
        needs to be regenerated at the appropriate times.

        Key Format:  Tuple: ('Weights', Sheet_Name, X_Number, Y_Number)
        """
        x,y = float(self.x_var.get()), float(self.y_var.get())
        
        # JABALERT: Need to display the actual x,y coordintes of the
        # nearest unit somehow, since that differs from the value requested.

        ep = [ep for ep in topo.sim.objects(Sheet).values()
              if ep.name == self.sheet_var.get()][0]
        # This assumes that displaying the rectangle information is enough.
        l,b,r,t = ep.bounds.aarect().lbrt()

        if ep.bounds.contains(x,y):
	    self.plotgroup.sheet_name = self.sheet_var.get()
	    self.plotgroup.x = x
	    self.plotgroup.y = y
        else:
            self.dialog = Pmw.Dialog(self,title = 'Error')
            message = 'The x/y coordinates are outside the bounding region.\n'\
                    + '  ' + str(l) + ' < X < ' + str(r) + '\n' \
                    + '  ' + str(b) + ' < Y < ' + str(t)
	    w = Label(self.dialog.interior(),
                              text = message,
                              background = 'black',
                              foreground = 'white',
                              pady = 20)
            w.pack(expand = 1, fill = 'both', padx = 4, pady = 4)
	self.plotgroup.situate=self.situate.get()
	self.plotgroup.sheet_name = self.sheet_var.get()


    def generate_plotgroup(self):
        """
        Create the right Plot Key that will define the needed
        information for a WeightsPlotGroup.  This is the key-word
        'Weights', and the necessary x,y coordinate.  Once the
        PlotGroup is created, call its do_plot_cmd() to prepare
        the Plot objects.
        """
	plotgroup = ConnectionFieldsPlotGroup([],self._pg_template(),self.sheet_var.get(),
                                              float(self.x_var.get()),float(self.y_var.get()),
                                              normalize=self.normalize.get(),
                                              sheetcoords=self.sheetcoords.get(),
                                              integerscaling=self.integerscaling.get())
	return plotgroup


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotGroupPanel's
        display_labels().
        """
        new_title = 'Connection Fields of ' + self.plotgroup.sheet_name + \
                    ' unit (' + str(self.plotgroup.x) + ',' + str(self.plotgroup.y) + ') at time '\
                    + str(self.plotgroup.time)
        self.plot_group_title.configure(tag_text = new_title)
        super(ConnectionFieldsPanel,self).display_labels()

    
        
    def refresh_title(self):
        self.title(topo.sim.name+': '+self.pgt.name + " %s (%0.3f,%0.3f) time:%s" %
                          (self.plotgroup.sheet_name,self.plotgroup.x,self.plotgroup.y,self.plotgroup.time))


    def update_back_fwd_button(self):
	super(ConnectionFieldsPanel,self).update_back_fwd_button()
	if (self.history_index > 0):
            self.situate_checkbutton.config(state=DISABLED)
	    self.xe.config(state=DISABLED)
	    self.ye.config(state=DISABLED)
	    ### JCALERT: Should find a way to disable the sheet menu
	    ### (What I tried below does not work)
	    ### Also, disabled the text for the xy_boxes (i.e., X,Y)
	    ## Also, when changing the menu while looking in history,
            ### it will replaced the old current one by the new one instead of adding
	    ### the new at the following.
	    #self.opt_menu.config(state=DISABLED)

        if self.history_index >= len(self.plotgroups_history)-1:
	    self.situate_checkbutton.config(state=NORMAL)
	    self.xe.config(state=NORMAL)
	    self.ye.config(state=NORMAL)
	    #self.opt_menu.config(state=NORMAL)

    def restore_panel_environment(self):
	super(ConnectionFieldsPanel,self).restore_panel_environment()
	if self.plotgroup.situate != self.situate.get():
	    self.situate_checkbutton.config(state=NORMAL)
	    self.situate_checkbutton.invoke()
	    self.situate_checkbutton.config(state=DISABLED)
