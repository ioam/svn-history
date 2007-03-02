"""
High-level user-level commands controlling the entire simulation.
$Id$
"""
__version__='$Revision$'

import cPickle as pickle
import gnosis.xml.pickle

import __main__
import gzip

import topo

from topo.base.parameterizedobject import ParameterizedObject, Parameter, PicklableClassAttributes
from topo.base.functionfamilies import OutputFn
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet
from topo.base.projection import ProjectionSheet
from topo.sheets.generatorsheet import GeneratorSheet


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


def save_snapshot(snapshot_name,xml=False):
    """
    Save a snapshot of the network's current state.

    The snapshot is saved as a gzip-compressed Python binary pickle.

    (xml snapshots are currently experimental, and will not work for
    most users.)

    As this function uses Python's 'pickle' module, it is subject to
    the same limitations (see the pickle module's documentation) -
    with the notable exception of class attributes. Python does not
    pickle class attributes, but this function stores class attributes
    of any ParameterizedObject class that is declared within the topo
    package. See the topo.base.PicklableClassAttributes class for more
    information.
    """    
    # For now we just search topo, but could do same for other packages.
    topoPOclassattrs = PicklableClassAttributes(topo,exclusions=('plotting','tests','tkgui'),
                                                startup_commands=topo.sim.startup_commands)

    topo.sim.RELEASE=topo.release

    # CEBHACKALERT: is a tuple guaranteed to be unpacked in order?
    # If not, then startup commands are not necessarily executed before
    # the simulation is unpickled
    if xml:
        # CEBALERT: gnosis.xml.pickle needs updating to work with
        # numpy.  However, you can test saving a simulation that
        # does not import numpy to see what the xml looks like.
        ParameterizedObject(name="save_snapshot").warning("XML snapshots are only experimental at present.")
        gnosis.xml.pickle.dump( (topoPOclassattrs,topo.sim) , open(snapshot_name,'w') )
    else:
        pickle.dump( (topoPOclassattrs,topo.sim) , gzip.open(snapshot_name,'w',compresslevel=5),2)


def load_snapshot(snapshot_name, xml=False):
    """
    Load the simulation stored in snapshot_name.
    """
    # unpickling the PicklableClassAttributes() executes startup_commands and
    # sets PO class parameters.

    snapshot = gzip.open(snapshot_name,'r')

    # If it's not gzipped, open as a normal file.
    try:
        snapshot.read(1)
        snapshot.seek(0)
    except IOError:
        snapshot = open(snapshot_name,'r')

    if xml:
        gnosis.xml.pickle.load(snapshot)
    else:
        pickle.load(snapshot)
    
    




