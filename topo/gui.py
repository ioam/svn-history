"""
Primary entry point for the Topographica GUI.  Based strongly off of
code taken verbatim from LISSOM 5.0.

To start the gui from the Topographica prompt, call gui.start().

$Id$
"""
from Tkinter import *
import Pmw, re, os
import tkFileDialog
from propertiesframe import *

MIN_PLOT_WIDTH = 100
KNOWN_FILETYPES = [('Python Files','*.py'),('Topographica Files','*.ty'),('All Files','*')]

class TopoConsole(Frame):
    def __init__(self, parent=None,**config):
        Frame.__init__(self,parent,config)

#        self._init_lissom()

        self.parent = parent
        self.num_activity_windows = 0
        self.num_orientation_windows = 0
        self.num_weights_windows = 0
        self.num_weights_array_windows = 0
        self.loaded_script = None

        self.auto_refresh_panels = []

        self.input_params_window = None
        
        self._init_widgets()


    def _init_widgets(self):


	# Create the Balloon.
	self.balloon = Pmw.Balloon(self)

	# Create and pack the MenuBar.
	self.menubar = Pmw.MenuBar(self,
                                   hull_relief = 'raised',
                                   hull_borderwidth = 1,
                                   balloon = self.balloon)
	self.menubar.pack(fill = X)

        self.menubar.addmenu('Simulation','Simulation commands')
        self.menubar.addmenuitem('Simulation', 'command', 'Load script file',
                                 label = 'Load',
                                 command = self.load_network)
        self.menubar.addmenuitem('Simulation', 'command', 'Reload script from disk',
                                 label = 'Reload',
                                 command = self.reload_network)
        self.menubar.addmenuitem('Simulation', 'command', 'Reset the network',
                                 label = 'Reset',
                                 ## Gray out menu item
                                 foreground = 'Gray',
                                 activeforeground = 'Gray',
                                 activebackground = 'Light Gray',
                                 ## 
                                 command = self.reset_network)
        self.menubar.addmenuitem('Simulation', 'command', 'Present a test pattern',
                                 label = 'Test Pattern',
                                 ## Gray out menu item
                                 foreground = 'Gray',
                                 activeforeground = 'Gray',
                                 activebackground = 'Light Gray',
                                 ##
                                 command = self.open_plot_params_window)
        self.menubar.addmenuitem('Simulation', 'separator')
        self.menubar.addmenuitem('Simulation', 'command', 'Close the GUI window',
                                 label = 'Quit',
                                 command = self.quit)

	# Create and pack the MessageBar.
	self.messageBar = Pmw.MessageBar(self,
                                         entry_width = 60,
                                         entry_relief='groove',
                                         labelpos = 'w',
                                         label_text = 'Status:')
	self.messageBar.pack(side = BOTTOM,fill=X,padx=4,pady=8)
	self.messageBar.message('state', 'OK')
	self.balloon.configure(statuscommand = self.messageBar.helpmessage)

        #
        # Plot menu
        #

        self.menubar.addmenu('Plots','Assorted plot displays')
        self.menubar.addmenuitem('Plots', 'command',
                             'New activity plot',
                             label="Activity",
                             command=self.dummy)
                             #command=self.new_activity_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New orientation, ocular dominance, or similar map plot',
                             label="Preference Map",
                             ## Gray out menu item
                             foreground = 'Gray',
                             activeforeground = 'Gray',
                             activebackground = 'Light Gray',
                             #command=self.new_preferencemap_window)
                             ##
                             command=None)
        self.menubar.addmenuitem('Plots', 'command',
                             'New weights plot',
                             label="Weights",
                             command=self.dummy)
                             #command=self.new_weights_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New weights array plot',
                             label="Weights Array",
                             ## Gray out menu item
                             foreground = 'Gray',
                             activeforeground = 'Gray',
                             activebackground = 'Light Gray',
                             #command=self.new_weights_array_window)
                             ##
                             command=self.dummy)
        self.menubar.addmenuitem('Plots','separator')
        self.menubar.addmenuitem('Plots', 'command',
                                 'Refresh auto-refresh plots',
                                 label="Refresh",
                                 command=self.dummy)
                                 #command=self.auto_refresh)
        

        #
        # Command entry
        #
        command_group = Pmw.Group(self,tag_text='Command')
        command_frame = command_group.interior()
        command_group.pack(side=TOP,expand=YES,fill=X,padx=4,pady=8)

        self.cmd_box = Pmw.ComboBox(command_frame, autoclear=1,history=1,dropdown=1,
                                    selectioncommand=Pmw.busycallback(self.do_command))
        self.cmd_box.pack(side=LEFT,expand=YES,fill=X)

        #
        # Training
        #
        training_group = Pmw.Group(self,tag_text='Training iterations')
        training_frame = training_group.interior()
        training_group.pack(side=TOP,expand=YES,fill=X,padx=4,pady=8)

        self.training_str = StringVar()
        self.training_str.set('1')
        Pmw.ComboBox(training_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.training_str,
                     selectioncommand=Pmw.busycallback(self.do_training)
                     ).pack(side=LEFT,expand=YES,fill=X)



    def _init_lissom(self):
        """
        No longer used by Topographica.  Staying here as a record of the steps
        that LISSOM needs to do, as a template for Topographica.
        """
        root_prefix = os.path.split(os.getcwd())[-1]
        initial_params_file = root_prefix+'.param'

        #
        # Load the initial params file and set the filebase
        #
        Lissom.cmd("exec_file "+initial_params_file)
        Lissom.cmd("set filebase="+root_prefix)
        init_cmds = [
            # Set parameters to generate individual images instead of combined plot
            "ppm_border=0",
            "spawn_viewer=False",
            "cmd::ppm_separate_plots=True",
            "cmd::ppm_combined_plots=False"]
        Lissom.cmds(init_cmds)
 

    def quit(self):
        """Close the main GUI window.  Does not exit Topographica interpreter."""
        self.cleanup_dir()
        Frame.quit(self)
        Frame.destroy(self)     # Get rid of widgets
        self.parent.destroy()   # Get rid of window


    def cleanup_dir(self):
        dir = os.listdir(os.curdir)
        for f in dir:
            m = re.match('gui\..*\.ppm$',f)
            if m != None:
                print 'removing: ' + f
                os.remove(f)

    def load_network(self):
        """
        Load a script file from disk and evaluate it.
        """
        self.loaded_script = tkFileDialog.askopenfilename(filetypes=KNOWN_FILETYPES)
        if self.loaded_script in ('',(),None):
            self.loaded_script = None
            self.messageBar.message('state', 'Load canceled')
        else:
            execfile(self.loaded_script)
            self.messageBar.message('state', 'Loaded ' + self.loaded_script)


    def reload_network(self):
        """
        Reload the previously loaded file from disk.  Does not
        prompt for new filename.  Currently does not flush any
        existing environment variables, so the loaded script needs
        to take that into account.  Also, the script is run in the
        existing namespace, so it all goes away upon exit of this
        function.
        """
        if self.loaded_script == None:
            self.messageBar.message('state', 'No script to reload')
        else:
            execfile(self.loaded_script)
            self.messageBar.message('state', 'Reloaded ' + self.loaded_script)
                
    def reset_network(self):
	self.messageBar.message('state', 'Reset not implemented')        

    #
    # auto-refresh handling
    #
    def auto_refresh(self):
        for win in self.auto_refresh_panels:
            win.refresh()

    def add_auto_refresh_panel(self,panel):
        self.auto_refresh_panels.append(panel)

    def del_auto_refresh_panel(self,panel):
        self.auto_refresh_panels.remove(panel)
    

    #
    # New plot windows
    #
    def new_activity_window(self):
        self.num_activity_windows += 1
        win = GUIToplevel(self)
        win.withdraw()
        win.title("Activity %d" % self.num_activity_windows)
        ActivityPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        win.deiconify()

    def new_preferencemap_window(self):
        self.num_orientation_windows += 1
        win = GUIToplevel(self)
        win.withdraw()
        win.title("Preference Map %d" % self.num_orientation_windows)
        PreferenceMapPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        win.deiconify()

    def new_weights_window(self):
        self.num_weights_windows += 1
        win = GUIToplevel(self)
        win.withdraw()
        win.title("Weights %d" % self.num_weights_windows)
        WeightsPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        win.deiconify()

    def new_weights_array_window(self):
        self.num_weights_array_windows += 1
        win = GUIToplevel(self)
        win.withdraw()
        win.title("Weights Array %d" % self.num_weights_array_windows)
        WeightsArrayPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        win.deiconify()

    def open_plot_params_window(self):
        """
        Test Pattern Parameters Window.  The original code is commented
        out until the next phase of development.  For now, this is a stub.
        """
        self.messageBar.message('state', 'Not yet implemented')
        # if self.input_params_window == None:
        #     self.input_params_window = Toplevel(self)
        #     self.input_params_window.title('Test Pattern Parameters')
        #     RetinalInputParamsPanel(self.input_params_window,self).pack(side=TOP,expand=YES,
        #                                                                 fill=BOTH)
        #     self.input_params_window.protocol('WM_DELETE_WINDOW',
        #                                       self.input_params_window.withdraw)
        # else:
        #     self.input_params_window.deiconify()
        #     self.input_params_window.lift()
        #     self.input_params_window.focus_set()


    #
    # Command buttons
    #
    def do_command(self,cmd):
        dummy()  # Added so do_command doesn't freak with empty body.
