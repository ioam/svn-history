"""
Abstract Class PlotPanel to support GUI windows that display bitmap plots. 

Undefined Variables:
    self.plot_key

Virtual Functions:
    refresh_title()
    do_plot_cmd()
    generate_plot_key()

Suggested functions to replace:
    display_plots()
    display_labels()
    

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

NYI = "Abstract method not implemented."

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

        # Must make assignment, even if only 'Activation'
        self.plot_key = NYI    

        # Each plot can have a different minimum size.  If INITIAL_PLOT_WIDTH
        # is set to None, then no initial zooming is performed.  However,
        # MIN_PLOT_WIDTH may cause a zoom if the raw bitmap is still too
        # tiny.
        self.MIN_PLOT_WIDTH = 50
        self.INITIAL_PLOT_WIDTH = 100

        self.pe = pengine
        self.pe_group = None
        self.plot_tuples = []
        self.images = []
        self.labels = []

        self.console = console
        self.parent = parent
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
        # self.refresh()


    def refresh(self):
        """
        Main steps for generating plots in the Frame.  These functions
        must be implemented, or overwritten.
        """
        Pmw.showbusycursor()
        self.do_plot_cmd()                # Create plot tuples
        self.load_images()                # Convert plots to bitmap images
        self.display_plots()              # Put images in GUI canvas
        self.display_labels()             # Match labels to grid
        self.refresh_title()              # Update Frame title.
        Pmw.hidebusycursor()


    def refresh_title(self):
        """
        Change the window title.  TopoConsole will call this on
        startup of window.  
        """
        raise NYI


    def generate_plot_key(self):
        """Should set a value to self.plot_key."""
        raise NYI
        

    def do_plot_cmd(self):
        """
        Subclasses of PlotPanel will need to create this function to
        generate the plots.  Upon completion, it must have done two things:

        1.  Create a PlotGroup and store it into self.pe_group
        2.  Create a list of plot tuples, and store it into self.plot_tuples

        Example:
            self.pe_group = self.pe.get_plot_group(self.plot_key)
            self.plot_tuples = self.pe_group.plots()

        See topo.tk.WeightsPanel and topo.tk.WeightsArrayPanel for
        more complicated examples.
        """
        raise NYI
    

    def load_images(self):
        """
        Pre:  self.pe_group contains a PlotGroup
              self.plot_tuples contains a list of tuples that match the
                  format defined by PlotGroup.plots()
        Post: self.images contains a list of Bitmap Images ready for display.

        No geometry or Sheet information is necessary to perform the
        operations in this function, so it is unlikely that load_images()
        will need to be redefined from a subclass.

        Image scaling is automatically done, as well as adjusted by the
        user.  self.MIN_PLOT_WIDTH is the number of pixels wide the
        smallest plot figure can be, and self.INITIAL_PLOT_WIDTH is the
        number of pixels wide the smallest plot figure will be on the
        first display.
        """
        self.plotlist = []
        # need to calculate the old min width, so we know if we need to reset
        # the zoom factors
        if self.images:
            old_min_width = reduce(min,[im.width() for im in self.images])
        else:
            old_min_width = -1

        self.images = []
        for (figure_tuple, hist_tuple) in self.plot_tuples:
            (r,g,b) = figure_tuple
            if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
                # Normalize activation to a maximum of 1.  Will scale brighter
                # or darker, depending.
                if max(r.flat) > 0: r = Numeric.divide(r,max(r.flat))
                if max(g.flat) > 0: g = Numeric.divide(g,max(g.flat)) 
                if max(b.flat) > 0: b = Numeric.divide(b,max(b.flat))
                win = topo.bitmap.RGBMap(r,g,b)
                self.images.append(win)
                self.plotlist.append(win)
        
        if self.images:
            min_width = reduce(min,[im.width() for im in self.images])
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
        Pre:  self.images contains a list of topo.bitmap objects.

        Post: The bitmaps have been displayed to the screen in the active
              console window.  All images are displayed from left to right,
              in a single row.  If the number if images have changed since
              the last display, the grid size is increased, or decreased
              accordingly.

        This function shuld be redefined in subclasses for interesting
        things such as 2D grids.
        """
        self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor))
                              for im in self.images]
        old_canvases = self.canvases
        self.canvases = [Canvas(self.plot_frame,
                                width=image.width(),
                                height=image.height(),
                                bd=0)
                         for image in self.zoomed_images]
        for i,image,canvas in zip(range(len(self.zoomed_images)),
                                  self.zoomed_images,self.canvases):
            canvas.grid(row=0,column=i,padx=5)
            canvas.create_image(image.width()/2,image.height()/2,image=image)

        for c in old_canvases:
            c.grid_forget()


    def display_labels(self):
        """
        Pre:  self.plot_names contains a list of strings that match the
              list of bitmap images is self.images.
        Post: Each string within self.plot_names has been displayed on the
              screen directly below its corresponding image in the GUI
              window.

        This function should be redefined by subclasses to match any
        changes made to display_plots().  Depending on the situation,
        it may be useful to make this function a stub, and display the
        labels at the same time the images are displayed.
        """
        old_labels = self.labels
        self.labels = [Label(self.plot_frame,text=name)
                       for name in self.plot_names]
        for i in range(len(self.labels)):
            self.labels[i].grid(row=1,column=i,sticky=NSEW)
        for l in old_labels:
            l.grid_forget()
                 

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


