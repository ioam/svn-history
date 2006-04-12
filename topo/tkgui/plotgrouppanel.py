"""
Plot panels to support GUI windows that display bitmap
plots. Related classes include Plot, PlotGroup, and PlotEngine.

BasicPlotPanel is the smallest class possible to create a new plot
window.  Look at it as an example of creating additional subclasses.

$Id$
"""
__version__='$Revision$'


import Numeric
import MLab
import copy

import PIL
import Image
import ImageTk
import Pmw, re, os, sys
from Tkinter import  Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE, \
     Scrollbar, Y, VERTICAL, HORIZONTAL

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.sheet import Sheet
import topo.base.simulator 

import topo.plotting.bitmap
import topo.plotting.plotgroup
from topo.plotting.templates import plotgroup_templates
from topo.plotting.plotgroup import plotgroup_dict,identity

import topo.tkgui

# def identity(x):
#     """No-op function for use as a default."""
#     return x

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
	# ballon help component
        self.balloon = Pmw.Balloon(parent)
        self.canvases = []

	# For a PlotGroupPanel, the plotgroup_key is the name passed at creation.
	# (e.g for testpattern it is 'Preview')
        # For a TemplatePlotGroupPanel, name is the name of the associated template 
        # For a ConnectionField or a Projection Panel, the plotgroup_key is re-generated
	self.plotgroup_key = plotgroup_key

	### JCALERT: do a create_plot_group function instead of so_plot_cmd
        #self.pe_group = self.create_plot_group()
        self.bitmaps = []
        self.bitmaps_history=[]
        self.time_history=[]
        self.history_index = -1
        self.plot_time = 0 # JABALERT: Should probably be in the plotgroup, not here.
        self.labels = []
        ### JCALERT! Figure out why we need that!
        self._num_labels = 0

        # Create and fill the control Frame
	self.shared_control_frame = Frame(self)
        self.shared_control_frame.pack(side=TOP,expand=YES,fill=X)

        # JAB: Because these three buttons are present in nearly every
        # window, and aren't particularly important, we should
        # probably use small icons for them instead of text.  That way
        # they will form a visual group that users can typically
        # ignore.  Of course, the icons will need to announce their
        # names as help text if the mouse lingers over them, so that
        # the user can figure them out the first time.
        # 
        # Refresh, Reduce, and Enlarge Buttons.
        Button(self.shared_control_frame,text="Refresh",
                                     command=self.refresh).pack(side=LEFT)
               
        self.reduce_button = Button(self.shared_control_frame,text="Reduce",
                                    command=self.reduce)
        self.reduce_button.pack(side=LEFT)
        
        Button(self.shared_control_frame,text="Enlarge",
                                     command=self.enlarge).pack(side=LEFT)

        self.back_button = Button(self.shared_control_frame,text="Back",
                                  state = DISABLED,
                                  command=self.back)
        self.back_button.pack(side=LEFT)


        self.forward_button = Button(self.shared_control_frame,text="Forward",
                                     state = DISABLED,
                                     command=self.forward)
        self.forward_button.pack(side=LEFT)



        # Auto_refresh check button.
        # Default is to not have the window Auto-refresh, because some
        # plots are very slow to generate (e.g. some preference map
        # plots).  Call self.auto_refresh_checkbutton.invoke() to
        # enable autorefresh in a subclassed constructor function.
        self.auto_refresh = False
        self.auto_refresh_checkbutton = Checkbutton(self.shared_control_frame,
                                                    text="Auto-refresh",
                                                    command=self.toggle_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=LEFT)
        self.auto_refresh_checkbutton.invoke()
        
        
        
        #self.sheetcoords = False
        
	self.normalize_checkbutton = Checkbutton(self.shared_control_frame,
                                                     text="Normalize",
                                                     command=self.toggle_normalize)
	self.normalize_checkbutton.pack(side=LEFT)
	self.normalize = False    
        
	self.integerscaling_checkbutton = Checkbutton(self.shared_control_frame,
                                                    text="Integer scaling",
                                                    command=self.toggle_integerscaling)
	self.integerscaling_checkbutton.pack(side=LEFT)
	self.integerscaling = False
        #self.sizeconvertfn = identity
            
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

        # For the first plot, use the INITIAL_PLOT_HEIGHT to calculate zoom.
