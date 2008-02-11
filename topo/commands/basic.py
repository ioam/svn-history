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

import topo

from topo.base.parameterizedobject import ParameterizedObject, Parameter, PicklableClassAttributes
from topo.base.functionfamilies import OutputFn
from topo.base.sheet import Sheet
from topo.base.cf import CFSheet
from topo.base.projection import ProjectionSheet

from topo.sheets.generatorsheet import GeneratorSheet

from topo.misc.utils import ExtraPickler
from topo.misc.filepaths import normalize_path
from topo.misc import filepaths


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


def pattern_present(inputs={},duration=1.0,plastic=False,overwrite_previous=False,apply_output_fn=True):
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
             sheet.disable_plasticity()

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

    # turn sheets' plasticity and output_fn plasticity back on if we turned it off before

    if not plastic:
        for sheet in topo.sim.objects(Sheet).values():
            sheet.restore_plasticity()
          
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
    of any ParameterizedObject class that is declared within the topo
    package. See the topo.base.PicklableClassAttributes class for more
    information.
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

    # If it's not xml, open as a normal pickle.
    try:
        gnosis.xml.pickle.load(snapshot,allow_rawpickles=True,class_search=gnosis.xml.pickle.SEARCH_ALL)
    except ExpatError:
        snapshot.seek(0) 
        pickle.load(snapshot)


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
default_analysis_plotgroups=["Activity","Orientation Preference"]

def default_analysis_function():
    """
    Basic example of an analysis command for run_batch; users are
    likely to need something similar but highly customized.
    """
    import topo
    from topo.commands.analysis import save_plotgroup
    from topo.base.projection import ProjectionSheet
    from topo.sheets.generatorsheet import GeneratorSheet

    # Build a list of all sheets worth measuring
    f = lambda x: hasattr(x,'measure_maps') and x.measure_maps
    measured_sheets = filter(f,topo.sim.objects(ProjectionSheet).values())
    input_sheets = topo.sim.objects(GeneratorSheet).values()
    
    # Set potentially reasonable defaults; not necessarily useful
    topo.commands.analysis.coordinate=(0.0,0.0)
    if input_sheets:    topo.commands.analysis.input_sheet_name=input_sheets[0].name
    if measured_sheets: topo.commands.analysis.sheet_name=measured_sheets[0].name

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg)

    # Plot all projections for all measured_sheets
    for s in measured_sheets:
        for p in s.projections().values():
            save_plotgroup("Projection",projection=p)



# JAB: Should also have some sort of time scaling, so that sims with
# different lengths don't need an entirely new set of analysis times.
# Should encode the cvs state somehow in the output directory, in a
# form that could be used to recreate the CVS version of each file
# used.  Should at least copy the script file into the output directory,
# in any case.
def run_batch(script_file,output_directory="Output",
              analysis_fn = default_analysis_function,
              times = [50,100,500,1000,2000,3000,4000,5000,10000],
              **params):
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
    in the analysis times list.  This function should perform whatever
    analysis of the simulation you want to perform, such as plotting
    or calculating some statistics.  The analysis_fn should avoid
    using any GUI functions (i.e., should not import anything from
    topo.tkgui), and it should save all of its results into files.

    Any other optional parameters supplied will be set in the main
    namespace before any scripts are run.  They will also be used to
    construct a unique topo.sim.name for the file, and they will be
    encoded into the simulation directory name, to make it clear how
    each simulation differs from the others.
    """
    import sys # CEBALERT: why I have to import this again? (Also done elsewhere below.)
    command_used_to_start = string.join(sys.argv)
    
    starttime=time.time()
    startnote = "Batch run started at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                           time.gmtime())
    print startnote

    # Ensure that saved state includes all parameter values
    from topo.commands.basic import save_script_repr
    from topo.base import parameterizedobject
    parameterizedobject.script_repr_suppress_defaults=False

    # Make sure pylab plots are saved to disk
    import matplotlib 
    matplotlib.use('Agg') # Is 'GD' required on some platforms?

    # Construct simulation name
    scriptbase= re.sub('.ty$','',os.path.basename(script_file))
    prefix = ""
    prefix += time.strftime("%Y%m%d%H%M")
    prefix += "_" + scriptbase

    simname = prefix

    if params.keys():
        for a in params.keys():
           prefix += "," + a + "=" + str(params[a])

    # Set provided parameter values in main namespace
    for a in params.keys():
        __main__.__dict__[a] = params[a]


    # Create output directories
    if not os.path.isdir(normalize_path(output_directory)):
        os.mkdir(normalize_path(output_directory))

    filepaths.output_path = normalize_path(os.path.join(output_directory,prefix))
    
    if os.path.isdir(filepaths.output_path):
	print "Batch run: Warning -- directory: " +  \
              filepaths.output_path + \
              " already exists! Run aborted; rename directory or wait one minute before trying again."
        import sys
        sys.exit(-1)
    else:
	os.mkdir(filepaths.output_path)
        print "Batch run output will be in " + filepaths.output_path

    ##################################
    # capture stdout
    #
    import StringIO
    stdout = StringIO.StringIO()
    sys.stdout = stdout
    ##################################


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
            parameterizedobject.ParameterizedObject(name="run_batch").message(
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
    
    print endnote

def wipe_out_activity():
    """
    Resets to zeros the activity in the sheets and projection activities of all sheets in the model
    """
    for sheet in topo.sim.objects().keys():
        topo.sim[sheet].activity*=0.0
        for con in topo.sim[sheet].in_connections:
            if hasattr(con, 'activity'):
                con.activity*=0.0
