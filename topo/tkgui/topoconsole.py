"""
TopoConsole class file.

$Id$
"""
__version__='$Revision$'


import os
import sys
import traceback
import __main__
import code
import StringIO
import time
import webbrowser
from math import fmod,floor
from inspect import getdoc

import Tkinter
from Tkinter import Frame, StringVar, X, BOTTOM, TOP, Button, \
     LEFT, RIGHT, YES, NO, BOTH, Label, Text, END, DISABLED, NORMAL, Scrollbar, Y
import tkMessageBox
import tkFileDialog
import Pmw

import topo
from topo.misc.keyedlist import KeyedList
from topo.base.parameterizedobject import ParameterizedObject
import topo.base.simulation
import topo.commands.basic
from topo.plotting.templates import PlotGroupTemplate, plotgroup_templates

import topo.tkgui 
from tkguiwindow import TkguiWindow
from templateplotgrouppanel import TemplatePlotGroupPanel
from connectionfieldspanel import ConnectionFieldsPanel
from projectionactivitypanel import ProjectionActivityPanel
from featurecurvepanel import FeatureCurvePanel, FullFieldFeatureCurvePanel
from projectionpanel import ProjectionPanel
from testpattern import TestPattern
from editorwindow import ModelEditor
from translatorwidgets import TaggedSlider




SCRIPT_FILETYPES = [('Topographica scripts','*.ty'),('Python scripts','*.py'),('All files','*')]
SAVED_FILE_EXTENSION = '.typ'
SAVED_FILETYPES = [('Topographica saved networks','*'+SAVED_FILE_EXTENSION),('All files','*')]


# Location of topographica main directory
topo_dir = os.path.split(os.path.split(sys.executable)[0])[0]

# Documentation locations: locally built and web urls.
# CEBALERT: is it appropriate to use Filename parameter here in some way?
user_manual_locations      = (os.path.join(topo_dir,'doc/User_Manual/index.html'),'http://topographica.org/User_Manual/')
tutorials_locations        = (os.path.join(topo_dir,'doc/Tutorials/index.html'),'http://topographica.org/Tutorials/')
reference_manual_locations = (os.path.join(topo_dir,'doc/Reference_Manual/index.html'),'http://topographica.org/Reference_Manual/')
python_doc_locations = ('http://www.python.org/doc/')
topo_www_locations = ('http://www.topographica.org/')
plotting_help_locations = (os.path.join(topo_dir,'doc/User_Manual/plotting.html'),'http://topographica.org/User_Manual/plotting.html')

# If a particular plotgroup_template needs (or works better with) a
# specific subclass of PlotPanel, the writer of the new subclass
# or the plotgroup_template can declare here that that template
# should use a specific PlotPanel subclass.  For example:
#   plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}


class InterpreterComboBox(Pmw.ComboBox):

    # Subclass of combobox to allow null strings to be passed to
    # the interpreter.
    
    def _addHistory(self):
        input = self._entryWidget.get()
        if input == '':
            self['selectioncommand'](input)
        else:
            Pmw.ComboBox._addHistory(self)
        


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

        
# CEB: what's the difference between label, description, etc?
class PlotsMenuEntry(ParameterizedObject):
    """
    Use these objects to populate the TopoConsole Plots pulldown.  The
    pulldown requires a name and a function to call when the item is
    selected.  self.command is used for that.  self.command has to be
    different for each plot type since this will include Activity,
    Connection Fields, Projection grids, Preference Maps and more.
    """
    def __init__(self,console,template,class_name=TemplatePlotGroupPanel,label=None,description=None,**params):
        super(PlotsMenuEntry,self).__init__(**params)
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
        if self.template.template_plot_type=='curve':
            class_name = plotpanel_classes.get(self.label,FeatureCurvePanel)
        self.class_name = plotpanel_classes.get(self.label,class_name)
        

        self.num_windows = 0
        self.title = ''


    def command(self,event=None,**args):
        """


        args are keyword arguments that are passed to the class that's
        being constructed
        """
        
        self.num_windows = self.num_windows + 1
        self.title = '%s %d' % (self.label, self.num_windows)
        #if 'valid_context' in dir(self.class_name):

        if self.class_name.valid_context():
            pn = self.class_name(console=self.console,pgt_name=self.template.name,**args)
            pn.refresh_title()
            self.console.messageBar.message('state', 'OK')
            return pn
        else:
            self.console.messageBar.message('state',
                                            'No suitable objects in this simulation for this operation.')
            return None



