"""
Contains tests to check a particular script's results or speed have
not changed.

Buildbot shows how to run all these tests.

$Id$
"""
__version__='$Revision$'


import pickle, copy, __main__, timeit, os, os.path, socket, cPickle, inspect, traceback, tempfile, shutil

from numpy.testing import assert_array_equal, assert_array_almost_equal

import param
from param import resolve_path, normalize_path

import topo


# CEBALERT: should get this from somewhere else!
TOPOGRAPHICAHOME = os.path.join(os.path.expanduser("~"),"topographica")

TESTSDATADIR = os.path.join(TOPOGRAPHICAHOME,"tests")
if not os.path.exists(TESTSDATADIR):
    os.makedirs(TESTSDATADIR)

# While training data is usually checked into topo/tests and is the
# same for all machines, speed data is generated by the machine
# running this makefile. Therefore, speed data is stored in a
# machine-specific directory.

MACHINETESTSDATADIR = os.path.join(TESTSDATADIR,socket.gethostname())
if not os.path.exists(MACHINETESTSDATADIR):
    os.makedirs(MACHINETESTSDATADIR)

FIXEDDATADIR = resolve_path("topo/tests",path_to_file=False)



######################################################################################
### Support fns

def _support_old_args(args):
    # support old data files which contain 'default_density', etc
    if 'default_density' in args:
        args['cortex_density']=args['default_density']
        #del args['default_density']
    if 'default_retina_density' in args:
        args['retina_density']=args['default_retina_density']
        #del args['default_retina_density']
    if 'default_lgn_density' in args:
        args['lgn_density']=args['default_lgn_density']
        #del args['default_lgn_density']
    # (left the dels commented out for now in case scripts still use old names)

def _setargs(args):
    for arg,val in args.items():
        print "Setting %s=%s"%(arg,val)
        __main__.__dict__[arg]=val

# For generating data in a separate process, leaving the parent with
# the original settings (i.e. avoids having to do a reset of
# simulation time, etc).
# CEBALERT: is this somehow causing func to run more slowly than
# without forking?
def _run_in_forked_process(func, *args, **kwds):
    # DSALERT: os.fork() is not supported on Windows
    pid = os.fork()
    if pid > 0:
        os.waitpid(pid, 0)
    else: 
        func(*args, **kwds)
        os._exit(0)


def _instantiate_everything(
    classes_to_exclude=("topo.base.simulation.Simulation","topo.base.simulation.Simulation"),
    modules_to_exclude=('plotting','tests','tkgui','command','util')):

    # default excludes currently set up for pickle tests

    # CEBALERT: this is basically get_PO_class_attributes from param.parameterized
    def get_classes(module,classes,processed_modules,module_excludes=()):
        exec "from %s import *"%module.__name__ in locals()
        dict_ = module.__dict__
        for (k,v) in dict_.items():
            if '__all__' in dict_ and inspect.ismodule(v) and k not in module_excludes:
                if k in dict_['__all__'] and v not in processed_modules:
                    get_classes(v,classes,processed_modules,module_excludes)
                processed_modules.append(v)
            else:
                # class & not parameterizedfunction & not __abstract & not excluded & starts with topo. or param.
                if isinstance(v,type) and not isinstance(v,param.ParameterizedFunction) and not (hasattr(v,"_%s__abstract"%v.__name__) and getattr(v,"_%s__abstract"%v.__name__) is True):
                    full_class_path = v.__module__+'.'+v.__name__
                    if (not full_class_path in classes) and (not full_class_path in classes_to_exclude) and (full_class_path.startswith("topo") or full_class_path.startswith("param")):
                        classes.append(full_class_path)

    classes = []
    processed_modules = []
     
    import topo
    get_classes(topo,classes,processed_modules,module_excludes=modules_to_exclude)
    get_classes(param,classes,processed_modules,module_excludes=modules_to_exclude)

    instances = []

    instantiated_names = []
    uninstantiated_names = []
     
    for class_name in classes:
        try:
            instances.append(eval(class_name+"()"))
            instantiated_names.append(class_name)
        except:
            #print "Could not instantiate %s"%class_name
            uninstantiated_names.append(class_name)

    print "\n ** Instantiated %s classes:"%len(instantiated_names)
    print "\n".join(instantiated_names)

    print "\n ** Could not instantiate %s classes:"%len(uninstantiated_names)
    print "\n".join(uninstantiated_names)
    
    return instances

