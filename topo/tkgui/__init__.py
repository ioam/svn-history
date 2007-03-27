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
    root = Tkinter.Tk()
    root.resizable(1,1)

    # This alows context menus to work on the Mac.  Widget code should bind
    # contextual menus to the virtual event <<right-click>>, not
    # <Button-3>.
    # JPALERT: We probably should do an OS check here if
    # ctrl-click means something else on Windows.

    root.event_add('<<right-click>>','<Button-3>','<Control-Button-1>')
    root.event_add('<<right-click-release>>','<ButtonRelease-3>','<Control-ButtonRelease-1>')
    Pmw.initialise(root)
    console = topoconsole.TopoConsole(parent=root)
    console.pack(expand=Tkinter.YES,fill=Tkinter.BOTH)

    # mainloop() freezes the commandline until the GUI window exits.
    # Without this line the command-line remains responsive.
    if mainloop:
        console.mainloop()



    ##########
    ### Make cascading menus open automatically on linux when the mouse
    ### is over the menu title.
    ### [Tkinter-discuss] Cascade menu issue
    ### http://mail.python.org/pipermail/tkinter-discuss/2006-August/000864.html
    from Tkinter import Menu
    # CEBALERT: there is now a kind of partial menu bar above the one
    # we use on topoconsole (this shows up as an extra line).  Because
    # we use pmw's menubar, we're not using the overall ('toplevel')
    # menu that tk apps would usually have.
    # The reason to use pmw's menu bar is that balloon help can be bound
    # to the options - this doesn't seem to be possible with tk alone
    # (at least in any reasonable way).
    menubar=Menu(root)  # toplevel menu
    root.configure(menu=menubar)
    activate_cascade = """\
    if {[%W cget -type] != {menubar} && [%W type active] == {cascade}} {
        %W postcascade active
    }
    """
    root.bind_class("Menu", "<<MenuSelect>>", activate_cascade)
    ##########


    return console


####################### 

if __name__ == '__main__':
    start(mainloop=True)
