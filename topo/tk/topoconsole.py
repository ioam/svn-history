"""
TopoConsole class file.

$Id$
"""
from Tkinter import Frame, Toplevel, StringVar, X, BOTTOM, TOP, \
     LEFT, RIGHT, YES, BOTH
import Pmw, re, os, sys, code, traceback, __main__
import tkFileDialog
from topo.tk.basicplotpanel import BasicPlotPanel
from topo.tk.weightspanel import WeightsPanel
from topo.tk.weightsarraypanel import ProjectionPanel
from topo.tk.inputparamspanel import InputParamsPanel
from topo.tk.preferencemappanel import PreferenceMapPanel
from topo.plotgroup import PlotGroupTemplate, PlotTemplate
import topo.simulator as simulator
import topo.plotengine
import topo.gui
import topo.base

KNOWN_FILETYPES = [('Python Files','*.py'),('Topographica Files','*.ty'),('All Files','*')]

plot_panel_list = []

class PlotsMenuEntry(topo.base.TopoObject):
    """
    Use these objects to populate the TopoConsole Plots pulldown.
    """
    def __init__(self,console,template,class_name=BasicPlotPanel,label=None,description=None,**config):
        super(PlotsMenuEntry,self).__init__(**config)
        self.console = console
        self.template = template
        self.class_name = class_name
        if not label:
            label = template.name
        self.label = label
        if not description:
            description = template.description
        self.description = description

        self.num_windows = 0
        self.title = ''


    def command(self):
        self.num_windows = self.num_windows + 1
        self.title = '%s %d' % (self.label, self.num_windows)

        pe = self.console.active_plotengine()
        if pe:
            win = GUIToplevel(self.console)
            win.withdraw()
            win.title(self.title)
            pn = self.class_name(console=self.console,pengine=pe,parent=win,
                                 plot_key=self.template,plotgroup_type=self.template)
            pn.pack(expand=YES,fill=BOTH)
            pn.refresh_title()
            win.deiconify()
            self.console.messageBar.message('state', 'OK')
        else:
            self.console.messageBar.message('state', 'No active Simulator object.')

        
    

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
        self.menubar.addmenuitem('Plots', 'command',
                             'New activity plot',
                             label="Activity",
                             command=self.new_activity_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New orientation, ocular dominance, or similar map plot',
                             label="Preference Map",
                             command=self.new_preferencemap_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New unit weights (connection fields) plot',
                             label="Unit Weights",
                             command=self.new_weights_window)
        self.menubar.addmenuitem('Plots', 'command',
                             'New projection (connection field array) plot',
                             label="Projection",
                             command=self.new_weights_array_window)
        self.menubar.addmenuitem('Plots','separator')

        self.populate_plots_menu(self.menubar)

        self.menubar.addmenuitem('Plots','separator')
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
        for (label,obj) in topo.plotengine.plotgroup_templates.items():
            entry = PlotsMenuEntry(self,obj,label=label)            
            menubar.addmenuitem('Plots','command',
                                obj.description,label=label,
                                command=entry.command)



    #
    # Accessors for the GUI's active simulator and active plotengine objects.
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
        """Get the active_simulator object relative to the GUI"""
        return self.__active_simulator_obj
    
    def active_plotengine(self):
        """Get the active_plotengine object relative to the GUI"""
        return self.__active_plotengine_obj


    ### JABHACKALERT!
    ### 
    ### If the GUI interface was requested on the command line,
    ### quitting from the GUI should also quit from the interpreter.
    ### If the GUI was started as a separate function from the
    ### Topographica interpreter, quitting from the GUI should 
    ### probably *not* exit the Topographica interpreter.
    def quit(self):
        """Close the main GUI window.  Does not exit Topographica interpreter."""
        topo.gui.set_console(None)
        Frame.quit(self)
        Frame.destroy(self)     # Get rid of widgets
        self.parent.destroy()   # Get rid of window


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
            result = self.load_script_file(self.loaded_script)
            if result:
                self.messageBar.message('state', 'Loaded ' + self.loaded_script)
            else:
                self.messageBar.message('state', 'Failed to load ' + self.loaded_script)
        topo.tk.show_cmd_prompt()

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
            result = self.load_script_file(self.loaded_script)
            if result:
                self.messageBar.message('state', 'Reloaded ' + self.loaded_script)
            else:
                self.messageBar.message('state', 'Failure reloading ' + self.loaded_script)
        topo.tk.show_cmd_prompt()
            
                
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
    

    ### JABHACKALERT!
    ### 
    ### Is it necessary to have all these new_*_window functions?
    ### They all seem very similar, and it seems like they could
    ### be handled by one shared function, e.g. new_plot_window.
        
    #
    # New plot windows
    #
    def new_activity_window(self):
        pe = self.active_plotengine()
        if pe:
            self.num_activity_windows += 1
            win = GUIToplevel(self)
            win.withdraw()
            ap = BasicPlotPanel(console=self,pengine=pe,parent=win)
            ap.pack(expand=YES,fill=BOTH)
            ap.refresh_title()
            win.deiconify()
            self.messageBar.message('state', 'OK')
        else:
            self.messageBar.message('state', 'No active Simulator object.')
            

    def new_preferencemap_window(self):
        pe = self.active_plotengine()
        if pe:
            self.num_orientation_windows += 1
            win = GUIToplevel(self)
            win.withdraw()
            win.title("Preference Map %d" % self.num_orientation_windows)
            ap = PreferenceMapPanel(console=self,pengine=pe,parent=win)
            ap.pack(expand=YES,fill=BOTH)
            ap.refresh_title()
            win.deiconify()
            self.messageBar.message('state', 'OK')
        else:
            self.messageBar.message('state', 'No active Simulator object.')


    def new_weights_window(self):
        pe = self.active_plotengine()
        if pe:
            self.num_weights_windows += 1
            win = GUIToplevel(self)
            win.withdraw()
            #win.title("Weights %d" % self.num_weights_windows)
            wp = WeightsPanel(console=self,pengine=pe,parent=win)
            wp.pack(expand=YES,fill=BOTH)
            wp.refresh_title()
            win.deiconify()
            self.messageBar.message('state', 'OK')
        else:
            self.messageBar.message('state', 'No active Simulator object.')


    def new_weights_array_window(self):
        pe = self.active_plotengine()
        if pe:
            self.num_weights_array_windows += 1
            win = GUIToplevel(self)
            win.withdraw()
            win.title("Projection %d" % self.num_weights_array_windows)
            wap = ProjectionPanel(console=self,pengine=pe,parent=win)
            wap.pack(expand=YES,fill=BOTH)
            wap.refresh_title()
            win.deiconify()
            self.messageBar.message('state', 'OK')
        else:
            self.messageBar.message('state', 'No active Simulator object.')


    def open_plot_params_window(self):
        """
        Test Pattern Window.  
        """
        pe = self.active_plotengine()
        if pe:
            if self.input_params_window == None:
                self.input_params_window = GUIToplevel(self)
                self.input_params_window.withdraw()
                self.input_params_window.title('Test Pattern')
                ripp = InputParamsPanel(self.input_params_window,pe,self)
                ripp.pack(side=TOP,expand=YES,fill=BOTH)
                self.input_params_window.deiconify()
                self.messageBar.message('state', 'OK')
            else:
                self.input_params_window.deiconify()
                self.input_params_window.lift()
                self.input_params_window.focus_set()
        else:
            self.messageBar.message('state', 'No active Simulator object.')


    ### JABHACKALERT!
    ### 
    ### This code does not work at all; the user sees
    ### "NameError: global name 'Label' is not defined" whenever the
    ### About menu option is selected.
    def new_about_window(self):
        win = GUIToplevel(self)
        win.withdraw()
        win.title("About Topographica")
        text = Label(win,text=topo.base.ABOUT_TEXT,justify=LEFT)
        text.pack(side=LEFT)
        win.deiconify()
        self.messageBar.message('state', 'OK')
            

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
        topo.tk.show_cmd_prompt()

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
        Returns True.  If execfile raises an exception, then it is not
        caught and passed to the calling function.
        """
        ### JABHACKALERT!
        ###
        ### Please clarify the last sentence above.  Is the exception
        ### passed to the calling function? (If so, say "and is
        ### instead passed on".)  Or is it not passed to the calling
        ### function? (If so, say "then it is neither caught nor
        ### passed to the calling function".)
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
        s = self.active_simulator()
        if s:
            i = float(count)
            s.run(i)
            message = 'Ran ' + count + ' to time ' + str(s.time())
            self.auto_refresh()
        else:
            message = 'Error: No active simulator.'

        self.messageBar.message('state', message)
        topo.tk.show_cmd_prompt()

        
    def dummy(self):
        print "Button pressed in ", self

    def refresh_title(self):
        """
        Create a main window title
        """
        title = "Topographica Console."
        if self.active_simulator() != None:
            title += "  Active = " + (self.active_simulator()).name
        self.parent.title(title)

        
####################

### JABHACKALERT!
### 
### Please explain what this class does.  It is not obvious to me, and
### the comments below don't appear to make sense.
class GUIToplevel(Toplevel):
    def __init__(self,parent,**config):
        # Megawidgets contain Toplevels in .hull  Either system is acceptable.
        # Pmw.MegaToplevel.__init__(self,parent)
        Toplevel.__init__(self,parent,config)
        self.protocol('WM_DELETE_WINDOW',self.destroy)
        self.resizable(1,1)

####################


# Populate the dynamic plot menu list registry:
if __name__ != '__main__':
    pgt = PlotGroupTemplate([('ActivationPref',
                              PlotTemplate({'Strength'   : 'Activation',
                                            'Hue'        : 'Activation',
                                            'Confidence' : 'Activation'}))])
    topo.plotengine.plotgroup_templates[pgt.name] = pgt
    pgt = PlotGroupTemplate([('Activity',
                              PlotTemplate({'Strength'   : 'Activation',
                                            'Hue'        : None,
                                            'Confidence' : None}))])
    topo.plotengine.plotgroup_templates[pgt.name] = pgt
