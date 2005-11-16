"""
Plot panels to support GUI windows that display bitmap
plots. Related classes include Plot, PlotGroup, and PlotEngine.

BasicPlotPanel is the smallest class possible to create a new plot
window.  Look at it as an example of creating additional subclasses.

$Id$
"""
__version__='$Revision $'

import Pmw, re, os, sys
from Tkinter import Frame, TOP, YES, BOTH, BOTTOM, X, Button, LEFT, \
     RIGHT, DISABLED, Checkbutton, NORMAL, Canvas, Label, NSEW, IntVar, StringVar
import topo
import topo.base.topoobject
import topo.plotting.bitmap
import topo.base.simulator as simulator
import topo.plotting.plotengine as plotengine
import topo.base.registry as registry
import topo.plotting.plotgroup
import PIL
import Image
import ImageTk
import Numeric
import MLab

### JCALERT: the name has been changed from PlotPanel to PlotGroupPanel
### I think we might also want to change the name of the subclasses (e.g. UnitWeightPanel...)
### also, the file can be renamed plotgrouppanel.py (carefull the import statement in others files 
### also have to be replaced

class PlotGroupPanel(Frame,topo.base.topoobject.TopoObject):
    """
    Abstract PlotGroupPanel class for displaying bitmapped images to a TK
    GUI window.  Must be subclassed to be usable.
    """

    @staticmethod
    def valid_context():
        """
        Test if this panel should be allowed to be opened by the TopoConsole.

        Given the existing Simulator definitions has no GeneratorSheets, or
        no ProjectionSheets, some panels should not be opened.  TopoConsole
        will call this function before creating an instance.
        """
        return True
