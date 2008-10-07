"""
High-level user-level commands controlling the entire simulation.
$Id$
"""
__version__='$Revision$'

import cPickle as pickle
import gnosis.xml.pickle
from xml.parsers.expat import ExpatError

import time
import string
import re
import os

import __main__

# gzip module might not have been built (if zlib could not be found when building)
try:
    import gzip
except ImportError:
    pass

from .. import param
from ..param.parameterized import PicklableClassAttributes

import topo
from topo.base.functionfamily import OutputFn
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet
from topo.base.projection import Projection, ProjectionSheet
from topo.sheet.generator import GeneratorSheet
from topo.misc.util import ExtraPickler
from topo.misc.filepath import normalize_path
from topo.misc import filepath




def save_input_generators():
    """Save a copy of the active_sim's current input_generators for all GeneratorSheets."""
    # ensure EPs get started (if save_input_generators is called before the simulation is run())
    topo.sim.run(0.0) 

    generator_sheets = topo.sim.objects(GeneratorSheet).values()
    for sheet in generator_sheets:
        sheet.push_input_generator()


def restore_input_generators():
    """Restore previously saved input_generators for all of topo.sim's GeneratorSheets."""
    generator_sheets = topo.sim.objects(GeneratorSheet).values()
    for sheet in generator_sheets:
        sheet.pop_input_generator()


def clear_event_queue():
    """Remove pending events from the simulator's event queue."""
    topo.sim.event_clear()


def pattern_present(inputs={},duration=1.0,plastic=False,overwrite_previous=False,apply_output_fn=True):
    """
    Present the specified test patterns for the specified duration.

    Given a set of input patterns (dictionary of
    GeneratorSheetName:PatternGenerator pairs), installs them into the
    specified GeneratorSheets, runs the simulation for the specified
    length of time, then restores the original patterns and the
    original simulation time.  Thus this input is not considered part
    of the regular simulation, and is usually for testing purposes.

    As a special case, if 'inputs' is just a single pattern, and not
    a dictionary, it is presented to all GeneratorSheets.
    
    If a simulation is not provided, the active simulation, if one
    exists, is requested.

    If this process is interrupted by the user, the temporary patterns
    may still be installed on the retina.

    If overwrite_previous is true, the given inputs overwrite those
    previously defined.

    If plastic is False, overwrites the existing values of Sheet.plastic
    to disable plasticity, then reenables plasticity.
    """
    # ensure EPs get started (if pattern_present is called before the simulation is run())
    topo.sim.run(0.0) 
    
       
    if not overwrite_previous:
        save_input_generators()

    if not plastic:
        # turn off plasticity everywhere
        for sheet in topo.sim.objects(Sheet).values():
             sheet.override_plasticity_state(new_plasticity_state=False)

    if not apply_output_fn:
        for each in topo.sim.objects(Sheet).values():
            if hasattr(each,'measure_maps'):
               if each.measure_maps: 
                   each.apply_output_fn = False

    # Register the inputs on each input sheet
    generatorsheets = topo.sim.objects(GeneratorSheet)
    if not isinstance(inputs,dict):
        for g in generatorsheets.values():
            g.set_input_generator(inputs)
    else:
        for each in inputs.keys():
            if generatorsheets.has_key(each):
                generatorsheets[each].set_input_generator(inputs[each])
            else:
                param.Parameterized().warning(
                    '%s not a valid Sheet name for pattern_present.' % each)

    topo.sim.event_push()
    topo.sim.run(duration) 
    topo.sim.event_pop()

    # turn sheets' plasticity and output_fn plasticity back on if we turned it off before

    if not plastic:
        for sheet in topo.sim.objects(Sheet).values():
            sheet.restore_plasticity_state()
          
    if not apply_output_fn:
        for each in topo.sim.objects(Sheet).values():
            each.apply_output_fn = True
 
        
    if not overwrite_previous:
        restore_input_generators()


def save_snapshot(snapshot_name=None,xml=False):
    """
    Save a snapshot of the network's current state.

    The snapshot is saved as a gzip-compressed Python binary pickle.

    (xml snapshots are currently experimental, and will not be useful
    for most users.)

    As this function uses Python's 'pickle' module, it is subject to
    the same limitations (see the pickle module's documentation) -
    with the notable exception of class attributes. Python does not
    pickle class attributes, but this function stores class attributes
    of any Parameterized class that is declared within the topo
    package. See the topo.param.parameterized.PicklableClassAttributes
    class for more information.
    """
    if not snapshot_name:
        snapshot_name = topo.sim.basename() + ".typ"

    # For now we just search topo, but could do same for other packages.
    topoPOclassattrs = PicklableClassAttributes(topo,exclusions=('plotting','tests','tkgui'),
                                                startup_commands=topo.sim.startup_commands)

    topo.sim.RELEASE=topo.release
    topo.sim.VERSION=topo.version

    # CEBHACKALERT: is a tuple guaranteed to be unpacked in order?
    # If not, then startup commands are not necessarily executed before
    # the simulation is unpickled
    to_save = (topoPOclassattrs,ExtraPickler(),topo.sim)

    if not xml:
        try:
            snapshot_file=gzip.open(normalize_path(snapshot_name),'w',compresslevel=5)
        except NameError:
            snapshot_file=open(normalize_path(snapshot_name),'w')

        pickle.dump(to_save,snapshot_file,2)
    else:
        snapshot_file=open(normalize_path(snapshot_name),'w')
        gnosis.xml.pickle.dump(to_save,snapshot_file,2,allow_rawpickles=True)
    
    snapshot_file.close()



