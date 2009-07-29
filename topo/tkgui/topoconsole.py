"""
TopoConsole class file.


$Id$
"""
__version__='$Revision$'


# CB: does the status bar need to keep saying 'ok'? Sometimes
# positive feedback is useful, but 'ok' doesn't seem too helpful.


import os
import copy
import sys
import __main__
import webbrowser

from inspect import getdoc

from Tkinter import Frame, StringVar, X, BOTTOM, TOP, Button, \
     LEFT, RIGHT, YES, NO, BOTH, Label, Text, END, DISABLED, \
     NORMAL, Scrollbar, Y, DoubleVar, Widget,Toplevel
from tkFileDialog import asksaveasfilename,askopenfilename

from .. import param
from ..param import tk
from ..param.external import Notebook

import topo
from topo.plotting.plotgroup import plotgroups, FeatureCurvePlotGroup
from topo.misc.keyedlist import KeyedList
from topo.misc.filepath import resolve_path,normalize_path
from topo.misc.commandline import sim_name_from_filename
import topo.command.basic

import topo.tkgui 

from templateplotgrouppanel import TemplatePlotGroupPanel
from featurecurvepanel import FeatureCurvePanel
from projectionpanel import CFProjectionPanel,ProjectionActivityPanel,ConnectionFieldsPanel,RFProjectionPanel
from testpattern import TestPattern
from editor import ModelEditor


tk.AppWindow.window_icon_path = resolve_path('tkgui/icons/topo.xbm')

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
python_doc_locations = ('http://www.python.org/doc/',)
topo_www_locations = ('http://www.topographica.org/',)
plotting_help_locations = ('doc/User_Manual/plotting.html',
                           'http://topographica.org/User_Manual/plotting.html')

# If a particular plotgroup_template needs (or works better with) a
# specific subclass of PlotPanel, the writer of the new subclass
# or the plotgroup_template can declare here that that template
# should use a specific PlotPanel subclass.  For example:
#   plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}
# CEBALERT: why are the other plotpanel_classes updates at the end of this file?





def open_plotgroup_panel(class_,plotgroup=None,**kw):

    if class_.valid_context():
        win = topo.guimain.some_area.new_window()
        panel = class_(win,plotgroup=plotgroup,**kw)

        if not panel.dock:
            topo.guimain.some_area.eject(win)
        else:
            topo.guimain.some_area.consume(win)

        panel.refresh_title()

        panel.pack(expand='yes',fill='both')
        win.sizeright()
        
        #frame.sizeright()
        
        topo.guimain.messageBar.message('state', 'OK')
        return panel
    else:
        topo.guimain.messageBar.message(
            'state',
            'No suitable objects in this simulation for this operation.')



        

class PlotsMenuEntry(param.Parameterized):
    """
    Stores information about a Plots menu command
    (including the command itself, and the plotgroup template).
    """
    def __init__(self,plotgroup,class_=TemplatePlotGroupPanel,**params):
        """
        Store the template, and set the class that will be created by this menu entry

        If users want to extend the Plot Panel classes, then they
        should add entries to the plotpanel_classes dictionary.
        If no entry is defined there, then the default class is used.

        The class_ is overridden for any special cases listed in this method.
        """
        super(PlotsMenuEntry,self).__init__(**params)

        self.plotgroup = plotgroup

        # Special cases.  These classes are specific to the topo/tkgui
        # directory and therefore this link must be made within the tkgui
        # files.
        if isinstance(self.plotgroup,FeatureCurvePlotGroup):
            class_ = plotpanel_classes.get(self.plotgroup.name,FeatureCurvePanel)

        self.class_ = plotpanel_classes.get(self.plotgroup.name,class_)
        

    def __call__(self,event=None,**kw):
        """
        Instantiate the class_ (used as menu commands' 'command' attribute).

        Keyword args are passed to the class_.
        """
        new_plotgroup = copy.deepcopy(self.plotgroup)

        # CB: hack to share plot_templates with the current
        # plotgroup in plotgroups
        new_plotgroup.plot_templates = topo.plotting.plotgroup.plotgroups[self.plotgroup.name].plot_templates

        return open_plotgroup_panel(self.class_,new_plotgroup,**kw)


