"""
Collection of widgets designed to interact with components of
Topographica.

$Id$
"""
__version__='$Revision$'


# CEBALERT: we can clean up some of these and then move them to
# widgets.py (i.e. some are not really tied to topographica). We can
# probably move the remaining classes elsewhere, and then remove this
# file.

import Tkinter
import operator

import Pmw
import bwidget

from topo.misc.filepaths import resolve_path
import topo.tkgui
from widgets import ResizableScrollableFrame




######################################################################            
######################################################################
# CB: Working here; *TkguiWindows need significant cleanup.
# Merge TkguiWindow and ScrolledTkguiWindow because scrollbars are automatic now.
# Clearly separate ResizableScrollableFrame.
class TkguiWindow(Tkinter.Toplevel):
    """
    The standard tkgui window; defines attributes common to tkgui windows.

    Currently these attributes are:
     - a window icon
    """
    def __init__(self,**config):
        Tkinter.Toplevel.__init__(self,**config)

        # CEBALERT: doesn't work on OS X, and is a strange color on
        # Windows.  To get a proper icon on OS X, we probably have to
        # bundle into an application package or something like that.
        # On OS X, could possibly alter the small titlebar icon with something like:
        # self.attributes("-titlepath","/Users/x/topographica/AppIcon.icns")
        self.iconbitmap('@'+(resolve_path('topo/tkgui/icons/topo.xbm')))

        ### Universal right-click menu
        # CB: not currently used by anything but the plotgrouppanels
        # self.context_menu = Tkinter.Menu(self, tearoff=0)
        # self.bind("<<right-click>>",self.display_context_menu)


class ScrolledTkguiWindow(TkguiWindow):
    """
    A TkguiWindow with automatic scrollbars.
    """
    def __init__(self,**config):
        TkguiWindow.__init__(self,**config)
                
        self.maxsize(self.winfo_screenwidth(),self.winfo_screenheight())
        self._scroll_frame = ResizableScrollableFrame(self,borderwidth=2,
                                                       relief="flat")
        self._scroll_frame.pack(expand="yes",fill="both")
        self.bind("<<SizeRight>>",self._scroll_frame.sizeright)
        self.bind("<Configure>",self._scroll_frame.barz)
        
        self.content = self._scroll_frame.contents

        # provide route to title() method for convenience
        self.content.title = self.title
######################################################################
######################################################################            





    

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

        self.progress_var = progress_var or Tkinter.DoubleVar()
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


class ProgressWindow(ProgressController,TkguiWindow):
    """
    Graphically displays progress information for a SomeTimer object.
    
    ** Currently expects a 0-100 (percent) value ***        
    """

    def __init__(self,timer=None,progress_var=None,title=None):
        ProgressController.__init__(self,timer,progress_var)
        TkguiWindow.__init__(self)

        self.protocol("WM_DELETE_WINDOW",self.set_stop)
        self.title(title or self.timer.func.__name__.capitalize())
        self.balloon = Pmw.Balloon(self)

        progress_bar = bwidget.ProgressBar(self,type="normal",
                                           maximum=100,height=20,width=200,
                                           variable=self.progress_var)
        progress_bar.pack(padx=15,pady=15)

        progress_box = Tkinter.Frame(self,border=2,relief="sunken")
        progress_box.pack()

        Tkinter.Label(progress_box,text="Duration:").grid(row=0,column=0,sticky='w')
        self.duration = Tkinter.Label(progress_box)
        self.duration.grid(row=0,column=1,sticky='w')

        Tkinter.Label(progress_box,text="Simulation time:").grid(row=1,column=0,sticky='w')
        self.sim_time = Tkinter.Label(progress_box)
        self.sim_time.grid(row=1,column=1,sticky='w')

        # Should say 'at current rate', since the calculation assumes linearity
        Tkinter.Label(progress_box,text="Remaining time:").grid(row=2,column=0,sticky='w')
        self.remaining = Tkinter.Label(progress_box)
        self.remaining.grid(row=2,column=1,sticky='w')
        
        
        stop_button = Tkinter.Button(self,text="Stop",command=self.set_stop)
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
        TkguiWindow.destroy(self)
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


# CEBALERT: entry background color hack.
# How to get the standard Frame background on all platforms?
from widgets import system_platform
entry_background = '#d9d9d9'
if system_platform=='mac':
    entry_background = 'SystemWindowBody'
elif system_platform=='win':
    entry_background = 'SystemWindow'
    
