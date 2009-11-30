"""
High-level user-level commands controlling the entire simulation.
$Id$
"""
__version__='$Revision$'

import cPickle as pickle

from xml.parsers.expat import ExpatError

import os,sys,re,string,time,platform

import __main__

# gzip module might not have been built (if zlib could not be found when building)
try:
    import gzip
except ImportError:
    pass


import param
from param.parameterized import PicklableClassAttributes, ParameterizedFunction
from param.parameterized import ParamOverrides
from param.external import OrderedDict

import topo
from topo.base.functionfamily import TransferFn
from topo.base.sheet import Sheet
from topo.base.projection import Projection, ProjectionSheet
from topo.sheet import GeneratorSheet
from topo.misc.util import MultiFile
from topo.misc.picklemain import PickleMain
from topo.misc.filepath import normalize_path
from topo.misc import filepath
from topo.base.functionfamily import PatternDrivenAnalysis

try:
    import gnosis.xml.pickle
    gnosis_imported = True
except ImportError:
    param.Parameterized().message("No 'gnosis' module: xml snapshots unavailable.")
    gnosis_imported = False




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


def pattern_present(inputs={},duration=1.0,plastic=False,overwrite_previous=False,apply_output_fns=True):
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

    if not apply_output_fns:
        for each in topo.sim.objects(Sheet).values():
            if hasattr(each,'measure_maps'):
               if each.measure_maps: 
                   each.apply_output_fns = False

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
    # CBENHANCEMENT: would be nice to break this up for visualizing motion
    topo.sim.run(duration) 
    topo.sim.event_pop()

    # turn sheets' plasticity and output_fn plasticity back on if we turned it off before

    if not plastic:
        for sheet in topo.sim.objects(Sheet).values():
            sheet.restore_plasticity_state()
          
    if not apply_output_fns:
        for each in topo.sim.objects(Sheet).values():
            each.apply_output_fns = True
 
        
    if not overwrite_previous:
        restore_input_generators()