class DockManager(Notebook):
    """Manages windows that can be tabs in a notebook, or toplevels."""
    def __init__(self, master=None, cnf={}, **kw):
        Notebook.__init__(self, master, cnf=cnf, **kw)
        self._tab_ids = {}

    def _set_tab_title(self,win,title):
        self.tab(self._tab_ids[win],text=title)

    def _set_toplevel_title(self,win,title):
        prefix = topo.sim.name+": "
        if not title.startswith(prefix):
            title=prefix+title
        self.tk.call("wm","title",win._w,title)

    def add(self, child, cnf={}, **kw):
        self._tab_ids[child]=len(self.tabs())
        Notebook.add(self,child,cnf=cnf,**kw)

##     def unhide(self,win):
##         if win in self._tab_ids:
##             self.tab(self._tab_ids[win],state='normal')

    def new_window(self):
        win = tk.AppWindow(self,status=True)
        #self.consume(win)
        return win

    def consume(self,win):
        if win not in self._tab_ids:
            self.tk.call('wm','forget',win._w)
            win.title = lambda x: self._set_tab_title(win,x)
            self.add(win)
        
    def eject(self,win):
        if win in self._tab_ids:
            self.forget(self._tab_ids[win])

            # manage my tab ids (HACK)
            del self._tab_ids[win]
            for w in self._tab_ids:
                self._tab_ids[w]-=1
                self._tab_ids[w]=max(self._tab_ids[w],0)
                
            self.tk.call('wm','manage',win._w)
            win.renew()
            win.title = lambda x: self._set_toplevel_title(win,x)
            return win




try:
    import ipythonTk
    ipythonTk_imported = True
except:
    ipythonTk_imported = False

if ipythonTk_imported:
    from ipythonTk.ipythonTk import IPythonView
    class IPythonInAFrame(Frame):
        def __init__(self, root, banner=None, user_ns=None,**kw):
            Frame.__init__(self,root)

            yscroll = Scrollbar(self)
            yscroll.pack(side='right',fill='y')

            console = IPythonView(self,user_ns=user_ns)
            console.pack(fill='both',expand=1)

            console.config(yscrollcommand=yscroll.set)
            yscroll.config(command=console.yview)