class TopoConsole(TkguiWindow):
    """
    Main window for the Tk-based GUI.
    """
    def __init__(self,**config):

        TkguiWindow.__init__(self,**config)
        #super(TopoConsole,self).__init__(**config)
    
        self.num_activity_windows = 0
        self.num_orientation_windows = 0
        self.num_weights_windows = 0
        self.num_weights_array_windows = 0

        self.loaded_script = None
        self.input_params_window = None
        self.auto_refresh_panels = []
        self._init_widgets()
                
        
        self.title("Topographica Console")

        # command interpreter for executing commands in the console (used by exec_cmd).
        self.interpreter = code.InteractiveConsole(__main__.__dict__)
        
        # Provide a way for other code to access the GUI when necessary
        topo.guimain=self

        # catch click on the 'x': offers choice to quit or not
        self.protocol("WM_DELETE_WINDOW",self.quit)

        
        ##########
        ### Make cascade menus open automatically on linux when the mouse
        ### is over the menu title.
        ### [Tkinter-discuss] Cascade menu issue
        ### http://mail.python.org/pipermail/tkinter-discuss/2006-August/000864.html
        if topo.tkgui.system_platform is 'linux':
            activate_cascade = """\
            if {[%W cget -type] != {menubar} && [%W type active] == {cascade}} {
                %W postcascade active
               }
            """
            self.bind_class("Menu", "<<MenuSelect>>", activate_cascade)
        ##########


# CB: example code for plot gallery
##         plots = []
##         for (label,obj) in plotgroup_templates.items():
##             entry = PlotsMenuEntry(self,obj,label=label)
##             # CB: description should be somewhere in the plot, along with a sample image?
##             plots.append((label,entry.command,entry.description+' desc.',"examples/ellen_arthur.pgm"))
            
