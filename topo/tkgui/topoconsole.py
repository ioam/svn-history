"""
TopoConsole class file.


$Id$
"""
__version__='$Revision$'


# CB: does the status bar need to keep saying 'ok'? Sometimes
# positive feedback is useful, but 'ok' doesn't seem too helpful.


import os
import sys
import __main__
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
from topo.base.parameterclasses import resolve_filename
from topo.base.parameterizedobject import ParameterizedObject
from topo.plotting.plotgroup import plotgroups, FeatureCurvePlotGroup
from topo.misc.keyedlist import KeyedList
import topo.commands.basic

import topo.tkgui 
from widgets import TaggedSlider,ControllableMenu, CommandPrompt
from topowidgets import ScrolledTkguiWindow,TkguiWindow,ProgressWindow
from templateplotgrouppanel import TemplatePlotGroupPanel
from featurecurvepanel import FeatureCurvePanel
from projectionpanel import CFProjectionPGPanel,ProjectionActivityPanel,ConnectionFieldsPanel
from testpattern import TestPattern
from editorwindow import ModelEditor





SCRIPT_FILETYPES = [('Topographica scripts','*.ty'),
                    ('Python scripts','*.py'),
                    ('All files','*')]
SAVED_FILE_EXTENSION = '.typ'
SAVED_FILETYPES = [('Topographica saved networks',
                    '*'+SAVED_FILE_EXTENSION),
                   ('All files','*')]



# Documentation locations: locally built and web urls.
user_manual_locations      = ('doc/User_Manual/index.html',
                              'http://topographica.org/User_Manual/')
tutorials_locations        = ('doc/Tutorials/index.html',
                              'http://topographica.org/Tutorials/')
reference_manual_locations = ('doc/Reference_Manual/index.html',
                              'http://topographica.org/Reference_Manual/')
python_doc_locations = ('http://www.python.org/doc/')
topo_www_locations = ('http://www.topographica.org/')
plotting_help_locations = ('doc/User_Manual/plotting.html',
                           'http://topographica.org/User_Manual/plotting.html')

# If a particular plotgroup_template needs (or works better with) a
# specific subclass of PlotPanel, the writer of the new subclass
# or the plotgroup_template can declare here that that template
# should use a specific PlotPanel subclass.  For example:
#   plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}
# CEBALERT: why are the other plotpanel_classes updates at the end of this file?





        

class PlotsMenuEntry(ParameterizedObject):
    """
    Stores information about a Plots menu command
    (including the command itself, and the plotgroup template).
    """
    def __init__(self,console,plotgroup,class_=TemplatePlotGroupPanel,**params):
        """
        Store the template, and set the class that will be created by this menu entry

        If users want to extend the Plot Panel classes, then they
        should add entries to the plotpanel_classes dictionary.
        If no entry is defined there, then the default class is used.

        The class_ is overridden for any special cases listed in this method.
        """
        super(PlotsMenuEntry,self).__init__(**params)
        
        self.console = console
        self.plotgroup = plotgroup

        # Special cases.  These classes are specific to the topo/tkgui
        # directory and therefore this link must be made within the tkgui
        # files.
        if isinstance(self.plotgroup,FeatureCurvePlotGroup):
            class_ = plotpanel_classes.get(plotgroup.name,FeatureCurvePanel)

        self.class_ = plotpanel_classes.get(plotgroup.name,class_)
        

    def __call__(self,event=None,**args):
        """
        Instantiate the class_ (used as menu commands' 'command' attribute).

        Keyword args are passed to the class_.

        (event is a dummy argument to allow use in callbacks.)
        """
        if self.class_.valid_context():
            # window hidden while being constructed to improve appearance
            window = ScrolledTkguiWindow() ; window.withdraw()
            panel = self.class_(self.console,window.content,self.plotgroup,**args)
            panel.pack(expand='yes',fill='both')
            window.sizeright()
            window.deiconify()
            
            self.console.messageBar.message('state', 'OK')
            return panel
        else:
            self.console.messageBar.message('state',
                                            'No suitable objects in this simulation for this operation.')
        
    command = __call__        