######################################################################################


# CEBALERT: document somewhere about when to delete data files
# (i.e. when to generate new data) for train-tests and speed-tests and
# startup-speed-tests.


######################################################################################
### train-tests

RUN_FOR = [1,99,150]
LOOK_AT = "V1"
TRAINTESTS_CORTEXDENSITY = 8
RETINA_DENSITY = 24
LGN_DENSITY = 24

def _generate_data(script,data_filename,look_at='V1',run_for=[1,99,150],**args):
    
    print "Generating data for %s's %s after topo.sim.run(%s)"%(script,look_at,run_for)
    
    _setargs(args)

    execfile(script,__main__.__dict__)
    
    data = {}

    for time in run_for:
        print "Running for %s iterations"%time
        topo.sim.run(time)
        print "Recording data for %s at %s"%(look_at,topo.sim.timestr())
        data[topo.sim.timestr()] = copy.deepcopy(topo.sim[look_at].activity)

    data['args']=args
    data['run_for']=run_for
    data['look_at']=look_at
    data['versions'] = topo.version,topo.release

    print "Saving data to %s"%data_filename
    pickle.dump(data,open(data_filename,'wb'),2)



def test_script(script,decimal=None):
    """
    Run script with the parameters specified when its DATA file was
    generated, and check for changes.

    Looks for the DATA file at FIXEDDATADIR/script_name.ty_DATA (for
    data checked into SVN). If not found there, looks at
    TESTSDATADIR/script_name.ty_DATA. If also not found there, first
    generates a new DATA file at TESTSDATADIR/script_name.ty_DATA
    (i.e. to generate new data, delete the existing data before running).

    The decimal parameter defines how many decimal points to use when
    testing for array equality. The default of None causes exact
    matching.
    """
    print "Comparing results for %s"%script
    
    script_name = os.path.basename(script)
    # CEBALERT: clean up
    data_filename_only = script_name+"_DATA"
    data_filename = os.path.join(TESTSDATADIR,data_filename_only)

    try:
        locn = resolve_path(data_filename_only,search_paths=[FIXEDDATADIR,TESTSDATADIR])
    except IOError:
        print "No existing data"
        _run_in_forked_process(_generate_data,script,data_filename,run_for=RUN_FOR,cortex_density=TRAINTESTS_CORTEXDENSITY,lgn_density=LGN_DENSITY,retina_density=RETINA_DENSITY)
        locn = resolve_path(data_filename)
            
    print "Reading data from %s"%locn

    data_file = open(locn,'rb')
    data = pickle.load(data_file)

    print "Data from release=%s, version=%s"%(data['versions'] if 'versions' in data else ("unknown","unknown"))

    # retrieve parameters used when script was run
    run_for=data['run_for']
    look_at = data['look_at']

    ####################################################
    # support very old data files that contain 'density' instead of args['cortex_density']
    if 'args' not in data:
        data['args']={'cortex_density' : data['density']}

    args = data['args']
    _support_old_args(args)
    ####################################################

    _setargs(args)

    print "Starting '%s'"%script
    execfile(script,__main__.__dict__)        

    #########################################################
    time_fmt = topo.sim.timestr
    # support old pickled data (could replace time_fmt(topo.sim.time()) with
    # just topo.sim.timestr() if we didn't need to support old data
    if topo.sim.timestr(run_for[0]) not in data:
        time_fmt = float
    #########################################################

    for time in run_for:
        print "Running for %s iterations"%time
        topo.sim.run(time)
        

        if decimal is None:
            assert_array_equal(data[time_fmt(topo.sim.time())],topo.sim[look_at].activity,
                           err_msg="\nAt topo.sim.time()=%d, with decimal=%s"%(topo.sim.time(),decimal))
        else:
            assert_array_almost_equal(data[time_fmt(topo.sim.time())],topo.sim[look_at].activity,
                           decimal,err_msg="\nAt topo.sim.time()=%d, with decimal=%s"%(topo.sim.time(),decimal))

    result = "Results from " + script + " have not changed."
    if decimal is not None: result+= " (%d dp)" % (decimal)
    print result+"\n"


