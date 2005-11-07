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
# Registry for subclasses of PatternGenerator.  Users can add to this
# list, and the GUI will automatically add them to the list of
# PatternGenerator inputs possible.  Additional work may be necessary if
# other than default Parameter names are used in the definition of the
# PatternGenerator.
# JAB: Please explain what that work might be, e.g. which files might
# need to be edited...
#
# Format:   {'NewPatternGeneratorClassName':<NewPatternGeneratorClass>,....}
pattern_generators = KeyedList()


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
# Singleton variable to register which Simulator is currently active
# in the Topographica simulator.  This should not be set directly, but
# through the two accessor functions.  This variable is also used by
# the GUI to know which simulator to drive.
__active_sim = None
def active_sim(): return __active_sim
def set_active_sim(a_sim):
    global __active_sim
    __active_sim = a_sim
    link_to_sim(a_sim)


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
def link_to_sim(sim):
    """Connect a simulator to the GUI."""
#    assert isinstance(sim,topo.Simulator) or sim is None, 'Parameter must be Simulator'
    if __gui_console:
        if __gui_console != None:
            __gui_console.set_active_simulator(sim)


