"""
Plot panels to support GUI windows that display bitmap
plots. Related classes include Plot, PlotGroup, and PlotEngine.

BasicPlotPanel is the smallest class possible to create a new plot
window.  Look at it as an example of creating additional subclasses.

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

from inspect import getdoc

import Image
import ImageTk
import Pmw
from Tkinter import  Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     BooleanVar, StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
     Scrollbar, Y, VERTICAL, HORIZONTAL

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import Sheet

from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import PlotGroup,identity

import topo.tkgui

BORDERWIDTH = 1

# Unfortunately, the canvas creation, border placement, and image
# positioning of Tkinter are very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.  
CANVASBUFFER = 1


class PlotGroupPanel(Frame,ParameterizedObject):
    """
    Abstract PlotGroupPanel class for displaying bitmapped images to a TK
    GUI window.  Must be subclassed to be usable.
    """
	
    @staticmethod
    def valid_context():
        """
        Return true if there appears to be data available for this type of plot.

        To avoid confusing error messages, this method should be
        defined to return False in the case where there is no
        appropriate data to plot.  This information can be used to,
        e.g., gray out the appropriate menu item.
        By default, PlotGroupPanels are assumed to be valid only for
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
	# For a PlotGroupPanel, the plotgroup_key is the name passed at creation.
	# (e.g for testpattern it is 'Preview')
        # For a TemplatePlotGroupPanel, name is the name of the associated template 
        # For a ConnectionField or a Projection Panel, the plotgroup_key is re-generated
	self.plotgroup_key = plotgroup_key

        self.plotgroups_history=[]
        self.history_index = -1
	# indicate if we are currently looking into the past
	self.looking_in_history = False

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
        # Refresh, Reduce, Enlarge, Back and Forward Buttons.
        self.refresh_button = Button(self.control_frame_1,text="Refresh",
                                          command=self.refresh)
        self.refresh_button.pack(side=LEFT)
        self.balloon.bind(self.refresh_button,"Force the current plot to be regenerated.")
               
        self.reduce_button = Button(self.control_frame_1,text="Reduce",
                                    command=self.reduce)
        self.reduce_button.pack(side=LEFT)
        self.balloon.bind(self.reduce_button,
"""Reduce the displayed size of the current plots by about 20%.  A minimum size that
preserves at least one pixel per unit is enforced, to ensure that
no data is lost when displaying.""")

        
        enlarge_button=Button(self.control_frame_1,text="Enlarge",
                              command=self.enlarge)
        enlarge_button.pack(side=LEFT)
        self.balloon.bind(enlarge_button,
"""Increase the displayed size of the current plots by about 20%.""")

        self.back_button = Button(self.control_frame_2,text="Back",
                                  state = DISABLED,command=self.back)
        self.back_button.pack(side=LEFT)
        self.balloon.bind(self.back_button,
"""Move backward through the history of all the plots shown in this window.
When showing a historical plot, some functions will be disabled, because the
original data is no longer available.""")

        self.forward_button = Button(self.control_frame_2,text="Forward",
                                     state = DISABLED,
                                     command=self.forward)
        self.forward_button.pack(side=LEFT)
        self.balloon.bind(self.forward_button,
"Move forward through the history of all the plots shown in this window.")

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

	# Normalize check button
	self.normalize = BooleanVar()
	self.normalize.set(False)
	self.normalize_checkbutton = Checkbutton(self.control_frame_1,
             text="Normalize",variable=self.normalize,command=self.set_normalize)
	self.normalize_checkbutton.pack(side=RIGHT)

        # Integerscaling check button
	self.integerscaling = BooleanVar()
	self.integerscaling.set(False)
	self.integerscaling_checkbutton = Checkbutton(self.control_frame_2,
             text="Integer scaling", variable=self.integerscaling,
             command=self.set_integerscaling)
        self.integerscaling_checkbutton.pack(side=RIGHT)
        self.sizeconvertfn = identity
        
	# Sheet coordinates check button
	self.sheetcoords = BooleanVar()
	self.sheetcoords.set(False)
	self.sheetcoords_checkbutton = Checkbutton(self.control_frame_2,
             text="Sheet coordinates",variable=self.sheetcoords,command=self.set_sheetcoords)
        self.sheetcoords_checkbutton.pack(side=RIGHT)
        self.sheetcoords_checkbutton.var=False
            
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

	# Factor for reducing or enlarging the Plots (20% anytime)
	self.zoom_factor = 1.2
        
	### JCALERT That has to be renamed.
        self.control_frame = Frame(self)
        self.control_frame.pack(side=TOP,expand=YES,fill=X)

	self.plotgroup = self.generate_plotgroup()

        # For now, the balloon help needs to be separate from the buttons
        # above, because it depends on the plotgroup and they are needed
        # for creating the plotgroup.  All of this needs to be cleaned up
        # drastically.
        self.balloon.bind(self.normalize_checkbutton,
                          getdoc(self.plotgroup.params()['normalize']))
        self.balloon.bind(self.sheetcoords_checkbutton,
                          getdoc(self.plotgroup.params()['sheetcoords']))
        self.balloon.bind(self.integerscaling_checkbutton,
                          getdoc(self.plotgroup.params()['integerscaling']))

	# Hotkey for killing the window
	self.parent.bind('<Control-q>',self.parent_destroy)


    def generate_plotgroup(self):
        """
	Function that creates the PlotGroupPanel's PlotGroup.
	Needs to be re-implemented for subclasses.
        """
        plotgroup = PlotGroup([],
                              normalize=self.normalize.get(),
			      sheetcoords=self.sheetcoords.get(),
                              integerscaling=self.integerscaling.get())
	return plotgroup


    def refresh(self,update=True):
        """
        Main steps for generating plots in the Frame.
        """
        Pmw.showbusycursor()
	# We copy the PlotGroup anytime we refresh, for saving in history
	self.plotgroup = copy.copy(self.plotgroup)
	self.update_plotgroup_variables() # update PlotGroup variables
	# if update is True, the SheetViews are re-generated
	self.plotgroup.update_plots(update)
	self.display_plots()              # Put images in GUI canvas
	self.add_to_history()             # Add current Plotgroup to history
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()


    def update_plotgroup_variables(self):
	"""
	Update the variables of the plotgroup according to the panel's variables.
	Re-implemented for sub-classes.
	"""
	pass


    def display_plots(self):
        """
        Pre:  self.bitmaps contains a list of topo.bitmap objects.

        Post: The bitmaps have been displayed to the screen in the active
              console window.  All images are displayed from left to right,
              in a single row.  If the number of images have changed since
              the last display, the grid size is increased, or decreased
              accordingly.

        This function should be redefined in subclasses for interesting
        things such as 2D grids.
        """
	plots = self.plotgroup.plots
	### JCALERT:Momentary: delete when sorting the bitmap history
	self.bitmaps = [p.bitmap for p in plots]
	self.zoomed_images = [ImageTk.PhotoImage(p.bitmap.image) for p in plots]
        # If the number of canvases or their sizes has changed, then
        # create a new set of canvases.  If the old canvases still can
        # work, then reuse them to prevent flicker.
        if self.canvases and len(self.zoomed_images) > 0:
            new_sizes = [(str(zi.width()+BORDERWIDTH*2+CANVASBUFFER),
                          str(zi.height()+BORDERWIDTH*2+CANVASBUFFER))
                         for zi in self.zoomed_images]
            old_sizes = [(zi.config()['width'][-1],zi.config()['height'][-1])
                         for zi in self.canvases]
        else:
            new_sizes, old_sizes = 0, 0
        if len(self.zoomed_images) != len(self.canvases) or \
               new_sizes != old_sizes:
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_frame,
                               width=image.width()+BORDERWIDTH*2+CANVASBUFFER,
                               height=image.height()+BORDERWIDTH*2+CANVASBUFFER,
                               bd=0)
                             for image in self.zoomed_images]
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                # BORDERWIDTH is added because the border is drawn on the
                # canvas, overwriting anything underneath it.
                # The +1 is necessary since the TKinter Canvas object
                # has a problem with axis alignment, and 1 produces
                # the best result.
                canvas.create_rectangle(1, 1, image.width()+BORDERWIDTH*2,
                                        image.height()+BORDERWIDTH*2,
                                        width=BORDERWIDTH,outline="black")
                canvas.create_image(image.width()/2+BORDERWIDTH+1,
                                    image.height()/2+BORDERWIDTH+1,
                                    image=image)
                canvas.config(highlightthickness=0,borderwidth=0,relief=FLAT)
                canvas.grid(row=0,column=i,padx=5)
            for c in old_canvases:
                c.grid_forget()
        else:  # Width of first plot still same, and same number of images.
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.create_image(image.width()/2+BORDERWIDTH+1,
                                    image.height()/2+BORDERWIDTH+1,image=image)
                canvas.grid(row=0,column=i,padx=5)
            

    def add_to_history(self):
	"""
        If new_iteration is True, advances the plot history counter; otherwise
        just overwrites the current one.
	"""
	# if we hit refresh during a Back research, we do not want to copy the 
	# same PlotGroup two times in the history.
	if self.looking_in_history == True:
	    self.history_index = len(self.plotgroups_history)-1
	    self.plotgroups_history[self.history_index]=self.plotgroup	
	else:
	    self.plotgroups_history.append(self.plotgroup)
	    self.history_index = len(self.plotgroups_history)-1
	self.update_back_fwd_button()


    def set_normalize(self):
        """Function called by Widget when check-box clicked"""
	self.plotgroup.normalize = self.normalize.get()
	self.plotgroup.update_plots(False)
        self.display_plots()


    def set_integerscaling(self):
        """Function called by Widget when check-box clicked"""
 	self.plotgroup.integerscaling = self.integerscaling.get()
        if self.integerscaling.get():
            self.plotgroup.sizeconvertfn = int
        else:
            self.plotgroup.sizeconvertfn = identity
	self.plotgroup.update_plots(False)
        self.display_plots()


    ### Momentary have to be re-moved:  
    def update_back_fwd_button(self):	
	if (self.history_index > 0):
            self.back_button.config(state=NORMAL)
	    self.normalize_checkbutton.config(state=DISABLED)
	    self.sheetcoords_checkbutton.config(state=DISABLED)
	    self.integerscaling_checkbutton.config(state=DISABLED)
        else:
            self.back_button.config(state=DISABLED)

        if self.history_index >= len(self.plotgroups_history)-1:
            self.forward_button.config(state=DISABLED)
	    self.normalize_checkbutton.config(state=NORMAL)
	    self.sheetcoords_checkbutton.config(state=NORMAL)
	    self.integerscaling_checkbutton.config(state=NORMAL)
	    self.looking_in_history = False
        else:
            self.forward_button.config(state=NORMAL)


    def display_labels(self):
        """
        This function should be redefined by subclasses to match any
        changes made to display__plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        if self._num_labels != len(self.canvases):
            old_labels = self.labels
            self.labels = [Label(self.plot_frame,text=each)
				 for each in self.plotgroup.labels]
            for i in range(len(self.labels)):
                self.labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self._num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.labels)):
                self.labels[i].configure(text=self.plotgroup.labels[i]) 
 
      
    def refresh_title(self):
        """
        Change the window title.  TopoConsole will call this on
        startup of window.  
        """
        self.parent.title(topo.sim.name+': '+"%s time:%s" % (self.plotgroup_key,self.plotgroup.time))
          

    def reduce(self):
        """Function called by Widget to reduce the plot size"""
        new_height = self.plotgroup.height_of_tallest_plot / self.zoom_factor

        if new_height < self.plotgroup.minimum_height_of_tallest_plot:
            self.reduce_button.config(state=DISABLED)
        else:
	    self.plotgroup.height_of_tallest_plot = new_height
            self.plotgroup.update_plots(False)
            self.display_plots()
    
    def enlarge(self):
        """Function called by Widget to increase the plot size"""
        self.reduce_button.config(state=NORMAL)
        self.plotgroup.height_of_tallest_plot *= self.zoom_factor
	self.plotgroup.update_plots(False)
        self.display_plots()

    # JLALERT: It would be nice to be able to scroll back through many
    # iterations.  Could put in a box for entering either the iteration
    # number you want to view, or perhaps how many you want to jump...
    def back(self):
        """Function called by Widget to scroll back through the previous bitmaps"""
	self.looking_in_history = True
        self.history_index -= 1
	self.update_back_fwd_button()
        self.plotgroup = self.plotgroups_history[self.history_index]
	self.display_plots()
        self.display_labels()
        self.refresh_title() 
	self.restore_panel_environment()
	self.update_back_fwd_button()


    def forward(self):
        """
        Function called by Widget to scroll forward through the bitmaps.
        Only useful if previously you have scrolled back.
        """
        self.history_index += 1
	self.plotgroup=self.plotgroups_history[self.history_index]
	self.display_plots()
        self.display_labels()
        self.refresh_title()
	self.restore_panel_environment()
	self.update_back_fwd_button()
	
    def restore_panel_environment(self):
	if self.plotgroup.normalize != self.normalize.get():
	    self.normalize_checkbutton.config(state=NORMAL)
	    self.normalize_checkbutton.invoke()
	    self.normalize_checkbutton.config(state=DISABLED)
	if self.plotgroup.sheetcoords != self.sheetcoords.get():
	    self.sheetcoords_checkbutton.config(state=NORMAL)
	    self.sheetcoords_checkbutton.invoke()
	    self.sheetcoords_checkbutton.config(state=DISABLED)
	if self.plotgroup.integerscaling != self.integerscaling.get():
	    self.integerscaling_checkbutton.config(state=NORMAL)
	    self.integerscaling_checkbutton.invoke()
	    self.integerscaling_checkbutton.config(state=DISABLED)
	

    def set_auto_refresh(self):
        """Function called by Widget when check-box clicked"""
	# when refreshing through auto-refresh, we know we want to
	# save the new plotgroup, so we reset history_index
        ### JABALERT: Really?  This is just the auto-refresh button.
	self.history_index = len(self.plotgroups_history)-1
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
        
    def set_sheetcoords(self):
        """Function called by Widget when check-box clicked"""
	self.plotgroup.sheetcoords = self.sheetcoords.get()
	self.plotgroup.update_plots(False)
	self.display_plots()


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