# CEBALERT: old name
#TestScript = test_script


###########################################################################
### speed-tests

SPEEDTESTS_CORTEXDENSITY=48
SPEEDTESTS_ITERATIONS = 250

# CEBALERT: see ALERT about variation by time_sim_startup()
def _time_sim_run(script,iterations=10):
    """
    Execute the script in __main__, then time topo.sim.run(iterations).

    Uses the timeit module.
    """
    print "Running '%s' for %s iterations"%(script,iterations)
    execfile(script,__main__.__dict__)
    topo.sim.run(1) # ensure compilations etc happen outside timing
    # CB: we enable garbage collection
    # (http://docs.python.org/lib/module-timeit.html)
    return timeit.Timer('topo.sim.run('+`iterations`+')','gc.enable(); import topo').timeit(number=1)


def _generate_speed_data(script,data_filename,iterations=100,**args):
    print "Generating speed data for %s"%script
    
    _setargs(args)
                
    how_long = _time_sim_run(script,iterations)

    speed_data = {'args':args,
                  'iterations':iterations,
                  'how_long':how_long}

    speed_data['versions'] = topo.version,topo.release
                          
    print "Saving data to %s"%data_filename
    pickle.dump(speed_data,open(data_filename,'wb'),2)


def compare_speed_data(script):
    """
    Run and time script with the parameters specified when its SPEEDDATA file was
    generated, and check for changes.

    Looks for the SPEEDDATA file at
    MACHINETESTSDATADIR/script_name.ty_DATA. If not found there, first
    generates a new SPEEDDATA file at
    MACHINETESTSDATADIR/script_name.ty_DATA (i.e. to generate new
    data, delete the existing data before running).
    """
    print "Comparing speed data for %s"%script
    
    script_name = os.path.basename(script)
    data_filename = os.path.join(MACHINETESTSDATADIR,script_name+"_SPEEDDATA")

    try:
        locn = resolve_path(data_filename)
    except IOError:
        print "No existing data"
        _run_in_forked_process(_generate_speed_data,script,data_filename,iterations=SPEEDTESTS_ITERATIONS,cortex_density=SPEEDTESTS_CORTEXDENSITY)
        #_generate_speed_data(script,data_filename,iterations=SPEEDTESTS_ITERATIONS,cortex_density=SPEEDTESTS_CORTEXDENSITY)
        locn = resolve_path(data_filename)
            
    print "Reading data from %s"%locn

    speed_data_file = open(locn,'r')

    try:
        speed_data = pickle.load(speed_data_file)
        print "Data from release=%s, version=%s"%(speed_data['versions'] if 'versions' in speed_data else ("unknown","unknown"))
    except:
    ###############################################################
    ## Support old data files (used to be string in the file rather
    ## than pickle)
        speed_data_file.seek(0)
        speed_data = speed_data_file.readline()

        iterations,old_time = speed_data.split('=')
        iterations = float(iterations); old_time=float(old_time)
        speed_data = {'iterations':iterations,
                      'how_long':old_time,
                      'args':{}}
    ###############################################################
        
    speed_data_file.close()
        
    old_time = speed_data['how_long']
    iterations = speed_data['iterations']
    args = speed_data['args']    

    _support_old_args(args)

    _setargs(args)

    new_time = _time_sim_run(script,iterations)

    percent_change = 100.0*(new_time-old_time)/old_time

    print "["+script+"]"+ '  Before: %2.1f s  Now: %2.1f s  (change=%2.1f s, %2.1f percent)'\
          %(old_time,new_time,new_time-old_time,percent_change)

    # CEBALERT: whatever compensations the python timing functions are supposed to make for CPU
    # activity, do they work well enough? If the processor is being used, these times jump all
    # over the place (i.e. vary by more than 10%).
    #assert percent_change<=5, "\nTime increase was greater than 5%"