# 	self.initial_plot=True
# 	self.height_of_tallest_plot=1.0
# 	self.min_master_zoom=3.0
	self.zoom_factor=1.2
        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=TOP,expand=YES,fill=X)
	### JCALERT: Put the button in here instead of in TemplatePanels
	self.sizeconvertfn = identity
	self.sheetcoords=False
	self.plotgroup=None


    def toggle_normalize(self):
        """Function called by Widget when check-box clicked"""
        self.normalize = not self.normalize
	self.plotgroup.normalize = self.normalize
        self.load_images()
	self.scale_images()
        self.display_plots()


    def toggle_integerscaling(self):
        """Function called by Widget when check-box clicked"""
        self.integerscaling = not self.integerscaling
        
        if self.integerscaling:
            self.plotgroup.sizeconvertfn = int
        else:
            self.plotgroup.sizeconvertfn = identity

        self.load_images()
	self.scale_images()        
        self.display_plots()

    def refresh(self,extra=None):
        """
        Main steps for generating plots in the Frame.  These functions
        must either be implemented, or overwritten.
        """
        Pmw.showbusycursor()
	### JCALERT! temporary hack.
	self.plotgroup=self.refresh_plotgroup()
	self.plotgroup.sheetcoords=self.sheetcoords
	self.plotgroup.sizeconvertfn=self.sizeconvertfn	
        self.load_images()                #  load bitmap images
        self.scale_images()               #scale bitmap images
        self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()



    ### JCALERT! 
    ### This function is called to re-generate the PlotGroup anytime if needed.
    ### It shouldn't be re-implmented by subclasses, only generate_sheet_views should be
    def refresh_plotgroup(self):
        """
	Function that re-generate the PlotGroup anytime.
        """
	plotgroup = plotgroup_dict.get(self.plotgroup_key,None)
	if plotgroup == None:
	    plotgroup = self.PlotGroup(self.plotgroup_key,[],self.normalize,
				       self.sheetcoords,self.integerscaling)
	return plotgroup
  
  
    def load_images(self):
	"""
	Pre:  self.pe_group contains a PlotGroup.
        Post: self.bitmaps contains a list of Bitmap Images ready for display.

        If new_iteration is True, advances the plot history counter; otherwise
        just overwrites the current one.
	"""
	self.bitmaps = self.plotgroup.load_images()

        # Repeated plots at the same time overwrite the top plot history item;
        # new ones are added to the list only when the simulator time changes.
        if self.time_history and (self.time_history[-1] ==
                                  self.console.simulator.time()):
            self.bitmaps_history.pop()
            self.time_history.pop()
        
        self.bitmaps_history.append(copy.copy(self.bitmaps))
        self.time_history.append(copy.copy(self.console.simulator.time()))
        self.history_index = len(self.bitmaps_history)-1
        self.plot_time=copy.copy(self.console.simulator.time())

    ### JCALERT! will have to disapear.
    def scale_images(self):
        """
        It is assumed that the PlotGroup code has not scaled the bitmap to the size currently
        desired by the GUI.
	"""
            
        if (self.history_index > 0):
            self.back_button.config(state=NORMAL)
        else:
            self.back_button.config(state=DISABLED)

        if self.history_index >= len(self.bitmaps_history)-1:
            self.forward_button.config(state=DISABLED)
        else:
            self.forward_button.config(state=NORMAL)



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
 
	### JCALERT: This has to be changed.
	self.zoomed_images = [ImageTk.PhotoImage(b.image) for b in self.bitmaps]
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
            


    def display_labels(self):
        """
        This function should be redefined by subclasses to match any
        changes made to display__plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        if self._num_labels != len(self.canvases):
            old_labels = self.labels
            self.labels = [Label(self.plot_frame,text=each.plot_src_name + '\n' + each.name)
				 for each in self.bitmaps]
            for i in range(len(self.labels)):
                self.labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self._num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.labels)):
                self.labels[i].configure(text=self.bitmaps[i].plot_src_name +'\n' + self.bitmaps[i].name) 
 
      
    def refresh_title(self):
        """
        Change the window title.  TopoConsole will call this on
        startup of window.  
        """
        self.parent.title(topo.sim.name+': '+"%s time:%s" % (self.plotgroup_key,self.plot_time))
          

    def reduce(self):
        """Function called by Widget to reduce the zoom factor"""
        if self.plotgroup.height_of_tallest_plot > self.plotgroup.min_master_zoom:	
	    self.plotgroup.height_of_tallest_plot = self.plotgroup.height_of_tallest_plot/self.zoom_factor

        if self.plotgroup.height_of_tallest_plot <= self.plotgroup.min_master_zoom:
            self.reduce_button.config(state=DISABLED)
         
        self.load_images()
        self.scale_images()
        self.display_plots()

    
    def enlarge(self):
        """Function called by Widget to increase the zoom factor"""
        self.reduce_button.config(state=NORMAL)
        self.plotgroup.height_of_tallest_plot = self.plotgroup.height_of_tallest_plot*self.zoom_factor
        self.load_images()
        self.scale_images()
        self.display_plots()

    # JLALERT: It would be nice to be able to scroll back through many
    # iterations.  Could put in a box for entering either the iteration
    # number you want to view, or perhaps how many you want to jump...
    def back(self):
        """Function called by Widget to scroll back through the previous bitmaps"""
        self.history_index -= 1
        
        self.bitmaps=self.bitmaps_history[self.history_index]
        self.plot_time=self.time_history[self.history_index]        
        self.display_labels()
        self.refresh_title()
        self.scale_images()
        self.display_plots()



    def forward(self):
        """
        Function called by Widget to scroll forward through the bitmaps.

        Only useful if previously you have scrolled back.
        """
        self.history_index += 1
        
	self.bitmaps=self.bitmaps_history[self.history_index]
        self.plot_time=self.time_history[self.history_index]
        self.display_labels()
        self.refresh_title()
        self.scale_images()
        self.display_plots()
        

    def toggle_auto_refresh(self):
        """Function called by Widget when check-box clicked"""
        self.auto_refresh = not self.auto_refresh
        self.debug("Auto-refresh = ", self.auto_refresh)
        topo.tkgui.show_cmd_prompt()
        if self.auto_refresh:
            self.console.auto_refresh_panels.append(self)
        else:
            self.console.auto_refresh_panels.remove(self)
        # JAB: it might make sense for turning on auto-refresh
        # to do a refresh automatically, though that might have
        # unexpected behavior for a preference map calculation
        # (where it would do unnecessary, and potentially lengthy,
        # recalculation).
        
    def toggle_sheetcoords(self):
        """Function called by Widget when check-box clicked"""
        self.sheetcoords = not self.sheetcoords
	self.plotgroup.sheetcoords = self.sheetcoords
        self.load_images()
        self.scale_images()
        self.display_plots()


    def destroy(self):
        if self.auto_refresh:
            self.console.auto_refresh_panels.remove(self)
        Frame.destroy(self)



