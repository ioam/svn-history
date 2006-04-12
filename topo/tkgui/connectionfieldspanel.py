"""
WeightsPanel object for GUI visualization.

Subclasses CFSheetPlotPanel, which is basically a PlotGroupPanel.

Uses a WeightsPlotGroup to generate the plots displayed in the main
widget.

$Id$
"""
__version__='$Revision$'

import Pmw
import __main__
from itertools import chain

from Tkinter import StringVar, Frame, TOP, LEFT, YES, X, Message, Entry,Label,NSEW, Checkbutton
from templateplotgrouppanel import TemplatePlotGroupPanel
from topo.base.projection import ProjectionSheet
from topo.plotting.plotgroup import plotgroup_dict, ConnectionFieldsPlotGroup
from topo.base.sheet import Sheet
import topoconsole
import topo.base.connectionfield

from topo.commands.analysis import *
import topo.commands.analysis

### JABALERT!  Why isn't there a Normalize button on this and
### ProjectionPanel like there is on ActivityPanel?
class ConnectionFieldsPanel(TemplatePlotGroupPanel):
    def __init__(self,parent,console=None,pgt_name=None,**config):       
        TemplatePlotGroupPanel.__init__(self,parent,console,pgt_name,**config)
        self.region = StringVar()
        self.region.set('None')
        self.__params_frame = Frame(master=self)
        self.__params_frame.pack(side=LEFT,expand=YES,fill=X)

        self._add_situate_button()
        self._add_region_menu()
        
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
	

	# By default, the UnitWeight Plots are situated.
        self.toggle_situate()
	self.situate_checkbutton.select()

        self.refresh()


    def _add_region_menu(self):
        """
        This function adds a Sheet: menu that queries the active
        simulation for the list of options.  When an update is made,
        _region_refresh() is called.  It can either call the refresh()
        funcion, or update another menu, and so on.
        """

        # Create the item list for CFSheet 'Sheet'  This will not change
        # since this window will only examine one Simulator.
        sim = topoconsole.active_sim()
        self._sim_eps = [ep for ep in sim.objects(Sheet).values()
                  if isinstance(ep,topo.base.connectionfield.CFSheet)]
	self._sim_eps.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        sim_ep_names = [ep.name for ep in self._sim_eps]
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

        # The GUI label says Sheet, not CFSheet, because users probably 
        # don't need to worry about the distinction.
        self.opt_menu = Pmw.OptionMenu(self.__params_frame,
                       command = self.refresh,
                       labelpos = 'w',
                       label_text = 'Sheet:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names)
        self.opt_menu.pack(side=LEFT)


    def _add_situate_button(self):
        
        self.situate = 0
        self.situate_checkbutton = Checkbutton(self.__params_frame,
                                                    text="Situate",
                                                    command=self.toggle_situate)
        self.situate_checkbutton.pack(side=LEFT)


    def toggle_situate(self):
        """Set the attribute situate"""
        self.situate = not self.situate
        if self.plotgroup != None:
            self.plotgroup.situate = self.situate
        self.initial_plot = True
        self.height_of_tallest_plot = self.min_master_zoom = 1
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
        Only open if there are Projections defined.
        """
        projectionsheets=topo.sim.objects(ProjectionSheet).values()
        if not projectionsheets:
            return False

        projectionlists=[i.projections().values() for i in projectionsheets]
        projections=[i for i in chain(*projectionlists)]
        return (not projections == [])


    ### JABALERT: This looks like too much intelligence to include in
    ### the GUI code; this function should probably just be calling a
    ### PlotGroup (or subclass) function to generate the key.  This
    ### file should have only GUI-specific stuff.
    def generate_plotgroup_key(self):
        """
        The plotgroup_key for the ConnectionFieldsPanel will change depending on the
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
            self.plotgroup_key = ('Weights',self.region.get(),self.x,self.y)
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
        


    def refresh_plotgroup(self):
        """
        Create the right Plot Key that will define the needed
        information for a WeightsPlotGroup.  This is the key-word
        'Weights', and the necessary x,y coordinate.  Once the
        PlotGroup is created, call its do_plot_cmd() to prepare
        the Plot objects.
        """
	 
        self.generate_plotgroup_key()
	
	topo.commands.analysis.coordinate = (self.x,self.y)
	topo.commands.analysis.sheet_name = self.region.get()

        exec self.cmdname.get()
		
	plotgroup = plotgroup_dict.get(self.plotgroup_key,None)
	if plotgroup == None:
	    plotgroup = ConnectionFieldsPlotGroup(self.plotgroup_key,[],self.normalize,
						  self.sheetcoords,self.integerscaling,self.pgt,self.region.get())

        plotgroup.situate = self.situate
	return plotgroup


    def display_labels(self):
        """
        Change the title of the grid group, then call PlotGroupPanel's
        display_labels().
        """
        new_title = 'Connection Fields of ' + self.region.get() + \
                    ' unit (' + str(self.x) + ',' + str(self.y) + ') at time '\
                    + str(self.plot_time)
        self.plot_group_title.configure(tag_text = new_title)

	if self._num_labels != len(self.canvases):
	    old_labels = self.labels
            self.labels = [Label(self.plot_frame,text=(each.name + '\n(from ' + each.plot_src_name+')') )
				 for each in self.bitmaps]
            for i in range(len(self.labels)):
                self.labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self._num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.labels)):
                self.labels[i].configure(text=self.bitmaps[i].name +'\n(from ' + self.bitmaps[i].plot_src_name+')') 

    
        
    def refresh_title(self):
        self.parent.title(topo.sim.name+': '+self.pgt.name + " %s (%0.3f,%0.3f) time:%s" %
                          (self.region.get(),self.displayed_x,self.displayed_y,self.plot_time))

