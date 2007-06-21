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

from topoconsole import TopoConsole

#### notes about tkgui ####
#
## Fonts
# I think we should setup some named font instances here to use
# throughout tkgui, and avoid all the various local specifications
# (which will become very tedious to maintain).  Doing this will give
# other advantages, too, like maybe allowing a user to say "make all
# the fonts a bit bigger", and so on.
# Some font links:
# http://www.pythonware.com/library/tkinter/introduction/x444-fonts.htm
# http://www.astro.washington.edu/owen/ROTKFolklore.html
#
## Geometry management
# In several places we use pack() when grid() would probably be
# simpler. Check you know which fits a task better rather than copying
# existing code.
#
## Pmw
# Not being maintained, and incompatible with some improvements to
# tk (like Tile). Everything we use from Pmw is available from
# other packages (like bwidget, Tix, etc). So maybe try to avoid
# adding more Pmw.
#
## Dialogs
# Don't know how to theme them (can't make them inherit from
# our own class, for instance). Consider making our own dialog
# boxes (subclass of Tkguiwindow) using transient and grab_set:
# http://thread.gmane.org/gmane.comp.python.tkinter/657/focus=659
#
## Mainloop
# Because we don't call mainloop(), it's necessary to call
# update() or update_idletasks() sometimes. Also, I think that sometimes
# current graphics do not update properly (but I'm not sure - I don't
# have a specific example yet). Need to clean up all the scattered
# update() and update_idletasks()...




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


##########
### Which os is being used (for gui purposes)?
#
# system_plaform can be:
# "linux"
# "mac"
# "win"
# "unknown"
#
# If you are programming tkgui and need to do something special
# for some other platform (or to further distinguish the above
# platforms), please modify this code.
#
# Right now tkgui only needs to detect if the platform is linux (do I
# mean any kind of non-OS X unix*?) or mac, because there is some
# special-purpose code for both those two: the mac code below, and the
# menu-activating code in topoconsole.  We might have some Windows-
# specific code for the window icons later on, too.
# * actually it's the window manager that's important, right?
# Does tkinter/tk itself give any useful information?
# What about root.tk.call("tk","windowingsystem")?
system_platform = 'unknown'
if platform.system()=='Linux':
    system_platform = 'linux'
elif platform.system()=='Darwin' or platform.mac_ver()[0]:
    system_platform = 'mac'
elif platform.system()=='Windows':
    system_platform = 'win'
##########


#
# Define up the right click (context menu) events. These variables can
# be appended or overridden in .topographicarc, if the user has some
# crazy input device.
#
if system_platform is 'mac':
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

    # Creating an initial Tk() instance and then withdrawing the
    # window is a common technique. Instead of doing this, having
    # TopoConsole itself be a subclass of Tk would make sense - since
    # it is the main application window - but then we could not have a
    # hierarchy in which all windows are given some common properties.
    root = Tkinter.Tk()
    root.withdraw()
    Pmw.initialise(root)
    
    console = TopoConsole()
    
    # This alows context menus to work on the Mac.  Widget code should bind
    # contextual menus to the virtual event <<right-click>>, not
    # <Button-3>.
    console.event_add('<<right-click>>',*right_click_events)
    console.event_add('<<right-click-release>>',*right_click_release_events)
    


    # GUI/threads:
    # http://thread.gmane.org/gmane.comp.python.scientific.user/4153
    # (inc. ipython info)
    # (Also http://mail.python.org/pipermail/python-list/2000-January/021250.html)

    # mainloop() freezes the commandline until the GUI window exits.
    # Without this line the command-line remains responsive.
    if mainloop:
        console.mainloop()

    return console



####################### 

if __name__ == '__main__':
    start(mainloop=True)


