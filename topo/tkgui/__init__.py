"""
Tk-based graphical user interface (GUI).

This package implements a Topographica GUI based on the Tk toolkit,
through the Tkinter interface to Python.  The rest of Topographica
does not depend on this package or any module in it, and thus other
GUIs or other types of interfaces can also be used.

$Id$
"""
__version__='$Revision$'

import Pmw, sys, Tkinter, platform, _tkinter,os
import topo.base.parameterizedobject

from topoconsole import TopoConsole

#### notes about tkgui ####
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
#
## Window or Frame?
# Maybe one day everything (PlotGroupPanels, ParametersFrames,
# ModelEditor, ...) will be Frames inside one master window (for
# e.g. a matlab-like workspace).  Nobody's been worrying too much
# about whether something's a Frame or a window when they've been
# implementing things, so 'close' buttons, title methods, and so on
# are a bit of a mix. This needs to be cleaned up when we have a
# final window organization method in mind.

# the most bwidget screenshots i could find:
# http://tcltk.free.fr/Bwidget/
# some bwidget ref's/notes I'm using/going to use:
# http://wiki.tcl.tk/1091 and 3909
# http://tkinter.unpythonic.net/bwidget/BWman/
# http://sourceforge.net/docman/display_doc.php?docid=17481&group_id=12883
# https://stat.ethz.ch/pipermail/r-sig-gui/2004-April/000258.html
# http://wiki.tcl.tk/8646
# http://wiki.tcl.tk/2251

# When not using the GUI, Topographica does not ordinarily import any of
# the classes in the separate Topographica packages. For example, none
# of the pattern types in topo.patterns is imported in Topographica by
# default.  But for the GUI, we want all such things to be available
# as lists from which the user can select.  To do this, we import all
# pattern types and other such classes here. User-defined classes will
# also appear in the GUI menus if they are derived from any class
# derived from the one specified in each widget, and imported before
# the relevant GUI window starts.
from topo.coordmapperfns import *
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
if system_platform=='mac':
    # if it's on the mac, these are the context-menu events
    right_click_events = ['<Button-2>','<Control-Button-1>']
    right_click_release_events = ['ButtonRelease-2', 'Control-ButtonRelease-1']
else:
    # everywhere else (I think) it's Button-3
    right_click_events = ['<Button-3>']
    right_click_release_events = ['ButtonRelease-2']


# CEBALERT: entry background color hack.
# How to get the standard Frame background on all platforms?
if system_platform=='mac':
    topo.entry_background = 'SystemWindowBody'
elif system_platform=='win':
    topo.entry_background = 'SystemWindow'
else:
    topo.entry_background = '#d9d9d9'





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


def __ttkify(root,widget):
    """Take widget from ttk instead of Tkinter"""
    la = "ttk::"+widget
    root.tk.call('namespace', 'import', '-force', la) # overwrites the current Tkinter one

    
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

    # Try to read in options from an options_database file
    # (see http://www.itworld.com/AppDev/1243/UIR000616regex/
    # or p. 49 Grayson)
    try:
        options_database = os.path.join(sys.path[0],"topo","tkgui","options_database")
        root.option_readfile(options_database)
        print "Read options database from",options_database
    except _tkinter.TclError:
        pass

    # CB: uncomment for Tile
##     root.tk.call('package', 'require', 'tile')
##     widgets_to_ttkify = [] # add widgets one by one until error,
##                            # then find cause, fix, continue...
##     #'text','scrollbar','button','frame','labelframe','label','combobox', etc
##     for w in widgets_to_ttkify:
##         __ttkify(root,w)
##     root.tk.call('tile::setTheme', 'default') # or classic or xpnative or winnative or aqua

    # CB: comment out for Tile
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