##         plot_gallery = Gallery(plots=plots,image_size=(50,50))
##         plot_gallery.title("Plots")
        


    def _init_widgets(self):
        


	### MessageBar.  (Shows "Status")
        msg_group = Pmw.Group(self,tag_text='Status')
        msg_group.pack(side=BOTTOM,expand=NO,fill=X,padx=4,pady=8)
	self.messageBar = Pmw.MessageBar(msg_group.interior(),
                                         entry_width = 45,
                                         entry_relief='groove')
	self.messageBar.pack(side = BOTTOM,fill=X,padx=4,pady=8)
	self.messageBar.message('state', 'OK')

	### Balloon, for pop-up help
	self.balloon = Pmw.Balloon(self)


	### Top-level (native) menu bar
        # (There is no context-sensitive help for the menu because mechanisms
        #  for implementing it are not available on all platforms. We used to
        #  have a Pmw Balloon bound to the menu, with its output directed to
        #  the status bar.)

	self.menubar = Tkinter.Menu(self)       
        self.configure(menu=self.menubar)



        self.__simulation_menu()
        self.__plot_menu()
        self.__help_menu()



        #
        # Running the simulation
        #
        learning_group = Pmw.Group(self,tag_text='Simulation control')
        learning_frame = learning_group.interior()
        learning_group.pack(side=TOP,expand=NO,fill=X,padx=4,pady=8)

        rf=Label(learning_frame,text='Run for: ')
        rf.pack(side=LEFT)
        
        learning_str=StringVar()
        learning_str.set('1.0')

        
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
        learning_frame.optional_action=self.do_learning

        go_button = Button(learning_frame,text="Go",
                           command=self.do_learning)
        go_button.pack(side=LEFT)
        
        self.balloon.bind(go_button,"Run the simulation for the specified duration.")


	self.stop_button = Button(learning_frame,text="Stop",state=DISABLED,
                                  command=lambda: self.set_stop())
	self.stop_button.pack(side=LEFT)
        self.balloon.bind(self.stop_button,"""
            Stop a running simulation.

            The simulation can be interrupted only on round integer
            simulation times, e.g. at 3.0 or 4.0 but not 3.15.  This
            ensures that stopping and restarting are safe for any
            model set up to be in a consistent state at integer
            boundaries, as the example Topographica models are.""")


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

                
        command_group.pack(fill = 'both', expand = YES, side='left')
        cw = Tkinter.Frame(command_group.interior())
        cw.pack(padx = 2, pady = 2, expand=YES, fill='both')
        command_frame.pack(padx = 6, pady = 6, expand='yes', fill='both')

        # empty frame to allow resizing to 0 (otherwise cw
        # would stay at the size it was before all widgets were removed)
        Tkinter.Frame(cw).pack(expand=NO)

        ### Make a ComboBox (command_entry) for entering commands.
        self.command_entry=InterpreterComboBox(cw,autoclear=1,history=1,dropdown=1,
                                               label_text='>>> ',labelpos='w',
                                               # CB: if it's a long command, the gui obviously stops responding.
                                               # On OS X, a spinning wheel appears. What about linux and win?
                                               selectioncommand=self.exec_cmd)
        
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
        self.command_output.pack(side=TOP,expand=YES,fill='both')
        scrollbar.config(command=self.command_output.yview)

        # note that pack() hasn't been called on command_output or on
        # command_entry - get called by toggle_command_widgets


        


    def __simulation_menu(self):
        """Add the simulation menu options to the menubar."""
        simulation_menu = Tkinter.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label='Simulation',menu=simulation_menu)

        simulation_menu.add_command(label='Run script',command=self.load_network)
        simulation_menu.add_command(label='Save script',command=self.save_script_repr)
        simulation_menu.add_command(label='Load snapshot',command=self.load_snapshot)
        simulation_menu.add_command(label='Run script',command=self.load_snapshot)
        #simulation_menu.add_command(label='Reset',command=self.reset_network)
        simulation_menu.add_command(label='Test Pattern',command=self.open_plot_params_window)
        simulation_menu.add_command(label='Model Editor',command=self.open_model_editor)
        simulation_menu.add_command(label='Quit',command=self.quit_topographica)

        


    def __plot_menu(self):
        """
        Add the plot menu to the menubar, and create categorized entries
        for all the plotgroup_templates.
        """
        # CEBALERT: more complex than it needs to be! (Hence the extra comments.)
        # Needs to be cleaned up, along with PlotsMenuEntry.
        # There seem to be several unnecessary steps, and the same thing is often
        # stored in too many different places.
        # Update the documentation.
        
        # (Note about plots_menu_entries: it's accessed in 1 other place in tkgui.)

        # create plots_menu_entries, and get categories
        self.plots_menu_entries=KeyedList() # keep the order of plotgroup_templates (which is also KL)
        categories = []
        for label,pgt in plotgroup_templates.items():
            entry = PlotsMenuEntry(self,pgt,label=label)            
            self.plots_menu_entries[label]=entry
            categories.append(entry.template.category)
        categories = sorted(set(categories))


        basic_category = 'Basic'
        assert basic_category in categories
        
        plots_menu = Tkinter.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label='Plots',menu=plots_menu)
        
        # The Basic category items appear on the menu itself.
        for label,entry in self.plots_menu_entries:
            if entry.template.category==basic_category:
                    plots_menu.add_command(label=entry.label,command=entry.command)
                                             
                                             
        categories.remove('Basic')
        plots_menu.add_separator()
        
        # Add the other categories to the menu as cascades, and the plots of each category to
        # their cascades.
        for category in categories:
            cat_menu = Tkinter.Menu(plots_menu,tearoff=0)
            plots_menu.add_cascade(label=category,menu=cat_menu)
            
            for label,entry in self.plots_menu_entries:
                if entry.template.category==category:
                    cat_menu.add_command(label=entry.label,command=entry.command)
            
        plots_menu.add_separator()
        plots_menu.add_command(label="Help",command=(lambda x=plotting_help_locations: self.open_location(x)))


    def __help_menu(self):
        """Add the help menu options."""

        help_menu = Tkinter.Menu(self.menubar,tearoff=0,name='help')
        self.menubar.add_cascade(label='Help',menu=help_menu) # CB: did I keep help right?

        help_menu.add_command(label='About',command=self.new_about_window)
        help_menu.add_command(label="User Manual",
                              command=(lambda x=user_manual_locations: self.open_location(x)))

        help_menu.add_command(label="Tutorials",
                              command=(lambda x=tutorials_locations: self.open_location(x)))
        
        help_menu.add_command(label="Reference Manual",
                              command=(lambda x=reference_manual_locations: self.open_location(x)))
        
        help_menu.add_command(label="Topographica.org",
                              command=(lambda x=topo_www_locations: self.open_location(x)))

        help_menu.add_command(label="Python documentation",
                              command=(lambda x=python_doc_locations: self.open_location(x)))




    def set_stop(self):
        """Declare that running should be interrupted."""
        self.stop=True

            
    def toggle_command_widgets(self):
        if self.show_command_widgets.get()==1:
            self.command_entry.pack(side=BOTTOM,expand=NO,fill=X)
            self.command_output_frame.pack(expand=YES,fill='both')
        else:
            self.command_entry.pack_forget()
            self.command_output_frame.pack_forget()
            

    def quit_topographica(self):
        """Quit topographica."""
        if tkMessageBox.askyesno("Quit Topographica","Really quit?"):
            self.destroy() 
            if topo.gui_cmdline_flag:
                print "Quit selected; exiting"

            # Workaround for obscure problem on some UNIX systems
            # as of 4/2007, probably including Fedora Core 5.  
            # On these systems, if Topographica is started from a
            # bash prompt and then quit from the Tkinter GUI (as
            # opposed to using Ctrl-D in the terminal), the
            # terminal would suppress echoing of all future user
            # input.  stty sane restores the terminal to sanity,
            # but it is not clear why this is necessary.
            # For more info:
            # http://groups.google.com/group/comp.lang.python/browse_thread/thread/68d0f33c8eb2e02d
            if topo.tkgui.system_platform!="win":  
                try: os.system("stty sane")   # Gives an error msg on Windows 
                except: pass                  # and is not required.
                
            sys.exit()


    # CEBALERT: change name to run_script
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
        

    def save_script_repr(self):
        script_name = tkFileDialog.asksaveasfilename(filetypes=SCRIPT_FILETYPES,initialfile=topo.sim.name+"_script_repr.ty")
        if script_name:
            script_file = open(script_name,'w') # CEBALERT: presumably stray, and should be removed
            topo.commands.basic.save_script_repr(script_name)
            self.messageBar.message('state', 'Script saved to ' + script_name)
            
    
    def load_snapshot(self):
        """
        Dialog to load a user-selected snapshot (see topo.commands.basic.load_snapshot() ).
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
        Dialog to save a snapshot (see topo.commands.basic.save_snapshot() ).
        
        Adds the file extension .typ if not already present.
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

        

    def refresh_activity_windows(self):
        """
        Update any windows with a plotgroup_key of 'Activity'.

        Used primarily for debugging long scripts that present a lot of activity patterns.
        """
        for win in self.auto_refresh_panels:
            if win.plotgroup_key=='Activity' or win.plotgroup_key=='ProjectionActivity' :
                win.refresh()
                self.update_idletasks()


    def open_model_editor(self):
        """Start the Model editor."""
	ModelEditor()



    # JABALERT: Shouldn't this be named open_test_pattern_window?
    def open_plot_params_window(self):
        """
        Test Pattern Window.  
        """
        if TestPattern.valid_context():
            self.input_params_window = TestPattern(self)
            self.input_params_window.title('Test Pattern')
            self.messageBar.message('state', 'OK')
        else:
            self.messageBar.message('state',
                                    'No suitable objects in this simulation for this operation.')


    def new_about_window(self):
        win = TkguiWindow()
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
        Pass cmd to the console's command interpreter.

        Redirects sys.stdout and sys.stderr to the output text window
        for the duration of the command.

        Updates the status bar to indicate success or not.
        """
        
        capture_stdout = StringIO.StringIO()
        capture_stderr = StringIO.StringIO()

        # capture output and errors
        sys.stdout = capture_stdout
        sys.stderr = capture_stderr

        if self.interpreter.push(cmd):
            self.command_entry.configure(label_text='... ')
            result = 'Continue: ' + cmd
        else:
            self.command_entry.configure(label_text='>>> ')
            result = 'OK: ' + cmd

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
        self.command_entry.component('entryfield').clear()
    
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
        ### command line and the batch interface.  Also see
        ### topo/analysis/featureresponses.py; maybe it should 
        ### be its own object instead; not sure.
        fduration = self.run_for.get_value()
        step   = 2.0
        iters  = int(floor(fduration/step))
        remain = fmod(fduration, step)
        starttime=time.time()
        recenttimes=[]

        # Temporary:
        self.title(topo.sim.name) ## this changes the title bar to more useful

        ## Duration of most recent times from which to estimate remaining time
        estimate_interval=50
        start_sim_time=topo.sim.time()
        self.stop=False
        self.stop_button.config(state=NORMAL)        
        for i in xrange(iters):
            recenttimes.append(time.time())
            length = len(recenttimes)

            if (length>estimate_interval):
                recenttimes.pop(0)
                length-=1
                
            topo.sim.run(step)
            percent = 100.0*i/iters

            estimate = (iters-i)*(recenttimes[-1]-recenttimes[0])/length

            # Should say 'at current rate', since the calculation assumes linearity
            message = ('Time %0.2f: %d%% of %0.0f completed (%02d:%02d remaining)' %
                       (topo.sim.time(),int(percent),fduration, int(estimate/60),
                        int(estimate%60)))

            self.messageBar.message('state', message)
            self.update()
            if self.stop:
                break
                                                                                                                                                  
        self.stop_button.config(state=DISABLED)
        if not self.stop:
            topo.sim.run(remain)
        
        message = ('Ran %0.2f to time %0.2f' %
                   (topo.sim.time()-start_sim_time, topo.sim.time()))
        self.auto_refresh()

        self.messageBar.message('state', message)

        

