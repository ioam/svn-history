"""
TopoConsole class file.

$Id$
"""
__version__='$Revision$'

# CEBALERT: widget and frame sizes (e.g. widths) are a mess
# throughout topo.tkgui
# Also, notice what happens on resizing: space between widgets increases,
# but the widgets themselves stay the same size. It would be better if
# some were allowed to expand, like the Text box for command output
# and in particular the status box.

from math import fmod,floor
import Tkinter
from Tkinter import Frame, Toplevel, StringVar, X, BOTTOM, TOP, Button, \
     LEFT, RIGHT, YES, BOTH, Label, Text, END, DISABLED, NORMAL, Scrollbar, Y
import Pmw, os, sys, traceback, __main__
import StringIO
import tkFileDialog
import time
import webbrowser
from inspect import getdoc

import topo
import topo.commands.basic
from topo.plotting.templates import PlotGroupTemplate, plotgroup_templates
import topo.base.simulation

from topo.base.parameterizedobject import ParameterizedObject
from templateplotgrouppanel import TemplatePlotGroupPanel
from connectionfieldspanel import ConnectionFieldsPanel
from projectionactivitypanel import ProjectionActivityPanel
from projectionpanel import ProjectionPanel
from testpattern import TestPattern
from editorwindow import ModelEditor
from translatorwidgets import TaggedSlider

SCRIPT_FILETYPES = [('Topographica scripts','*.ty'),('Python scripts','*.py'),('All files','*')]

SAVED_FILE_EXTENSION = '.typ'
SAVED_FILETYPES = [('Topographica saved networks','*'+SAVED_FILE_EXTENSION),('All files','*')]



# Documentation locations: locally built and web urls.
# CEBALERT: is it appropriate to use Filename parameter here in some way?
topo_dir = os.path.split(os.path.split(sys.executable)[0])[0]
user_manual_locations      = (os.path.join(topo_dir,'doc/User_Manual/index.html'),'http://topographica.org/User_Manual/')
tutorials_locations        = (os.path.join(topo_dir,'doc/Tutorials/index.html'),'http://topographica.org/Tutorials/')
reference_manual_locations = (os.path.join(topo_dir,'doc/Reference_Manual/index.html'),'http://topographica.org/Reference_Manual/')
python_doc_locations = ('http://www.python.org/doc/')
topo_www_locations = ('http://www.topographica.org/')


# If a particular plotgroup_template needs (or works better with) a
# specific subclass of PlotPanel, the writer of the new subclass
# or the plotgroup_template can declare here that that template
# should use a specific PlotPanel subclass.  For example:
#   plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}




# jprovost: The command output window could be implemented using the
# PMW HistoryText widget, but we need to figure out how to get the
# output that normally goes to the shell window and put it in a gui
# pane.  Pyro Robotics does this, so we might be able to steal their
# code.
# 
# CEB: It might be better to have one pane (like IDLE), but the
# two-pane approach we have gives some advantages. For example, I can
# press the "up" arrow in the 'Command:' box to find previous
# commands. It was also very simple to implement.

class OutputText(Text):
    """
    A Tkinter Text widget but with some convenience methods.

    (Notably the Text stays DISABLED (i.e. not editable)
    except when we need to display new text).
    """

    def append_cmd(self,cmd,output):
        """
        Print out:
        >>> cmd
        output

        And scroll to the end.
        """
        self.config(state=NORMAL)
        self.insert(END,">>> "+cmd+"\n"+output)
        self.insert(END,"\n")
        self.config(state=DISABLED)        
        self.see(END)

    def append_text(self,text):
        """
        Print out:
        text

        And scroll to the end.
        """
        self.config(state=NORMAL)
        self.insert(END,text)
        self.insert(END,"\n")
        self.config(state=DISABLED)
        self.see(END)

        

class PlotsMenuEntry(ParameterizedObject):
    """
    Use these objects to populate the TopoConsole Plots pulldown.  The
    pulldown requires a name and a function to call when the item is
    selected.  self.command is used for that.  self.command has to be
    different for each plot type since this will include Activity,
    Connection Fields, Projection grids, Preference Maps and more.
    """
    def __init__(self,console,template,class_name=TemplatePlotGroupPanel,label=None,description=None,**config):
        super(PlotsMenuEntry,self).__init__(**config)
        self.console = console
        self.template = template

        if not label:
            label = template.name
        self.label = label
        if not description:
            description = template.name
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

        if self.class_name.valid_context():
            win = GUIToplevel(self.console)
            win.withdraw()
            win.title(self.title)
            pn = self.class_name(parent=win,console=self.console,pgt_name=self.template.name)
            pn.pack(expand=YES,fill=BOTH)

            pn.refresh_title()
            win.deiconify()
            self.console.messageBar.message('state', 'OK')
            return pn
        else:
            self.console.messageBar.message('state',
                                            'No suitable objects in this simulation for this operation.')
            return None



