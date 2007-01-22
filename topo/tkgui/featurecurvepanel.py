"""
class FeatureCurvePanel and FullFieldFeatureCurvePanel

Panel for displaying tuning curves.

Uses a PlotGroup to generate the pylab plots 
which are currently displayed separately from the gui.

$Id$
"""
__version__='$Revision$'

import Pmw
import __main__
import copy

from Tkinter import StringVar, BooleanVar, Frame, TOP, LEFT, RIGHT, YES, X, Message, Button
from Tkinter import Entry, Label, NSEW, Checkbutton, NORMAL, DISABLED

import topo

from inspect import getdoc

from topo.plotting.templates import plotgroup_templates
from plotgrouppanel import BasicPlotGroupPanel
from topo.base.projection import ProjectionSheet
from topo.plotting.plotgroup import FeatureCurvePlotGroup
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet
import topoconsole


class FeatureCurvePanel(BasicPlotGroupPanel):
    def __init__(self,parent,console=None,pgt_name=None,**config):       

        self.pgt = plotgroup_templates.get(pgt_name,None)
	self.plotgroup_key=self.pgt.name 
     
	BasicPlotGroupPanel.__init__(self,parent,console,pgt_name,**config)

        self.region = StringVar()
	self.x = 0
	self.y = 0

	self.plotgroup = self.generate_plotgroup()

        # Command used to refresh the plot, if any
        self.cmdname = StringVar()
	self.cmdname.set(self.plotgroup.updatecommand)
      
	self.params_frame = Frame(master=self)
        self.params_frame.pack(side=TOP,expand=YES,fill=X)
        
	cmdlabel = Message(self.params_frame,text="Update command:",aspect=1000)
        cmdlabel.pack(side=LEFT)
        self.balloon.bind(cmdlabel,getdoc(self.plotgroup.params()['updatecommand'])) 

        cmdbox = Pmw.ComboBox(self.params_frame,autoclear=1,history=1,dropdown=1,
                              entry_textvariable=self.cmdname,
                              scrolledlist_items=([self.cmdname]))
        cmdbox.pack(side=LEFT,expand=YES,fill=X)
        self.balloon.bind(cmdbox,getdoc(self.plotgroup.params()['updatecommand']))
  
        self.__params_frame = Frame(master=self)
        self.__params_frame.pack(side=LEFT,expand=YES,fill=X)

        
	self.x_str = StringVar()
        self.x_str.set(0.0)
        self.y_str = StringVar()
        self.y_str.set(0.0)
        self._add_region_menu()
        self._add_xy_boxes()

          
        self.auto_refresh.set(False)
        self.set_auto_refresh()

        if self.pgt.initial_plot: self.refresh()

    def refresh_variables(self, update=True):
        """
        Command to be called when plotgroup variables are updated in the GUI
        """
        Pmw.showbusycursor()
	self.plotgroup = copy.copy(self.plotgroup)
	self.update_plotgroup_variables()# update PlotGroup variables
        self.plotgroup.plotcommand = self.plot_cmdname.get()# in this case must also update plotcommand
	self.plotgroup.update_environment()
	self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()

              
    def _add_region_menu(self):
        """
        This function adds a Sheet: menu that queries the active
        simulation for the list of options.  When an update is made,
        refresh_variables() is called.
        """

        self._sim_eps = topo.sim.objects(CFSheet).values()
	self._sim_eps.sort(lambda x, y: cmp(-x.precedence,-y.precedence))
        sim_ep_names = [ep.name for ep in self._sim_eps]
	
        if len(sim_ep_names) > 0:
            self.region.set(sim_ep_names[0])

     
        self.opt_menu = Pmw.OptionMenu(self.__params_frame,
                       command = self.refresh_variables,
                       labelpos = 'w',
                       label_text = 'Sheet:',
                       menubutton_textvariable = self.region,
                       items = sim_ep_names)
        self.opt_menu.pack(side=LEFT)
        self.balloon.bind(self.opt_menu,"""Sheet whose unit(s) will be plotted.""")

        for prerequisite in self.pgt.prerequisites:
            if prerequisite not in topo.sim[str(self.region.get())].sheet_view_dict:
                self.dialog = Pmw.Dialog(self.parent,title = 'Warning')
                if prerequisite=='XPreference':
                    message = 'Position preference should be plotted before plotting '+ str(self.plotgroup_key)+'\n'\
                              'Otherwise will use default values'
                else:
                    message = prerequisite + ' preference should be plotted before plotting '+ str(self.plotgroup_key)+'\n'\
                              'Otherwise will use default values'
                w = Label(self.dialog.interior(),
                          text = message,
                          background = 'black',
                          foreground = 'white',
                          pady = 20)
                w.pack(expand = 1, fill = 'both', padx = 4, pady = 4)
               

    def _add_xy_boxes(self):
        """
        This function adds boxes that allow the user to input the x and y variables
        When an update is made,refresh_variables() is called.
        """
      
        Message(self.__params_frame,text="Unit  X:",aspect=1000).pack(side=LEFT)
        self.xe = Entry(self.__params_frame,textvariable=self.x_str)
        # JC: we would like to update when the user leaves the box,
	# but we don't know yet how to do it.(id for ye)
        self.xe.bind('<Return>',self.refresh_variables)
        self.xe.pack(side=LEFT,expand=YES,fill=X)
        self.balloon.bind(self.xe,
"""Sheet coordinate location desired.  The unit nearest this location will be returned.
It is an error to request a unit outside the area of the Sheet.""")
        #self.tag.bind('<KeyRelease>', self.tag_keypress)

        Message(self.__params_frame,text="Y:",aspect=1000).pack(side=LEFT)
        self.ye = Entry(self.__params_frame,textvariable=self.y_str)
	self.ye.bind('<Return>', self.refresh_variables)
        self.ye.pack(side=LEFT,expand=YES,fill=X,padx=5)
        self.balloon.bind(self.ye,
"""Sheet coordinate location desired.  The unit nearest this location will be returned.
It is an error to request a unit outside the area of the Sheet.""")


    def update_plotgroup_variables(self):
        """
        Get the plotgroup variables (ie. x,y, sheet and update command) from the gui before
        updating the plots.
        """
        g = __main__.__dict__
        self.x = eval(self.x_str.get(),g)
        self.y = eval(self.y_str.get(),g)
        if isinstance(self.x,int): self.x = float(self.x)
        if isinstance(self.y,int): self.y = float(self.y)
        # JABALERT: Need to display the actual x,y coordintes of the
        # nearest unit somehow, since that differs from the value requested.

        ep = [ep for ep in topo.sim.objects(Sheet).values()
              if ep.name == self.region.get()][0]
        # This assumes that displaying the rectangle information is enough.
        l,b,r,t = ep.bounds.aarect().lbrt()

        if ep.bounds.contains(self.x,self.y):
	    self.plotgroup.sheet_name = self.region.get()
	    self.plotgroup.x = self.x
	    self.plotgroup.y = self.y
        else:
            self.dialog = Pmw.Dialog(self.parent,title = 'Error')
            message = 'The x/y coordinates are outside the bounding region.\n'\
                    + '  ' + str(l) + ' < X < ' + str(r) + '\n' \
                    + '  ' + str(b) + ' < Y < ' + str(t)
	    w = Label(self.dialog.interior(),
                              text = message,
                              background = 'black',
                              foreground = 'white',
                              pady = 20)
            w.pack(expand = 1, fill = 'both', padx = 4, pady = 4)
	self.plotgroup.sheet_name = self.region.get()
        self.plotgroup.updatecommand = self.cmdname.get()

       

    def generate_plotgroup(self):
        """
        Create the right Plot Key that will define the needed
        information for a FeatureCurvePlotGroup. 
        """
	plotgroup = FeatureCurvePlotGroup([],self.pgt,self.region.get(),self.x,self.y)
                                           
                                            
	return plotgroup


    def display_labels(self):
        """
        Change the title of the grid group by refreshing the simulated time.
        """
        self.plot_group_title.configure(tag_text = str(self.plotgroup_key) + \
                                  ' at time ' + str(self.plotgroup.time))
     


