"""
Central location for registering and retrieving information needed by
Topographica.  Primarily useful when extending Topographica to provide
new components; once the components are registered here, they will
usually show up automatically in menus, online help, etc.  

$Id$
"""
__version__='$Revision$'
from keyedlist import KeyedList


############################################################
# Global repository of plot templates, which can be augmented
# as necessary.
plot_templates = {}
plotgroup_templates = KeyedList()


############################################################
# Global repository for links between a plot group template name and a
# subclassed Plot Panel to use instead of the default.
#
# An example: plotpanel_classes['Hue Pref Map'] = HuePreferencePanel
plotpanel_classes = {}


############################################################
# Even though Topographica base is not allowed to point to a
# particular GUI, there are still times when a GUI may wish to be
# notified when the active Simulator has been changed.  This mechanism
# allows that to happen, by having the active Simulator function call
# a registered GUI, which by default is a no-op.
#
### JABHACKALERT!
### 
### This code should be changed to be a registry for anything that
### might want to be notified that the Simulator has changed; it is
### not specific to a GUI.  E.g. various external plotting programs,
### non-graphical user interfaces, pipes to interface to Matlab, and
### so on, might all need to know this.  So it should be a list or
### dictionary, not a single item, and it should never assume or state
### that it's a GUI that is being held here.
###
__gui_console = None
def get_console():
    return __gui_console

def set_console(con):
    global __gui_console
    __gui_console = con

def link_console_to_active_sim():
    """
    """
    if __gui_console != None:
        __gui_console.set_active_simulator()