class TopoConsole(Frame):
    """
    Main window for the Tk-based GUI.
    """
    def __init__(self, parent=None,**config):
        Frame.__init__(self,parent,config)

        self.parent = parent
        self.num_activity_windows = 0
        self.num_orientation_windows = 0
        self.num_weights_windows = 0
        self.num_weights_array_windows = 0

	# Create the Balloon.
	self.balloon = Pmw.Balloon(self)

        self.loaded_script = None
        self.input_params_window = None
        self.auto_refresh_panels = []
        self._init_widgets()
        # Doesn't work for providing icon for the window:
        #parent.wm_iconbitmap('@/home/jbednar/research/topographica/topo.xpm')
        title = "Topographica Console"
        self.parent.title(title)

        # Provide a way for other code to access the GUI when necessary
        topo.guimain=self



    def _init_widgets(self):
        

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
        self.menubar.addmenuitem('Simulation', 'command', "Save simulation's state to disk",
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
	self.menubar.addmenuitem('Simulation', 'command', 'Open the model editor',
				 label = 'Model Editor', command = self.open_model_editor)
        self.menubar.addmenuitem('Simulation', 'separator')
        self.menubar.addmenuitem('Simulation', 'command', 'Close the GUI window',
                                 label = 'Quit',
                                 command = self.quit)

	# Create and pack the MessageBar.  (Shows "Status")
        msg_group = Pmw.Group(self,tag_text='Status')
        msg_group.pack(side=BOTTOM,expand=YES,fill=X,padx=4,pady=8)
	self.messageBar = Pmw.MessageBar(msg_group.interior(),
                                         entry_width = 45,
                                         entry_relief='groove')
	self.messageBar.pack(side = BOTTOM,fill=X,padx=4,pady=8)
	self.messageBar.message('state', 'OK')
        # JABALERT: Commenting this out restores the balloons for the
        # widgets in this window, but not for the menus.  Any idea how
        # to make balloons appear for both?
	self.balloon.configure(statuscommand = self.messageBar.helpmessage,
                               state='status')

        #
        # Plot menu
        #
        self.menubar.addmenu('Plots','Assorted plot displays')
        self.populate_plots_menu(self.menubar)

        #
        # Help menu
        #
        self.menubar.addmenu('Help','Information about Topographica', side='right')
        self.menubar.addmenuitem('Help', 'command',
                                 'Licensing and release information',
                                 label="About",
                                 command=self.new_about_window)

        self.menubar.addmenuitem('Help', 'command',
                                 'How to use Topographica',
                                 label="User Manual",
                                 command=(lambda x=user_manual_locations: self.open_location(x)))

        self.menubar.addmenuitem('Help', 'command',
                                 'Walk-through examples',
                                 label="Tutorials",
                                 command=(lambda x=tutorials_locations: self.open_location(x)))
        
        self.menubar.addmenuitem('Help', 'command',
                                 'Detailed code documentation',
                                 label="Reference Manual",
                                 command=(lambda x=reference_manual_locations: self.open_location(x)))
        
        self.menubar.addmenuitem('Help', 'command',
                                 'Topographica on the web',
                                 label="Topographica.org",
                                 command=(lambda x=topo_www_locations: self.open_location(x)))

        self.menubar.addmenuitem('Help', 'command',
                                 'Python reference',
                                 label="Python documentation",
                                 command=(lambda x=python_doc_locations: self.open_location(x)))


        #
        # Running the simulation
        #
        learning_group = Pmw.Group(self,tag_text='Simulation control')
        learning_frame = learning_group.interior()
        learning_group.pack(side=TOP,expand=YES,fill=X,padx=4,pady=8)

        rf=Label(learning_frame,text='Run for: ')
        rf.pack(side=LEFT)
        self.balloon.bind(rf,"Duration to run the simulation when Go is pressed.")
        
        learning_str=StringVar()
        learning_str.set('1.0')

        # CEBHACKALERT: does the busycallback actually work? I don't
        # see a busy cursor under metacity (the default GNOME window
        # manager), but I do see one under twm.
        
        self.run_for = TaggedSlider(learning_frame,
                                    tagvariable=learning_str,
                                    tag_width=11,
                                    slider_length=150,
                                    min_value=0,max_value=20000,
                                    string_format='%.4f')
        self.balloon.bind(self.run_for,"Duration to run the simulation, e.g. 0.0500, 1.0, or 20000.")
        self.run_for.pack(side=LEFT)

        # When return is pressed, the TaggedSlider updates itself...but we also want to run
        # the simulation in this case.
        learning_frame.optional_action=Pmw.busycallback(self.do_learning)

        go = Button(learning_frame,text="Go",
                    command=Pmw.busycallback(self.do_learning))
        go.pack(side=LEFT)
        # CEBHACKALERT: this prevents the simulation time from being updated
        # in the messagebar
        #self.balloon.bind(go,"Run the simulation for the specified duration.")




        #
        # Command entry
        #
        ### Make a Frame inside of which is a Pmw.Group, with a tag
        ### that incorporates a checkbutton. Deselecting the
        ### checkbutton empties the frame of the widgets (see
        ### toggle_command_widgets() and shrinks it) (i.e. it
        ### shows/hides command entry/output widgets).
        self.show_command_widgets = Tkinter.IntVar()
        self.show_command_widgets.set(0)
        command_frame = Frame(self)
        command_group = Pmw.Group(command_frame,
                              tag_pyclass = Tkinter.Checkbutton,
                              tag_text='Command prompt',
                              tag_command = self.toggle_command_widgets,
                              tag_variable = self.show_command_widgets)

                
        command_group.pack(fill = 'both', expand = 1, side='left')
        cw = Tkinter.Frame(command_group.interior())
        cw.pack(padx = 2, pady = 2, expand='yes', fill='both')
        command_frame.pack(padx = 6, pady = 6, expand='yes', fill='both')

        # empty frame to allow resizing to 0 (otherwise cw
        # would stay at the size it was before all widgets were removed)
        Tkinter.Frame(cw).pack()

        ### Make a ComboBox (command_entry) for entering commands.
        self.command_entry=Pmw.ComboBox(cw,autoclear=1,history=1,dropdown=1,
                                        label_text='>>> ',labelpos='w',
                               selectioncommand=Pmw.busycallback(self.exec_cmd))
        self.balloon.bind(self.command_entry,
             """Accepts any valid Python command and executes it in main as if typed at a terminal window.""")

        ### Make a Text (command_output, for output from commands)
        ### with a Scrollbar, both inside a Frame (command_output_frame,
        ### for convenient access)
        self.command_output_frame = Tkinter.Frame(cw)
        scrollbar = Scrollbar(self.command_output_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        # CEBALERT: what length history is this going to keep?
        self.command_output = OutputText(self.command_output_frame,
                                         state=DISABLED,
                                         height=10,
                                         yscrollcommand=scrollbar.set)
        self.command_output.pack(side=TOP,expand=YES,fill=X)
        scrollbar.config(command=self.command_output.yview)

        # note that pack() hasn't been called on command_output or on
        # command_entry - get called by toggle_command_widgets


    def toggle_command_widgets(self):
        if self.show_command_widgets.get()==1:
            self.command_entry.pack(side=BOTTOM,expand=YES,fill=X)
            self.command_output_frame.pack()
        else:
            self.command_entry.pack_forget()
            self.command_output_frame.pack_forget()
            

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
                                obj.name,label=label,
                                command=entry.command)
    
    def quit(self):
        """
        Close the main GUI window.

        Exits the Topographica interpreter.
        """
        Frame.quit(self)
        Frame.destroy(self)     # Get rid of widgets
        self.parent.destroy()   # Get rid of window
        if topo.gui_cmdline_flag:
            print "Quit selected; exiting"
            sys.exit()


    # CEBALERT: the way this works might be a surprise, because previously
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
        

    # CEBALERT:
    # save_ and load_snapshot() and load_network() ought to close open windows such
    # as Activity.  Currently it just refreshes the windows, but that could get
    # confusing.
    
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

        self.auto_refresh()


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
    
                
    def reset_network(self):
	self.messageBar.message('state', 'Reset not yet implemented')


    # auto-refresh handling
    def auto_refresh(self):
        """
        Refresh all windows in auto_refresh_panels.
        
        Panels can add and remove themselves to the list; those in the list
        will have their refresh() method called whenever this console's
        autorefresh() is called.
        """
        for win in self.auto_refresh_panels:
            win.refresh()
        self.update_idletasks()
                    
    # open the model editor window
    def open_model_editor(self) :
	ModelEditor()



    #
    # New plot windows
    # JABALERT: Shouldn't this be named open_test_pattern_window?
    def open_plot_params_window(self):
        """
        Test Pattern Window.  
        """
        if TestPattern.valid_context():
            self.input_params_window = GUIToplevel(self)
            self.input_params_window.withdraw()
            self.input_params_window.title('Test Pattern')
            ripp = TestPattern(self.input_params_window,self)
            ripp.pack(side=TOP,expand=YES,fill=BOTH)
            self.input_params_window.deiconify()
            self.messageBar.message('state', 'OK')
        else:
            self.messageBar.message('state',
                                    'No suitable objects in this simulation for this operation.')


    def new_about_window(self):
        win = GUIToplevel(self)
        win.withdraw()
        win.title("About Topographica")
        text = Label(win,text=topo.about(display=False),justify=LEFT)
        text.pack(side=LEFT)
        win.deiconify()
        self.messageBar.message('state', 'OK')
            
    def open_location(self, locations):
        """
        Try to open one of the specified locations in a new window of the default
        browser. See webbrowser module for more information.

        locations should be a tuple.
        """
        # CB: could have been a list. This is only here because if locations is set
        # to a string, it will loop over the characters of the string.
        assert isinstance(locations,tuple),"locations must be a tuple."
        
        for location in locations:
            try:
                webbrowser.open(location,new=True,autoraise=True)
                self.messageBar.message('state', 'Opened '+location+' in browser.')
                return
            # Since one of the possible exception appears to be a 'WindowsError' (at least
            # on the Windows platform), just catch all exceptions.
            except Exception:
                self.messageBar.message('state', "Couldn't open "+location+" in browser.")

                
    def exec_cmd(self,cmd):
        """
        exec the cmd in __main__.__dict__.

        Redirects sys.stdout and sys.stderr to the output text window
        for the duration of the command.

        Updates the status bar to indicate success or not.
        """
        capture_stdout = StringIO.StringIO()
        capture_stderr = StringIO.StringIO()

        # capture output and errors
        sys.stdout = capture_stdout
        sys.stderr = capture_stderr

        try:
            exec cmd in __main__.__dict__
            result = 'OK: ' + cmd
            
        except Exception, e:
            traceback.print_exc()
            result = 'Exception Raised: ' + getdoc(e)

        output = capture_stdout.getvalue()
        error = capture_stderr.getvalue()

        self.command_output.append_cmd(cmd,output)
        
        if error:
            self.command_output.append_text("*** Error:\n"+error)
            
        # stop capturing
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
                
        capture_stdout.close()
        capture_stderr.close()

	self.messageBar.message('state', result)

    
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


    def do_learning(self):
        """
        Run the simulation for the duration specified in the
        'run for' taggedslider.
        
        All this routine truly needs to do is
        topo.sim.run(self.run_for.get_value()), but it adds other useful
        features like periodically displaying the simulated and real
        time remaining.
        """
        
        # Should replace with a progress bar; see
        # http://tkinter.unpythonic.net/bwidget/
        # http://tkinter.unpythonic.net/wiki/ProgressBar

        ### JABALERT: Most of this code should move to the
        ### Simulation class, because it is not specific to the GUI.
        ### E.g. we'll also want time remaining estimates from the
        ### command line and the batch interface.
        fduration = self.run_for.get_value()
        step   = 2.0
        iters  = int(floor(fduration/step))
        remain = fmod(fduration, step)
        starttime=time.time()
        recenttimes=[]

        # Temporary:
        self.parent.title(topo.sim.name) ## this changes the title bar to more useful

        ## Duration of most recent times from which to estimate remaining time
        estimate_interval=50.0
        for i in xrange(iters):
            recenttimes.append(time.time())
            length = len(recenttimes)

            if (length>50):
                recenttimes.pop(0)
                length-=1
                
            topo.sim.run(step)
            percent = 100.0*i/iters

            estimate = (iters-i)*(recenttimes[-1]-recenttimes[0])/length
            
            message = 'Time ' + str(topo.sim.time()) + ': ' + \
                      str(int(percent)) + '% of '  + str(fduration) + ' completed ' + \
                      ('(%02d' % int(estimate/60))+':' + \
                      ('%02d' % int(estimate%60))+ ' remaining at current rate).'

            self.messageBar.message('state', message)
            self.update_idletasks()
                                                                                                                                                  
        topo.sim.run(remain)
        message = 'Ran ' + str(fduration) + ' to time ' + str(topo.sim.time())
        self.auto_refresh()


        self.messageBar.message('state', message)

        
        
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
    plotpanel_classes['Connection Fields'] = ConnectionFieldsPanel
    plotpanel_classes['Projection'] = ProjectionPanel 
    plotpanel_classes['Projection Activity'] = ProjectionActivityPanel 