#        Lissom.cmd(cmd)

    def do_training(self,count):
#        Lissom.cmd("training +" + count)
        self.auto_refresh()
        
    def reload_saved_network(self):
#        Lissom.cmd('load_snapshot')
        self.auto_refresh()


    def dummy(self):
        print "Button pressed in ", self

    def not_yet_implemented(self):
        print "Operation not yet implemented."
    

        
class PlotPanel(Frame):

    def __init__(self,parent=None,console=None,**config):

        Frame.__init__(self,parent,config)
        
        self.console = console
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
        Pmw.showbusycursor()
        init_cmds = [
            #set file names just before plot command to ensure that they are correct
            "PlotGroup::Activity::filename_format=gui.$${current_region}_$${current_plot}",
            "PlotGroup::Weights::filename_format=gui.$${current_region}_$${current_plot}",
            "PlotGroup::WeightsMap::filename_format=gui.$${current_region}_$${current_plot}",
            "PlotGroup::*Preference::filename_format=gui.$${current_region}_$${current_plot}",]
#        Lissom.cmds(init_cmds)
        
#        plots = Lissom.plot_cmd(self.plot_cmd)
        self.plotlist   = map(self.plotname_to_filename,plots);
        self.plotlabels = map(self.plotname_to_label,plots);

        #print `self`+".plotlist = "+`self.plotlist`
        #print `self`+".plotlabels = "+`self.plotlabels`

        # remove non-existent plots
        goodplots = [t for t in zip(self.plotlist,self.plotlabels) if os.access(t[0],os.F_OK)]
        self.plotlist = [i for i,p in goodplots]
        self.plotlabels = [p for i,p in goodplots]
        
        #print `self`+".plotlist = "+`self.plotlist`
        #print `self`+".plotlabels = "+`self.plotlabels`
        
        Pmw.hidebusycursor()
        
    def load_images(self):

        # need to calculate the old min width, so we know if we need to reset
        # the zoom factors
        if self.images:
            old_min_width = reduce(min,[im.width() for im in self.images])
        else:
            old_min_width = -1
        
        self.images = [PhotoImage(file=pfile,master=self.plot_frame)
                       for pfile in self.plotlist]
        if self.images:
            min_width = reduce(min,[im.width() for im in self.images])
        else:
            min_width = 0
        
        if old_min_width != min_width:
            # if the min width changed, then recalculate the zoom factor
            if MIN_PLOT_WIDTH > min_width:
                self.min_zoom_factor = MIN_PLOT_WIDTH/min_width + 1
            else:
                self.min_zoom_factor = 1

            self.zoom_factor = self.min_zoom_factor
            self.reduce_button.config(state=DISABLED)

        
    def display_plots(self):
        self.zoomed_images = [im.zoom(self.zoom_factor) for im in self.images]
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
        for i,file in enum(self.plotlabels):
            print i, " ", file
            Label(self.plot_frame,text=file).grid(row=1,column=i,sticky=NSEW)

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
        print "Auto-refresh = ", self.auto_refresh
        if self.auto_refresh:
            self.console.add_auto_refresh_panel(self)
        else:
            self.console.del_auto_refresh_panel(self)

    def plotname_to_filename(self,plotname):
        """Converts a string like Eye0::Activity to the corresponding lissom filename.
        Does not have any decent error checking.""" 
        return 'gui.%s_%s.ppm' % self.plotname_components(plotname)
        
    def plotname_to_label(self,plotname):
        """Converts a string like Eye0::Activity to the corresponding label.
        Does not have any decent error checking.""" 
        return '%s %s' % self.plotname_components(plotname)

    def plotname_components(self,plotname):
        """Gets the components of a plotname, e.g. 'Primary', 'Afferent00',
        and returns them in a tuple."""
        m =  re.match("([^ ]*)::([^ ]*)",plotname)
        return (m.group(1),m.group(2))


    def destroy(self):
        if self.auto_refresh:
            self.console.del_auto_refresh_panel(self)
        Frame.destroy(self)
