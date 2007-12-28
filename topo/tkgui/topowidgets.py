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



    



######################################################################            
######################################################################
# CB: Working here; *TkguiWindows need significant cleanup.
# Merge TkguiWindow and ScrolledTkguiWindow because scrollbars are automatic now.
# Clearly separate ResizableScrollableFrame.

# Actually...
# Before trying to simplify, see if bwidget has been updated
# (most of the complications come from bwidget bugs).
# Otherwise, *consider wrapping scrodget* to get a better scrolledframe.
# (The problem there is we'll probably have to add a package to tcl/tk
# and that might not work on os x because we're not using our own
# tcl/tk...I'm not sure).

# Might wonder why we need <<SizeRight>> event, and don't just use the
# <Configure> event for calling sizeright: Can't distinguish manual
# resize from autoresizing.


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


class ResizableScrollableFrame(Tkinter.Frame):
    """
    A scrollable frame that can also be manually resized.

    Any normal scrollable frame will not resize automatically to
    accommodate its contents, because that would defeat the
    purpose of scrolling in the first place.  However, having a
    scrollable frame that can be resized manually is useful; this
    class adds easy resizing to a bwidget
    ScrollableFrame/ScrolledWindow combination.

    ** BEING CONSTRUCTED: not currently suitable for standalone use **
    """
    def __init__(self,master,**config):
        """
        The 'contents' attribute is the frame into which contents
        should be placed (for the contents to be inside the
        scrollable area), i.e. almost all use of
        f=ResizableScrollableFrame(master) will be via f.contents.
        """
        self.__hack=False
        Tkinter.Frame.__init__(self,master,**config)
        self.master = master

        # non-empty Frames ignore any specified width/height, so create two empty
        # frames used purely for setting height & width
        self.__height_sizer = Tkinter.Frame(self,height=0,width=0)#2,borderwidth=2,relief='sunken',background="blue")
        self.__height_sizer.pack(side="left")
        self.__width_sizer = Tkinter.Frame(self,width=0,height=0)#2,background="red",borderwidth=2,relief="sunken")
        self.__width_sizer.pack()

        # the scrollable frame, with scrollbars
        self._scrolled_window = bwidget.ScrolledWindow(self,auto="both",scrollbar="both") #auto="both") #*shscrollbar="none")#,,
                                                       #scrollbar="both")
        # set small start height/width, will grow if necessary
        scrolled_frame = bwidget.ScrollableFrame(self._scrolled_window,
                                                 height=50,width=50)
        self.scrolled_frame = scrolled_frame
        self._scrolled_window.setwidget(scrolled_frame)
        self._scrolled_window.pack(fill="both",expand='yes')

        # CB: tk docs say getframe() not necessary? Where did I see that?
        self.contents = scrolled_frame.getframe()

        self.oldsize=(-1,-1)


    def barz(self,e=None):
        self.after_idle(self.barz2)

    def barz2(self,e=None):
        import topo.tkgui
        if topo.tkgui.system_platform!="mac":
            self.__hack=True # can't call update_idletasks() in after_idle().
            # fortunately we only need to call update_idletasks() for
            # autoresize not to put extra space round the side; this method only needs to get things exactly correct for manual resize.
            scrollbar = self._which_scrollbars()
            self.__hack=False
            self._scrolled_window.config(scrollbar=scrollbar)
        
        
    def set_size(self,width=None,height=None):
        """
        Manually specify the size of the scrollable frame area.
        """
        if width:self.__width_sizer['width']=width
        if height:self.__height_sizer['height']=height

    # CB: rename, rename event
    def sizeright(self,e=None):
        self.master.geometry('')

        # Extra for width of scrollbars; should be found programmatically. But how?
        extraw = 19; extrah = 19

        self.update_idletasks()
        
        w = min(self.contents.winfo_reqwidth()+extraw,
                self.winfo_screenwidth()-extraw)
        # -60 for task bars etc on screen...how to find true viewable height?
        h = min(self.contents.winfo_reqheight()+extrah,
                self.winfo_screenheight()-60-extrah)

        if self.oldsize!=(w,h):
            self.set_size(w,h)
            self.oldsize = (w,h)

        scrollbar = self._which_scrollbars()

        dw = extraw-3; dh = extrah-3

        # can't seem to do this anywhere but right here
        # (get attributeerror otherwise)
        import topo.tkgui
        if topo.tkgui.system_platform!="mac":
            self._scrolled_window.config(scrollbar=scrollbar)

        if scrollbar=="none":
            w-=dw
            h-=dh
        elif scrollbar=="vertical":
            h-=dh
        elif scrollbar=="horizontal":
            w-=dw

        self.set_size(w,h)
        # don't set self.oldsize=(w,h)


    def _need_bars(self):
        sw = self._scrolled_window
        c = self.contents
        need_x,need_y = False,False

        if not self.__hack: self.update_idletasks()

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
    
##     def _fractions_visible(self):
##         X = [float(x) for x in self.scrolled_frame.xview().split(' ')]
##         Y = [float(x) for x in self.scrolled_frame.xview().split(' ')]
##         return X[1]-X[0],Y[1]-Y[0]

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
    