class _VersionPrinter(object):
    """When unpickled, prints version & release information about snapshot."""
    def __init__(self,release,version):
        self.release = release
        self.version = version
    def __getstate__(self):
        return {'release':self.release,
                'version':self.version}
    def __setstate__(self,state):
        release = state['release']
        version = state['version']
        self.release=release
        self.version=version
        param.Parameterized(name="load_snapshot").debug("Snapshot is from release '%s' (version '%s')."%(release,version))
        

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
    package. See the param.parameterized.PicklableClassAttributes
    class for more information.
    """
    if not snapshot_name:
        snapshot_name = topo.sim.basename() + ".typ"

    # For now we just search topo, but could do same for other packages.
    topoPOclassattrs = PicklableClassAttributes(topo,exclusions=('plotting','tests','tkgui'),
                                                startup_commands=topo.sim.startup_commands)

    from topo.misc.commandline import global_params

    topo.sim.RELEASE=topo.release
    topo.sim.VERSION=topo.version

    # CEBHACKALERT: is a tuple guaranteed to be unpacked in order?
    # If not, then startup commands are not necessarily executed before
    # the simulation is unpickled
    #
    # CB: if we first pickle.dumps() each of these things, then
    # pickle.dump() a dictionary (probably), we'll have more control
    # over unpickling. E.g. we could in the future choose not to
    # unpickle something. And we can certainly control the unpickling
    # order this way.
    
    to_save = (_VersionPrinter(topo.release,topo.version),PickleMain(),global_params,topoPOclassattrs,topo.sim)

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
    if gnosis_imported:
        try:
            gnosis.xml.pickle.load(snapshot,allow_rawpickles=True,class_search=gnosis.xml.pickle.SEARCH_ALL)
        except ExpatError:
            snapshot.seek(0) 
            # If it's not xml, open as a normal pickle.
            pickle.load(snapshot)
    else:
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
            
            # CEBALERT: should store original exception so it can be
            # displayed here.
    
            m = """
            Snapshot could not be loaded.

            If you make a copy of the snapshot available to
            Topographica's developers, support for it can be added to
            Topographica; please file a bug report via the website.

            Error:
            """
            p.warning(m)
            raise 

    snapshot.close()

    # Restore subplotting prefs without worrying if there is a
    # problem (e.g. if topo/analysis/ is not present)
    try: 
        from topo.analysis.featureresponses import Subplotting
        Subplotting.restore_subplots()
    except:
        p = param.Parameterized(name="load_snapshot")
        p.message("Unable to restore Subplotting settings")




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


# decorator that changes to filepath.application_path for duration of fn
def in_application_path(fn):
    import os
    def temporarily_change_to_application_path(*args,**kw):
        orig_path = os.getcwd()
        os.chdir(filepath.application_path)
        try:
            result = fn(*args,**kw)
        finally:
            # ensure dir put back even if there's an error calling fn
            os.chdir(orig_path)
        return result
    return temporarily_change_to_application_path


@in_application_path
def _get_vc_commands():
    # return name of version control system (None if no vc could be
    # detected)
    import os.path
    vc_types = {'git':["status","diff",["log","-n1"],["svn","log","--limit=1"]],
                'svn':["info","status","diff"],
                'bzr':['info','status','diff']}
    for vc_type,commands in vc_types.items():
        if os.path.exists(".%s"%vc_type):
            return vc_type,commands

@in_application_path
def _print_vc_info(filename):
    """Save the version control status of the current code to the specified file."""
    try:
        import subprocess
        file = open(normalize_path(filename),'w')
        file.write("Information about working copy used for batch run\n\n")
        file.write("topo.version=%s\n"% topo.version)
        file.flush()
        vctype,commands = _get_vc_commands()
        for cmd in commands:
            fullcmd = [vctype,cmd] if isinstance(cmd,str) else [vctype]+cmd
        
            # Note that we do not wait for the process below to finish
            # (by calling e.g. wait() on the Popen object). Although
            # this was probably done unintentionally, for a slow svn
            # connection, it's an advantage. But it does mean the
            # output of each command can appear in the file at any
            # time (i.e. the command outputs appear in the order of
            # finishing, rather than in the order of starting, making
            # it impossible to label the commands).
            subprocess.Popen(fullcmd,stdout=file,stderr=subprocess.STDOUT)
    except:
        print "Unable to retrieve version control information."
    finally:
        file.close()

@in_application_path
def _save_parameters(p,filename):
    from topo.misc.commandline import global_params
    
    g = {'global_params_specified':p,
         'global_params_all':dict(global_params.get_param_values())}

    for d in g.values():
        if 'name' in d:
            del d['name']
        if 'print_level' in d:
            del d['print_level']

    pickle.dump(g,open(normalize_path(filename),'w'))
     

# I'd expect your personal name_replacements to be set in some file
# you use to create batch runs, but it can alsp be set on the
# commandline. Before calling run_batch(), include something like the
# following:
# run_batch.dirname_params_filter.map=OrderedDict(("cortex_density","cd"))

class param_formatter(ParameterizedFunction):

    # CEBALERT: should I have made this a parameter at the run_batch
    # level? And I don't know what to call it.
    map = param.Dict(default=OrderedDict(),doc="""
        Optional ordered dictionary of alternative names to use for
        parameters, parameter_name:alternative_name

        Use to shorten common parameter names (directory names are
        limited in length on most file systems), and to specify an
        order.

        Names not specified here will be sorted alphabetically.""")

    def __call__(self,params):
        result = ""        
        unspecified_in_map = sorted(set(params).difference(set(self.map)))
        for pname in self.map.keys()+unspecified_in_map:
            val = params[pname]
            # Special case to give reasonable filenames for lists
            valstr= ("_".join([str(i) for i in val]) if isinstance(val,list)
                     else str(val))
            result += "," + self.map.get(pname,pname) + "=" + valstr
        return result


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

    # Save all plotgroups listed in default_analysis_plotgroups
    for pg in default_analysis_plotgroups:
        save_plotgroup(pg,use_cached_results=True)

    # Plot projections from each measured map
    measured_sheets = [s for s in topo.sim.objects(ProjectionSheet).values()
                       if hasattr(s,'measure_maps') and s.measure_maps]
    for s in measured_sheets:
        for p in s.in_connections:
            save_plotgroup("Projection",projection=p)

    # Test response to a standardized pattern
    from topo.pattern.basic import Gaussian
    from math import pi
    pattern_present(inputs=Gaussian(orientation=pi/4,aspect_ratio=4.7))
    save_plotgroup("Activity",saver_params={"filename_suffix":"_45d"})


# ALERT: Need to move docs into params.
class run_batch(ParameterizedFunction):
    """
    Run a Topographica simulation in batch mode.

    Features:

      - Generates a unique, well-defined name for each 'experiment'
        (i.e. simulation run) based on the date, script file, and
        parameter settings. Note that very long names may be truncated
        (see the max_name_length parameter).

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

    If requested by setting snapshot=True, saves a snapshot at the
    end of the simulation.

    If available and requested by setting vc_info=True, prints
    the revision number and any outstanding diffs from the version
    control system.
    """
    output_directory=param.String("Output")

    analysis_fn = param.Callable(default_analysis_function)
    
    times = param.Parameter(1.0)

    snapshot=param.Boolean(True)

    vc_info=param.Boolean(True)

    dirname_prefix = param.String(default="",doc="""
        Optional prefix for the directory name (allowing e.g. easy
        grouping).""")

    # CB: do any platforms also have a maximum total path length?
    max_name_length = param.Number(default=200,doc="""
        The experiment's directory name will be truncated at this
        number of characters (since most filesystems have a
        limit).""")

    name_time_format = param.String(default="%Y%m%d%H%M",doc="""
        String format for the time included in the output directory
        and file names.  See the Python time module library
        documentation for codes.
        
        E.g. Adding '%S' to the default would include seconds.""")

    save_global_params = param.Boolean(default=True,doc="""
        Whether to save the script's global_parameters to a pickle in
        the output_directory after the script has been loaded (for
        e.g. future inspection of the experiment).""")

    dirname_params_filter = param.Callable(param_formatter.instance(),doc="""
        Function to control how the parameter names will appear in the
        output_directory's name.""")


    def _truncate(self,p,s):
        """
        If s is greater than the max_name_length parameter, truncate it
        (and indicate that it has been truncated).
        """
        # '___' at the end is supposed to represent '...'
        return s if len(s)<=p.max_name_length else s[0:p.max_name_length-3]+'___' 
                
    def __call__(self,script_file,**params_to_override):
        p=ParamOverrides(self,params_to_override,allow_extra_keywords=True)

        import sys # CEBALERT: why do I have to import this again? (Also done elsewhere below.)
        import os
        import shutil
    
        # Construct simulation name, etc.
        scriptbase= re.sub('.ty$','',os.path.basename(script_file))
        prefix = ""
        prefix += time.strftime(p.name_time_format)
        prefix += "_" + scriptbase
        simname = prefix

        # Construct parameter-value portion of filename; should do more filtering
        # CBENHANCEMENT: should provide chance for user to specify a
        # function (i.e. make this a function, and have a parameter to
        # allow the function to be overridden).
        # And sort by name by default? Skip ones that aren't different
        # from default, or at least put them at the end?
        prefix += p.dirname_params_filter(p.extra_keywords())

        # Set provided parameter values in main namespace
        from topo.misc.commandline import global_params
        global_params.set_in_context(**p.extra_keywords())
    
        # Create output directories
        if not os.path.isdir(normalize_path(p['output_directory'])):
            os.mkdir(normalize_path(p['output_directory']))
    
        
        dirname = self._truncate(p,p.dirname_prefix+prefix)
        filepath.output_path = normalize_path(os.path.join(p['output_directory'],dirname))
        
        if os.path.isdir(filepath.output_path):
            print "Batch run: Warning -- directory already exists!"
            print "Run aborted; wait one minute before trying again, or else rename existing directory: \n" + \
                  filepath.output_path
    
            import sys
            sys.exit(-1)
        else:
            os.mkdir(filepath.output_path)
            print "Batch run output will be in " + filepath.output_path
    
    
        if p['vc_info']:
            _print_vc_info(simname+".diffs")
    
        hostinfo = "Host: " + " ".join(platform.uname())
        topographicalocation = "Topographica: " + os.path.abspath(sys.argv[0])
        topolocation = "topo package: " + os.path.abspath(topo.__file__)
        scriptlocation = "script: " + os.path.abspath(script_file)

        starttime=time.time()
        startnote = "Batch run started at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                               time.gmtime())
        command_used_to_start = string.join(sys.argv)
    
        # Shadow stdout to a .out file in the output directory, so that
        # print statements will go to both the file and to stdout.
        batch_output = open(normalize_path(simname+".out"),'w')
        batch_output.write(command_used_to_start+"\n")
        sys.stdout = MultiFile(batch_output,sys.stdout)
    
        print
        print hostinfo
        print topographicalocation
        print topolocation
        print scriptlocation
        print
        print startnote
    
        from topo.misc.commandline import auto_import_commands
        auto_import_commands()
        
        # Ensure that saved state includes all parameter values
        from topo.command.basic import save_script_repr
        param.parameterized.script_repr_suppress_defaults=False
    
        # Save a copy of the script file for reference
        shutil.copy2(script_file, filepath.output_path)
        shutil.move(normalize_path(scriptbase+".ty"),
                    normalize_path(simname+".ty"))
    
        
        # Default case: times is just a number that scales a standard list of times
        times=p['times']
        if not isinstance(times,list):
            times=[t*times for t in [0,50,100,500,1000,2000,3000,4000,5000,10000]]
    
        # Run script in main
        error_count = 0
        initial_warning_count = param.parameterized.warning_count
        try:
            execfile(script_file,__main__.__dict__) #global_params.context
            global_params.check_for_unused_names()
            if p.save_global_params:
                _save_parameters(p.extra_keywords(),simname+".global_params.pickle")
            print_sizes()
            topo.sim.name=simname
    
            # Run each segment, doing the analysis and saving the script state each time
            for run_to in times:
                topo.sim.run(run_to - topo.sim.time())
                p['analysis_fn']()
                save_script_repr()
                elapsedtime=time.time()-starttime
                param.Parameterized(name="run_batch").message(
                    "Elapsed real time %02d:%02d." % (int(elapsedtime/60),int(elapsedtime%60)))
    
            if p['snapshot']:
               save_snapshot()
                
        except:
            error_count+=1
            import traceback
            traceback.print_exc(file=sys.stdout)
            sys.stderr.write("Warning -- Error detected: execution halted.\n")
    
    
        print "\nBatch run completed at %s." % time.strftime("%a %d %b %Y %H:%M:%S +0000",
                                                             time.gmtime())
        print "There were %d error(s) and %d warning(s)%s." % \
              (error_count,(param.parameterized.warning_count-initial_warning_count),
               ((" (plus %d warning(s) prior to entering run_batch)"%initial_warning_count
                 if initial_warning_count>0 else "")))
        
        # restore stdout
        sys.stdout = sys.__stdout__
        batch_output.close()
    


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



def n_bytes():
    """
    Estimate the minimum memory needed for the Sheets in this Simulation, in bytes.

    This estimate is a lower bound only, based primarily on memory for
    the matrices used for activity and connections.
    """
    return sum([s.n_bytes() for s in topo.sim.objects(Sheet).values()])



def n_conns():
    """
    Count the number of connections in all ProjectionSheets in the current Simulation.  
    """     
    return sum([s.n_conns() for s in topo.sim.objects(ProjectionSheet).values()])


def print_sizes():
    """Format the results from n_conns() and n_bytes() for use in batch output."""
    print "Defined %d-connection network; %0.0fMB required for weight storage." % \
    (n_conns(),max(n_bytes()/1024.0/1024.0,1.0))

# added these two function to the PatternDrivenAnalysis hooks 
PatternDrivenAnalysis.pre_presentation_hooks.append(wipe_out_activity)
PatternDrivenAnalysis.pre_presentation_hooks.append(clear_event_queue)

            
# maybe an explicit list would be better?
import types
__all__ = list(set([k for k,v in locals().items()
                    if isinstance(v,types.FunctionType) or 
                    (isinstance(v,type) and issubclass(v,ParameterizedFunction))
                    and not v.__name__.startswith('_')]))
