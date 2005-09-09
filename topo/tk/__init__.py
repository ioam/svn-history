# Tk based GUI support files
#
# $Id$

# For importing the tk GUI files
import topo.tk.propertiesframe
import topo.tk.taggedslider
import topo.tk.topoconsole
import topo.tk.plotpanel
import topo.tk.basicplotpanel
import topo.tk.unitweightspanel
import topo.tk.projectionpanel
import topo.tk.cfsheetplotpanel
import topo.tk.inputparamspanel
import topo.tk.preferencemappanel

# For show_cmd_prompt() and start()
import Pmw, sys, Tkinter
import topo.simulator
import topo.base
import topo.gui

def show_cmd_prompt():
    """
    Small helper to print the sys.ps1 prompt to the command-line.
    Useful after a bunch of output has been displayed to stdout,
    so as to let the user know that the command-line is still
    active.
    """
    if topo.base.min_print_level >= topo.base.MESSAGE:
        print "\n", sys.ps1,
        sys.stdout.flush()
    
def start(sim=None, mainloop=False):
    """
    Startup code for GUI.

    sim: Adds a simulation object into the GUI's active_simulator
    variable. The GUI will request plots and other types of data
    from this simulator.

    mainloop: If True, then the command-line is frozen while the GUI
    is open.  If False, then commands can be entered at the command-line
    even while the GUI is operational.  Default is False.
    """
    assert isinstance(sim,topo.simulator.Simulator) or sim == None, 'sim is not a Simulator object'

    root = Tkinter.Tk()
    root.resizable(1,1)
    Pmw.initialise(root)
    console = topo.tk.topoconsole.TopoConsole(parent=root)
    console.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)
    if sim is None:
        console.set_active_simulator(topo.simulator.active_sim())
    else:
        console.set_active_simulator(sim)

    topo.gui.set_console(console)

    # mainloop() freezes the commandline until the GUI window exits.
    # Without this line the command-line remains responsive.
    if mainloop:
        console.mainloop()

    return console


####################### 

if __name__ == '__main__':
    start(mainloop=True)
