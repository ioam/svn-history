"""
Collection of widgets designed to interact with components of
Topographica.

$Id$
"""
__version__='$Revision$'


# CEBALERT: could be possible to clean up some of these and then move
# them to widgets.py (i.e. some are not really tied to
# topographica). We can probably move the remaining classes elsewhere,
# and then remove this file.

import Tkinter
import operator

import Pmw
import bwidget

from topo.misc.filepaths import resolve_path
import topo.tkgui
from widgets import TaggedSlider, ResizableScrollableFrame

######################################################################
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

######################################################################


######################################################################
# CB: needs significant cleanup. Some methods will move to
# the resizable frame. 
# Also see current task list.
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
        self.content = self._scroll_frame.contents

        # provide route to title() method for convenience
        self.content.title = self.title

        
# The ScrolledTkguiWindow receives 100s of <Configure> events in a
# short time when a button like "Enlarge" is pressed.  I *guess* this
# is because there are lots of widgets in the window, and each time
# some <Configure> event is generated for a certain one of them,
# pack() goes through all the widgets, which generates a <Configure>
# for each. In turn, each of those <Configure> events goes up to this
# window, generating a <Configure> from it each time. So there's a
# whole slew of <Configure> events.
# 
# We do *not* want to call sizeright() for every <Configure> event,
# because it would be too expensive. So the code below schedules
# delayed_sizeright() to be called a time t after a <Configure> event;
# delayed_sizeright() in turn only calls sizeright() if the time
# since the last <Configure> is (about) the same as t.
        self.bind("<Configure>",self.handle_configure_event)

    def handle_configure_event(self,e=None):
        self.after_idle(self.sizeright)
        #return ""    

    def _need_bars(self):
        sw = self._scroll_frame._scrolled_window
        c = self.content
        need_x,need_y = False,False
        if sw.winfo_width()<c.winfo_reqwidth() and \
               abs(sw.winfo_width()-c.winfo_reqwidth())>1: 
            need_x=True
        if sw.winfo_height()<c.winfo_reqheight() and \
               abs(sw.winfo_height()-c.winfo_reqheight())>1:
            need_y=True
        return need_x,need_y

    def _which_scrollbars(self):
        need_x,need_y = self._need_bars()
        if need_x and need_y:
            scrollbar = 'both'
        elif need_x and not need_y:
            scrollbar = 'horizontal'
        elif not need_x and need_y:
            scrollbar = 'vertical'
        elif not need_x and not need_y:
            scrollbar = 'none'
        return scrollbar

    def sizeright(self):
        # if user has changed window size, need to tell tkinter that it should take
        # control again.
        self.geometry('')

        # Extra for width of scrollbars; should be found programmatically. But how?
        extraw = 19
        extrah = 19

        w = min(self.content.winfo_reqwidth(),self.winfo_screenwidth())
        # -60 for task bars etc on screen...how to find true viewable height?
        h = min(self.content.winfo_reqheight(),self.winfo_screenheight()-60)

        if not hasattr(self,'oldsize') or self.oldsize!=(w,h):
            self._scroll_frame.set_size(w,h)
            self.oldsize = (w,h)
            scrollbars = self._which_scrollbars()
            self._scroll_frame._scrolled_window.config(scrollbar=scrollbars)

            if scrollbars!="none": 
                w+=extraw
                h+=extrah
                
            self._scroll_frame.set_size(w,h)
            self.oldsize = (w,h)
        else:
            self._scroll_frame._scrolled_window.config(scrollbar=self._which_scrollbars())
        

######################################################################            


# CB: haven't decided what to do. Might be temporary.
class TkPOTaggedSlider(TaggedSlider):
    """
    A TaggedSlider with extra features for use with
    TkParameterizedObjects.
    
    Adds extra ability to set slider when e.g. a variable
    name is in the tag.
    """
    def _try_to_set_slider_resolution(self):
        if not TaggedSlider._try_to_set_slider_resolution(self):
            # get the actual value as set on
            # the object (which might be the "last good" value)
            try:
                self._set_slider_resolution(self.variable._true_val())
            except: # probably tclerror
                pass


    def _try_to_set_slider(self):
        if not TaggedSlider._try_to_set_slider(self):
            v = self.variable._true_val()

            if operator.isNumberType(v):
                self.set_slider_bounds(min(self.bounds[0],v),
                                       max(self.bounds[1],v))
                self.slider.set(v)

    
    def refresh(self):
        """Could anything survive in tkgui without a refresh() method?"""
        self.tag_set()



    

######################################################################
        




# CEB: working here; this is *not* finished
# (needs to become tkparameterizedobject, so we can have some parameters
#  to control formatting etc)
class ProgressWindow(TkguiWindow):
    """
    Graphically displays progress information for a SomeTimer object.
    
    ** Currently expects a 0-100 (percent) value ***        
    """

    def __init__(self,timer=None,progress_var=None,title=None,display=True,**config):
        TkguiWindow.__init__(self,**config)

        self.protocol("WM_DELETE_WINDOW",self.set_stop)

        if not display:self.withdraw()
        
        self.timer = timer or topo.sim.timer
        self.timer.receive_info.append(self.timing_info)
        
        self.title(title or self.timer.func.__name__.capitalize())
        self.balloon = Pmw.Balloon(self)

        self.progress_var = progress_var or Tkinter.DoubleVar()
        # trace the variable so that at 100 we can destroy the window
        self.progress_trace_name = self.progress_var.trace_variable(
            'w',lambda name,index,mode: self._close_if_complete())

        progress_bar = bwidget.ProgressBar(self,type="normal",
                                           maximum=100,
                                           height=20,
                                           width=200,
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

    def _close_if_complete(self):
        """
        Close the specified progress window if the value of progress_var has reached 100.
        """
        if self.progress_var.get()>=100:
            # delete the variable trace (necessary?)
            self.progress_var.trace_vdelete('w',self.progress_trace_name)

            self._close_window(last_message="Time %s: Finished %s"%(topo.sim.timestr(),
                                                                    self.timer.func.__name__))
                                                        

    # CB: should allow interruption of whatever process it's timing
    def set_stop(self):
        """Declare that running should be interrupted."""
        self.timer.stop=True
        self._close_window(last_message="Interrupted %s"%self.timer.func.__name__)
        
    def _close_window(self,last_message=None):
        self.timer.receive_info.remove(self.timing_info)
        if last_message: topo.guimain.status_message(last_message)
        TkguiWindow.destroy(self)
        self.destroyed=True

    def timing_info(self,time,percent,name,duration,remaining):
        self.progress_var.set(percent)

        # hack because i'm doing something in the wrong order
        if not hasattr(self,'destroyed'):
            self.duration['text'] = str(duration)
            self.sim_time['text'] = str(time)
            self.remaining['text'] = "%02d:%02d"%(int(remaining/60),int(remaining%60))
            self.update()





