"""
High-level user-level commands controlling the entire simulation.
$Id$
"""
__version__='$Revision$'

import __main__
import StringIO

import topo
from topo.base.parameterizedobject import ParameterizedObject, Parameter
from topo.base.sheet import Sheet
from topo.base.projection import ProjectionSheet
from topo.sheets.generatorsheet import GeneratorSheet
from topo.misc.utils import get_states_of_classes_from_module,ExtraPickler,ExtraUnpickler




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
def pattern_present(inputs=None,duration=1.0,learning=False,overwrite_previous=False,apply_output_fn=True):
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
        
    # turn off sheets' learning if learning=False
    if not learning:
        for each in topo.sim.objects(Sheet).values():
             each.learning = False


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

    topo.sim.state_push()
    topo.sim.run(duration)
    topo.sim.state_pop()

    # turn sheets' learning back on if we turned it off before
    if not learning:
        for each in topo.sim.objects(Sheet).values():
            each.learning = True
  

    if not apply_output_fn:
        for each in topo.sim.objects(Sheet).values():
            each.apply_output_fn = True
 
        
    if not overwrite_previous:
        restore_input_generators()


def save_snapshot(snapshot_name):
    """
    Save a snapshot of the network's current state.

    Commands listed in topo.sim.startup_commands are stored ready
    to run before the simulation is unpickled in the future.

    Uses Python's 'pickle' module, so subject to the same limitations (see
    the pickle module's documentation) - except that class attributes
    of ParameterizedObjects declared within the topo package (including
    all subpackages - except ones like 'plotting') are pickled.
    """
    ### Classes etc defined in __main__ won't unpickle (so warn).
    # The source code won't exist to recreate the class. If e.g. a class
    # is redefined in main before unpickling, it will be ok though.
    import types
    for k,v in __main__.__dict__.items():
        # there's classes and functions...what else?
        if isinstance(v,type) or isinstance(v,types.FunctionType):
            if v.__module__ == "__main__":
                ParameterizedObject().warning("%s (type %s) has source in __main__; it will not be found on unpickling."%(k,type(v)))


    ### Get ParameterizedObject class attributes
    #
    states_of_classes = {}
    classes = {}

    # For now we just search topo, but it could be extended to all packages.
    # We exclude certain subpackages that contain classes that aren't part
    # of the simulation.
    exclude = ('plotting','tkgui','tests') 
    get_states_of_classes_from_module(topo,states_of_classes,[],exclude)


    ### Get startup commands
    #
    startup_commands = topo.sim.startup_commands


    ### Set the release version for this simulation.
    #
    topo.sim.RELEASE = topo.release


    ### Pickle the simulation itself
    #
    # Note that simulation is subjected to two levels of pickling so
    # that commands can be executed before it's unpickled.
    # CEBHACKALERT: someone should figure out if that is really
    # necessary
    pickled_sim=StringIO.StringIO()
    p = ExtraPickler(pickled_sim,2)
    p.dump(topo.sim.actual_sim)

    ### Now pickle the lot to a file
    #
    q = ExtraPickler(open(snapshot_name,'wb'),2)
    q.dump((startup_commands,states_of_classes,pickled_sim))
    pickled_sim.close() # necessary?


def load_snapshot(snapshot_name):
    """
    Load the simulation stored in snapshot_name.

    First executes any commands that were stored previously in
    topo.sim.startup_commands, then restores class attributes
    for ParameterizedObjects, then loads the simulation.
    """
    u = ExtraUnpickler(open(snapshot_name,'rb'))
    startup_commands,states_of_classes,pickled_sim = u.load()

    ### First execute the startup commands
    #
    for cmd in startup_commands:
        exec cmd in __main__.__dict__


    ### Now set class attributes
    #
    # i.e. execute the command "path.to.module.Class.x=y" for each
    for class_name,state in states_of_classes.items():

        # Import class back to __main__
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

    # CEBHACKALERT? Assumes parameters weren't added dynamically to a class
    # i.e. they're all in the source code.

    ### Now unpickle the simulation and set it to be topo.sim
    #
    pickled_sim.seek(0)
    v = ExtraUnpickler(pickled_sim)
    topo.sim.change_sim(v.load())

