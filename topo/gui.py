"""
Access the gui (topo.tk) from the commandline.

IMPORTANT: This file must remain able to be imported without requiring
Tk or topo.tk.  This feature allows running on remote machines that do
not have gui support.  To preserve this behavior, all Tk dependent
files in topo.tk should not be auto-imported from this file.  Instead,
a conditional test should be performed to see if the topo.tk package
has already been loaded, and call the needed functions only if they
already exist.

It is reasonable to create a function that will import topo.tk, but
calling that function must not be forced, so users can still use this
file without needing to have Tk or topo.tk installed.

gui.py has three main functions:
1. Registering which Simulator is active.
   (Allows then allows the GUI to requst views from a known simulation.)
2. Letting the command-line run the gui with the '-g' flag.
   (topographica_script.py runs topo.gui.start())
3. Allows the GUI to be run with a single command: topo.gui.start().
   This is instead of having to "import topo.tk" first. 

To start the topo.tk gui from the Topographica prompt, run:
  topo.gui.start()
or
  import topo.tk
  topo.tk.start()
  
  
$Id$
"""

### JABHACKALERT!
### 
### This file should be renamed to something like ui.py, to truly
### reflect whatever it does.  What it seems to do is to provide a way
### for a user interface to be registered, or at least provide a way
### for such an interface to be connected to simulator.py.  So this
### could be renamed and generalized to allow any user interface to be
### selected, of which the one in topo.tk is only an example.  At most
### topographica_script.py should be the only thing that even knows
### topo.tk exists; because it needs to know what to do with -g.  If
### someone changes the implementation of -g to select some other GUI,
### eg. topo/gtk, then it should not be necessary to modify any code
### in this directory.  This file does not respect that rule, and
### needs to be changed.

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
    assert isinstance(sim,topo.simulator.Simulator) or sim is None, 'Parameter must be Simulator'
    if gui_imported():
        if gui_console != None:
            gui_console.set_active_simulator(sim)

def start(sim=None):
    """Import the topo.tk package, and fire 'er up."""
    import topo.tk
    topo.tk.start(sim)