##############################################
#
# Different kinds of plot panels
#


class ActivityPanel(PlotPanel):
    def __init__(self,parent,console=None,**config):
        self.plot_cmd = "plot"
        PlotPanel.__init__(self,parent,console=console,**config)
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
    def __init__(self,parent,console=None,**config):

        self.row_str = StringVar()
        self.row_str.set('current_height/2')

        self.col_str = StringVar()
        self.col_str.set('current_width/2')

        PlotPanel.__init__(self,parent,console,**config)

        params_frame = Frame(master=self)
        params_frame.pack(side=TOP,expand=YES,fill=X)

        # hack alert!
        # This shouldn't be hard-coded
        # region_names = ['Primary', 'Ganglia00', 'Ganglia01', 'Secondary']
        # still need a dropdown... from Tix?

        Message(params_frame,text="Row:",aspect=1000).pack(side=LEFT)
        Entry(params_frame,textvariable=self.row_str).pack(side=LEFT,expand=YES,fill=X)
        Message(params_frame,text="Column:",aspect=1000).pack(side=LEFT)
        Entry(params_frame,textvariable=self.col_str).pack(side=LEFT,expand=YES,fill=X)

    def do_plot_cmd(self):        
        self.plot_cmd = "plot_unit %s %s" % (self.row_str.get(),self.col_str.get())
        PlotPanel.do_plot_cmd(self)

