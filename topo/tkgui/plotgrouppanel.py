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

import topo.tkgui
import topo.base.parameterizedobject
import topo.base.simulator 
from topo.base.sheet import Sheet

import topo.plotting.bitmap
import topo.plotting.plotgroup
from topo.plotting.templates import plotgroup_templates

def identity(x):
    """No-op function for use as a default."""
    return x

BORDERWIDTH = 1

# Unfortunately, the canvas creation, border placement, and image
# positioning of Tkinter are very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.  
CANVASBUFFER = 1


class PlotGroupPanel(Frame,topo.base.parameterizedobject.ParameterizedObject):
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

    def __init__(self,parent,console,name,**params):
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

	# For a PlotGroupPanel, the plot_group_key is the name passed at creation.
	# (e.g for testpattern it is 'Preview')
        # For a TemplatePlotGroupPanel, name is the name of the associated template 
        # For a ConnectionField or a Projection Panel, the plotgroup_key is re-generated
	self.plot_group_key = name

        # Each plot can have a different minimum size.  If INITIAL_PLOT_WIDTH
        # is set to None, then no initial zooming is performed.  However,
        # MIN_PLOT_WIDTH may cause a zoom if the raw bitmap is still too
        # tiny.
        self.MIN_PLOT_HEIGHT = 1
        self.INITIAL_PLOT_HEIGHT = 150

        self.pe_group = None        
        self.bitmaps = []
        self.bitmaps_history=[]
        self.time_history=[]
        self.history_index = -1
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
                                    state=DISABLED,
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
        
        
        
        self.sheetcoords = False
        
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
        self.sizeconvertfn = identity
            
        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')

	self.plot_group_title = Pmw.Group(self,tag_text=str(self.plot_group_key))
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
        self.initial_plot = True
        self.zoom_factor = 1
	self.min_zoom_factor = 1
        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=TOP,expand=YES,fill=X)


        

    def toggle_normalize(self):
        """Function called by Widget when check-box clicked"""
        self.normalize = not self.normalize
	self.pe_group.normalize = self.normalize
        self.load_images()
        self.history_index = self.history_index -1 #ensure index is changed only by an iteration 
        self.display_plots()

    def toggle_integerscaling(self):
        """Function called by Widget when check-box clicked"""
        self.integerscaling = not self.integerscaling
        
        if self.integerscaling:
            self.sizeconvertfn = int
        else:
            self.sizeconvertfn = identity

        identity
        self.load_images()
        self.history_index = self.history_index -1 
        self.display_plots()

    def refresh(self,extra=None):
        """
        Main steps for generating plots in the Frame.  These functions
        must either be implemented, or overwritten.
        """
        Pmw.showbusycursor()
        self.do_plot_cmd()                # Create plot tuples
        self.load_images()                #  load bitmap images
        self.scale_images()               #scale bitmap images
        self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()



    ### JCALERT! 
    ### This function is actually always re-implemented....
    ### It can also be made so that we spared the templateplotgrouppanel re-implementation...
    def do_plot_cmd(self):
        """
        Subclasses of PlotGroupPanel will need to create this function to
        generate the plots.

        See ConnectionFieldsPanel and ProjectionPanel for
        examples.
        """
        self.pe_group = self.PlotGroup(self.plot_group_key,[],self.normalize)
	### JCALERT! That should be make uniform with the templateplotgrouppanel and then eventually maybe
        ### get rid of the basicplotgrouppanel. (i.E. merged plotgrouppanel and basicplotgrouppanel)
	self.pe_group.initialize_plot_list(plot_list=[])
        self.pe_group.do_plot_cmd()
  
  
    def load_images(self):
	"""
	Pre:  self.pe_group contains a PlotGroup.
        Post: self.bitmaps contains a list of Bitmap Images ready for display.
	"""
        self.history_index = self.history_index +1
        if (self.history_index > 0):
           self.back_button.config(state=NORMAL)
        else:
            self.back_button.config(state=DISABLED)
        
	self.bitmaps = self.pe_group.load_images()
        self.bitmaps_history.append(copy.copy(self.bitmaps))
        self.time_history.append(copy.copy(self.console.simulator.time()))
        


        
    def scale_images(self):
        """
        It is assumed that the PlotGroup code has not scaled the bitmap to the size currently
        desired by the GUI.
        """
        
        
        ### Should probably compute an initial master_zoom for both 
        ### sheetcoords=1 and sheetcoords=0, and then we can switch back
        ### and forth between them at will.
        #if self.sheetcoords==1:
            #sheet_heights = [i.get(bitmap.plot_src_name,None).bounds().lbrt().top()- ... for i in topo.sim.objects(Sheet)]
            #max_density = float(reduce(max,[im.height() for im in self.bitmaps if im.resize]))

            #[i.get(bitmap.plot_src_name,None).density()- ... for i in topo.sim.objects(Sheet)]
            #max_height = density*max_sheet_height....
        #else:
        max_height = float(reduce(max,[im.height() for im in self.bitmaps if im.resize]))

	tmp_list = []

 	### JCALERT/JABALERT! The calculation of the initial and minimum sizes
        ### might need to be in a sub-function so that it can be overridden
        ### for ProjectionPanel.  It also might be necessary to move the
        ### calculation into PlotGroup, because similar things will be needed
        ### even when saving plots directly to disk.
	if (self.initial_plot == True):
            if (max_height == 0 or max_height >= self.INITIAL_PLOT_HEIGHT):
	       self.zoom_factor = 1
            else:
	       self.zoom_factor = int(self.INITIAL_PLOT_HEIGHT/max_height)
               self.reduce_button.config(state=NORMAL)
	    self.initial_plot=False
	for bitmap in self.bitmaps:

            if not bitmap.resize:
                adjust=1
            else:
                if self.sheetcoords==1:
                    s = topo.sim.objects(Sheet).get(bitmap.plot_src_name,None)
                    # JABALERT: Instead of arbitrary factor 10, should
                    # scale largest bitmap to INITIAL_PLOT_HEIGHT in every case
                    # Maybe: rename zoom_factor to master_zoom, and adjust to zoom_factor
                    adjust=self.zoom_factor*self.sizeconvertfn(10/float(s.density))
                else:
                    adjust=self.zoom_factor*self.sizeconvertfn(max_height/bitmap.height())
                              
            tmp_list = tmp_list + [bitmap.zoom(adjust)]
	
	self.zoomed_images = [ImageTk.PhotoImage(im) for im in tmp_list]

        if (self.history_index ==0):
            self.back_button.config(state=DISABLED)

        if (self.history_index >= self.console.simulator.time()):
            self.forward_button.config(state=DISABLED)
        
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
        self.parent.title(topo.sim.name+': '+"%s time:%s" % (self.plot_group_key,topo.sim.time()))
          

    def reduce(self):
        """Function called by Widget to reduce the zoom factor"""
        if self.zoom_factor > self.min_zoom_factor:
            self.zoom_factor = self.zoom_factor - 1

        if self.zoom_factor == self.min_zoom_factor:
            self.reduce_button.config(state=DISABLED)
         
	self.load_images()
        self.history_index = self.history_index -1
        self.scale_images()
        self.display_plots()

    
    def enlarge(self):
        """Function called by Widget to increase the zoom factor"""
        self.reduce_button.config(state=NORMAL)
        self.zoom_factor = self.zoom_factor + 1

	self.load_images()
        self.history_index = self.history_index -1 
        self.scale_images()
        self.display_plots()

