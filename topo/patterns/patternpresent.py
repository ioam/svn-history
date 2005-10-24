"""
patternpresent.py

Functions for presenting PatternGenerators to Simulator objects.
Designed with the intention that users can use pattern_present to
temporarily (or permanently) change the default PatternGenerator in
InputSheets.

NOTE: It may be reasonable to reorganize the functions into some form
of object.
"""

from topo.base.topoobject import TopoObject
from topo.base.sheet import Sheet
import topo.base.simulator
import topo.base.registry
from topo.sheets.generatorsheet import GeneratorSheet


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


def save_current_input_generators(sim=None):
    """
    For each of the GeneratorSheets in the given simulation,
    save the current input_generator (onto the stack).
    """
    if not sim:
        sim = topo.base.registry.active_sim()

    if sim:
        generator_sheets = sim.objects(GeneratorSheet).values()
        for sheet in generator_sheets:
            sheet.save_current_input_generator()
    else:
        TopoObject().warning('No active Simulator.')


def restore_previous_input_generators(sim=None):
    """
    For each of the GeneratorSheets in the given simulation,
    restore the previous input_generator (from the stack).
    """
    if not sim:
        sim = topo.base.registry.active_sim()

    if sim:
        generator_sheets = sim.objects(GeneratorSheet).values()
        for sheet in generator_sheets:
            sheet.restore_previous_input_generator()
    else:
        TopoObject().warning('No active Simulator.')



def pattern_present(inputs=None,duration=1.0,sim=None, learning=False):
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
        # turn off sheets' learning if learning=False
        if not learning:
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.learning = False
                    
                gen_eps_list = sim.objects(GeneratorSheet)
        _register_inputsheet_patterns(inputs,gen_eps_list)
        sim.run(duration)

        # turn sheets' learning back on if we turned it off before
        if not learning:
            for each in sim.get_event_processors():
                if isinstance(each,Sheet):
                    each.learning = True

    else:
        TopoObject().warning('No active Simulator.')
