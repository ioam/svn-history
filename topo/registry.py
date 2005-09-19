"""
Package to store registry information that is accessed by the
Topographica system.  Many of the entries in this class are designed
to be added to by users.

$Id$
"""
import topo

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
__gui_console = None
def get_console():
    return __gui_console
def set_console(con):
    global __gui_console
    __gui_console = con
def link_to_sim(sim):
    """Connect a simulator to the GUI."""
    assert isinstance(sim,topo.simulator.Simulator) or sim is None, 'Parameter must be Simulator'
    if __gui_console:
        if __gui_console != None:
            __gui_console.set_active_simulator(sim)
