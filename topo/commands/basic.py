"""
High-level user-level commands controlling the entire simulation.
$Id$
"""
__version__='$Revision$'

import pickle
import __main__

import topo

from topo.base.parameterizedobject import ParameterizedObject, Parameter
from topo.base.functionfamilies import OutputFn
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet
from topo.base.projection import ProjectionSheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.misc.utils import get_states_of_classes_from_module





def save_input_generators():
    """Save a copy of the active_sim's current input_generators for all GeneratorSheets."""
    generator_sheets = topo.sim.objects(GeneratorSheet).values()
    for sheet in generator_sheets:
        sheet.push_input_generator()


def restore_input_generators():
    """Restore previously saved input_generators for all of topo.sim's GeneratorSheets."""
    generator_sheets = topo.sim.objects(GeneratorSheet).values()
    for sheet in generator_sheets:
        sheet.pop_input_generator()


### JABHACKALERT!  Should leave the state of all learning flags
### unchanged upon return; currently it's overwriting all of them.
def pattern_present(inputs={},duration=1.0,learning=False,overwrite_previous=False,apply_output_fn=True):
    """
    Present the specified test patterns for the specified duration.

    Given a set of input patterns (dictionary of
    GeneratorSheetName:PatternGenerator pairs), installs them into the
    specified GeneratorSheets, runs the simulation for the specified
    length of time, then restores the original patterns and the
    original simulation time.  Thus this input is not considered part
    of the regular simulation, and is usually for testing purposes.

    If a simulation is not provided, the active simulation, if one
    exists, is requested.

    If this process is interrupted by the user, the temporary patterns
    may still be installed on the retina.

    If overwrite_previous is true, the given inputs overwrite those
    previously defined.

    If learning is False, overwrites the existing values of Sheet.learning
    to disable learning, then reenables learning.
    """
       
    if not overwrite_previous:
        save_input_generators()

    ### JABALERT!  Should clean up how these are set on each
    ### sheet; it overwrites any old values.
        
    # turn off sheets' learning and output function learning
    #(e.g. in Homeostatic output functions) if learning=False
    if not learning:
        for each in topo.sim.objects(Sheet).values():
             each.learning = False
        for each in topo.sim.objects(ProjectionSheet).values():
            each.output_fn.learning = False
                              
       
    if not apply_output_fn:
        for each in topo.sim.objects(Sheet).values():
             each.apply_output_fn = False


    gen_eps_list = topo.sim.objects(GeneratorSheet)
    
    # Register the inputs on each input sheet
    for each in inputs.keys():
        if gen_eps_list.has_key(each):
            gen_eps_list[each].set_input_generator(inputs[each])
        else:
            ParameterizedObject().warning('%s not a valid Sheet Name.' % each)

    topo.sim.event_push()
    topo.sim.run(duration) 
    topo.sim.event_pop()

    # turn sheets' learning and output_fn learning back on if we turned it off before
    if not learning:
        for each in topo.sim.objects(Sheet).values():
            each.learning = True
        for each in topo.sim.objects(ProjectionSheet).values():
            each.output_fn.learning = True
                              
    if not apply_output_fn:
        for each in topo.sim.objects(Sheet).values():
            each.apply_output_fn = True
 
        
    if not overwrite_previous:
        restore_input_generators()


def save_snapshot(snapshot_name):
    """
    Save a snapshot of the network's current state.

    Commands stored in topo.sim.startup_commands will be executed
    by the corresponding load_snapshot() function.

    Uses Python's 'pickle' module, so subject to the same limitations
    (see the pickle module's documentation) - with the notable
    exception of class attributes. Python does not pickle class
    attributes, but this function stores class attributes of any
    ParameterizedObject class that is declared within the topo
    package.

    (Subpackages of topo that are not part of the simulation are
    excluded from having their classes' attributes saved: plotting,
    tkgui, and tests.)
    """
    ### Warn that classes & functions defined in __main__ won't unpickle
    #
    import types
    for k,v in __main__.__dict__.items():
        # there's classes and functions...what else?
        if isinstance(v,type) or isinstance(v,types.FunctionType):
            if v.__module__ == "__main__":
                ParameterizedObject().warning("%s (type %s) has source in __main__; it will only be found on unpickling if the class is explicitly defined (e.g. by running the same script first) before unpickling."%(k,type(v)))


    ### Get ParameterizedObject class attributes
    #
    states_of_classes = {}

    # For now we just search topo, but it could be extended to all packages.
    # We exclude certain subpackages that contain classes that aren't part
    # of the simulation.
    exclude = ('plotting','tkgui','tests') 
    get_states_of_classes_from_module(topo,states_of_classes,[],exclude)


    ### Set the release version for this simulation.
    #
    topo.sim.RELEASE = topo.release


    ### Now pickle the lot to a file
    #
    pickle.dump( (topo.sim.actual_sim,states_of_classes), open(snapshot_name,'wb'),2)


def load_snapshot(snapshot_name):
    """
    Load the simulation stored in snapshot_name.

    Unpickles the simulation, sets ParameterizedObject class
    attributes, and executes commands in topo.sim.startup_commands
    """
    sim,states_of_classes = pickle.load(open(snapshot_name,'rb'))

    topo.sim.change_sim(sim)

    ### Set class attributes
    #
    # (i.e. execute in __main__ the command "path.to.module.Class.x=y" for each class)
    for class_name,state in states_of_classes.items():

        # from "topo.base.parameter.Parameter", we want "topo.base.parameter"
        module_path = class_name[0:class_name.rindex('.')]
        exec 'import '+module_path in __main__.__dict__

        # now restore class Parameter values
        for p_name,p in state.items():
            __main__.__dict__['val'] = p
            try:
                exec 'setattr('+class_name+',"'+p_name+'",val)' in __main__.__dict__
            except:
                ParameterizedObject().warning('Problem restoring parameter %s=%s for class %s; name may have changed since the snapshot was created.' % (p_name,repr(p),class_name))


    ### Execute the startup commands
    #
    for cmd in topo.sim.startup_commands:
        exec cmd in __main__.__dict__