# No longer useful since there is no LISSOM, but these should be replaced
# with functions for filename saving.
#     def plotname_to_filename(self,plotname):
#         """Converts a string like Eye0::Activity to the corresponding lissom filename.
#         Does not have any decent error checking.""" 
#         return 'gui.%s_%s.ppm' % self.plotname_components(plotname)
#         
#     def plotname_to_label(self,plotname):
#         """Converts a string like Eye0::Activity to the corresponding label.
#         Does not have any decent error checking.""" 
#         return '%s %s' % self.plotname_components(plotname)
# 
#     def plotname_components(self,plotname):
#         """Gets the components of a plotname, e.g. 'Primary', 'Afferent00',
#         and returns them in a tuple."""
#         m =  re.match("([^ ]*)::([^ ]*)",plotname)
#         return (m.group(1),m.group(2))

















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


    def do_plot_cmd(self):
        Pmw.showbusycursor()
#        Lissom.cmd(self.cmdname.get())
        self.plot_cmd = "plot " + self.mapname.get()
        PlotPanel.do_plot_cmd(self)
        Pmw.hidebusycursor()



class RetinalInputParamsPanel(Frame):
    def __init__(self,parent,console=None,**config):

        self.console = console
        self.input_type = StringVar()
        self.input_type.set('Gaussian')
        self.learning = IntVar()
        self.learning.set(0)

        Frame.__init__(self,parent,config)

        input_types = [ 'Gaussian',
                        'SineGrating',
                        'Gabor',
                        'UniformRandomNoise',
                        'Rectangle',
                        'FuzzyLine',
                        'FuzzyDisc',
                        'Photograph']

        buttonBox = Pmw.ButtonBox(self,
                                  orient = 'horizontal',
                                  padx=0,pady=0,
                                  #frame_borderwidth = 2,
                                  #frame_relief = 'groove'
                                  )
        buttonBox.pack(side=TOP)

        Pmw.OptionMenu(self,
                       labelpos = 'w',
                       label_text = 'Input Type:',
                       menubutton_textvariable = self.input_type,
                       items = input_types
                       ).pack(side=TOP)
 

        buttonBox.add('Present', command = self.present)
        buttonBox.add('Reset to Defaults', command = self.reset_to_defaults)
        buttonBox.add('Use for Training', command = self.use_for_training)
        Checkbutton(self,text='learning',variable=self.learning).pack(side=TOP)
       

        self.prop_frame = PropertiesFrame(self)


        #                name          min-value    max-value  init-value
        #				    	       
        self.add_slider( 'theta',        "0"     ,   "PI*2"   ,  "PI/2"    )
        self.add_slider( 'cx'   ,        "-RN/4" ,   "5*RN/4" ,  "RN/2"    )
        self.add_slider( 'cy'   ,        "-RN/4"  ,  "5*RN/4"  , "RN/2"    )
        self.add_slider( 'xsigma',       "0"     ,   "RN"     ,  "7.5"     )
        self.add_slider( 'ysigma',       "0"     ,   "RN"     ,  "1.5"     )
        self.add_slider( 'center_width', "0"     ,   "RN"     ,  "10"      )
        self.add_slider( 'scale',        "0"     ,   "3"      ,  "1.0"     )
        self.add_slider( 'offset',       "-3"    ,   "3"      ,  "0.0"     )
        self.add_slider( 'freq',         "0.01"  ,   "1.25"   ,  "0.5"     )
        self.add_slider( 'phase',        "0"     ,   "PI*2"   ,  "PI/2"    )

        self.prop_frame.add_combobox_property('Photograph',
                                              value='small/ellen_arthur.pgm',
                                              scrolledlist_items=('small/arch.pgm',
                                                                  'small/ellen_arthur.pgm',
                                                                  'small/gene.pgm',
                                                                  'small/lochnessroad.pgm',
                                                                  'small/loghog.pgm',
                                                                  'small/skye.pgm'))

        self.add_slider( 'size_scale' ,  "0"     ,   "5"      ,  "1"    )

       
        self.prop_frame.pack(side=TOP,expand=YES,fill=X)

        self.default_values = self.prop_frame.get_values()

    def add_slider(self,name,min,max,init):
        self.prop_frame.add_tagged_slider_property(name,init,
                                                   min_value=min,max_value=max,
                                                   width=30,
                                                   string_format='%.3f',
                                                   string_translator=Lissom.eval_expr)




    def present(self):
