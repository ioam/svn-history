"""
BasicPlotGroupPanel is the smallest class possible to create a new plot group
of any type. 

$Id$
"""
__version__='$Revision$'


### JABHACKALERT!!!!!!!!!!!!  Need to totally redo this class
### hierarchy so that the panel does not store any extra copies of the
### variables like normalize, sheetcoords, etc. --- it's impossible to
### reason about it in its current form.  Each panel should simply
### instantiate some PlotGroup type, and from then on query the
### PlotGroup for the variables that it needs, and change them directly
### in the PlotGroup rather than in shadow copies within the panel.
### It should be possible to do this in a very general way based on
### Parameters in the PlotGroup, so that the Tk-specific stuff is as
### simple as possible.
### This *may* require some changes in PlotGroup so that each PlotGroup
### can be instantiated without any plots, and can then have plots
### added. 

import Numeric
import copy


import Image
import ImageTk
import Pmw
from Tkinter import  Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     BooleanVar, StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
     Scrollbar, Y, VERTICAL, HORIZONTAL

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import Sheet

from topo.plotting.plotgroup import PlotGroup,identity

import topo.tkgui


class BasicPlotGroupPanel(Frame,ParameterizedObject):
    """
    Abstract BasicPlotGroupPanel class for displaying plots to a TK
    GUI window. Implements only basic buttons required. 
    Must be subclassed to be usable.
    """
	
    @staticmethod
    def valid_context():
        """
        Return true if there appears to be data available for this type of plot.

        To avoid confusing error messages, this method should be
        defined to return False in the case where there is no
        appropriate data to plot.  This information can be used to,
        e.g., gray out the appropriate menu item.
        By default, PlotPanels are assumed to be valid only for
        simulations that contain at least one Sheet.  Subclasses with
        more specific requirements should override this method with
        something more appropriate.
        """
        if topo.sim.objects(Sheet).items():
            return True
        else:
            return False


    def __init__(self,parent,console,plotgroup_key,**params):
        """
        parent:  it is the window (GUIToplevel()) that contains the panel.
        console: is the associated console, (i.e. the TopoConsole that has this panel)
        name: name associated with the panel
	"""

        Frame.__init__(self,parent)
        topo.plotting.plot.ParameterizedObject.__init__(self,**params)

	self.console = console
        self.parent = parent
	# balloon help component
        self.balloon = Pmw.Balloon(parent)
        self.canvases = []

	### JCALERT: we will have to rename plotgroup_key to something like 
	### plotgroup_label.
	# For a BasicPlotGroupPanel, the plotgroup_key is the name passed at creation.
	# (e.g for testpattern it is 'Preview')
        # For a TemplatePlotGroupPanel, name is the name of the associated template 
        # For a ConnectionField or a Projection Panel, the plotgroup_key is re-generated
	self.plotgroup_key = plotgroup_key

        self.labels = []
        ### JCALERT! Figure out why we need that!
        self._num_labels = 0

        # Create and fill the 2 control Frames
	self.control_frame_1 = Frame(self)
        self.control_frame_1.pack(side=TOP,expand=YES,fill=X)
	self.control_frame_2 = Frame(self)
        self.control_frame_2.pack(side=TOP,expand=YES,fill=X)

        # JAB: Because these three buttons are present in nearly every
        # window, and aren't particularly important, we should
        # probably use small icons for them instead of text.  That way
        # they will form a visual group that users can typically
        # ignore.  Of course, the icons will need to announce their
        # names as help text if the mouse lingers over them, so that
        # the user can figure them out the first time.
        # 
       
        self.refresh_button = Button(self.control_frame_1,text="Refresh",
                                          command=self.refresh)
        self.refresh_button.pack(side=LEFT)
        self.balloon.bind(self.refresh_button,"Force the current plot to be regenerated.")
               
        # Auto_refresh check button.
        # Default is to not have the window Auto-refresh, because some
        # plots are very slow to generate (e.g. some preference map
        # plots).  Call self.auto_refresh.set(True) to enable
        # autorefresh in a subclassed constructor function.
	self.auto_refresh = BooleanVar()
	self.auto_refresh.set(False)
        if self.auto_refresh.get():
            self.console.auto_refresh_panels.append(self)
        self.auto_refresh_checkbutton = \
            Checkbutton(self.control_frame_1, text="Auto-refresh",
                        variable=self.auto_refresh,command=self.set_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=RIGHT)
        self.balloon.bind(self.auto_refresh_checkbutton,
            "Whether to regenerate this plot whenever the simulation time advances.")

        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')
	self.plot_group_title = Pmw.Group(self,tag_text=str(self.plotgroup_key))
        self.plot_group_title.pack(side=TOP,expand=YES,fill=BOTH,padx=5,pady=5)
	self.plot_frame = self.plot_group_title.interior()

        ### JABALERT! Need to implement scrollbars for viewing plots
        ### too large for the screen.
	# JC: A way of implementing it. Needs more work: for the moment,
        # the window expands without the scrollbar, but does not when the scrollbar is on.
# 	self.scrollbar = Pmw.ScrolledFrame(self,borderframe=0,
# 					   horizflex = 'elastic', vertflex='elastic',
# 					   hscrollmode = 'dynamic', vscrollmode = 'dynamic')
# 	self.scrollbar.pack(side=TOP,expand=YES,fill=X)
#       self.plot_frame = self.scrollbar.interior()

        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=TOP,expand=YES,fill=X)

	# Hotkey for killing the window
	self.parent.bind('<Control-q>',self.parent_destroy)


    def refresh(self,update=True):
        """
        Main steps for generating plots in the Frame. 
	Must be re-implemented in sub-classes which save a history of the plots.
        """
        Pmw.showbusycursor()
	self.plotgroup = copy.copy(self.plotgroup)
	self.update_plotgroup_variables() # update PlotGroup variables
	# if update is True, the SheetViews are re-generated
	self.plotgroup.update_plots(update)
	self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()


    def refresh_title(self):
        """
        Change the window title.  TopoConsole will call this on
        startup of window.  
        """
        self.parent.title(topo.sim.name+': '+"%s time:%s" % (self.plotgroup_key,self.plotgroup.time))
          
    def display_plots(self):
	"""
	Implemented in sub-classes
	"""
	pass

    def display_labels(self):
	"""
	Implemented in sub-classes
	"""
	pass

    def set_auto_refresh(self):
        """Function called by Widget when check-box clicked"""

        if self.auto_refresh.get():
            if not (self in self.console.auto_refresh_panels):
                self.console.auto_refresh_panels.append(self)
        else:
            if self in self.console.auto_refresh_panels:
                self.console.auto_refresh_panels.remove(self)
            
        # JAB: it might make sense for turning on auto-refresh
        # to do a refresh automatically, though that might have
        # unexpected behavior for a preference map calculation
        # (where it would do unnecessary, and potentially lengthy,
        # recalculation).
        
    def destroy(self):
        if self.auto_refresh.get():
            if self in self.console.auto_refresh_panels:
                self.console.auto_refresh_panels.remove(self)
        Frame.destroy(self)

    # YCHACKALERT: This is a hack to avoid number of argument mismatch
    # when the Control-q hotkey binding is activated.
    def parent_destroy(self,dummy):
	self.destroy()
	self.parent.destroy()