def _load_pickle(snapshot):
    # If it's not xml, open as a normal pickle.
    try:
        gnosis.xml.pickle.load(snapshot,allow_rawpickles=True,class_search=gnosis.xml.pickle.SEARCH_ALL)
    except ExpatError:
        snapshot.seek(0) 
        pickle.load(snapshot)
    

def load_snapshot(snapshot_name):
    """
    Load the simulation stored in snapshot_name.
    """
    # unpickling the PicklableClassAttributes() executes startup_commands and
    # sets PO class parameters.

    # If it's not gzipped, open as a normal file.
    try:
        snapshot = gzip.open(snapshot_name,'r')
        snapshot.read(1)
        snapshot.seek(0)
    except (IOError,NameError):
        snapshot = open(snapshot_name,'r')

        
    try:
        _load_pickle(snapshot)
    except: # what?
        p = param.Parameterized(name="load_snapshot")
        p.message("snapshot '%s' couldn't be loaded; installing legacy support"%snapshot_name)
        import topo.misc.legacy as L 
        L.SnapshotSupport.install()
        try:
            _load_pickle(snapshot)
            p.message("snapshot loaded successfully with legacy support")
        except: # what?
            m = "snapshot could not be loaded. If you make a copy " + \
                "of the snapshot available to Topographica's developers, support " + \
                "can probably be added to Topographica; please email " + \
                "developers[at]topographica.org, or file a bug report at " + \
                "www.sf.net/projects/topographica.\n" + \
                "Error:"
            p.warning(m)
            raise 

    snapshot.close()


def save_script_repr(script_name=None):
    """
    Save the current simulation as a Topographica script.

    Generates a script that, if run, would generate a simulation with
    the same architecture as the one currently in memory.  This can be
    useful when defining networks in place, so that the same general
    configuration can be recreated later.  It also helps when
    comparing two similar networks generated with different scripts,
    so that the corresponding items can be matched rigorously.

    Note that the result of this operation is usually just a starting
    point for further editing, because it will not usually be runnable
    as-is (for instance, some parameters may not have runnable
    representations).  Even so, this is usually a good start.
    """
    if not script_name:
        script_name = topo.sim.basename() + "_script_repr.ty"
        
    header = ("# Generated by Topographica %s on %s\n\n" %
              (topo.release,time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())))
    script = header+topo.sim.script_repr()
    
    script_file = open(normalize_path(script_name),'w')
    script_file.write(script)


# Used only by default_analysis_function
# Should be in order they are needed; e.g. Activity after map measurement,
# in case Activity plot includes map subplots
default_analysis_plotgroups=["Orientation Preference","Activity"]

def default_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    import topo
    from topo.command.analysis import save_plotgroup
    from topo.base.projection import ProjectionSheet
    from topo.sheet.generator import GeneratorSheet

    # Build a list of all sheets worth measuring
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(ProjectionSheet).values())
    input_sheets = topo.sim.objects(GeneratorSheet).values()
    
    # Set potentially reasonable defaults; not necessarily useful
    topo.command.analysis.coordinate=(0.0,0.0)
    if input_sheets:    topo.command.analysis.input_sheet_name=input_sheets[0].name
    if measured_sheets: topo.command.analysis.sheet_name=measured_sheets[0].name

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    # Save at least one projection plot
    if measured_sheets:
        for p in measured_sheets[0].in_connections:
            save_plotgroup("Projection",projection=p)

    # Test response to a standardized pattern
    from topo.pattern.basic import Gaussian
    from math import pi
    pattern_present(inputs=Gaussian(orientation=pi/4,aspect_ratio=4.7))
    save_plotgroup("Activity",saver_params={"filename_suffix":"_45d"})