class TopoConsole(tk.AppWindow,tk.TkParameterized):
    """
    Main window for the Tk-based GUI.
    """

    def _getmenubar(self):
        return self.master.menubar

    menubar = property(_getmenubar)

    def __getitem__(self,menu_name):
        """Allow dictionary-style access to the menu bar."""
        return self.menubar[menu_name]

    def __init__(self,root,console=False,**params):

        tk.AppWindow.__init__(self,root,status=True)
        tk.TkParameterized.__init__(self,root,**params)

        #CBALERT
        self._rooot=root

        self.auto_refresh_panels = []
        self._init_widgets(console)
        self.title(topo.sim.name) # If -g passed *before* scripts on commandline, this is useless.
                                  # So topo.misc.commandline sets the title as its last action (if -g)



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

    def title(self,t=None):
        newtitle = "Topographica"
        if t: newtitle+=": %s" % t
        tk.AppWindow.title(self,newtitle)
        

    def _init_widgets(self,console):
        
        ## CEBALERT: now we can have multiple operations at the same time,
        ## status bar could be improved to show all tasks?

        # CEBALERT
        self.messageBar = self.status

        self.some_area = DockManager(self)
        self.some_area.pack(fill="both", expand=1)

        ### Balloon, for pop-up help
        self.balloon = tk.Balloon(self.content)

        ### Top-level (native) menu bar
        #self.menubar = tk.ControllableMenu(self.content)       
        self.configure(menu=self.menubar)

        #self.menu_balloon = Balloon(topo.tkgui.root)

        # no menubar in tile yet
        # http://news.hping.org/comp.lang.tcl.archive/4679.html

        self.__simulation_menu()
        self.__create_plots_menu()
        self.refresh_plots_menu()
        self.__help_menu()

        
        ### Running the simulation
        run_frame = Frame(self.content)
        run_frame.pack(side='top',fill='x',padx=4,pady=8)

        self.run_frame = run_frame
        
        Label(run_frame,text='Run for: ').pack(side=LEFT)
        
        self.run_for_var=DoubleVar()
        self.run_for_var.set(1.0)

        run_for = tk.TaggedSlider(run_frame,
                               variable=self.run_for_var,
                               tag_width=11,
                               slider_length=150,
                               bounds=(0,20000))
        self.balloon.bind(run_for,"Duration to run the simulation, e.g. 0.0500, 1.0, or 20000.")
        run_for.pack(side=LEFT,fill='x',expand=YES)
        run_for.tag.bind("<Return>",self.run_simulation)

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

        # CEBALERT: total hack
        if console and ipythonTk_imported:
            self.console_frame = Frame(self)
            self.console_frame.pack(expand=1,fill='both')

            import topo.tkgui.plotgrouppanel
            topo.tkgui.plotgrouppanel.PlotGroupPanel.dock=True

            import __main__
            self.console = IPythonInAFrame(self,self._rooot,
                                           user_ns=__main__.__dict__)
            self.console.pack(expand=1,fill='both')

        
        self.sizeright()


    def __simulation_menu(self):
        """Add the simulation menu options to the menubar."""
        simulation_menu = ControllableMenu(self.menubar,tearoff=0)

        self.menubar.add_cascade(label='Simulation',menu=simulation_menu)

        simulation_menu.add_command(label='Run script',command=self.run_script)
        simulation_menu.add_command(label='Save script',command=self.save_script_repr)
        simulation_menu.add_command(label='Load snapshot',command=self.load_snapshot)
        simulation_menu.add_command(label='Save snapshot',command=self.save_snapshot)
        #simulation_menu.add_command(label='Reset',command=self.reset_network)
        simulation_menu.add_command(label='Test Pattern',command=self.open_test_pattern)

        simulation_menu.add_command(label='Model Editor',command=self.open_model_editor)
        simulation_menu.add_command(label='Quit',command=self.quit_topographica)

        

    def open_test_pattern(self):
        return open_plotgroup_panel(TestPattern)


    
    


    def __create_plots_menu(self):
        """
        Add the plot menu to the menubar, with Basic plots on the menu itself and
        others in cascades by category (the plots come from plotgroup_templates).
        """
        plots_menu = ControllableMenu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label='Plots',menu=plots_menu)
        

    # CEBALERT: should split other menus in same way as plots (create/refresh)
    def refresh_plots_menu(self):
        plots_menu = self['Plots']
        plots_menu.delete(0,'end')

        # create menu entries, and get list of categories
        entries=KeyedList() # keep the order of plotgroup_templates (which is also KL)
        categories = []
        for label,plotgroup in plotgroups.items():
            entries[label] = PlotsMenuEntry(plotgroup)
            categories.append(plotgroup.category)
        categories = sorted(set(categories))

        
        # The Basic category items appear on the menu itself.
        assert 'Basic' in categories, "'Basic' is the category for the standard Plots menu entries."
        for label,entry in entries:
            if entry.plotgroup.category=='Basic':
                    plots_menu.add_command(label=label,command=entry.__call__)
                    
        categories.remove('Basic')

        plots_menu.add_separator()
        
        # Add the other categories to the menu as cascades, and the plots of each category to
        # their cascades.
        for category in categories:
            category_menu = ControllableMenu(plots_menu,tearoff=0)
            plots_menu.add_cascade(label=category,menu=category_menu)

            # could probably search more efficiently than this
            for label,entry in sorted(entries):
                if entry.plotgroup.category==category:
                    category_menu.add_command(label=label,command=entry.__call__)

            
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



            
    def quit_topographica(self,check=True,exit_status=0):
        """Quit topographica."""
        if not check or (check and tk.askyesno("Quit Topographica","Really quit?")):
            self.destroy() 

            # matplotlib's tk backend starts its own Tk instances; we
            # need to close these ourselves (at least to avoid error
            # message about 'unusual termination' in Windows).
            try: # not that there should be an error, but just in case...
                import matplotlib._pylab_helpers
                for figman in matplotlib._pylab_helpers.Gcf.get_all_fig_managers():
                    figman.destroy()
            except:
                pass
                
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
            if topo.tkgui.system_platform=="linux" and os.getenv('EMACS')!='t':
                try: os.system("stty sane")
                except: pass
                
            sys.exit(exit_status)


    def run_script(self):
        """
        Dialog to run a user-selected script

        The script is exec'd in __main__.__dict__ (i.e. as if it were specified on the commandline.)
        """
        script = askopenfilename(filetypes=SCRIPT_FILETYPES)
        if script in ('',(),None): # (representing the various ways no script was selected in the dialog)
            self.messageBar.message('state', 'Run canceled')
        else:
            try:
                execfile(script,__main__.__dict__)
                self.messageBar.message('state', 'Ran ' + script)
                sim_name_from_filename(script)
                self.title(topo.sim.name)
            except:
                self.messageBar.message('state', 'Failed to run ' + script)
                raise # at least display the error somewhere 

        

    def save_script_repr(self):
        script_name = asksaveasfilename(filetypes=SCRIPT_FILETYPES,
                                        initialdir=normalize_path(),
                                        initialfile=topo.sim.basename()+"_script_repr.ty")
        
        if script_name:
            topo.command.basic.save_script_repr(script_name)
            self.messageBar.message('state', 'Script saved to ' + script_name)
            
    
    def load_snapshot(self):
        """
        Dialog to load a user-selected snapshot (see topo.command.basic.load_snapshot() ).
        """
        snapshot_name = askopenfilename(filetypes=SAVED_FILETYPES)

        if snapshot_name in ('',(),None):
            self.messageBar.message('state','No snapshot loaded.')
        else:
            self.messageBar.message('state', 'Loading snapshot (may take some time)...')
            self.update_idletasks()            
            topo.command.basic.load_snapshot(snapshot_name)
            self.messageBar.message('state', 'Loaded snapshot ' + snapshot_name)
            self.title(topo.sim.name)

        self.auto_refresh()


    def save_snapshot(self):
        """
        Dialog to save a snapshot (see topo.command.basic.save_snapshot() ).
        
        Adds the file extension .typ if not already present.
        """
        snapshot_name = asksaveasfilename(filetypes=SAVED_FILETYPES,
                                          initialdir=normalize_path(),
                                          initialfile=topo.sim.basename()+".typ")
        
        if snapshot_name in ('',(),None):
            self.messageBar.message('state','No snapshot saved.')
        else:
            if not snapshot_name.endswith('.typ'):
                snapshot_name = snapshot_name + SAVED_FILE_EXTENSION
                
            self.messageBar.message('state', 'Saving snapshot (may take some time)...')
            self.update_idletasks()            
            topo.command.basic.save_snapshot(snapshot_name)
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


        

    def open_model_editor(self):
        """Start the Model editor."""
        return ModelEditor(self)




    def new_about_window(self):
        win = tk.AppWindow(self)
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
                location = resolve_path(location)
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

    
    def run_simulation(self,event=None): # event=None allows use as callback
        """
        Run the simulation for the duration specified in the
        'run for' taggedslider.        
        """
        fduration = self.run_for_var.get()

        # CB: clean up (+ docstring)
        if fduration>9:
            ProgressWindow(self)
        else:
            ProgressController()
            
        topo.sim.run_and_time(fduration)
        self.auto_refresh()


    # CEBERRORALERT: Step button does strange things at time==0.
    # E.g. for lissom_oo_or, nothing appears to happen. For
    # hierarchical, runs to time==10.
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
        return ProgressWindow(self,timer=timer,title=title)