if __name__ != '__main__':
    plotpanel_classes['Connection Fields'] = ConnectionFieldsPanel
    plotpanel_classes['Projection'] = ProjectionPanel 
    plotpanel_classes['Projection Activity'] = ProjectionActivityPanel
    plotpanel_classes['Orientation Tuning Fullfield'] = FullFieldFeatureCurvePanel



# CB: example code for plot gallery
## import Image,ImageOps
## import ImageTk
## import bwidget

# Could change to something with tabs to divide up plotlist
##  class Gallery(Tkinter.Toplevel):
##     """
##     A window displaying information about and allowing execution
##     of plotting commands.


##     Given a list of tuples [(label1,command1,description1,image1),
##                             (label2,command2,description2,image2),
##                             ...
##                             ]
##     displays a window

##     [image1] label1
##     [image2] label2

##     where the descriptions are displayed as popup help over the
##     labels, and double clicking a label executes the corresponding
##     command.
##     """    
##     def __init__(self,plots,image_size=(40,40),**config):

##         Tkinter.Toplevel.__init__(self,**config)
##         self.dynamic_help = Pmw.Balloon(self)
##         self.image_size = image_size

##         # bwidget's scrolled frame: the frame to work
##         # with is self.contents
##         sw = bwidget.ScrolledWindow(self)
##         sf = bwidget.ScrollableFrame(self)#,height=40*5+10)
##         sw.setwidget(sf)
##         sw.pack(fill="both",expand="yes")
##         self.contents = sf.getframe()