# JAB: Should also have some sort of time scaling, so that sims with
# different lengths don't need an entirely new set of analysis times.
# Should encode the cvs state somehow in the output directory, in a
# form that could be used to recreate the CVS version of each file
# used.  Should at least copy the script file into the output directory,
# in any case.
def run_batch(script_file,output_directory="Output",
              analysis_fn = default_analysis_function,
              times = 1.0,**params):
    """
    Run a Topographica simulation in batch mode.

    Features:

      - Generates a unique, well-defined name for each 'experiment'
        (i.e. simulation run) based on the date, script file, and
        parameter settings

      - Allows parameters to be varied on the command-line,
        to allow comparing various settings

      - Saves a script capturing the simulation state periodically,
        to preserve parameter values from old experiments and to allow
        them to be reproduced exactly later

      - Can perform user-specified analysis routines periodically,
        to monitor the simulation as it progresses.

      - Stores commandline output (stdout) in the output directory
        
    A typical use of this function is for remote execution of a large
    number of simulations with different parameters, often on remote
    machines (such as clusters).
    
    The script_file parameter defines the .ty script we want to run in
    batch mode. The output_directory defines the root directory in
    which a unique individual directory will be created for this
    particular run.  The optional analysis_fn can be any python
    function to be called at each of the simulation iterations defined
    in the analysis times list.  The analysis_fn should perform
    whatever analysis of the simulation you want to perform, such as
    plotting or calculating some statistics.  The analysis_fn should
    avoid using any GUI functions (i.e., should not import anything
    from topo.tkgui), and it should save all of its results into
    files.

    As a special case, a number can be passed for the times list, in
    which case it is used to scale a default list of times up to
    10000; e.g. times=2 will select a default list of times up to
    20000.  Alternatively, an explicit list of times can be supplied.

    Any other optional parameters supplied will be set in the main
    namespace before any scripts are run.  They will also be used to
    construct a unique topo.sim.name for the file, and they will be
    encoded into the simulation directory name, to make it clear how
    each simulation differs from the others.
    """
    import sys # CEBALERT: why I have to import this again? (Also done elsewhere below.)
    
   
    from topo.misc.commandline import auto_import_commands
    auto_import_commands()
    
    command_used_to_start = string.join(sys.argv)
    
    starttime=time.time()
    startnote = "Batch run started at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())
    print startnote

    # Ensure that saved state includes all parameter values
    from topo.command.basic import save_script_repr
    param.parameterized.script_repr_suppress_defaults=False

    # Make sure pylab plots are saved to disk

    # Construct simulation name
    scriptbase= re.sub('.ty$','',os.path.basename(script_file))
    prefix = ""
    prefix += time.strftime("%Y%m%d%H%M")
    prefix += "_" + scriptbase

    simname = prefix

    # Construct parameter-value portion of filename; should do more filtering
    for a in params.keys():
        val=params[a]
        
        # Special case to give reasonable filenames for lists
        valstr= ("_".join([str(i) for i in val]) if isinstance(val,list)
                 else str(params[a]))
        prefix += "," + a + "=" + valstr


    # Set provided parameter values in main namespace
    for a in params.keys():
        __main__.__dict__[a] = params[a]


    # Create output directories
    if not os.path.isdir(normalize_path(output_directory)):
        os.mkdir(normalize_path(output_directory))

    filepath.output_path = normalize_path(os.path.join(output_directory,prefix))
    
    if os.path.isdir(filepath.output_path):
	print "Batch run: Warning -- directory: " +  \
              filepath.output_path + \
              " already exists! Run aborted; rename directory or wait one minute before trying again."
        import sys
        sys.exit(-1)
    else:
	os.mkdir(filepath.output_path)
        print "Batch run output will be in " + filepath.output_path

    ##################################
    # capture stdout
    #
    import StringIO
    stdout = StringIO.StringIO()
    sys.stdout = stdout
    ##################################

    # Default case: times is just a number that scales a standard list of times
    if not isinstance(times,list):
        times=[t*times for t in [50,100,500,1000,2000,3000,4000,5000,10000]]

    # Run script in main
    try:
        execfile(script_file,__main__.__dict__)

        topo.sim.name=simname

        # Run each segment, doing the analysis and saving the script state each time
        for run_to in times:
            topo.sim.run(run_to - topo.sim.time())
            analysis_fn()
            save_script_repr()
            elapsedtime=time.time()-starttime
            param.Parameterized(name="run_batch").message(
                "Elapsed real time %02d:%02d." % (int(elapsedtime/60),int(elapsedtime%60)))
    except:
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stderr.write("Warning -- Error detected: execution halted.\n")


    endnote = "Batch run completed at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())

    ##################################
    # Write stdout to output file and restore original stdout
    stdout_file = open(normalize_path(simname+".out"),'w')
    stdout_file.write(command_used_to_start+"\n")
    stdout_file.write(startnote+"\n")
    stdout_file.write(stdout.getvalue())
    stdout_file.write(endnote+"\n")
    stdout.close()
    sys.stdout = sys.__stdout__
    ##################################

    # ALERT: Need to count number of errors and warnings and put that on stdout
    # and at the end of the .out file, so that they will be sure to be noticed.
    
    print endnote


def wipe_out_activity():
    """
    Resets activity of all Sheets and their connections to zero.
    """
    # ALERT: this works for now, but it may need to be implemented
    # recursively using methods implemented separately on each class,
    # if there are often new types of objects created that store an
    # activity value.
    for s in topo.sim.objects(Sheet).values():
        s.activity*=0.0
        for c in s.in_connections:
            if hasattr(c,'activity'):
                c.activity*=0.0


# maybe an explicit list would be better?
import types
__all__ = list(set([k for k,v in locals().items()
                    if isinstance(v,types.FunctionType)
                    and not v.__name__.startswith('_')]))