###########################################################################


###########################################################################
### startup timing

# CEBALERT: figure out what this meant: "expect variation in these
# results! see python's timeit module documentation"
def _time_sim_startup(script):
    print "Starting %s"%script
    return timeit.Timer("execfile('%s',__main__.__dict__)"%script,'import __main__;gc.enable()').timeit(number=1)

     
def _generate_startup_speed_data(script,data_filename,**args):
    print "Generating startup speed data for %s"%script

    _setargs(args)
    how_long = _time_sim_startup(script)

    speed_data = {'args':args,
                  'how_long':how_long}

    speed_data['versions'] = topo.version,topo.release

    print "Saving data to %s"%data_filename
    pickle.dump(speed_data,open(data_filename,'wb'),2)


def compare_startup_speed_data(script):
    """
    Run and time script with the parameters specified when its
    STARTUPSPEEDDATA file was generated, and check for changes.

    Looks for the STARTUPSPEEDDATA file at
    MACHINETESTSDATADIR/script_name.ty_STARTUPSPEEDDATA. If not found
    there, first generates a new STARTUPSPEEDDATA file at
    MACHINETESTSDATADIR/script_name.ty_STARTUPSPEEDDATA (i.e. to
    generate new data, delete the existing data before running).
    """
    print "Comparing startup speed data for %s"%script
    
    script_name = os.path.basename(script)
    data_filename = os.path.join(MACHINETESTSDATADIR,script_name+"_STARTUPSPEEDDATA")

    try:
        locn = resolve_path(data_filename)
    except IOError:
        print "No existing data"
        _run_in_forked_process(_generate_startup_speed_data,script,data_filename,cortex_density=SPEEDTESTS_CORTEXDENSITY)        
        #_generate_startup_speed_data(script,data_filename,cortex_density=SPEEDTESTS_CORTEXDENSITY)
        locn = resolve_path(data_filename)
            
    print "Reading data from %s"%locn

    speed_data_file = open(locn,'r')

    try:
        speed_data = pickle.load(speed_data_file)
        print "Data from release=%s, version=%s"%(speed_data['versions'] if 'versions' in speed_data else ("unknown","unknown"))
    except:
    ###############################################################
    ## Support old data files (used to be string in the file rather
    ## than pickle)
        speed_data_file.seek(0)
        speed_data = speed_data_file.readline()

        density,old_time = speed_data.split('=')
        speed_data = {'cortex_density':float(density),
                      'how_long':float(old_time),
                      'args':{}}

    _support_old_args(speed_data['args'])
    ###############################################################

    _setargs(speed_data['args'])

    speed_data_file.close()

    old_time = speed_data['how_long']        
    new_time = _time_sim_startup(script)

    percent_change = 100.0*(new_time-old_time)/old_time

    print "["+script+ ' startup]  Before: %2.1f s  Now: %2.1f s  (change=%2.1f s, %2.1f percent)'\
          %(old_time,new_time,new_time-old_time,percent_change)


### end startup timing
###########################################################################


###########################################################################
### Snapshot tests

# This is clumsy. We could control topographica subprocesses, but I
# can't remember how to do it

