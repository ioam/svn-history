"""
GUI windows to display bitmap plots. 

$Id$
"""
#from Tkinter import *
import Pmw, re, os, sys
import __main__
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

MIN_PLOT_WIDTH = 100

class PlotPanel(Frame,topo.base.TopoObject):
    """
    Base class for GUI windows displaying bitmap images.  Subclassed to
    display various categories of bitmaps.
    """
    def __init__(self,parent=None,pengine=None,console=None,**config):
        assert isinstance(pengine,plotengine.PlotEngine) or pengine == None, 'Variable pengine not PlotEngine object.'

        Frame.__init__(self,parent,config)
        topo.plot.TopoObject.__init__(self,**config)

        self.pe = pengine
        self.pe_group = None
        self.plot_tuples = []

        self.console = console
        self.parent = parent
        self.canvases = []

        self.images = []
        
        self.plot_group = Pmw.Group(self,tag_pyclass=None)
        self.plot_group.pack(side=TOP,expand=YES,fill=BOTH,padx=5,pady=5)
        self.plot_frame = self.plot_group.interior()

        self.zoom_factor = self.min_zoom_factor = 1
        
        
        self.control_frame = Frame(self)
        self.control_frame.pack(side=BOTTOM,expand=YES,fill=X)

        Button(self.control_frame,text="Refresh",command=self.refresh).pack(side=LEFT)
        self.reduce_button = Button(self.control_frame,text="Reduce",
                                   state=DISABLED,
                                   command=self.reduce)
        self.reduce_button.pack(side=LEFT)
        Button(self.control_frame,text="Enlarge",command=self.enlarge).pack(side=LEFT)        

        self.auto_refresh = 0
        self.auto_refresh_checkbutton = Checkbutton(self.control_frame,
                                                    text="Auto-refresh",
                                                    command=self.toggle_auto_refresh)
        self.auto_refresh_checkbutton.pack(side=LEFT)

        self.refresh()


    def refresh(self):
        self.do_plot_cmd()
        self.load_images()
        self.display_plots()
        self.display_labels()


    def do_plot_cmd(self):
        """
        Poll the PlotEngine for the plotgroup linked to self.plot_key.
        Since the get_plot_group is being called, it may update the
        plots, or it may use a cached version, depending on the type
        of plot_group being requested.
        """
        Pmw.showbusycursor()

        self.pe_group = self.pe.get_plot_group(self.plot_key)
        self.plot_tuples = self.pe_group.plots()
        self.pe.debug('Type of plot_group', type(self.pe_group))

