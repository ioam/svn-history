"""
TopoConsole class file.


$Id$
"""
__version__='$Revision$'



# CB: does the status bar need to keep saying 'ok'? Sometimes
# positive feedback is useful, but 'ok' doesn't seem too helpful.


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

try:
    import bwidget
    bwidget_imported=True
except:
    bwidget_imported=False


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
from projectionpanel import CFProjectionPGPanel
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
# CEBALERT: why are the other plotpanel_classes updates at the end of this file?


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



# CB: can we embed some shell or even ipython instead? Maybe not ipython for a while:
# http://lists.ipython.scipy.org/pipermail/ipython-user/2006-March/003352.html
# If we were to use ipython as the default interpreter for topographica, then we wouldn't need any of this,
# since all platforms could have a decent command line (could users override what they wanted to use
# as their interpreter in a config file?).
# Otherwise maybe we can turn this into something capable of passing input to and from some program
# that the user can specify?
class CommandPrompt(Tkinter.Frame):
    """
    A Tkinter Frame widget that provides simple access to python interpreter.

    Useful when there is no decent system terminal (e.g. on Windows).

    Provides status messages to any supplied msg_bar (which should be a Pmw.MessageBar).
    """
    def __init__(self,master,msg_bar=None,**config):
        Tkinter.Frame.__init__(self,master,**config)

        self.msg_bar=msg_bar
        self.balloon = Pmw.Balloon(self)

        # command interpreter for executing commands (used by exec_cmd).
        self.interpreter = code.InteractiveConsole(__main__.__dict__)
        
        ### Make a ComboBox (command_entry) for entering commands.
        self.command_entry=InterpreterComboBox(self,autoclear=1,history=1,dropdown=1,
                                               label_text='>>> ',labelpos='w',
                                               # CB: if it's a long command, the gui obviously stops responding.
                                               # On OS X, a spinning wheel appears. What about linux and win?
                                               selectioncommand=self.exec_cmd)
        
        self.balloon.bind(self.command_entry,
             """Accepts any valid Python command and executes it in main as if typed at a terminal window.""")

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        # CEBALERT: what length history is this going to keep?
        self.command_output = OutputText(self,
                                         state=DISABLED,
                                         height=10,
                                         yscrollcommand=scrollbar.set)
        self.command_output.pack(side=TOP,expand=YES,fill=BOTH)
        scrollbar.config(command=self.command_output.yview)

        self.command_entry.pack(side=BOTTOM,expand=NO,fill=X)


    def exec_cmd(self,cmd):
        """
        Pass cmd to the command interpreter.

        Redirects sys.stdout and sys.stderr to the output text window
        for the duration of the command.
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

        if self.msg_bar: self.msg_bar.message('state', result)

        self.command_entry.component('entryfield').clear()



        

class PlotsMenuEntry(ParameterizedObject):
    """
    Stores information about a Plots menu command
    (including the command itself, and the plotgroup template).
    """
    def __init__(self,console,template,class_=TemplatePlotGroupPanel,**params):
        """
        Store the template, and set the class that will be created by this menu entry

        If users want to extend the Plot Panel classes, then they
        should add entries to the plotpanel_classes dictionary.
        If no entry is defined there, then the default class is used.

        The class_ is overridden for any special cases listed in this method.
        """
        super(PlotsMenuEntry,self).__init__(**params)
        
        self.console = console
        self.template = template

        # Special cases.  These classes are specific to the topo/tkgui
        # directory and therefore this link must be made within the tkgui
        # files.
        if self.template.template_plot_type=='curve':
            class_ = plotpanel_classes.get(template.name,FeatureCurvePanel)

        self.class_ = plotpanel_classes.get(template.name,class_)
        

    def command(self,event=None,**args):
        """
        Instantiate the class_ (used as menu commands' 'command' attribute).

        Keyword args are passed to the class_.

        (event is a dummy argument to allow use in callbacks.)
        """
        # CEBHACKALERT
        if self.class_.valid_context():
            t = TkguiWindow()
            self.class_(self.console,t,self.template,**args).pack()
            self.console.messageBar.message('state', 'OK')

        else:
            self.console.messageBar.message('state',
                                            'No suitable objects in this simulation for this operation.')



class TopoConsole(TkguiWindow):
    """
    Main window for the Tk-based GUI.
    """
    def __init__(self,**config):

        TkguiWindow.__init__(self,**config)

        
    
        self.auto_refresh_panels = []
        self._init_widgets()
        self.title("Topographica Console")


        # Provide a way for other code to access the GUI when necessary
        topo.guimain=self

        # catch click on the 'x': offers choice to quit or not
        self.protocol("WM_DELETE_WINDOW",self.quit_topographica)

        
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


## CEBHACKALERT: see PO.warning() ################
        ParameterizedObject.receive_warnings.append(self)

    def warn(self,msg):
        tkMessageBox.showwarning("title",msg)
##################################################


        


    def _init_widgets(self):
        
        ## CEBALERT: now we can have multiple operations at the same time,
        ## status bar could be improved to show all tasks?

        ### Status bar
	self.messageBar = Pmw.MessageBar(self,
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
        self.__plots_menu()
        self.__help_menu()

        ### Running the simulation
        # CB: could replace with bwidget LabelFrame, if necessary
        run_frame = Tkinter.Frame(self,bd=2,relief=Tkinter.GROOVE)
        run_frame.pack(side='top',fill='x',padx=4,pady=8)
        
        Label(run_frame,text='Run for: ').pack(side=LEFT)
        
        run_for_var=StringVar()
        run_for_var.set('1.0')

        self.run_for = TaggedSlider(run_frame,
                                    variable=run_for_var,
                                    tag_width=11,
                                    slider_length=150,
                                    min_value=0,max_value=20000,
                                    string_format='%.4f')
        self.balloon.bind(self.run_for,"Duration to run the simulation, e.g. 0.0500, 1.0, or 20000.")
        self.run_for.pack(side=LEFT)

        # When return is pressed, the TaggedSlider updates itself...but we also want to run
        # the simulation in this case.
        run_frame.optional_action=self.run_simulation

        ## CEBALERT: ever tried pressing 'go' a couple of times while measuring e.g. an orientation preference map?
        ## The various parts weren't designed to operate in parallel...
        go_button = Button(run_frame,text="Go",
                           command=self.run_simulation)
        go_button.pack(side=LEFT)
        
        self.balloon.bind(go_button,"Run the simulation for the specified duration.")


	self.stop_button = Button(run_frame,text="Stop",state=DISABLED,
                                  command=lambda: self.set_stop())
	self.stop_button.pack(side=LEFT)
        self.balloon.bind(self.stop_button,"""
            Stop a running simulation.

            The simulation can be interrupted only on round integer
            simulation times, e.g. at 3.0 or 4.0 but not 3.15.  This
            ensures that stopping and restarting are safe for any
            model set up to be in a consistent state at integer
            boundaries, as the example Topographica models are.""")




    def __simulation_menu(self):
        """Add the simulation menu options to the menubar."""
        simulation_menu = Tkinter.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label='Simulation',menu=simulation_menu)

        simulation_menu.add_command(label='Run script',command=self.run_script)
        simulation_menu.add_command(label='Save script',command=self.save_script_repr)
        simulation_menu.add_command(label='Load snapshot',command=self.load_snapshot)
        simulation_menu.add_command(label='Save snapshot',command=self.save_snapshot)
        #simulation_menu.add_command(label='Reset',command=self.reset_network)
        simulation_menu.add_command(label='Test Pattern',command=self.open_test_pattern_window)
        simulation_menu.add_command(label='Model Editor',command=self.open_model_editor)
        simulation_menu.add_command(label='Command prompt',command=self.open_command_prompt)
        simulation_menu.add_command(label='Quit',command=self.quit_topographica)

        


    def __plots_menu(self):
        """
        Add the plot menu to the menubar, with Basic plots on the menu itself and
        others in cascades by category (the plots come from plotgroup_templates).
        """
        # create plots_menu_entries, and get categories
        self.plots_menu_entries=KeyedList() # keep the order of plotgroup_templates (which is also KL)
        categories = []
        for label,template in plotgroup_templates.items():
            self.plots_menu_entries[label] = PlotsMenuEntry(self,template)
            categories.append(template.category)
        categories = sorted(set(categories))

        # 'Plots' menu
        plots_menu = Tkinter.Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label='Plots',menu=plots_menu)
        
        # The Basic category items appear on the menu itself.
        assert 'Basic' in categories, "'Basic' is the category for the standard Plots menu entries."
        for label,entry in self.plots_menu_entries:
            if entry.template.category=='Basic':
                    plots_menu.add_command(label=label,command=entry.command)
        categories.remove('Basic')

        plots_menu.add_separator()
        
        # Add the other categories to the menu as cascades, and the plots of each category to
        # their cascades.
        for category in categories:
            category_menu = Tkinter.Menu(plots_menu,tearoff=0)
            plots_menu.add_cascade(label=category,menu=category_menu)

            # could probably search more efficiently than this
            # (Note about plots_menu_entries: it's accessed in 1 other place in tkgui.)
            for label,entry in self.plots_menu_entries:
                if entry.template.category==category:
                    category_menu.add_command(label=label,command=entry.command)

            
        plots_menu.add_separator()

        plots_menu.add_command(label="Help",command=(lambda x=plotting_help_locations: self.open_location(x)))


    def __help_menu(self):
        """Add the help menu options."""

        help_menu = Tkinter.Menu(self.menubar,tearoff=0,name='help')
        self.menubar.add_cascade(label='Help',menu=help_menu) 

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


    def run_script(self):
        """
        Dialog to run a user-selected script

        The script is exec'd in __main__.__dict__ (i.e. as if it were specified on the commandline.)
        """
        script = tkFileDialog.askopenfilename(filetypes=SCRIPT_FILETYPES)
        if script in ('',(),None): # (representing the various ways no script was selected in the dialog)
            self.messageBar.message('state', 'Run canceled')
        else:
            try:
                execfile(script,__main__.__dict__)
                self.messageBar.message('state', 'Ran ' + script)
            except:
                self.messageBar.message('state', 'Failed to run ' + script)
                raise # at least display the error somewhere 

        

    def save_script_repr(self):
        script_name = tkFileDialog.asksaveasfilename(filetypes=SCRIPT_FILETYPES,initialfile=topo.sim.name+"_script_repr.ty")
        if script_name:
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

        

    ### CEBHACKALERT: why doesn't updatecommand("display=True") for an orientation preference map
    ### measurement work with the hierarchical example? I guess this is the reason I thought
    ### the updating never worked properly (or I really did break it recently - or I'm confused)...
    def refresh_activity_windows(self):
        """
        Update any windows with a plotgroup_key of 'Activity'.

        Used primarily for debugging long scripts that present a lot of activity patterns.
        """
        for win in self.auto_refresh_panels:
            if win.plotgroup_label=='Activity' or win.plotgroup_label=='ProjectionActivity' :
                win.refresh()
                self.update_idletasks()


    def open_command_prompt(self):
        prompt_win = TkguiWindow()
        prompt_win.title("Topographica Command Prompt")
        CommandPrompt(prompt_win,self.messageBar).pack(expand='yes',fill='both')
        

        

    def open_model_editor(self):
        """Start the Model editor."""
	ModelEditor()



    def open_test_pattern_window(self):
        """
        Test Pattern Window.  
        """
        if TestPattern.valid_context():
            t = TkguiWindow()
            TestPattern(self,t).pack()
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


    
    def progress_window(self,progress_var,title=""):
        """
        Simplistic (& demo) progress bar in a window.

        Specify a Tkinter variable (e.g. IntVar) as progress_var and the progress
        bar will remain in sync with the value, and will disappear when the value is 100.


        For (untested!) example:

         progval = Tkinter.IntVar(self)        
         self.progress_window(progval)

         for i in range(100):
             progval.set(i)

        should give a progress meter that goes from 0 to 100 then disappears.


        ** Currently expects a 0-100 (percent) value ***        
        """
        # relies on bwidget, which nobody has built yet
        if not bwidget_imported:
            return

        # CB: could add more info to the window/bar, like time estimates...
        # (elapsed,remaining,axis label)
        
        window = TkguiWindow()
        window.title(title)

        # trace the variable so that at 100 we can destroy the window
        window.progress_trace_name = progress_var.trace_variable('w',lambda name,index,mode,x=window,y=progress_var: self.__close_progress_window_if_complete(x,y))

        progress_bar = bwidget.ProgressBar(window,type="normal",
                                           maximum=100,
                                           height=20,
                                           width=200,
                                           variable=progress_var)
        progress_bar.pack(padx=15,pady=15)


    def __close_progress_window_if_complete(self,progress_window,progress_var):
        """
        Close the specified progress window if the value of progress_var has reached 100.
        """
        if progress_var.get()>=100:
            # delete the variable trace (necessary?)
            progress_var.trace_vdelete('w',progress_window.progress_trace_name)
            progress_window.destroy()



    def run_simulation(self):
        """
        Run the simulation for the duration specified in the
        'run for' taggedslider.
        
        All this routine truly needs to do is
        topo.sim.run(self.run_for.get_value()), but it adds other useful
        features like periodically displaying the simulated and real
        time remaining.
        """

        # progress bar updates per 1.0 iteration, so it's not always
        # going to be helpful
        progval = Tkinter.IntVar(self)        
        self.progress_window(progval,title="Running Simulation")

        
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

            progval.set(percent)

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
        progval.set(100) # CB: shouldn't percent have reached 100?

        

if __name__ != '__main__':
    plotpanel_classes['Connection Fields'] = ConnectionFieldsPanel
    plotpanel_classes['Projection'] = CFProjectionPGPanel 
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
            