def compare_with_and_without_snapshot_NoSnapshot(script="examples/lissom.ty",look_at='V1',cortex_density=8,lgn_density=4,retina_density=4,dims=['or','od','dr','cr','dy','sf'],dataset="Gaussian",run_for=10,break_at=5):

    data_filename=os.path.split(script)[1]+"_PICKLETEST"
    
    # we must execute in main because e.g. scheduled events are run in __main__
    # CEBALERT: should set global params
    __main__.__dict__['cortex_density']=cortex_density
    __main__.__dict__['lgn_density']=lgn_density
    __main__.__dict__['retina_density']=retina_density
    __main__.__dict__['dims']=dims
    __main__.__dict__['dataset']=dataset
    
    execfile(script,__main__.__dict__)
    
    data = {}
    topo.sim.run(break_at)
    data[topo.sim.time()]= copy.deepcopy(topo.sim[look_at].activity)
    topo.sim.run(run_for-break_at)
    data[topo.sim.time()]= copy.deepcopy(topo.sim[look_at].activity)
        
    data['run_for']=run_for
    data['break_at']=break_at
    data['look_at']=look_at

    data['cortex_density']=cortex_density
    data['lgn_density']=lgn_density
    data['retina_density']=retina_density
    data['dims']=dims
    data['dataset']=dataset
    
    locn = normalize_path(os.path.join("tests",data_filename))
    print "Writing pickle to %s"%locn
    pickle.dump(data,open(locn,'wb'),2)


def compare_with_and_without_snapshot_CreateSnapshot(script="examples/lissom.ty"):
    data_filename=os.path.split(script)[1]+"_PICKLETEST"

    locn = resolve_path(os.path.join('tests',data_filename))
    print "Loading pickle at %s"%locn
        
    try:
        data = pickle.load(open(locn,"rb"))
    except IOError:
        print "\nData file '"+data_filename+"' could not be opened; run _A() first."
        raise

    # retrieve parameters used when script was run
    run_for=data['run_for']
    break_at=data['break_at']
    look_at=data['look_at']

    # CEBALERT: shouldn't need to re-list - should be able to read from data!
    cortex_density=data['cortex_density']
    lgn_density=data['lgn_density']
    retina_density=data['retina_density']
    dims=data['dims']
    dataset=data['dataset']

    __main__.__dict__['cortex_density']=cortex_density
    __main__.__dict__['lgn_density']=lgn_density
    __main__.__dict__['retina_density']=retina_density
    __main__.__dict__['dims']=dims
    __main__.__dict__['dataset']=dataset
    execfile(script,__main__.__dict__)        

    # check we have the same before any pickling
    topo.sim.run(break_at)
    assert_array_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                       err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())

    from topo.command import save_snapshot
    locn = normalize_path(os.path.join('tests',data_filename+'.typ_'))
    print "Saving snapshot to %s"%locn
    save_snapshot(locn)


def compare_with_and_without_snapshot_LoadSnapshot(script="examples/lissom.ty"):
    data_filename=os.path.split(script)[1]+"_PICKLETEST"
    snapshot_filename=os.path.split(script)[1]+"_PICKLETEST.typ_"

    locn = resolve_path(os.path.join('tests',data_filename))
    print "Loading pickle from %s"%locn
    try:
        data = pickle.load(open(locn,"rb"))
    except IOError:
        print "\nData file '"+data_filename+"' could not be opened; run _A() first"
        raise

    # retrieve parameters used when script was run
    run_for=data['run_for']
    break_at=data['break_at']
    look_at=data['look_at']

#    # CEBALERT: shouldn't need to re-list - should be able to read from data!
#    cortex_density=data['cortex_density']
#    lgn_density=data['lgn_density']
#    retina_density=data['retina_density']
#    dims=data['dims']
#    dataset=data['dataset']
    
    from topo.command import load_snapshot

    locn = resolve_path(os.path.join('tests',snapshot_filename))
    print "Loading snapshot at %s"%locn

    try:
        load_snapshot(locn)
    except IOError:
        print "\nPickle file '"+snapshot_filename+"' could not be opened; run _B() first."
        raise

    assert topo.sim.time()==break_at
    assert_array_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                       err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())
    print "Match at %s after loading snapshot"%topo.sim.time()

    topo.sim.run(run_for-break_at)
                
    assert_array_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                       err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())

    print "Match at %s after running loaded snapshot"%topo.sim.time()

### end Snapshot tests
###########################################################################