#         plots = Lissom.plot_cmd(self.plot_cmd)
#         self.plotlist   = map(self.plotname_to_filename,plots);
#         self.plotlabels = map(self.plotname_to_label,plots);
#         # remove non-existent plots
#         goodplots = [t for t in zip(self.plotlist,self.plotlabels) if os.access(t[0],os.F_OK)]
#         self.plotlist = [i for i,p in goodplots]
#         self.plotlabels = [p for i,p in goodplots]
        self.plotlist = []
        self.plotlabels = []

        Pmw.hidebusycursor()
        

    def load_images(self):
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
                self.plotlabels.append(self.pe_group.name + ' ' + str(len(self.plotlist)))

        
        if self.images:
            min_width = reduce(min,[im.width() for im in self.images])
        else:
            min_width = 0
        
        if old_min_width != min_width:
            # if the min width changed, then recalculate the zoom factor
            # If no plots, then no window.
            if MIN_PLOT_WIDTH > min_width and old_min_width != -1:
                self.min_zoom_factor = MIN_PLOT_WIDTH/min_width + 1
            else:
                self.min_zoom_factor = 1

            self.zoom_factor = self.min_zoom_factor
            self.reduce_button.config(state=DISABLED)

        
    def display_plots(self):
        self.zoomed_images = [ImageTk.PhotoImage(im.zoom(self.zoom_factor)) for im in self.images]
        old_canvases = self.canvases
        self.canvases = [Canvas(self.plot_frame,
                                width=image.width(),
                                height=image.height(),
                                bd=2)
                         for image in self.zoomed_images]
        for i,image,canvas in zip(range(len(self.zoomed_images)),
                                  self.zoomed_images,self.canvases):
            canvas.grid(row=0,column=i,padx=5)
            canvas.create_image(image.width()/2,image.height()/2,image=image)

        for c in old_canvases:
            c.grid_forget()

    def display_labels(self):
        for i,name in enum(self.plotlabels):
            self.debug(i, " ", name)
            Label(self.plot_frame,text=name).grid(row=1,column=i,sticky=NSEW)

    def reduce(self):
        if self.zoom_factor > self.min_zoom_factor:
            self.zoom_factor = self.zoom_factor - 1

        if self.zoom_factor == self.min_zoom_factor:
            self.reduce_button.config(state=DISABLED)
            
        self.display_plots()
    
    def enlarge(self):
        self.reduce_button.config(state=NORMAL)
        self.zoom_factor = self.zoom_factor + 1
        self.display_plots()

    def toggle_auto_refresh(self):
        self.auto_refresh = not self.auto_refresh

        self.message("Auto-refresh = ", self.auto_refresh)
        topo.tk.show_cmd_prompt()

        if self.auto_refresh:
            self.console.add_auto_refresh_panel(self)
        else:
            self.console.del_auto_refresh_panel(self)

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


    def destroy(self):
        if self.auto_refresh:
            self.console.del_auto_refresh_panel(self)
        Frame.destroy(self)
##############################################
#
# Different kinds of plot panels
#


class ActivityPanel(PlotPanel):
    def __init__(self,parent,pengine=None,console=None,**config):
        self.plot_key = "Activation"
        PlotPanel.__init__(self,parent,pengine,console=console,**config)
        self.auto_refresh_checkbutton.invoke()


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



class WeightsPanel(PlotPanel):
    def __init__(self,parent,pengine,console=None,**config):

        self.r = 0
        self.row_str = StringVar()
        self.row_str.set(0.0)
#         self.row_str.set('current_height/2')
        self.c = 0
        self.col_str = StringVar()
        self.col_str.set(0.0)
#         self.col_str.set('current_width/2')
        self.WEIGHT_PLOT_INITIAL_SIZE = 100

        # Generate the initial plot_key
        self.generate_plot_key()
        self.debug('plot_key = ' + str(self.plot_key))
        
        PlotPanel.__init__(self,parent,pengine,console,**config)

        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)

        Message(params_frame,text="Row:",aspect=1000).pack(side=LEFT)
        Entry(params_frame,textvariable=self.row_str).pack(side=LEFT,expand=YES,fill=X)
        Message(params_frame,text="Column:",aspect=1000).pack(side=LEFT)
        Entry(params_frame,textvariable=self.col_str).pack(side=LEFT,expand=YES,fill=X)

        # The plot_key needs to be set, and the parent constructor as well,
        # since a throw-away PlotGroup is going to be used to estimate an
        # initial zoom factor.
        self.set_initial_zoom_factor()
        self.refresh()
        

    def set_initial_zoom_factor(self):
        """
        The initial zoom factor of 1 makes tiny RFs very hard to see.
        By setting an initial dynamic zoom factor, the starting plot
        will not have to be scaled much by the user.

        It's very inefficient that an entire PlotGroup has to be
        created, then discarded just to estimate how big to set the
        initial scale size.  This should be replaced with something
        more efficient later.
        """
        self.pe_group = self.pe.get_plot_group(self.plot_key)
        self.plot_tuples = self.pe_group.plots()
        # print 'self.plot_tuples = ', self.plot_tuples
        shapes = [(each[0])[0].shape for each in self.plot_tuples]
        main_dimension = [max(x,y) for (x,y) in shapes]
        main = max(main_dimension)
        self.zoom_factor = self.WEIGHT_PLOT_INITIAL_SIZE // main


    def generate_plot_key(self):
        """
        The plot_key for the WeightsPanel will change depending on the
        input within the window widgets.  This means that the key
        needs to be regenerated at the appropriate times.
        """
        g = __main__.__dict__
        self.r = eval(self.row_str.get(),g)
        self.c = eval(self.col_str.get(),g)
        if isinstance(self.r,int): self.r = float(self.r)
        if isinstance(self.c,int): self.c = float(self.c)
        self.plot_key = ('Weights',self.r,self.c)
        
        
    def do_plot_cmd(self):
        """
        Overloaded do_plot_cmd() so that the plot_key can change to the
        active row/col pair in the window.
        """
        self.generate_plot_key()
        super(WeightsPanel,self).do_plot_cmd()
        self.parent.title("Weights Array %d. (r=%0.4f, c=%0.4f)" %
                          (self.console.num_weights_windows,self.r, self.c))