#    valid_context = MakeStaticFunction(valid_context)

    def __init__(self,parent,pengine,console,plot_key,pgt_name=None,
                 plotgroup_type='BasicPlotGroup',**config):
        """
        parent:  it is the window (GUIToplevel()) that contains the panel.
        pengine: is the associated PlotEngine; it might end up to be unnecessary, needs fixing.
        console: is the associated console, (i.e. the TopoConsole that has this panel)
        plot_key: defines the title of the panel.
                  In the case of an activity plot or a feature map plot the title
                  is only the name of template (pgt_name)
                  In the case of projection and unit weights there is additional information
                  that are added by the method generate_plt_key (e.g. density, unit coordinates...)
        pgt_name: name of the PlotGroupTemplate associated with the panel
        plot_group_type: type of the PlotGroup associated with the panel
        
        """

        Frame.__init__(self,parent,config)
        topo.plotting.plot.TopoObject.__init__(self,**config)

        ### Usually the pgt_name is the plot_key by default,
        ### but for inputparamspanel pgt_name = None and the plot_key is 'Preview'
        ### passed by default when creating the class
        if pgt_name!=None:
            self.plot_key = pgt_name
        else:
            self.plot_key=plot_key

            
        self.plotgroup_type = plotgroup_type 
        self.pgt_name = pgt_name  #Plot Group Template name

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

        self.pe = pengine
        self.pe_group = None
        self.plots = []
        self.bitmaps = []
        self.labels = []
        self.__num_labels = 0

        self.console = console
        self.parent = parent
        self.balloon = Pmw.Balloon(parent)
        self.canvases = []

        # I think we can get rid of that
        #self.panel_num = self.console.num_activity_windows

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
        pgt = registry.plotgroup_templates[self.pgt_name]
        if pgt:
            ### JABALERT! Why is it checking the first template for this?            
            self.normalize = pgt.plot_templates[0].channels.get('Normalize',False)
            self.normalize_checkbutton = Checkbutton(self.shared_control_frame,
                                                     text="Normalize",
                                                     command=self.toggle_normalize)
            if self.normalize:
                self.normalize_checkbutton.select()
            self.normalize_checkbutton.pack(side=LEFT)

        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')
        self.plot_group = Pmw.Group(self,tag_text=str(self.plot_key))
        self.plot_group.pack(side=TOP,expand=YES,fill=BOTH,padx=5,pady=5)
        self.plot_frame = self.plot_group.interior()

        # For the first plot, use the INITIAL_PLOT_WIDTH to calculate zoom.
        self.initial_plot = True
        self.zoom_factor = self.min_zoom_factor = 1
        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=TOP,expand=YES,fill=X)

        # self.refresh()


    def toggle_normalize(self):
        """Function called by Widget when check-box clicked"""
        self.normalize = not self.normalize
        pgt = registry.plotgroup_templates[self.pgt_name]
        for (k,each) in pgt.plot_templates:
            each.channels['Normalize'] = self.normalize
        self.refresh()


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


    def refresh_title(self):
        """
        Change the window title.  TopoConsole will call this on
        startup of window.  
        """
        self.parent.title("%s time:%s" % (self.plot_key,self.pe.simulation.time()))


    def do_plot_cmd(self):
        """
        Subclasses of PlotGroupPanel will need to create this function to
        generate the plots.

        See UnitWeightsPanel and ProjectionPanel for
        examples.
        """
        self.pe_group = self.pe.get_plot_group(self.plot_key,
                                               self.plotgroup_type)
        self.pe_group.do_plot_cmd()
        self.plots = self.pe_group.plots()
    

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

        Image scaling is automatically done, as well as adjusted by the
        user.  self.MIN_PLOT_WIDTH is the number of pixels wide the
        smallest plot figure can be, and self.INITIAL_PLOT_WIDTH is the
        number of pixels wide the smallest plot figure will be on the
        first display.
        """
        # need to calculate the old min width, so we know if we need to reset
        # the zoom factors
        if self.bitmaps:
            old_min_width = reduce(min,[im.width() for im in self.bitmaps])
        else:
            old_min_width = -1

        if self.pe_group:
            self.bitmaps = self.pe_group.load_images()
        
        if self.bitmaps:
            min_width = reduce(min,[im.width() for im in self.bitmaps])
        else:
            min_width = 0

        # If the min width changed, then recalculate the zoom factor
        # If no plots, then no window.
        if old_min_width != min_width:
            if self.initial_plot and min_width != 0 and self.INITIAL_PLOT_WIDTH != None:
                self.zoom_factor = int(self.INITIAL_PLOT_WIDTH/min_width) + 1
                if self.zoom_factor < self.min_zoom_factor:
                    self.zoom_factor = self.min_zoom_factor
                self.initial_plot = False
            if self.MIN_PLOT_WIDTH > min_width and min_width != 0:
                self.min_zoom_factor = int(self.MIN_PLOT_WIDTH/min_width) + 1
                if self.zoom_factor < self.min_zoom_factor:
                    self.zoom_factor = self.min_zoom_factor
            else:
                self.min_zoom_factor = 1

            if self.zoom_factor > self.min_zoom_factor:
                self.reduce_button.config(state=NORMAL)
            else:
                self.reduce_button.config(state=DISABLED)

        
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
        self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor))
                              for im in self.bitmaps]

        # If the number of canvases or their sizes has changed, then
        # create a new set of canvases.  If the old canvases still can
        # work, then reuse them to prevent flicker.
        if self.canvases and len(self.zoomed_images) > 0:
            new_sizes = [(str(zi.width()),str(zi.height()))
                         for zi in self.zoomed_images]
            old_sizes = [(zi.config()['width'][-1],zi.config()['height'][-1])
                         for zi in self.canvases]
        else:
            new_sizes, old_sizes = 0, 0
        if len(self.zoomed_images) != len(self.canvases) or \
               new_sizes != old_sizes:
            old_canvases = self.canvases
            self.canvases = [Canvas(self.plot_frame,
                                    width=image.width(),
                                    height=image.height(),
                                    bd=0)
                             for image in self.zoomed_images]
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.create_image(image.width()/2,image.height()/2,image=image)
                canvas.grid(row=0,column=i,padx=5)
            for c in old_canvases:
                c.grid_forget()
        else:  # Width of first plot still same, and same number of images.
            for i,image,canvas in zip(range(len(self.zoomed_images)),
                                      self.zoomed_images,self.canvases):
                canvas.create_image(image.width()/2,image.height()/2,image=image)
                canvas.grid(row=0,column=i,padx=5)
            


    def display_labels(self):
        """
        This function should be redefined by subclasses to match any
        changes made to display__plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        if self.__num_labels != len(self.canvases):
            old_labels = self.labels
            self.labels = [Label(self.plot_frame,text=each.view_info['src_name'])
                           for each in self.bitmaps]
            for i in range(len(self.labels)):
                self.labels[i].grid(row=1,column=i,sticky=NSEW)
            for l in old_labels:
                l.grid_forget()
            self.__num_labels = len(self.canvases)
        else:  # Same number of labels; reuse to avoid flickering.
            for i in range(len(self.labels)):
                self.labels[i].configure(text=self.bitmaps[i].view_info['src_name']) 
                 

    def reduce(self):
        """Function called by Widget to reduce the zoom factor"""
        if self.zoom_factor > self.min_zoom_factor:
            self.zoom_factor = self.zoom_factor - 1

        if self.zoom_factor == self.min_zoom_factor:
            self.reduce_button.config(state=DISABLED)
            
        self.display_plots()

    
    def enlarge(self):
        """Function called by Widget to increase the zoom factor"""
        self.reduce_button.config(state=NORMAL)
        self.zoom_factor = self.zoom_factor + 1
        self.display_plots()


    def toggle_auto_refresh(self):
        """Function called by Widget when check-box clicked"""
        self.auto_refresh = not self.auto_refresh

        self.debug("Auto-refresh = ", self.auto_refresh)
        topo.tkgui.show_cmd_prompt()

        if self.auto_refresh:
            self.console.add_auto_refresh_panel(self)
        else:
            self.console.del_auto_refresh_panel(self)


    def destroy(self):
        if self.auto_refresh:
            self.console.del_auto_refresh_panel(self)
        Frame.destroy(self)



