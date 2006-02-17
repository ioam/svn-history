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

import PIL
import Image
import ImageTk
import Pmw, re, os, sys
from Tkinter import Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, \
     StringVar, FLAT, SUNKEN, RAISED, GROOVE, RIDGE

import topo.tkgui
import topo.base.topoobject
import topo.base.simulator 

import topo.plotting.bitmap
import topo.plotting.plotgroup
from topo.plotting.templates import plotgroup_templates


BORDERWIDTH = 1

# Unfortunately, the canvas creation, border placement, and image
# positioning of Tkinter are very fragile.  This value boosts the size
# of the canvas that the plot image is displayed on.  Too large and
# the border will not be close, too small, and some of the image is
# not displayed.  
CANVASBUFFER = 1


class PlotGroupPanel(Frame,topo.base.topoobject.ParameterizedObject):
    """
    Abstract PlotGroupPanel class for displaying bitmapped images to a TK
    GUI window.  Must be subclassed to be usable.
    """

    @staticmethod
    def valid_context():
        """
        Return true if there appears to be data available for this type of plot.

        Some PlotGroupPanel classes plot only certain types of Sheets,
        such as GeneratorSheets or ProjectionSheets.  To avoid
        confusion and avoid errors later, callers can check this
        static method before instantiating a plot of this type.
        Subclasses should define this method to return false when it
        is clear there is no appropriate data to plot."""
        return True

    def __init__(self,parent,console,pgt_name,**config):
        """
        parent:  it is the window (GUIToplevel()) that contains the panel.
        console: is the associated console, (i.e. the TopoConsole that has this panel)
        pgt_name: name of the PlotGroupTemplate associated with the panel
	"""

	### JCALERT! what is config and why is it passed to both ParameterizedObject and Frame?
        Frame.__init__(self,parent,config)
        topo.plotting.plot.ParameterizedObject.__init__(self,**config)

	self.console = console
        self.parent = parent
        self.balloon = Pmw.Balloon(parent)
        self.canvases = []

	self.pgt = plotgroup_templates.get(pgt_name,None)

	# By default, the plot_group_key is the pgt_name.
	# for testpattern it is 'Preview' that does not corresponds to any template.
        # for connectionfield and projection panel, the plotgroup_key is re-generated
	self.plot_group_key = pgt_name
         
	### JCALERT! This is not used for the moment, but it could:
        ### if the template specified an associated PlotGroup, we could do
	### self.plotgroup_type = self.pgt.plotgroup_type
        ### and then used that in the do_plot_cmd to create the PlotGroup.
        ### this has to be discussed, as well as the topoconsole line that associate template with panel:
        ### could all be done from the template.
        ### Also, do we want to associate panel and plotgroup: in which case, we could only specified a panel
        ### for a template and then creating a single type of PlotGroup for any panel (as it is now)

        #self.plotgroup_type = plotgroup_type # type of the PlotGroup 

        ### JABHACKALERT!
        ###
        ### When the GeneratorSheet.density is changed to a relatively
        ### large but not unreasonable number, e.g. 512*512, the plot
        ### window is many times larger than the screen, and there's
        ### no way to reach the Reduce button.  In general, there need
        ### to be scrollbars for viewing plots too large for the
        ### screen.
        ###
        ### In this particular case, there appears to be a bug in how
        ### INITIAL_PLOT_WIDTH is handled, because with a size of 512
        ### a fixed INITIAL_PLOT_WIDTH of 60 shouldn't have any effect
        ### at all.  Yet changing INITIAL_PLOT_WIDTH to 1 fixes the
        ### size problem, and makes the images fit on screen with no
        ### problem.  Very strange.  My guess for the culprit is the line:
        ###
        ###   self.zoom_factor = int(self.INITIAL_PLOT_WIDTH/min_width) + 1
        ###
        ### (below), which doesn't seem at all a correct way to
        ### enforce a minimum width and an initial width.
        
        
        # Each plot can have a different minimum size.  If INITIAL_PLOT_WIDTH
        # is set to None, then no initial zooming is performed.  However,
        # MIN_PLOT_WIDTH may cause a zoom if the raw bitmap is still too
        # tiny.
        self.MIN_PLOT_WIDTH = 1
        self.INITIAL_PLOT_WIDTH = 60


        self.pe_group = None
        self.plots = []
        self.bitmaps = []
        self.labels = []
        self._num_labels = 0

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

        # Default is to not have the window Auto-refresh, because some
        # plots are very slow to generate (e.g. some preference map
        # plots).  Call self.auto_refresh_checkbutton.invoke() to
        # enable autorefresh in a subclassed constructor function.
        self.auto_refresh = 0
        self.auto_refresh_checkbutton = Checkbutton(self.shared_control_frame,
                                                    text="Auto-refresh",
                                                    command=self.toggle_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=LEFT)
        self.auto_refresh_checkbutton.invoke()

        # Normalization check button.
	### JCALERT! Do we want to always pass a template (for the moment, the exception is testpattern?)
        ### there is no normalize button for the testpattern... is this right?
        if self.pgt:        
            self.normalize_checkbutton = Checkbutton(self.shared_control_frame,
                                                     text="Normalize",
                                                     command=self.toggle_normalize)
	    self.normalize_checkbutton.pack(side=LEFT)
	    self.normalize = self.pgt.normalize    
            if self.normalize:
                self.normalize_checkbutton.select()
            
        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')
        self.plot_group_title = Pmw.Group(self,tag_text=str(self.plot_group_key))
        self.plot_group_title.pack(side=TOP,expand=YES,fill=BOTH,padx=5,pady=5)
        self.plot_frame = self.plot_group_title.interior()

        # For the first plot, use the INITIAL_PLOT_WIDTH to calculate zoom.
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
        self.display_plots()


    def refresh(self,extra=None):
        """
        Main steps for generating plots in the Frame.  These functions
        must either be implemented, or overwritten.
        """
        Pmw.showbusycursor()
        self.do_plot_cmd()                # Create plot tuples
        self.load_images()                # Scale bitmap images
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
  
  
    ### JCALERT! Re-write the doc for this function
    def load_images(self):
	"""
	Pre:  self.pe_group contains a PlotGroup
              self.plots contains a list of plots following the
	      format provided by PlotGroup.plots()
        Post: self.bitmaps contains a list of Bitmap Images ready for display.

        No geometry or Sheet information is necessary to perform the
        operations in this function, so it is unlikely that load_images()
        will need to be redefined from a subclass.  It is assumed that
        the PlotGroup code has not scaled the bitmap to the size currently
        desired by the GUI.
	"""

	self.bitmaps = self.pe_group.load_images()

	min_width = reduce(min,[im.width() for im in self.bitmaps if im.resize])
	max_height = float(reduce(max,[im.height() for im in self.bitmaps if im.resize]))
	tmp_list = []

	### JCALERT! We should work on this part in order to find a way to ensure a correct minimum size...
        ### it should be in a sub-function in order to override it from projectionpanel.py
	if ((self.initial_plot == True) and (min_width != 0)):
	    self.zoom_factor = int(self.INITIAL_PLOT_WIDTH/min_width) + 1
	    self.initial_plot=False
	    
	for bitmap in self.bitmaps:
	    if not bitmap.resize:
		tmp_list = tmp_list + [bitmap.zoom(self.zoom_factor*max_height/bitmap.height())]
	    else:
		tmp_list = tmp_list + [bitmap.zoom(self.zoom_factor*int(max_height/bitmap.height()))]
	    
	self.zoomed_images = [ImageTk.PhotoImage(im) for im in tmp_list]

        
    def display_plots(self):
        """
        Pre:  self.bitmaps contains a list of topo.bitmap objects.

        Post: The bitmaps have been displayed to the screen in the active
              console window.  All images are displayed from left to right,
              in a single row.  If the number of images have changed since
              the last display, the grid size is increased, or decreased
              accordingly.

        This function shuld be redefined in subclasses for interesting
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
        self.parent.title("%s time:%s" % (self.plot_group_key,self.console.simulator.time()))
          

    def reduce(self):
        """Function called by Widget to reduce the zoom factor"""
        if self.zoom_factor > self.min_zoom_factor:
            self.zoom_factor = self.zoom_factor - 1

        if self.zoom_factor == self.min_zoom_factor:
            self.reduce_button.config(state=DISABLED)
         
	self.load_images()
        self.display_plots()

    
    def enlarge(self):
        """Function called by Widget to increase the zoom factor"""
        self.reduce_button.config(state=NORMAL)
        self.zoom_factor = self.zoom_factor + 1

	self.load_images()
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


    def destroy(self):
        if self.auto_refresh:
            self.console.auto_refresh_panels.remove(self)
        Frame.destroy(self)



