"""
Tk-based graphical user interface (GUI).

This package implements a Topographica GUI based on the Tk toolkit,
through the Tkinter interface to Python.  The rest of Topographica
does not depend on this package or any module in it, and thus other
GUIs or other types of interfaces can also be used.

$Id$
"""
__version__='$Revision$'

import Pmw, sys, Tkinter
import topo.base.topoobject
import topoconsole

# CEBHACKALERT:

# PatternGenerators, OutputFunctions (, LearningFunctions, ...)
# ------------------------------------------------------------
#
# By default, none of the classes in the separate Topographica
# packages is imported. For example,
# none of the pattern types in topo/patterns/ is imported
# in Topographica by default.
# But for the GUI, we want all such [things] to be
# available as lists from which the user can select.
# To do this, we
# import all of the PatternGenerator [etc] classes in all of the modules
# mentioned in topo.patterns [etc.] .__all__, and will also use any that the
# user has defined and registered.

# See topo.base.parameter.ClassSelectorParameter ? or topo.patterns__init etc?

# CEBHACKALERT:  ... in the right namespace
# and so on for other things

from topo.patterns import *
topo.patterns.make_classes_from_all_imported_modules_available()

from topo.outputfns import *
topo.outputfns.make_classes_from_all_imported_modules_available()

from topo.learningfns import *
topo.learningfns.make_classes_from_all_imported_modules_available()

from topo.responsefns import *
topo.responsefns.make_classes_from_all_imported_modules_available()


def show_cmd_prompt():
    """
    Small helper to print the sys.ps1 prompt to the command-line.
    Useful after a bunch of output has been displayed to stdout,
    so as to let the user know that the command-line is still
    active.
    """
    if topo.base.topoobject.min_print_level >= topo.base.topoobject.MESSAGE:
        print "\n", sys.ps1,
        sys.stdout.flush()
    
def start(mainloop=False):
    """
    Startup code for GUI.

    mainloop: If True, then the command-line is frozen while the GUI
    is open.  If False, then commands can be entered at the command-line
    even while the GUI is operational.  Default is False.
    """
    root = Tkinter.Tk()
    root.resizable(1,1)
    Pmw.initialise(root)
    console = topoconsole.TopoConsole(parent=root)
    console.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)

    # mainloop() freezes the commandline until the GUI window exits.
    # Without this line the command-line remains responsive.
    if mainloop:
        console.mainloop()

    return console


####################### 

if __name__ == '__main__':
    start(mainloop=True)
