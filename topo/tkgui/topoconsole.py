"""
TopoConsole class file.

$Id$
"""
__version__='$Revision$'

from Tkinter import Frame, Toplevel, StringVar, X, BOTTOM, TOP, \
     LEFT, RIGHT, YES, BOTH, Label
import Pmw, re, os, sys, code, traceback, __main__
import tkFileDialog
from basicplotgrouppanel import BasicPlotGroupPanel
from unitweightspanel import UnitWeightsPanel
from projectionpanel import ProjectionPanel
from inputparamspanel import InputParamsPanel
from topo.plotting.templates import PlotGroupTemplate, PlotTemplate, plotgroup_templates
import topo.base.simulator
import topo.plotting.plotengine
import topo.base.topoobject

import topo.commands.basic
import webbrowser

SCRIPT_FILETYPES = [('Topographica scripts','*.ty'),('Python scripts','*.py'),('All files','*')]

SAVED_FILE_EXTENSION = '.typ'
SAVED_FILETYPES = [('Topographica saved networks','*'+SAVED_FILE_EXTENSION),('All files','*')]

# CEBHACKALERT: will there be "not found" errors if they
# didn't build doc/ (for which they need php...)?
tutorial_url         = 'doc/Tutorial/index.html'
reference_manual_url = 'doc/Reference_Manual/index.html'

python_doc_url       = 'http://www.python.org/doc/'
topo_www_url         = 'http://www.topographica.org/'

# CEBHACKALERT: finish this instruction after making base class for PatternGeneratorParameter etc. 
# By default, none of the pattern types in topo/patterns/ are imported
# in Topographica, but for the GUI, we want all of them to be
# available as a list from which the user can select. To do this, we
# import all of the PatternGenerator classes in all of the modules
# mentioned in topo.patterns.__all__, and will also use any that the
# user has defined and registered.

# menus populated with full range of patterns
# if you want to add, install your own file in one of the following namespaces...
# should this be in tkgui/__init__.py?
from topo.patterns import *
# should this go into __init__?


# CEBHACKALERT: lose this and get TopoConsole.simulator instead
def active_sim():
    return topo.base.simulator.get_active_sim()


# If a particular plotgroup_template needs (or works better with) a
# specific subclass of PlotPanel, the writer of the new subclass
# or the plotgroup_template can declare here that that template
# should use a specific PlotPanel subclass.  For example:
#   plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}


class PlotsMenuEntry(topo.base.topoobject.TopoObject):
    """
    Use these objects to populate the TopoConsole Plots pulldown.  The
    pulldown requires a name and a function to call when the item is
    selected.  self.command is used for that.  self.command has to be
    different for each plot type since this will include Activity,
    Unit Weights, Projection grids, Preference Maps and more.
    """
    def __init__(self,console,template,class_name=BasicPlotGroupPanel,label=None,description=None,**config):
        super(PlotsMenuEntry,self).__init__(**config)
        self.console = console
        self.template = template

        if not label:
            label = template.name
        self.label = label
        if not description:
            description = template.description
        self.description = description

        # Special cases.  These classes are specific to the topo/tkgui
        # directory and therefore this link must be made within the tkgui
        # files.
        #
        # If users want to extend the Plot Panel classes, then they
        # should add entries to plotpanel_classes.  If no dictionary
        # entry is defined then the default class is used.
        self.class_name = plotpanel_classes.get(self.label,class_name)

        self.num_windows = 0
        self.title = ''


    def command(self):
        self.num_windows = self.num_windows + 1
        self.title = '%s %d' % (self.label, self.num_windows)
        #if 'valid_context' in dir(self.class_name):

        if self.console.plot_engine:
            if self.class_name.valid_context():
                win = GUIToplevel(self.console)
                win.withdraw()
                win.title(self.title)
                pn = self.class_name(parent=win,pengine=self.console.plot_engine,console=self.console,
                                     plot_group_key=self.template.name,pgt_name=self.template.name,plotgroup_type=self.template)
                pn.pack(expand=YES,fill=BOTH)

                pn.refresh_title()
                win.deiconify()
                self.console.messageBar.message('state', 'OK')
                return pn
            else:
                self.console.messageBar.message('state',
                            'Simulator does not have proper Sheet type.')
                return None
        else:
            self.console.messageBar.message('state', 'No active Simulator object.')
            return None
        