# CEBALERT: of course dictionary access is used as an alternative to
# the config method or whatever it's called! So this could cause
# serious confusion to someone trying to set config options using the
# dictionary style access rather than .config()! Either document
# clearly or abandon, and get() and set() to access menu entries by
# name.
class ControllableMenu(tk.Menu):
    """
    A Menu, but where entries are accessible by name (using
    dictionary-style access).

    ** Not truly compatible with Tkinter; work in progress **
    """
    def __getitem__(self,name):
        return self.named_commands[name]


# CB: temporary - will later be able to import from Tile
class Progressbar(Widget):
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, "ttk::progressbar", cnf, kw)
        
    def step(self, amount=1.0):
        """Increments the -value by amount. amount defaults to 1.0 
        if omitted. """
        return self.tk.call(self._w, "step", amount)
        
    def start(self):
        self.tk.call("ttk::progressbar::start", self._w)
        
    def stop(self):
        self.tk.call("ttk::progressbar::stop", self._w)




######################################################################
######################################################################
# CEB: working here - not finished
# (needs to become tkparameterizedobject, so we can have some parameters
#  to control formatting etc)
# Split up to solve a problem on windows for release 0.9.4.
# Wait until we've decided what to do with SomeTimer before recoding.
class ProgressController(object):
    def __init__(self,timer=None,progress_var=None):

        self.timer = timer or topo.sim.timer
        self.timer.receive_info.append(self.timing_info)

        self.progress_var = progress_var or DoubleVar()
        # trace the variable so that at 100 we can destroy the window
        self.progress_trace_name = self.progress_var.trace_variable(
            'w',lambda name,index,mode: self._close_if_complete())


    def _close_if_complete(self):
        """
        Close the specified progress window if the value of progress_var has reached 100.
        """
        if self.progress_var.get()>=100:
            # delete the variable trace (necessary?)
            self.progress_var.trace_vdelete('w',self.progress_trace_name)

            self._close(last_message="Time %s: Finished %s"%(topo.sim.timestr(),
                                                             self.timer.func.__name__))
            
    # CB: should allow interruption of whatever process it's timing
    def _close(self,last_message=None):
        self.timer.receive_info.remove(self.timing_info)
        if last_message: topo.guimain.status_message(last_message)

    def timing_info(self,time,percent,name,duration,remaining):
        self.progress_var.set(percent)

    # CB: should allow interruption of whatever process it's timing
    def set_stop(self):
        """Declare that running should be interrupted."""
        self.timer.stop=True
        last_message = "Time %s: Interrupted %s"%(topo.sim.timestr(),
                                                  self.timer.func.__name__)
        self._close(last_message)


