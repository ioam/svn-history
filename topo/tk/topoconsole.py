"""
TopoConsole class file.

$Id$
"""
from Tkinter import *
import Pmw, re, os, sys, code, traceback, __main__
import tkFileDialog
from topo.tk.propertiesframe import *
from topo.tk.plotpanel import *
import topo.simulator as simulator
import topo.plotengine

MIN_PLOT_WIDTH = 100
KNOWN_FILETYPES = [('Python Files','*.py'),('Topographica Files','*.ty'),('All Files','*')]


class TopoConsole(Frame):
    """
    TopoConsole class file.
    
    Primary window for the Tk-based GUI.  Loads, saves, calls other window
    frames in plotframe.py.  Keeps tabs on the active Simulation, and
    which PlotEngine is driving it.  If the active simulation is switched,
    then the PlotEngine is changed, but the old PlotEngine is stored and
    reactivated if the old Simulator is reactivated as well.
    """
    def __init__(self, parent=None,**config):
        Frame.__init__(self,parent,config)

        self.parent = parent
        self.num_activity_windows = 0
        self.num_orientation_windows = 0
        self.num_weights_windows = 0
        self.num_weights_array_windows = 0

        # One location to store and retrieve the Simulator object that
        # will be used for plot data.  Do not directly use these, but
        # go through the accessor functions.
        self.__active_simulator_obj = None
        self.__active_plotengine_obj = None
        # Stores inactive simulator/plotengine pairs for relinking
        self.__plotengine_dict = {None: None}
        
        self.loaded_script = None
        self.input_params_window = None
        self.auto_refresh_panels = []

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

        #
        # Simulation Menu
        #
        self.menubar.addmenu('Simulation','Simulation commands')
        self.menubar.addmenuitem('Simulation', 'command', 'Load script file',
                                 label = 'Load',
                                 command = self.load_network)
        self.menubar.addmenuitem('Simulation', 'command', 'Reload script from disk',
                                 label = 'Reload',
                                 command = self.reload_network)
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
                                 foreground = 'Gray',            #
                                 activeforeground = 'Gray',      #
                                 activebackground = 'Light Gray',#
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
        self.menubar.addmenuitem('Plots', 'command',
                             'New activity plot',
                             label="Activity",
                             command=self.new_activity_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New orientation, ocular dominance, or similar map plot',
                             label="Preference Map",
                             ## Gray out menu item ###########
                             foreground = 'Gray',            #
                             activeforeground = 'Gray',      #
                             activebackground = 'Light Gray',#
                             #################################
                             command=self.new_preferencemap_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New weights plot',
                             label="Weights",
                             command=self.new_weights_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New weights array plot',
                             label="Weights Array",
                             ## Gray out menu item ###########
                             foreground = 'Gray',            #
                             activeforeground = 'Gray',      #
                             activebackground = 'Light Gray',#
                             #################################
                             command=self.new_weights_array_window)
        self.menubar.addmenuitem('Plots','separator')
        self.menubar.addmenuitem('Plots', 'command',
                                 'Refresh auto-refresh plots',
                                 label="Refresh",
                                 command=self.auto_refresh)
        

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


    #
    # Accessors for the active simulator and active plotengine objects.
    #
    def set_active_simulator(self, new_sim):
        """
        Set the active_simulator that the GUI will use to the variable
        passed in.  A matching PlotEngine will either be created, or
        pulled from a dictionary if the GUI has seen the Simulator before.
        """
        assert isinstance(new_sim,simulator.Simulator) or new_sim == None, "Not a Simulator"
    
        self.__active_simulator_obj = new_sim
        if self.__plotengine_dict.has_key(new_sim):
            self.__active_plotengine_obj = self.__plotengine_dict[new_sim]
        else:
            self.__active_plotengine_obj = topo.plotengine.PlotEngine(new_sim)
            self.__plotengine_dict[new_sim] = self.__active_plotengine_obj
        self.refresh_title()
    
    def active_simulator(self):
        """Get the active_simulator object"""
        return self.__active_simulator_obj
    
    def active_plotengine(self):
        """Get the active_plotengine object"""
        return self.__active_plotengine_obj



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
        Load a script file from disk and evaluate it.  The file is evaluated
        from within the globals() namespace.
        """
        self.loaded_script = tkFileDialog.askopenfilename(filetypes=KNOWN_FILETYPES)
        if self.loaded_script in ('',(),None):
            self.loaded_script = None
            self.messageBar.message('state', 'Load canceled')
        else:
            result = simulator.load_script_file(self.loaded_script)
            if result:
                self.messageBar.message('state', 'Loaded ' + self.loaded_script)
            else:
                self.messageBar.message('state', 'Failure loading ' + self.loaded_script)
        show_cmd_prompt()

    def reload_network(self):
        """
        Reload the previously loaded file from disk.  Will not
        prompt for new filename.  Currently does not flush any
        existing environment variables, so the loaded script needs
        to take that into account.  execfile() is run within the
        globals() namespace.

        WARNING: This function does not use the built-in reload()
        function, so imports will not be reevaluated unless explicitly
        commanded from within the loaded script.
        """
        if self.loaded_script == None:
            self.messageBar.message('state', 'No script to reload')
        else:
            result = simulator.load_script_file(self.loaded_script)
            if result:
                self.messageBar.message('state', 'Reloaded ' + self.loaded_script)
            else:
                self.messageBar.message('state', 'Failure reloading ' + self.loaded_script)
        show_cmd_prompt()
            
                
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
    def new_activity_window(self):
        # Judah - MUST SHOW WINDOW.
        self.num_activity_windows += 1
        win = GUIToplevel(self)
        win.withdraw()
        win.title("Activity %d" % self.num_activity_windows)
        ActivityPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        win.deiconify()

    def new_preferencemap_window(self):
        self.messageBar.message('state', 'Not yet implemented')
        # self.num_orientation_windows += 1
        # win = GUIToplevel(self)
        # win.withdraw()
        # win.title("Preference Map %d" % self.num_orientation_windows)
        # PreferenceMapPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        # win.deiconify()

    def new_weights_window(self):
        # Judah - MUST SHOW THIS WINDOW
        self.num_weights_windows += 1
        win = GUIToplevel(self)
        win.withdraw()
        win.title("Weights %d" % self.num_weights_windows)
        WeightsPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        win.deiconify()

    def new_weights_array_window(self):
        self.messageBar.message('state', 'Not yet implemented')
        # self.num_weights_array_windows += 1
        # win = GUIToplevel(self)
        # win.withdraw()
        # win.title("Weights Array %d" % self.num_weights_array_windows)
        # WeightsArrayPanel(console=self,parent=win).pack(expand=YES,fill=BOTH)
        # win.deiconify()

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
        show_cmd_prompt()

    def exec_cmd(self,cmd):
        """
        Use exec to evaluate the command.  This is a prototype that needs to be
        tested to see what kind of issues develop.  Exceptions raised by the exec
        command are caught, and the name of the exception is passed back to the
        calling function.  If the command goes through, an OK is sent, along with
        a copy of the command.
    
        The exec is run inside of the global namespace.  This function is run
        inside of a class, but the global space is shared between classes, so
        collisions between simultaneously running simulatiors is possible.
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
        Returns True.  If execfile raises an exception, then it is not
        caught and passed to the calling function.
        """
        if filename in ('',(),None):
            return False
        else:
            # g = globals()
            g = __main__.__dict__
            execfile(filename,g)
            # print 'Loaded ' + filename + ' in ' + __name__
            return True


    def do_training(self,count):
        """
        LOGIC ERROR: It is no longer possible to do training
        iterations on an unnamed simulation since there may be
        multiple objects.  There needs to be a way to link to a
        particular simulation.
        """
        # Judah - THIS MUST BE IMPLEMENTED
        #        Lissom.cmd("training +" + count)
        self.auto_refresh()
        
    def dummy(self):
        print "Button pressed in ", self

    def refresh_title(self):
        """
        Create a main window title
        """
        title = "Topographica Console."
        if self.active_simulator() != None:
            title += "  Active Simulator = " + (self.active_simulator()).name
        self.parent.title(title)

        
####################

class GUIToplevel(Toplevel):
    def __init__(self,parent,**config):
        Toplevel.__init__(self,parent,config)
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.resizable(0,0)

####################


