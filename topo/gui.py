"""
Access the gui (topo.tk) from the commandline.

IMPORTANT: This file must be able to be imported without requiring Tk
or topo.tk.  This feature allows running on remote machines that do
not have gui support.  To preserve this behavior, all Tk dependent
files in topo.tk should not be auto-imported from this file.  Instead,
a conditional test should be performed to see if the topo.tk package
has already been loaded, and call the needed functions only if they
already exist.

It is reasonable to create a function that will import topo.tk, but
calling that function must not be forced, so users can still use this
file without needing to have Tk or topo.tk installed.

To start the topo.tk gui from the Topographica prompt, run:
  import topo.tk
  topo.tk.start()
  
$Id$
"""

import sys, __main__
import topo.simulator
import topo.base

GUIPACKAGE = 'topo.tk'
gui_console = None

def gui_imported():
    """Return True if the GUIPACKAGE has already been imported"""
    return sys.modules.has_key(GUIPACKAGE)

def get_console():
    """Return the TopoConsole"""
    return gui_console

def set_console(con):
    """Set the GUI console"""
    global gui_console
    gui_console = con

def link_to_sim(sim):
    """Connect a simulator to the GUI."""
    assert isinstance(sim,topo.simulator.Simulator), 'Parameter must be Simulator'
    if gui_imported():
        if gui_console != None:
            gui_console.set_active_simulator(sim)
        else:
            topo.base.TopoObject().message('No active GUI console')