class WeightsArrayPanel(PlotPanel):
    def __init__(self,parent,console=None,**config):

        self.skip_str = StringVar()
        self.skip_str.set('N/8')

        self.situate = IntVar()
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

        if self.situate.get():
            prefix = 'ppm_border=1 '
            situate = 'True'
            suffix = ' weight_bare=false ppm_outline_width=1 ppm_interior_border=0 ppm_interior_outline=False'
        else:
            prefix = ''
            situate = 'False'
            suffix = ''
            
        self.plot_cmd = prefix + 'plot_unit_range'
        self.plot_cmd += ' region=' + self.region.get()
        self.plot_cmd += ' name=' + self.weight_name.get()
        self.plot_cmd += ' verbose=true ppm_separate_plots=false ppm_combined_plots=true'
        self.plot_cmd += ' ppm_neuron_skip_aff=' + self.skip_str.get()
        self.plot_cmd += ' weight_situate=' + situate +  suffix

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

        
        
        
####################

class GUIToplevel(Toplevel):
    def __init__(self,parent,**config):
        Toplevel.__init__(self,parent,config)
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.resizable(0,0)

####################
        

def enum(seq):
    return zip(range(len(seq)),seq)


def start():
    """
    Startup code for GUI.  Template pulled from default __main__ code
    originally written for LISSOM.
    """
    root = Tk()
    root.resizable(0,0)
    Pmw.initialise(root)
    console = TopoConsole(parent=root).pack(expand=YES,fill=BOTH)
    root.title("Topographica Console")
    # mainloop() takes control of the commandline.  Without this line
    # the command-line is still responsive.
    # root.mainloop()


#  Original main rountine for LISSOM 5.0.  Useful as an example of
#  how it used to be done, but should not be moved to the tests
#  directory.  New entry point is gui.start()
#
#  import sys,getopt
#  
#  if __name__ == '__main__':
#      opts,args = getopt.getopt(sys.argv[1:],'',['noloop'])
#      print 'opts = ' + `opts` + ' args = ' + `args`
#  
#      root = Tk()
#      root.resizable(0,0)
#      Pmw.initialise(root)
#      console = LissomConsole(parent=root).pack(expand=YES,fill=BOTH)
#      root.title("Lissom Console")
#      if not (('--noloop','') in opts):
#          root.mainloop()