class ProgressWindow(ProgressController,tk.AppWindow):
    """
    Graphically displays progress information for a SomeTimer object.
    
    ** Currently expects a 0-100 (percent) value ***        
    """

    def __init__(self,parent,timer=None,progress_var=None,title=None):
        ProgressController.__init__(self,timer,progress_var)
        tk.AppWindow.__init__(self,parent)

        self.protocol("WM_DELETE_WINDOW",self.set_stop)
        name = title or topo.sim.name
        self.title((name+": " if name else "") + self.timer.func.__name__)
        
        self.balloon = tk.Balloon(self)

        progress_bar = Progressbar(self,#type="normal",
                                   #maximum=100,height=20,width=200,
                                   variable=self.progress_var)
        progress_bar.pack(padx=15,pady=15)

        progress_box = Frame(self,border=2,relief="sunken")
        progress_box.pack()

        Label(progress_box,text="Duration:").grid(row=0,column=0,sticky='w')
        self.duration = Label(progress_box)
        self.duration.grid(row=0,column=1,sticky='w')

        Label(progress_box,text="Simulation time:").grid(row=1,column=0,sticky='w')
        self.sim_time = Label(progress_box)
        self.sim_time.grid(row=1,column=1,sticky='w')

        # Should say 'at current rate', since the calculation assumes linearity
        Label(progress_box,text="Remaining time:").grid(row=2,column=0,sticky='w')
        self.remaining = Label(progress_box)
        self.remaining.grid(row=2,column=1,sticky='w')
        
        
        stop_button = Button(self,text="Stop",command=self.set_stop)
        stop_button.pack(side="bottom")
        self.balloon.bind(stop_button,"""
        Stop a running simulation.
            
        The simulation can be interrupted only on round integer
        simulation times, e.g. at 3.0 or 4.0 but not 3.15.  This
        ensures that stopping and restarting are safe for any
        model set up to be in a consistent state at integer
        boundaries, as the example Topographica models are.""")
            
        
    def _close(self,last_message=None):
        ProgressController._close(self,last_message)
        tk.AppWindow.destroy(self)
        self.destroyed=True

    def timing_info(self,time,percent,name,duration,remaining):
        ProgressController.timing_info(self,time,percent,name,duration,remaining)
        
        # hack because i'm doing something in the wrong order
        if not hasattr(self,'destroyed'):
            self.duration['text'] = str(duration)
            self.sim_time['text'] = str(time)
            self.remaining['text'] = "%02d:%02d"%(int(remaining/60),int(remaining%60))
            self.update()
######################################################################
######################################################################








        
if __name__ != '__main__':
    plotpanel_classes['Connection Fields'] = ConnectionFieldsPanel
    plotpanel_classes['RF Projection'] = RFProjectionPanel
    plotpanel_classes['Projection'] = CFProjectionPanel 
    plotpanel_classes['Projection Activity'] = ProjectionActivityPanel






