"""
High-level user-level commands controlling the entire simulator.
$Id$
"""
__version__='$Revision$'

from topo.base.topoobject import TopoObject
from topo.base.sheet import Sheet
from topo.base.projection import ProjectionSheet
import topo.base.simulator
from topo.sheets.generatorsheet import GeneratorSheet

import pickle

def save_input_generators():
    """Save a copy of the active_sim's current input_generators for all GeneratorSheets."""
    sim = topo.base.simulator.get_active_sim()

    if sim:
        generator_sheets = sim.objects(GeneratorSheet).values()
        for sheet in generator_sheets:
            sheet.push_input_generator()


def restore_input_generators():
    """Restore previously saved input_generators for all of active_sim's GeneratorSheets."""
    sim = topo.base.simulator.get_active_sim()

    if sim:
        generator_sheets = sim.objects(GeneratorSheet).values()
        for sheet in generator_sheets:
            sheet.pop_input_generator()


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
    sim = topo.base.simulator.get_active_sim()

    if sim:

        if not overwrite_previous:
            save_input_generators()

        ### JABALERT!  Should clean up how these are set on each
        ### sheet; it overwrites any old values.
            
        # turn off sheets' learning if learning=False
        if not learning:
            for each in sim.objects(Sheet).values():
                 each.learning = False


        if not apply_output_fn:
            for each in sim.objects(Sheet).values():
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
            for each in sim.objects(Sheet).values():
                each.learning = True
  

        if not apply_output_fn:
            for each in sim.objects(Sheet).values():
                each.apply_output_fn = True
 
            
        if not overwrite_previous:
            restore_input_generators()


# CEBHACKALERT: see below
from topo.patterns.basic import GaussianGenerator
from topo.patterns.random import UniformRandomGenerator
from topo.base.sheet import Sheet
import __main__

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
    
    # CEBHACKALERT:
    # Should this execute in __main__.__dict__?
    # load_cmd = 'import pickle; saved_sim=pickle.load(open("'+snapshot_name+'","rb")); import topo.base.simulator; topo.base.simulator.set_active_sim(saved_sim)'
    #  exec load_cmd in __main__.__dict__
    #
    # Also confusion that current simulator is left behind as e.g. s

    saved_sim = pickle.load(open(snapshot_name,'rb'))         
    topo.base.simulator.set_active_sim(saved_sim)

    # CEBHACKALERT:
    # Until I figure out how to pickle random properties of the GaussianGenerator properly...


    hack = """
from topo.base.simulator import get_active_sim
from topo.sheets.generatorsheet import GeneratorSheet
gs_list = get_active_sim().objects(GeneratorSheet).values()
try:
    [gs.set_input_generator(GaussianGenerator()) for gs in gs_list]
except NameError:
    pass
"""
#    exec hack in __main__.__dict__

def save_snapshot(snapshot_name):
    """
    Save a snapshot of the current network's state.

    snapshot_name is the file name string.

    Uses Python's 'pickle' module, so subject to the same limitations.
    """
    sim = topo.base.simulator.get_active_sim()

    if sim != None:
        pickle.dump(sim, open(snapshot_name,'wb'), 2)


