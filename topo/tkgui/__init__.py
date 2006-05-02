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

# We'll make all the classes from the following packages available:
from topo.patterns import *
from topo.outputfns import *
from topo.learningfns import *
from topo.responsefns import *
# CEBHACKALERT: Still to add others: sheets, projections


### Populating GUI lists
#   --------------------
# 
# By default, none of the classes in the separate Topographica
# packages is imported. For example, none of the pattern types in
# topo.patterns is imported in Topographica by default.  But for the
# GUI, we want all such things to be available as lists from which the
# user can select.  To do this, we import all pattern types here
# and add the topo.patterns package to PatternGeneratorParameter's
# package list. We do the same for other classes like this - see the
# imports list at the top of the file.
#
# User-defined classes will appear in these lists if they are in the
# namespace of the appropriate package.  e.g. if I define the class
# StarPatternGenerator, so long as it is added to topo.patterns
# somewhere
# (e.g. 'topo.patterns.basic.StarPatternGenerator=StarPatternGenerator')
# it will appear in GUI lists.
#

def add_package(class_selector,package):
    class_selector.packages.append(package)


# PatternGenerators
from topo.base.patterngenerator import PatternGeneratorParameter
add_package(PatternGeneratorParameter,topo.patterns)

# OutputFns
from topo.base.functionfamilies import OutputFnParameter
from topo.base.cf import CFPOutputFnParameter
add_package(OutputFnParameter,topo.outputfns)
add_package(CFPOutputFnParameter,topo.outputfns)

# LearningFns
from topo.base.functionfamilies import LearningFnParameter
from topo.base.cf import CFPLearningFnParameter
add_package(LearningFnParameter,topo.learningfns)
add_package(CFPLearningFnParameter,topo.learningfns)

# ResponseFns
from topo.base.functionfamilies import ResponseFnParameter
from topo.base.cf import CFPResponseFnParameter
add_package(ResponseFnParameter,topo.responsefns)
add_package(CFPResponseFnParameter,topo.responsefns)

### End 'Populating GUI lists'



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