###########################################################################
### pickle tests
def pickle_unpickle_everything(existing_pickles=None):

    pickle_errors = 0

    if existing_pickles is None:

        instances = _instantiate_everything()
        pickles = {}

        for instance in instances:
            try:
                pickles[str(instance)]=pickle.dumps(instance)
            except:
                print "Error pickling %s:"%instance
                pickle_errors+=1
                traceback.print_exc()
    else:
        pickles = pickle.load(open(existing_pickles))

    unpickle_errors = 0
    
    for instance_name,pickled_instance in pickles.items():
        try:
            pickle.loads(pickled_instance)
        except:
            print "Error unpickling %s"%instance_name
            unpickle_errors+=1
            traceback.print_exc()

    print

    if existing_pickles is None:
        print "Instances that failed to pickle: %s"%pickle_errors
        
    print "Pickled instances that failed to unpickle: %s"%unpickle_errors

    return pickle_errors+unpickle_errors
###########################################################################



###########################################################################
# basic test of run batch
def test_runbatch():
    from topo.misc.genexamples import find_examples
    from topo.command import run_batch

    original_output_path = param.normalize_path.prefix
    start_output_path = tempfile.mkdtemp()
    param.normalize_path.prefix = start_output_path
    
    tiny = os.path.join(find_examples(),"tiny.ty")
    run_batch(tiny,cortex_density=1,retina_density=1,times=[1],snapshot=True,output_directory="testing123")

    new_output_path = param.normalize_path.prefix

    assert new_output_path.startswith(start_output_path)
    assert "testing123" in new_output_path # not perfect test, but better than nothing.

    base = os.path.basename(new_output_path).split(",")[0]

    def exists(endpart):
        whole = os.path.join(new_output_path,base+endpart)
        print "Checking for %s"%whole
        return os.path.isfile(whole)
    
    assert exists(".global_params.pickle")
    assert exists(".out")
    assert exists("_000001.00_V1_Activity.png")
    assert exists("_000001.00_script_repr.ty")
    assert exists("_000001.00.typ")

    print "Deleting %s"%param.normalize_path.prefix
    shutil.rmtree(param.normalize_path.prefix)
    param.normalize_path.prefix=original_output_path
###########################################################################





###########################################################################
## CEBALERT: for C++ reference simulations - should be moved elsewhere
def run_multiple_density_comparisons(ref_script):
    from topo.misc.util import cross_product
    import subprocess
    import traceback
    import os
    
    #k = [8,10,12,13,14,34]
    #x = cross_product([k,k])

    
    x = [[ 8, 8],[ 8, 9],[ 8,10],[ 8,11],[ 8,12],[ 8,13],[ 8,14],[ 8,15],
         [24,14],[24,17],[24,20],
         [24,24],[24,48]]

    cmds = []
    for spec in x:
        c="""./topographica -c "verbose=False;BaseRN=%s;BaseN=%s;comparisons=True;stop_at_1000=False" topo/tests/reference/%s"""%(spec[0],spec[1],ref_script)
        cmds.append(c)

    results = []
    errs=[]
    for cmd in cmds:
        print 
        print "************************************************************"
        print "Executing '%s'"%cmd
        
#        errout = os.tmpfile()#StringIO.StringIO()

        p = subprocess.Popen(cmd, shell=True,stderr=subprocess.PIPE)
        p.wait()
        r = p.returncode
        
        errout = p.stderr
        #r = subprocess.call(cmd,shell=True)#,stderr=subprocess.PIPE)#errout)
        #print "TB",traceback.print_exc()
        
        if r==0:
            result = "PASS"
        else:
            result = "FAIL"
        results.append(result)

        l = errout.readlines()
        i = 0
        L=0
        for line in l:
            if line.startswith("AssertionError"):
                L=i
                break
            i+=1
        
        errs.append(l[L::])
        errout.close()

    print "================================================================================"
    print
    print "SUMMARY"
    print
    nerr = 0
    for xi,result,err in zip(x,results,errs):
        print
        print "* %s ... BaseRN=%s,BaseN=%s"%(result,xi[0],xi[1])
        if result=="FAIL":
            e = ""
            print e.join(err)
            
            nerr+=1
    print "================================================================================"
    
    return nerr

###########################################################################