class WeightsArrayPanel(PlotPanel):
    def __init__(self,parent,console=None,**config):

        self.skip_str = StringVar()
        self.skip_str.set('N/8')

        self.situate = StringVar()
        self.situate.set(0)

        self.region = StringVar()
        self.region.set('Primary')

        self.weight_name = StringVar()
#        self.weight_name.set(Lissom.eval_param("cmd::plot_unit_range::name"))

        PlotPanel.__init__(self,parent,console,**config)

        params_frame1 = Frame(master=self)
        params_frame1.pack(side=BOTTOM,expand=YES,fill=X)

        Message(params_frame1,text="Skip:",aspect=1000).pack(side=LEFT)
        Entry(params_frame1,textvariable=self.skip_str).pack(side=LEFT,expand=YES,fill=X)
        Checkbutton(params_frame1,text="Situate",variable=self.situate,
                    command=self.refresh).pack(side=LEFT)

        params_frame2 = Frame(master=self)
        params_frame2.pack(side=BOTTOM,expand=YES,fill=X)

        Pmw.OptionMenu(params_frame2,
                       labelpos = 'w',
                       label_text = 'Region:',
                       menubutton_textvariable = self.region,
                       items = ['Primary', 'Ganglia00', 'Ganglia01', 'Secondary']
                       ).pack(side=LEFT)

        Pmw.OptionMenu(params_frame2,
                       labelpos = 'w',
                       label_text = 'Name:',
                       menubutton_textvariable = self.weight_name,
                       items = [ self.weight_name.get(),
                                 'Afferent0', 'LateralExcitatory', 'LateralInhibitory']
                       ).pack(side=LEFT)



    def do_plot_cmd(self):
        """
        Behaves similarly to Activation plots, except that these Weights
        plots are (currently) only defined for RFSheets.
        """
        
        Pmw.showbusycursor()

        self.pe_group = self.pe.get_plot_group(self.plot_key)
        self.plot_tuples = self.pe_group.plots()
        self.pe.debug('Type of plot_group', type(self.pe_group))

        self.plotlist = []
        self.plotlabels = []

        Pmw.hidebusycursor()


#         if self.situate.get():
#             prefix = 'ppm_border=1 '
#             situate = 'True'
#             suffix = ' weight_bare=false ppm_outline_width=1 ppm_interior_border=0 ppm_interior_outline=False'
#         else:
#             prefix = ''
#             situate = 'False'
#             suffix = ''
#         self.plot_cmd = prefix + 'plot_unit_range'
#         self.plot_cmd += ' region=' + self.region.get()
#         self.plot_cmd += ' name=' + self.weight_name.get()
#         self.plot_cmd += ' verbose=true ppm_separate_plots=false ppm_combined_plots=true'
#         self.plot_cmd += ' ppm_neuron_skip_aff=' + self.skip_str.get()
#         self.plot_cmd += ' weight_situate=' + situate +  suffix

        PlotPanel.do_plot_cmd(self)


    def plotname_to_filename(self,plotname):
        return 'gui.'+self.plotname_components(plotname)[0]+'_Weights.ppm'
####################


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

        
def enum(seq):
    return zip(range(len(seq)),seq)


