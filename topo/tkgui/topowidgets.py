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

import os.path
import sys
import Tkinter

import Pmw
import bwidget

import topo.tkgui
from widgets import TaggedSlider, ResizableScrollableFrame

######################################################################
topo_dir = os.path.split(os.path.split(sys.executable)[0])[0]
class TkguiWindow(Tkinter.Toplevel):
    """
    The standard tkgui window; defines attributes common to tkgui windows.
    """
    def __init__(self,**config):
        Tkinter.Toplevel.__init__(self,**config)

        ### Window icon
        if topo.tkgui.system_platform is 'mac':
            # CB: To get a proper icon on OS X, we probably have to bundle into an application
            # package or something like that.
            pass # (don't know anything about the file format required)
            # self.attributes("-titlepath","/Users/vanessa/topographica/AppIcon.icns")
        else:
            # CB: It may be possible for the icon be in color (using
            # e.g. topo/tkgui/icons/topo.xpm), see http://www.thescripts.com/forum/thread43119.html
            # or http://mail.python.org/pipermail/python-list/2005-March/314585.html
            self.iconbitmap('@'+(os.path.join(topo_dir,'topo/tkgui/icons/topo.xbm')))


        ### Universal right-click menu   CB: not currently used by anything but the plotgrouppanels
        self.context_menu = Tkinter.Menu(self, tearoff=0)
##         self.bind("<<right-click>>",self.display_context_menu)

##     # CB: still to decide between frame/window; the right-click stuff will probably change.
    
######################################################################



# CB: needs significant cleanup
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


# CB: will try to make the window know when to resize itself, rather
# than having window users tell it
##         self.bind("<Configure>",self.deal_with_configure)

##     def deal_with_configure(self,e=None):
##         print e


    # CB: should be able to move to resizablescrollableframe
    def sizeright(self):
        # if user has changed window size, need to tell tkinter that it should take
        # control again.
        self.geometry('')

        self.update_idletasks()

        # extra for width of scrollbars
        # CEBALERT: the calculated values don't work on linux
        extraw = 19 #self._scroll_frame._scrolled_window.winfo_reqwidth() - \
                  #self._scroll_frame.scrolled_frame.winfo_reqwidth() + 3
        extrah = 19 #self._scroll_frame._scrolled_window.winfo_reqheight() - \
                  #self._scroll_frame.scrolled_frame.winfo_reqheight() + 3

        w = min(self.content.winfo_reqwidth()+extraw,self.winfo_screenwidth())
        # -60 for task bars etc on screen...how to find true viewable height?
        h = min(self.content.winfo_reqheight()+extrah,self.winfo_screenheight()-60)

        if not hasattr(self,'oldsize') or self.oldsize!=(w,h): 
            self._scroll_frame.set_size(w,h)
            self.oldsize = (w,h)
            


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

    def __init__(self,timer=topo.sim.timer,progress_var=None,title=None,display=True,**config):
        TkguiWindow.__init__(self,**config)

        self.protocol("WM_DELETE_WINDOW",self.set_stop)

        if not display:self.withdraw()
        
        self.timer = timer
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

            self._close_window(last_message="Time %s: Finished %s"%(topo.sim.time(),
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