class TopoConsole(TkguiWindow):
    """
    Main window for the Tk-based GUI.
    """

    def __getitem__(self,menu_name):
        """Allow dictionary-style access to the menu bar."""
        return self.menubar[menu_name]

    
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
	self.menubar = ControllableMenu(self)       
        self.configure(menu=self.menubar)

        self.__simulation_menu()
        self.__plots_menu()
        self.__help_menu()

        ### Running the simulation
        # CB: could replace with bwidget LabelFrame, if necessary
        run_frame = Tkinter.Frame(self,bd=2,relief=Tkinter.GROOVE)
        run_frame.pack(side='top',fill='x',padx=4,pady=8)
        
        Label(run_frame,text='Run for: ').pack(side=LEFT)
        
        self.run_for_var=Tkinter.DoubleVar()
        self.run_for_var.set(1.0)

        run_for = TaggedSlider(run_frame,
                               variable=self.run_for_var,
                               tag_width=11,
                               slider_length=150,
                               bounds=(0,20000))
        self.balloon.bind(run_for,"Duration to run the simulation, e.g. 0.0500, 1.0, or 20000.")
        run_for.pack(side=LEFT,fill='x',expand=YES)

        # When return is pressed, the TaggedSlider updates itself...but we also want to run
        # the simulation in this case.
        run_frame.optional_action=self.run_simulation

        go_button = Button(run_frame,text="Go",
                           command=self.run_simulation)
        go_button.pack(side=LEFT)
        
        self.balloon.bind(go_button,"Run the simulation for the specified duration.")

        self.step_button = Button(run_frame,text="Step",command=self.run_step)
        self.balloon.bind(self.step_button,"Run the simulation through the time at which the next events are processed.")
        self.step_button.pack(side=LEFT)


    def __simulation_menu(self):
        """Add the simulation menu options to the menubar."""
        simulation_menu = ControllableMenu(self.menubar,tearoff=0)

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
        # create menu entries, and get list of categories
        entries=KeyedList() # keep the order of plotgroup_templates (which is also KL)
        categories = []
        for label,plotgroup in plotgroups.items():
            entries[label] = PlotsMenuEntry(self,plotgroup)
            categories.append(plotgroup.category)
        categories = sorted(set(categories))

        # 'Plots' menu
        plots_menu = ControllableMenu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label='Plots',menu=plots_menu)
        
        # The Basic category items appear on the menu itself.
        assert 'Basic' in categories, "'Basic' is the category for the standard Plots menu entries."
        for label,entry in entries:
            if entry.plotgroup.category=='Basic':
                    plots_menu.add_command(label=label,command=entry.command)
        categories.remove('Basic')

        plots_menu.add_separator()
        
        # Add the other categories to the menu as cascades, and the plots of each category to
        # their cascades.
        for category in categories:
            category_menu = ControllableMenu(plots_menu,tearoff=0)
            plots_menu.add_cascade(label=category,menu=category_menu)

            # could probably search more efficiently than this
            for label,entry in entries:
                if entry.plotgroup.category==category:
                    category_menu.add_command(label=label,command=entry.command)

            
        plots_menu.add_separator()

        plots_menu.add_command(label="Help",command=(lambda x=plotting_help_locations: self.open_location(x)))


    def __help_menu(self):
        """Add the help menu options."""

        help_menu = ControllableMenu(self.menubar,tearoff=0,name='help')
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



            
    def quit_topographica(self,check=True):
        """Quit topographica."""
        if not check or (check and tkMessageBox.askyesno("Quit Topographica","Really quit?")):
            self.destroy() 
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
        script_name = tkFileDialog.asksaveasfilename(filetypes=SCRIPT_FILETYPES,initialfile=topo.sim.basename()+"_script_repr.ty")
        
        if script_name:
            topo.commands.basic.save_script_repr(script_name)
            self.messageBar.message('state', 'Script saved to ' + script_name)
            
    
    def load_snapshot(self):
        """
        Dialog to load a user-selected snapshot (see topo.commands.basic.load_snapshot() ).
        """
        snapshot_name = tkFileDialog.askopenfilename(filetypes=SAVED_FILETYPES,initialdir="examples")

        if snapshot_name in ('',(),None):
            self.messageBar.message('state','No snapshot loaded.')
        else:
            self.messageBar.message('state', 'Loading snapshot (may take some time)...')
            self.update_idletasks()            
            topo.commands.basic.load_snapshot(snapshot_name)
            self.messageBar.message('state', 'Loaded snapshot ' + snapshot_name)

        self.auto_refresh()


    def save_snapshot(self):
        """
        Dialog to save a snapshot (see topo.commands.basic.save_snapshot() ).
        
        Adds the file extension .typ if not already present.
        """
        snapshot_name = tkFileDialog.asksaveasfilename(filetypes=SAVED_FILETYPES,
            initialfile=topo.sim.basename()+".typ")
        
        if snapshot_name in ('',(),None):
            self.messageBar.message('state','No snapshot saved.')
        else:
            if not snapshot_name.endswith('.typ'):
                snapshot_name = snapshot_name + SAVED_FILE_EXTENSION
                
            self.messageBar.message('state', 'Saving snapshot (may take some time)...')
            self.update_idletasks()            
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

        self.set_step_button_state()
        self.update_idletasks()

        

    ### CEBERRORALERT: why doesn't updatecommand("display=True") for an
    ### orientation preference map measurement work with the
    ### hierarchical example? I guess this is the reason I thought the
    ### updating never worked properly (or I really did break it
    ### recently - or I'm confused)...
    def refresh_activity_windows(self):
        """
        Update any windows with a plotgroup_key of 'Activity'.

        Used primarily for debugging long scripts that present a lot of activity patterns.
        """
        for win in self.auto_refresh_panels:
            if win.plotgroup.name=='Activity' or win.plotgroup.name=='ProjectionActivity' :
                win.refresh()
                self.update_idletasks()


    def open_command_prompt(self):
        prompt_win = TkguiWindow()
        prompt_win.title("Topographica Command Prompt")
        CommandPrompt(prompt_win,self.messageBar).pack(expand='yes',fill='both')
        

        

    def open_model_editor(self):
        """Start the Model editor."""
	return ModelEditor()




    def open_test_pattern_window(self):
        """
        Test Pattern Window.  
        """
        if TestPattern.valid_context():
            window = ScrolledTkguiWindow() ; window.withdraw()
            panel = TestPattern(self,window.content)
            panel.pack(expand='yes',fill='both')
            window.sizeright()
            window.deiconify()


            self.messageBar.message('state', 'OK')
            return panel
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
            # a path on the disk might need converting
            try:
                location = resolve_filename(location)
            except:
                pass
            
            try:
                webbrowser.open(location,new=True,autoraise=True)
                self.messageBar.message('state', 'Opened '+location+' in browser.')
                return
            # Since one of the possible exceptions when opening a
            # browser appears to be a 'WindowsError' (at least on the
            # Windows platform), just catch all exceptions.
            except:
                self.messageBar.message('state', "Couldn't open "+location+" in browser.")


    # CEBALERT: need to take care of removing old messages automatically?
    # (Otherwise callers might always have to pass 'ok'.)
    def status_message(self,m):
        self.messageBar.message('state',m)



    # CEB: Will add a method to allow other things to access the
    # timing stuff (e.g. progress bar) in a simple way. (Also
    # this class will use the method). Probably will add support
    # for multiple things getting timed.

    
    def run_simulation(self):
        """
        Run the simulation for the duration specified in the
        'run for' taggedslider.        
        """
        self.title(topo.sim.name) # ALERT: Temporary

        fduration = self.run_for_var.get()

        # CB: clean up (+ docstring)
        if fduration>9:
            display_progress=True
        else:
            display_progress=False

        ProgressWindow(display=display_progress)
        topo.sim.run_and_time(fduration)
        self.auto_refresh()
        
    def run_step(self):

        if not topo.sim.events:
            # JP: step button should be disabled if there are no events,
            # but just in case...
            return

        # JPALERT: This should really use .run_and_time() but it doesn't support
        # run(until=...)
        topo.sim.run(until=topo.sim.events[0].time)
        self.auto_refresh()

    def set_step_button_state(self):
        if topo.sim.events:
            self.step_button.config(state=NORMAL)
        else:
            self.step_button.config(state=DISABLED)


    def open_progress_window(self,timer,title=None):
        """
        Provide a convenient link to progress bars.
        """
        return ProgressWindow(timer=timer,title=title)






        
if __name__ != '__main__':
    plotpanel_classes['Connection Fields'] = ConnectionFieldsPanel
    plotpanel_classes['Projection'] = CFProjectionPGPanel 
    plotpanel_classes['Projection Activity'] = ProjectionActivityPanel




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
            



