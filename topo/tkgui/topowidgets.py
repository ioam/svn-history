"""
Collection of widgets designed to interact with components of
Topographica.

$Id$
"""
__version__='$Revision$'


# We should now be able to move these classes elsewhere 

import Tkinter

from widgets import Balloon, TkguiWindow
import topo



class StatusBar(Tkinter.Frame):

    def __init__(self, master):
        Tkinter.Frame.__init__(self, master)
        self.label = Tkinter.Label(self, borderwidth=1, relief='sunken', anchor='w')
        self.label.pack(fill='x')

    def message(self,chuck=None,message=None):
        self.set(message)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()







class Progressbar(Tkinter.Widget):
    def __init__(self, master=None, cnf={}, **kw):
        Tkinter.Widget.__init__(self, master, "ttk::progressbar", cnf, kw)
        
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

    def __init__(self,parent,timer=None,progress_var=None,title=None):
        ProgressController.__init__(self,timer,progress_var)
        TkguiWindow.__init__(self,parent)

        self.protocol("WM_DELETE_WINDOW",self.set_stop)
        self.title(title or self.timer.func.__name__.capitalize())
        self.balloon = Balloon(self)

        progress_bar = Progressbar(self,#type="normal",
                                   #maximum=100,height=20,width=200,
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




