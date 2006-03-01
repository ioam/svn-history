"""
High-level user-level commands controlling the entire simulator.
$Id$
"""
__version__='$Revision$'

import __main__
import pickle

import topo
import topo.base.simulator
from topo.base.parameterizedobject import ParameterizedObject, Parameter
from topo.base.sheet import Sheet
from topo.base.projection import ProjectionSheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.misc.utils import get_states_of_classes_from_module




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
def pattern_present(inputs=None,duration=1.0,learning=False,overwrite_previous=False,apply_output_fn=True):
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
                ParameterizedObject().warning('%s not a valid Sheet Name.' % each)

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


def save_snapshot(snapshot_name):
    """
    Save a snapshot of the current network's state.

    snapshot_name is the file name string.

    Uses Python's 'pickle' module, so subject to the same limitations.

    CEBHACKALERT: update both save_snapshot doc and load_snapshot doc
    """
    states_of_classes = {}
    classes = {}

    # for now we just search topo, but it could be extended to all packages.
    topo_ = __main__.__dict__['topo']
    get_states_of_classes_from_module(topo_,states_of_classes,[])
    
    pickle.dump((topo.sim.actual_sim,states_of_classes), open(snapshot_name,'wb'), 2)


def load_snapshot(snapshot_name):
    """
    Return the current network to the state of the specified snapshot.

    snapshot_name is the file name string.
    """
    
    sim,states_of_classes = pickle.load(open(snapshot_name,'rb'))
    topo.sim.change_sim(sim)

    # Set class attributes
    # i.e. "path.to.module.Class.x=y"
    for class_name,state in states_of_classes.items():

        # Import class back to __main__
        # from "topo.base.parameter.Parameter", we want "topo.base.parameter"
        module_path = class_name[0:class_name.rindex('.')] 
        #print 'import '+module_path
        exec 'import '+module_path in __main__.__dict__

        # now restore class Parameter values
        for p_name,p in state.items():
            __main__.__dict__['val'] = p
            #print 'setattr('+class_name+',"'+p_name+'",val)'
            exec 'setattr('+class_name+',"'+p_name+'",val)' in __main__.__dict__

    # (? assumes parameters weren't added dynamically to a class i.e. they're all
    # in the source code)
