"""
High-level user-level commands controlling the entire simulator.
"""

from topo.base.topoobject import TopoObject
from topo.base.sheet import Sheet
from topo.base.projection import ProjectionSheet
import topo.base.simulator
import topo.base.registry
from topo.sheets.generatorsheet import GeneratorSheet

import pickle

### JABALERT!  We're likely to have a lot of commands like this that
### need to work on the active simulator.  We should figure out a way
### to avoid duplicating all this code about if sim, not sim, else,
### etc.; is there some way to write that only once and just have all
### commands use it?
            
def save_input_generators(sim=None):
    """Save a copy of the current input_generators for all GeneratorSheets."""
    if not sim:
        sim = topo.base.registry.active_sim()

    if sim:
        generator_sheets = sim.objects(GeneratorSheet).values()
        for sheet in generator_sheets:
            sheet.push_input_generator()
    else:
        TopoObject().warning('No active Simulator.')


def restore_input_generators(sim=None):
    """Restore previously saved input_generators for all GeneratorSheets."""
    if not sim:
        sim = topo.base.registry.active_sim()

    if sim:
        generator_sheets = sim.objects(GeneratorSheet).values()
        for sheet in generator_sheets:
            sheet.pop_input_generator()
    else:
        TopoObject().warning('No active Simulator.')


### JABHACKALERT!  Should leave the state of all learning flags
### unchanged upon return; currently it's overwriting all of them.
def pattern_present(inputs=None,duration=1.0,sim=None,learning=False,overwrite_previous=False,apply_output_fn=True):
    """
    Present the specified test patterns for the specified duration.

    Given a set of input patterns (dictionary of
    GeneratorSheetName:PatternGenerator pairs), installs them into the
    specified GeneratorSheets, runs the simulator for the specified
    length of time, then restores the original patterns and the
    original simulator time.  Thus this input is not considered part
    of the regular simulation, and is usually for testing purposes.

    If a simulator is not provided, the active simulator, if one
    exists, is requested.

    If this process is interrupted by the user, the temporary patterns
    may still be installed on the retina.

    If overwrite_previous is true, the given inputs overwrite those
    previously defined.

    If learning is False, overwrites the existing values of Sheet.learning
    to disable learning, then reenables learning.
    """
    if not sim:
        sim = topo.base.registry.active_sim()
    if sim:

        if not overwrite_previous:
            save_input_generators(sim)

        ### JABALERT!  Should clean up how these are set on each
        ### sheet; it overwrites any old values.
            
        # turn off sheets' learning if learning=False
        if not learning:
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.learning = False

        if not apply_output_fn:
            for each in sim.get_event_processors():
                if isinstance(each,ProjectionSheet):
                    each.apply_output_fn = False

        gen_eps_list = sim.objects(GeneratorSheet)
        
        # Register the inputs on each input sheet
        for each in inputs.keys():
            if gen_eps_list.has_key(each):
                gen_eps_list[each].set_input_generator(inputs[each])
            else:
                TopoObject().warning('%s not a valid Sheet Name.' % each)

        sim.state_push()
        sim.run(duration)
        sim.state_pop()

        # turn sheets' learning back on if we turned it off before
        if not learning:
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.learning = True

        if not apply_output_fn:
            for each in sim.get_event_processors():
                if isinstance(each,ProjectionSheet):
                    each.apply_output_fn = True
            
        if not overwrite_previous:
            restore_input_generators(sim)

    else:
        TopoObject().warning('No active Simulator.')
    

def load_snapshot(snapshot_name):
    """
    Return the current network to the state of the specified snapshot.

    snapshot_name is the file name string.

    The specified snapshot should correspond to the network
    structure currently loaded, e.g. a snapshot saved from the
    lissom_or.ty example should be loaded only if lissom_or.ty has
    itself first been run. Otherwise, the loaded snapshot is likely
    to have incorrect behaviour.
    """
    # CEBHACKALERT:
    # Should there be a check that the right kind of network has
    # been loaded? If so, add it and change docstring above.
    saved_sim = pickle.load(open(snapshot_name))         
    topo.base.registry.set_active_sim(saved_sim)


def save_snapshot(snapshot_name):
    """
    Save a snapshot of the current network's state.

    snapshot_name is the file name string.

    Uses Python's 'pickle' module, so subject to the same limitations.
    """
    # CEBHACKALERT:
    # Protocol 2 is faster and results in smaller file sizes.
    # I'll switch once we have the tutorial working.
    pickle.dump(topo.base.registry.active_sim(), open(snapshot_name,'w'))


