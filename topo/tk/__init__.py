# Tk based GUI support files
#
# $Id$

import propertiesframe
import taggedslider
import topoconsole
import plotpanel

from Tkinter import *
import Pmw, sys
import topo.simulator as simulator
from topo.tk.topoconsole import *


def show_cmd_prompt():
    """
    Small helper to print the sys.ps1 prompt to the command-line.
    Useful after a bunch of output has been displayed to stdout,
    so as to let the user know that the command-line is still
    active.
    """
    print "\n", sys.ps1,
    sys.stdout.flush()
    
def start(sim=None, mainloop=False):
    """
    Startup code for GUI.

    sim: Adds a simulation object into the GUI's active_simulator
    variable This simulator will be the one that the GUI polls for
    plots and other types of data.

    mainloop: If True, then the command-line is frozen while the GUI
    is open.  If False, then commands can be entered at the command-line
    even while the GUI is operational.  Default is False.
    """
    assert isinstance(sim,simulator.Simulator) or sim == None, 'sim is not a Simulator object'

    root = Tk()
    root.resizable(1,1)
    Pmw.initialise(root)
    console = TopoConsole(parent=root)
    console.pack(expand=YES,fill=BOTH)
    console.set_active_simulator(sim)

    # mainloop() freezes the commandline until the GUI window exits.
    # Without this line the command-line remains responsive.
    if mainloop:
        console.mainloop()

    return console


####################### 

if __name__ == '__main__':
    start(mainloop=True)