#        Lissom.cmd(self.get_cmd())
        self.console.auto_refresh()
        
    def use_for_training(self):
        dummy()  # Added so do_command doesn't freak with no body.
#        Lissom.cmd(self.get_training_pattern_cmd())

    def reset_to_defaults(self):
        self.prop_frame.set_values(self.default_values)
        self.input_type.set('Gaussian')
        self.learning.set(0)

    def get_cmd(self):
        format = """input_present_object learning=%s All Input_%s %s
                    theta=%s cx=%s cy=%s xsigma=%s ysigma=%s scale=%s
                    offset=%s freq=%s phase=%s center_width=%s size_scale=%s"""
        params = self.get_params()
        return format % (params['learning'],
                         params['type'],
                         params['filename'],
                         params['theta'],
                         params['cx'],
                         params['cy'],
                         params['xsigma'],
                         params['ysigma'],
                         params['scale'],
                         params['offset'],
                         params['freq'],
                         params['phase'],
                         params['center_width'],
                         params['size_scale'])


    def get_training_pattern_cmd(self):

        format = """exec input_undefine 'input_define Obj0 All
                    Input_%s %s xsigma=%s ysigma=%s scale=%s offset=%s
                    freq=%s phase=%s center_width=%s size_scale=%s'"""
        params = self.get_params()
        return format % (params['type'],
                         params['filename'],
                         params['xsigma'],
                         params['ysigma'],
                         params['scale'],
                         params['offset'],
                         params['freq'],
                         params['phase'],
                         params['center_width'],
                         params['size_scale'])
        

    def get_params(self):

        # Get the property values as a dictionary
        params = self.prop_frame.get_values()

        if self.input_type.get() == 'Photograph':
            # if it's a photo, the type is PGM and the file name is the Photograph
            params['type'] = 'PGM'
            params['filename'] = "'" + params['Photograph'] + "'"
        else:
            # Otherwise get the type from the input_type selector
            # and set the filename to null
            params['type'] = self.input_type.get()
            params['filename'] = ''

        if self.learning.get():
            params['learning'] = 'true'
        else:
            params['learning'] = 'false'
        
        return params

        