class TopoConsole(Frame):
    """
    TopoConsole class file.
    
    Primary window for the Tk-based GUI.  Loads, saves, calls other window
    frames in plotframe.py.
    """
    def __init__(self, parent=None,**config):
        Frame.__init__(self,parent,config)

        self.parent = parent
        self.num_activity_windows = 0
        self.num_orientation_windows = 0
        self.num_weights_windows = 0
        self.num_weights_array_windows = 0

        self.plot_engine = None
        self.simulator = None
        # Ask simulator to tell this console if the active_sim changes
        topo.base.simulator.objects_to_notify_of_active_sim.append(self)
        # CEBHACKALERT: this adds itself to the list above, but unless
        # 'quit' is selected from the menu, it leaves itself behind in
        # the list (e.g. if X is clicked to shut the window). Do I have
        # to worry about that or will Python later remove it anyway? I
        # think I have to worry...I need to find an 'on close' or similar
        # method.

        self.loaded_script = None
        self.input_params_window = None
        self.auto_refresh_panels = []
        self._init_widgets()
        # Doesn't work for providing icon for the window:
        #parent.wm_iconbitmap('@/home/jbednar/research/topographica/topo.xpm')

        title = "Topographica Console"
        self.parent.title(title)

    def _init_widgets(self):
        
	# Create the Balloon.
	self.balloon = Pmw.Balloon(self)

	# Create and pack the MenuBar.
	self.menubar = Pmw.MenuBar(self,
                                   hull_relief = 'raised',
                                   hull_borderwidth = 1,
                                   balloon = self.balloon)
	self.menubar.pack(fill = X)

        #
        # Simulation Menu
        #
        self.menubar.addmenu('Simulation','Simulation commands')
        self.menubar.addmenuitem('Simulation', 'command', 'Load script file',
                                 label = 'Load script',
                                 command = self.load_network)
        self.menubar.addmenuitem('Simulation', 'command', "Save simulator's state to disk",
                                 label = 'Save snapshot',
                                 command = self.save_snapshot)
        self.menubar.addmenuitem('Simulation', 'command', 'Load the previously saved state',
                                 label = 'Load snapshot',
                                 command = self.load_snapshot)
        self.menubar.addmenuitem('Simulation', 'command', 'Reset the network',
                                 label = 'Reset',
                                 ## Gray out menu item ###########
                                 foreground = 'Gray',            #
                                 activeforeground = 'Gray',      #
                                 activebackground = 'Light Gray',#
                                 #################################
                                 command = self.reset_network)
        self.menubar.addmenuitem('Simulation', 'command', 'Present a test pattern',
                                 label = 'Test Pattern',
                                 ## Gray out menu item ###########
                                 # foreground = 'Gray',            #
                                 # activeforeground = 'Gray',      #
                                 # activebackground = 'Light Gray',#
                                 #################################
                                 command = self.open_plot_params_window)
        self.menubar.addmenuitem('Simulation', 'separator')
        self.menubar.addmenuitem('Simulation', 'command', 'Close the GUI window',
                                 label = 'Quit',
                                 command = self.quit)

	# Create and pack the MessageBar.  (Shows "Status:")
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
        self.populate_plots_menu(self.menubar)

        self.menubar.addmenuitem('Plots','separator')

        # CEBHACKALERT: what's this?
        self.menubar.addmenuitem('Plots', 'command',
                                 'Refresh auto-refresh plots',
                                 label="Refresh",
                                 command=self.auto_refresh)


        #
        # Help menu
        #
        self.menubar.addmenu('Help','Information about Topographica', side='right')
        self.menubar.addmenuitem('Help', 'command',
                                 'Licensing and release information',
                                 label="About",
                                 command=self.new_about_window)
         
        self.menubar.addmenuitem('Help', 'command',
                                 'Walk-through LISSOM example',
                                 label="Tutorial",
                                 command=(lambda url=tutorial_url: self.open_url(url,relative=True)))
        self.menubar.addmenuitem('Help', 'command',
                                 'Detailed documentation',
                                 label="Reference Manual",
                                 command=(lambda url=reference_manual_url: self.open_url(url,relative=True)))
        self.menubar.addmenuitem('Help', 'command',
                                 'Python reference',
                                 label="Python documentation",
                                 command=(lambda url=python_doc_url: self.open_url(url)))
        self.menubar.addmenuitem('Help', 'command',
                                 'Topographica on the web',
                                 label="Topographica.org",
                                 command=(lambda url=topo_www_url: self.open_url(url)))

        
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
        # Learning
        #
        learning_group = Pmw.Group(self,tag_text='Learning iterations')
        learning_frame = learning_group.interior()
        learning_group.pack(side=TOP,expand=YES,fill=X,padx=4,pady=8)

        self.learning_str = StringVar()
        self.learning_str.set('1')
        Pmw.ComboBox(learning_frame,autoclear=1,history=1,dropdown=1,
                     entry_textvariable=self.learning_str,
                     selectioncommand=Pmw.busycallback(self.do_learning)
                     ).pack(side=LEFT,expand=YES,fill=X)


    def populate_plots_menu(self, menubar):
        """
        Poll for a list of class types, and put them into the Console
        plots list.  This replaces something of this form:

        self.menubar.addmenuitem('Plots', 'command',
                             'New activity plot',
                             label="Activity",
                             command=self.new_activity_window)
        """
        for (label,obj) in plotgroup_templates.items():
            entry = PlotsMenuEntry(self,obj,label=label)            
            menubar.addmenuitem('Plots','command',
                                obj.description,label=label,
                                command=entry.command)
    
    def notify_of_active_sim(self):
        """        
        """
        self.simulator = topo.base.simulator.get_active_sim()
        self.plot_engine = topo.plotting.plotengine.PlotEngine(self.simulator)


    # CEBHACKALERT: this *does* exit the interpreter if topographica was
    # started with -g.
    def quit(self):
        """Close the main GUI window.  Does not exit Topographica interpreter."""
        topo.base.simulator.objects_to_notify_of_active_sim.remove(self)
        Frame.quit(self)
        Frame.destroy(self)     # Get rid of widgets
        self.parent.destroy()   # Get rid of window
        if topo.gui_cmdline_flag:
            sys.exit()


    # CEBHACKALERT: the way this works might be a surprise, because previously
    # defined things stay around. E.g. load hierarchical.ty, then lissom_or.ty.
    # Because the BoundingBox is set for GeneratorSheet in hierarchical.ty but
    # not lissom_or.ty, LISSOM is loaded with a rectangular retina.
    def load_network(self):
        """
        Load a script file from disk and evaluate it.  The file is evaluated
        from within the globals() namespace.
        """
        self.loaded_script = tkFileDialog.askopenfilename(filetypes=SCRIPT_FILETYPES)
        if self.loaded_script in ('',(),None):
            self.loaded_script = None
            self.messageBar.message('state', 'Load canceled')
        else:
            result = self.load_script_file(self.loaded_script)
            if result:
                self.messageBar.message('state', 'Loaded ' + self.loaded_script)
            else:
                self.messageBar.message('state', 'Failed to load ' + self.loaded_script)
        topo.tkgui.show_cmd_prompt()


    # CEBHACKALERT:
    # save_ and load_snapshot() and load_network() ought to close open windows such
    # as Activity.
    
    def load_snapshot(self):
        """
        Return the current network to the state of the chosen snapshot.

        See topo.commands.basic.load_snapshot().
        """
        snapshot_name = tkFileDialog.askopenfilename(filetypes=SAVED_FILETYPES)

        if snapshot_name in ('',(),None):
            self.messageBar.message('state','No snapshot loaded.')
        else:
            topo.commands.basic.load_snapshot(snapshot_name)
            self.messageBar.message('state', 'Loaded snapshot ' + snapshot_name)

        self.notify_of_active_sim()
        topo.tkgui.show_cmd_prompt()


    def save_snapshot(self):
        """
        Save a snapshot of the current network's state.

        See topo.commands.basic.save_snapshot().
        save_snapshot() here adds the file extension  if not already present.
        """
        snapshot_name = tkFileDialog.asksaveasfilename(filetypes=SAVED_FILETYPES)

        if snapshot_name in ('',(),None):
            self.messageBar.message('state','No snapshot saved.')
        else:
            if not snapshot_name.endswith('.typ'):
                snapshot_name = snapshot_name + SAVED_FILE_EXTENSION
                
            topo.commands.basic.save_snapshot(snapshot_name)
            self.messageBar.message('state', 'Snapshot saved to ' + snapshot_name)

        topo.tkgui.show_cmd_prompt()
    
                
    def reset_network(self):
	self.messageBar.message('state', 'Reset not yet implemented')


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
    def open_plot_params_window(self):
        """
        Test Pattern Window.  
        """
        if self.simulator: #CEBHACKALERT & plot_engine?
            if InputParamsPanel.valid_context():
                self.input_params_window = GUIToplevel(self)
                self.input_params_window.withdraw()
                self.input_params_window.title('Test Pattern')
                # CEBHACKALERT: alter this...don't need to pass self & self.plot_engine
                ripp = InputParamsPanel(self.input_params_window,self.plot_engine,self)
                ripp.pack(side=TOP,expand=YES,fill=BOTH)
                self.input_params_window.deiconify()
                self.messageBar.message('state', 'OK')
            else:
                self.messageBar.message('state',
                            'Simulator does not have proper Sheet type.')
                return None
        else:
            self.messageBar.message('state', 'No active Simulator object.')


    def new_about_window(self):
        win = GUIToplevel(self)
        win.withdraw()
        win.title("About Topographica")
        text = Label(win,text=topo.ABOUT_TEXT,justify=LEFT)
        text.pack(side=LEFT)
        win.deiconify()
        self.messageBar.message('state', 'OK')
            
    def open_url(self, location, relative=False):
        """
        """
        
        if relative:
            location = os.path.join(os.getcwd(),location)
            
        try:
            webbrowser.open(location,autoraise=True)
            self.messageBar.message('state', 'Launched browser to '+location)
        except Error:
            self.messageBar.message('state', 'Unable to launch a browser')


    #
    # Command buttons.
    #
    def do_command(self,cmd):
        """
        Pass a Python command to a simulator object so that it can execute it
        in the simulator namespace.  Print the result that comes back.  Assumes
        that the simulator always returns and does not throw any exceptions
        if the cmd contains an error.
        """
        result = self.exec_cmd(cmd)
	self.messageBar.message('state', result)
        topo.tkgui.show_cmd_prompt()

    def exec_cmd(self,cmd):
        """
        Use exec to evaluate the command.  This is a prototype that needs to be
        tested to see what kind of issues develop.  Exceptions raised by the exec
        command are caught, and the name of the exception is passed back to the
        calling function.  If the command goes through, an OK is sent, along with
        a copy of the command.
        Collisions between simultaneously running simulators are possible.
        """
        try:
            #g = globals()
            g = __main__.__dict__
            exec cmd in g
            result = 'OK: ' + cmd
            # print 'Ran in namespace: ' + __name__
        except Exception, e:
            result = 'Exception Raised: ' + e.__doc__
            traceback.print_exc()
        return result
    
    
    def load_script_file(self,filename):
        """
        Load a script file from disk and evaluate it from within this
        package globals() namespace.  The purpose is to allow a
        Simulation to add in new script code into an existing
        Simulation.  Care needs to be taken that namespace variable
        collisions don't take place across multiple simulations or
        script files.
    
        This function was originally written so that the same script
        can be loaded into a simulation from the GUI or from the
        command-line.
    
        Returns False if the filename is '', (), or None.  Otherwise
        Returns True.  Exceptions raised by execfile are not caught
        here, and are instead passed on to the calling function.
        """
        if filename in ('',(),None):
            return False
        else:
            # g = globals()
            g = __main__.__dict__
            execfile(filename,g)
            # print 'Loaded ' + filename + ' in ' + __name__
            return True


    def do_learning(self,count):
        """
        A simulation object should be linked to the GUI before this
        learning command is issued on the Simulator object.
        """
        s = active_sim()
        
        if s:
            i = float(count)
            s.run(i) 
            message = 'Ran ' + count + ' to time ' + str(s.time())
            self.auto_refresh()
        else:
            message = 'Error: No active simulator.'

        self.messageBar.message('state', message)
        topo.tkgui.show_cmd_prompt()

        
    def dummy(self):
        print "Button pressed in ", self
        
        
class GUIToplevel(Toplevel):
    """
    Each new TK window requires a new Toplevel class that contains the
    object that created it, to handle such things as allowing resizing
    windows, etc.  (In this file, it's usually called with something
    like win = GUIToplevel(self).)
    
    The PMW Megawidgets classes also contain a Tkinter.toplevel object
    stored within the object variable .hull.  For now the GUIToplevel
    is subclassing the Tkinter Toplevel, but the Megawidgets could
    also be used here and the same function calls made upon the object
    stored in the .hull
    """
    def __init__(self,parent,**config):
        # Megawidgets contain Toplevels in .hull  Either system is acceptable.
        # Pmw.MegaToplevel.__init__(self,parent)
        Toplevel.__init__(self,parent,config)
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.resizable(1,1)


if __name__ != '__main__':
    plotpanel_classes['Unit Weights'] = UnitWeightsPanel
    plotpanel_classes['Projection'] = ProjectionPanel
    plotpanel_classes['Orientation Preference'] = BasicPlotGroupPanel