class FullFieldFeatureCurvePanel(FeatureCurvePanel):
    """
    In some cases it is not necessary to use the full updatecommand before plotting.
    This class creates a gui window showing the reduced update command and in which updating the
    plotgroup variables from the gui calls the plotcommand rather than the full updatecommand.
    """
    def __init__(self,parent,console=None,pgt_name=None,**config):

        FeatureCurvePanel.__init__(self,parent,console,pgt_name,**config)

        self.plot_cmdname = StringVar()
	self.plot_cmdname.set(self.plotgroup.plotcommand)
      
	plot_cmdlabel = Message(self.params_frame, text="Plot command:",aspect=1000)
        plot_cmdlabel.pack(side=LEFT)
        self.balloon.bind(plot_cmdlabel,getdoc(self.plotgroup.params()['plotcommand']))

        plot_cmdbox = Pmw.ComboBox(self.params_frame,autoclear=1,history=1,dropdown=1,
                              entry_textvariable=self.plot_cmdname,
                              scrolledlist_items=([self.plot_cmdname]))
        plot_cmdbox.pack(side=TOP,expand=YES,fill=X)
        self.balloon.bind(plot_cmdbox,getdoc(self.plotgroup.params()['plotcommand']))
                     
    def refresh_variables(self, update=True):
        """
        Command called when variables are updated in the gui.
        In this case only the plotcommand is called rather than the full updatecommand.
        """
        Pmw.showbusycursor()
	self.plotgroup = copy.copy(self.plotgroup)
	self.update_plotgroup_variables()# update PlotGroup variables
        self.plotgroup.plotcommand = self.plot_cmdname.get()# in this case must also update plotcommand
	self.plotgroup.update_variables()
	self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()

 