##         ####
##         ##  CEBALERT: got to keep references to the images, or they vanish.
##         ##  [http://infohost.nmt.edu/tcc/help/pubs/pil/image-tk.html]
##         ##  There is a bug in the current version of the Python
##         ##  Imaging Library that can cause your images not to display
##         ##  properly. When you create an object of class PhotoImage,
##         ##  the reference count for that object does not get properly
##         ##  incremented, so unless you keep a reference to that object
##         ##  somewhere else, the PhotoImage object may be
##         ##  garbage-collected, leaving your graphic blank on the
##         ##  application.
##         self.__image_hack = []
##         #####

##         self.__create_entries(plots)

        
        

##     def __create_entries(self,plots):
##         """
##         Use the grid manager to display the (image,label) pairs
##         in rows of columns.
##         """
##         for row,(label,command,description,image_path) in zip(range(len(plots)),plots):


##             # (labels should be buttons so they get highlighted
##             # and you would press on them naturally, and no need
##             # to bind click event)
##             image = ImageTk.PhotoImage(ImageOps.fit(Image.open(image_path),self.image_size))

##             li = Button(self.contents,command=command)
##             li['image'] = image
##             li.grid(row=row,column=0,sticky='w')

##             l = Label(self.contents,text=label)
##             l.grid(row=row,column=1,sticky='w')

##             # (the order of binding pmw balloon and a something else
##             # matters, since balloon clears previous bindings)
##             self.dynamic_help.bind(l,description)

##             # see alert in __init__
##             self.__image_hack.append(image)
            
