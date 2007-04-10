"""
Tk-based graphical user interface (GUI).

This package implements a Topographica GUI based on the Tk toolkit,
through the Tkinter interface to Python.  The rest of Topographica
does not depend on this package or any module in it, and thus other
GUIs or other types of interfaces can also be used.

$Id$
"""
__version__='$Revision$'

import Pmw, sys, Tkinter, platform
import topo.base.parameterizedobject
import topoconsole

# CB: I think we should setup some named font instances here
# to use throughout tkgui, and avoid all the various local
# specifications (which will become very tedious to maintain).
# Doing this will give other advantages, too, like maybe allowing
# a user to say "make all the fonts a bit bigger", and so on.
#
# Some font links:
# http://www.pythonware.com/library/tkinter/introduction/x444-fonts.htm
# http://www.astro.washington.edu/owen/ROTKFolklore.html




# When not using the GUI, Topographica does not ordinary import any of
# the classes in the separate Topographica packages. For example, none
# of the pattern types in topo.patterns is imported in Topographica by
# default.  But for the GUI, we want all such things to be available
# as lists from which the user can select.  To do this, we import all
# pattern types and other such classes here. User-defined classes will
# also appear in the GUI menus if they are derived from any class
# derived from the one specified in each widget, and imported before
# the relevant GUI window starts.
from topo.eps import *
from topo.learningfns import *
from topo.outputfns import *
from topo.patterns import *
from topo.projections import *
from topo.responsefns import *
from topo.sheets import *

from topo.base.cf import CFPLearningFnParameter,CFPOutputFnParameter,CFPResponseFnParameter
from topo.base.functionfamilies import LearningFnParameter,OutputFnParameter,ResponseFnParameter
from topo.base.patterngenerator import PatternGeneratorParameter

#
# Define up the right click (context menu) events. These variables can
# be appended or overridden in .topographicarc, if the user has some
# crazy input device.
#
if platform.mac_ver()[0]:
    # if it's on the mac, these are the context-menu events
    right_click_events = ['<Button-2>','<Control-Button-1>']
    right_click_release_events = ['ButtonRelease-2', 'Control-ButtonRelease-1']
else:
    # everywhere else (I think) it's Button-3
    right_click_events = ['<Button-3>']
    right_click_release_events = ['ButtonRelease-2']
    

def show_cmd_prompt():
    """
    Small helper to print the sys.ps1 prompt to the command-line.
    Useful after a bunch of output has been displayed to stdout,
    so as to let the user know that the command-line is still
    active.
    """
    if topo.base.parameterizedobject.min_print_level >= topo.base.parameterizedobject.MESSAGE:
        print "\n", sys.ps1,
        sys.stdout.flush()
    
def start(mainloop=False):
    """
    Startup code for GUI.

    mainloop: If True, then the command-line is frozen while the GUI
    is open.  If False, then commands can be entered at the command-line
    even while the GUI is operational.  Default is False.
    """
    console = topoconsole.TopoConsole()

    # This alows context menus to work on the Mac.  Widget code should bind
    # contextual menus to the virtual event <<right-click>>, not
    # <Button-3>.
    # JPALERT: We probably should do an OS check here if
    # ctrl-click means something else on Windows.

    console.event_add('<<right-click>>',*right_click_events)
    console.event_add('<<right-click-release>>',*right_click_release_events)
    Pmw.initialise(console)

    # mainloop() freezes the commandline until the GUI window exits.
    # Without this line the command-line remains responsive.
    if mainloop:
        console.mainloop()

    return console


####################### 

if __name__ == '__main__':
    start(mainloop=True)
