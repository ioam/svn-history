"""

Abstract Class PlotPanel to support GUI windows that display bitmap
plots. PlotPanel should deal with the GUI, and as much as possible use
GUI independent code from outside the topo.tk package.  See Plots,
PlotGroups, and PlotEngine.

activitypanel.py is the smallest class possible to create a new plot
window.  Look at it as an example of creating additional subclasss.

$Id$
"""
import Pmw, re, os, sys
import topo
import topo.base
import topo.bitmap
from topo.tk.propertiesframe import *
import topo.simulator as simulator
import topo.plotengine as plotengine
import PIL
import Image
import ImageTk
import Numeric
import MLab

NYI = "Not Yet Implemented."

def enum(seq):  return zip(range(len(seq)),seq)

class PlotPanel(Frame,topo.base.TopoObject):
    """
    Abstract PlotPanel class for displaying bitmaped images to a TK
    GUI window.  Must be subclassed.
    """

    def __init__(self,parent=None,pengine=None,console=None,**config):
        assert isinstance(pengine,plotengine.PlotEngine) or pengine == None, \
               'Variable pengine not PlotEngine object.'

        Frame.__init__(self,parent,config)
        topo.plot.TopoObject.__init__(self,**config)

        self.plot_key = NYI    
        self.plotgroup_type = NYI

        # Each plot can have a different minimum size.  If INITIAL_PLOT_WIDTH
        # is set to None, then no initial zooming is performed.  However,
        # MIN_PLOT_WIDTH may cause a zoom if the raw bitmap is still too
        # tiny.
        self.MIN_PLOT_WIDTH = 1
        self.INITIAL_PLOT_WIDTH = 100

        self.pe = pengine
        self.pe_group = None
        self.plots = []
        self.bitmaps = []
        self.labels = []
        self.__num_labels = 0
        self.panel_num = 1

        self.console = console
        self.parent = parent
        self.balloon = Pmw.Balloon(parent)
        self.canvases = []

        # Main Plot group title can be changed from a subclass with the
        # command: self.plot_group.configure(tag_text='NewName')
        self.plot_group = Pmw.Group(self,tag_text='Plot')
        self.plot_group.pack(side=TOP,expand=YES,fill=BOTH,padx=5,pady=5)
        self.plot_frame = self.plot_group.interior()

        # For the first plot, use the INITIAL_PLOT_WIDTH to calculate zoom.
        self.initial_plot = True
        self.zoom_factor = self.min_zoom_factor = 1
        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=BOTTOM,expand=YES,fill=X)

        # Refresh, Reduce, and Enlarge Buttons.
        Button(self.control_frame,text="Refresh",
               command=self.refresh).pack(side=LEFT)
        self.reduce_button = Button(self.control_frame,text="Reduce",
                                   state=DISABLED,
                                   command=self.reduce)
        self.reduce_button.pack(side=LEFT)
        Button(self.control_frame,text="Enlarge",
               command=self.enlarge).pack(side=LEFT)        

        # Default is to not have the window Auto-refresh, because of
        # possible slow plots.  Call self.auto_refresh_checkbutton.invoke()
        # to enable it in a subclassed constructor function.
        self.auto_refresh = 0
        self.auto_refresh_checkbutton = Checkbutton(self.control_frame,
                                                    text="Auto-refresh",
                                                    command=self.toggle_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=LEFT)
        self.auto_refresh_checkbutton.invoke()
        # self.refresh()


    def refresh(self):
        """
        Main steps for generating plots in the Frame.  These functions
        must be implemented, or overwritten.
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
        self.parent.title("%s %d" % (self.plot_key,self.panel_num))


    def do_plot_cmd(self):
        """
        Subclasses of PlotPanel will need to create this function to
        generate the plots.

        See topo.tk.WeightsPanel and topo.tk.WeightsArrayPanel for
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

        # If the number of canvases has changed, or the width of the
        # first plot and canvas no longer match, then create a new set
        # of canvases.  If the old canvases still can work, then use
        # them to prevent flicker.
        if self.canvases:
            first_new_width = str(self.zoomed_images[0].width())
            first_old_width = self.canvases[0].config()['width'][-1]
        else:
            first_new_width, first_old_width = 0, 0
        if len(self.zoomed_images) != len(self.canvases) or \
               first_new_width != first_old_width:
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
        """Function called by Widget, to reduce the zoom factor"""
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
        topo.tk.show_cmd_prompt()

        if self.auto_refresh:
            self.console.add_auto_refresh_panel(self)
        else:
            self.console.del_auto_refresh_panel(self)


    def destroy(self):
        if self.auto_refresh:
            self.console.del_auto_refresh_panel(self)
        Frame.destroy(self)


##############################################
#
# Different kinds of plot panels.  Unchanged since LISSOM.  Will need
# to be exported to their own files and rewritten.
#


class PreferenceMapPanel(PlotPanel):
    def __init__(self,parent,console=None,**config):

        # Default cmdname for each mapname
        self.mapcmds = dict((('OrientationPreference',      'call measure_or_pref '),
                             ('OcularPreference',           'call measure_or_pref'),
                             ('DirectionPreference',        'call measure_dir_pref'),
                             ('PositionPreference',         'call measure_cog'),
                             ('SpatialFrequencyPreference', 'call measure_or_pref'),
                             ('SpatialPhasePreference',     'call measure_or_pref'),
                             ('SpeedPreference',            'call measure_dir_pref')))

        # Name of the plotgroup to plot
        self.mapname = StringVar()
        self.mapname.set('OrientationPreference')

        # lissom command used to refresh the plot, if any
        self.cmdname = StringVar()
        self.cmdname.set(self.mapcmds[self.mapname.get()])
        
        PlotPanel.__init__(self,parent,console=console,**config)

        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)
        
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.mapname,
                     scrolledlist_items=('OrientationPreference',
                                         'OcularPreference',
                                         'DirectionPreference',
                                         'PositionPreference',
                                         'SpatialFrequencyPreference',
#                                        'SpatialPhasePreference',
                                         'SpeedPreference')
                     ).pack(side=LEFT,expand=YES,fill=X)

        # Ideally, whenever self.mapname changes this selection would be 
        # updated automatically by looking in self.mapcmds.  However, I 
        # don't know how to set up such a callback. (jbednar@cs)
        Pmw.ComboBox(params_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.cmdname,
                     scrolledlist_items=('call measure_or_pref',
                                         'call measure_od_pref',
                                         'call measure_dir_pref',
                                         'call measure_cog')
                     ).pack(side=LEFT,expand=YES,fill=X)





        