# JLHACKALERT Back and forward buttons - There is no need for back and forward buttons on the connection field window,
# also currently will only scroll through bitmaps that have been explicity loaded - can it display any bitmap by loading the image for that iteration?
# I also think this will need to be implemented seperately for each window type to get the correct plot_group_title and parent.title
# It would also be nice to be able to scroll back through many iterations - put in a box for entering either the iteration number
# you want to view or how many you want to jump maybe?

    def back(self):
        """Function called by Widget to scroll back through the previous bitmaps"""
        self.history_index = self.history_index - 1
        self.forward_button.config(state=NORMAL)

        self.bitmaps=self.bitmaps_history[self.history_index]
        current_time=self.time_history[self.history_index]

        self.plot_group_title.configure(tag_text = self.mapname.get() + ' at time ' + str(current_time))
        self.parent.title(topo.sim.name+': '+"%s time:%s" % (self.plot_group_key,current_time))

        self.scale_images()
        self.display_plots()



    def forward(self):
        """Function called by Widget to scroll forward through the bitmaps if previously you have scrolled back"""
        self.history_index = self.history_index + 1
        self.back_button.config(state=NORMAL)
	self.bitmaps=self.bitmaps_history[self.history_index]
        current_time=self.time_history[self.history_index]

        self.plot_group_title.configure(tag_text = self.mapname.get() + ' at time ' + str(current_time))
        self.parent.title((topo.sim.name+': '+"%s time:%s" %(self.plot_group_key, current_time)))

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
        self.load_images()
        self.history_index = self.history_index -1 
        self.scale_images()
        self.display_plots()


    def destroy(self):
        if self.auto_refresh:
            self.console.auto_refresh_panels.remove(self)
        Frame.destroy(self)



