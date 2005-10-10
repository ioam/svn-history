from topo.base.object import TopoObject
import topo.base.simulator
import topo.base.registry
from topo.sheets.generatorsheet import GeneratorSheet


def generator_eps(sim):
    """
    Return a dictionary of event processors in the passed in simulator
    that can have Factories added to them.

    Post: Key = String name, Value = object.

    Anything that is an GeneratorSheet will be added.
    """
    eps = sim.get_event_processors()
    i_eps = dict([(i.name,i) for i in eps if isinstance(i,GeneratorSheet)])
    return i_eps



def _store_inputsheet_patterns(gen_eps_dict):
    """
    Store the patterns currently in the GeneratorSheets.  This allows
    restoring them if changes are made.

    Pre: gen_eps_dict is a dictionary of GeneratorSheets that can be
    adjusted.  Key is the string name of the GeneratorSheet, Value
    points to the object.

    Post: A new dictionary is returned that has the name entries as
    keys, and each value now has the PatternGenerator object
    originally stored in the GeneratorSheet.
    """
    pattern_dict = dict([(each.name, each.get_input_generator())
                         for each in gen_eps_dict.values()])
    return pattern_dict


def _register_inputsheet_patterns(inputs,gen_eps_dict):
    """
    Make an instantiation of the current user patterns stored in
    inputs, and put them into all of the requested input sheets.

    Pre: inputs is a dictionary with a string name of a GeneratorSheet
    as a key, and a new PatternGenerator as a value.  All PatternGenerators
    must have already been created and their Parameters set.  This includes
    basic ones such as 'bounds' and 'density.'

    Pre: gen_eps_dict is a dictionary (Key: string name, Value: object) of
    the GeneratorSheets that can be adjusted in the Simulator.

    Post: The GeneratorSheets have had their PatternGenerators swapped
    out.  If no effort was previously made to preserve the original
    PatternGenerators then they are lost.
    """
    for each in inputs.keys():
        if gen_eps_dict.has_key(each):
            gen_eps_dict[each].set_input_generator(inputs[each])
        else:
            TopoObject().warning('%s not a valid Sheet Name.' % each)


def pattern_present(inputs=None,duration=1.0,sim=None, restore=True):
    """
    Generalized function that grew out of the inputparamspanel.py
    code.  Move the user created patterns into the GeneratorSheets,
    run for the specified length of time, then restore the original
    patterns.  The system may become unstable if the user breaks this
    thread so that the original patterns are not properly restored,
    but then there are going to be other problems with the Simulator
    state if a run is interrupted.

    This function can be run no matter if learning is enabled or
    disabled since run() will detect sheet attributes.

    -- inputs should be a dictionary with string keys and
       PatternGenerators as values.
    -- duration is length of time to run simulation.
    -- simulator is the Simulator object to drive.  If a simulator is
       not provided, the active simulator, if one exists, is requested.
    -- restore: If this is False, then the original PatternGenerators
       are not replaced in the InputSheets afterward.
    """
    if not sim:
        sim = topo.base.registry.active_sim()
    if sim:
        gen_eps_list = generator_eps(sim)
        original_patterns = _store_inputsheet_patterns(gen_eps_list)
        _register_inputsheet_patterns(inputs,gen_eps_list)
            
        sim.run(duration)
            
        if restore:
            _register_inputsheet_patterns(original_patterns,gen_eps_list)
    else:
        TopoObject().warning('No active Simulator.')
