"""
Contains tests to check a particular script's results or speed have not changed.


Test that the results of a script have not changed
==================================================

The current results from running x are checked against the results
stored in x_DATA, where x is the path to the script (including the
filename).

You can generate a new data file like this:
  ./topographica -c 'from topo.tests.test_script import GenerateData; GenerateData(x)'

You can run the test like this:
  ./topographica -c 'from topo.tests.test_script import TestScript; TestScript(x,6)'

You can specify which sheet to look at, its density, the number of iterations, and
how many decimal places to check (defaulting to all).

The script x is assumed to support 'default_density' (see e.g. examples/lissom_oo_or.ty)



Test that the speed of running a simulation has not changed
===========================================================

You can generate a new data file like this:
  ./topographica -c 'from topo.tests.test_script import *; generate_speed_data(script="examples/hierarchical.ty",iterations=50)'

You can run a test like this:
  ./topographica -c 'from topo.tests.test_script import compare_speed_data; compare_speed_data("examples/hierarchical.ty")'


You should select enough iterations that the timings can be reliable.



$Id$
"""
__version__='$Revision$'


import pickle, copy, __main__, timeit

import topo
from topo.tests.utils import assert_array_equal, assert_array_almost_equal


# CEBALERT: will these 'script="examples..."' paths work on Windows?

# CBALERT: guess I should have named this generate_data, since it's a function (same for TestScript).
def GenerateData(script="examples/lissom_oo_or.ty",data_filename=None,look_at='V1',density=4,run_for=[1,99,150]):
    """
    Run script (with the sheet look_at set to the specified density)
    for the times in run_for; after each run_for time the activity of
    look_at is saved.

    For the default data_filename of None, saves the resulting data to
    the pickle script_DATA.
    """
    if data_filename==None:
        data_filename=script+"_DATA"
    
    # we must execute in main because e.g. scheduled events are run in __main__
    __main__.__dict__['default_density']=density
    execfile(script,__main__.__dict__)
    
    data = {}

    for time in run_for:
        topo.sim.run(time)
        data[topo.sim.time()] = copy.deepcopy(topo.sim[look_at].activity)
        
    data['run_for']=run_for
    data['density']=density
    data['look_at']=look_at
    
    pickle.dump(data,open(data_filename,'wb'),2)



def TestScript(script="examples/lissom_oo_or.ty",data_filename=None,decimal=None):
    """
    Run script with the parameters specified when its DATA file was
    generated, and check for changes.

    data_filename allows the location of the DATA file to be specified
    (for the default of None, the location is assumed to be
    script_DATA).
    
    The decimal parameter defines to how many decimal points will the
    equality with the DATA file be measured. Setting it to the default
    of None will cause exact matching.
    """
    if data_filename==None:
        data_filename=script+"_DATA"
        
    try:
        data = pickle.load(open(data_filename,"r"))
    except IOError:
        print "\nData file '"+data_filename+"' could not be opened; run GenerateData() to create a data file before making changes to the script you wish to check."
        raise

    # retrieve parameters used when script was run
    run_for=data['run_for']    
    look_at=data['look_at']
    density=data['density']
    
    __main__.__dict__['default_density']=density
    execfile(script,__main__.__dict__)        

    for time in run_for:
        topo.sim.run(time)
        if decimal is None:
            assert_array_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                           err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())
        else:
            assert_array_almost_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                           decimal,err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())

    result = "Results from " + script + " have not changed."
    if decimal is not None: result+= " (%d dp)" % (decimal)
    print "\n"+result+"\n"




# CB: ought to tell users that they should expect variation in results etc
# so they might know what is significant. Or use repeat(3 or 4) and return
# the minimum value to try to make the result more reliable.
def time_sim_run(script="examples/lissom_oo_or.ty",iterations=10):
    """
    Execute the script in __main__, then time topo.sim.run(iterations).

    Uses the timeit module.
    """
    execfile(script,__main__.__dict__)

    # CB: not clear whether to turn off GC?
    # http://docs.python.org/lib/module-timeit.html
    # """
    # By default, timeit() temporarily turns off garbage collection
    # during the timing. The advantage of this approach is that it
    # makes independent timings more comparable. This disadvantage is
    # that GC may be an important component of the performance of the
    # function being measured. If so, GC can be re-enabled as the
    # first statement in the setup string. For example:
    # timeit.Timer('for i in xrange(10):oct(i)','gc.enable()').timeit()
    # """
    return timeit.Timer('topo.sim.run('+`iterations`+')','gc.enable(); import topo').timeit(number=1)

     
def generate_speed_data(script="examples/lissom_oo_or.ty",iterations=100,data_filename=None):
    """
    Calls time_sim_run(script,iterations) and saves 'iterations=time'
    to script_SPEEDDATA.
    """
    if data_filename==None:
        data_filename=script+"_SPEEDDATA"

    how_long = time_sim_run(script,iterations)

    speed_data_file = open(data_filename,'w')
    speed_data_file.write("%s=%s"%(iterations,how_long))
    speed_data_file.close()


def compare_speed_data(script="examples/lissom_oo_or.ty",data_filename=None):
    """
    Using previously generated script_SPEEDDATA, compares current
    time_sim_run(script) with the previous.
    """
    if data_filename==None:
        data_filename=script+"_SPEEDDATA"

    speed_data_file = open(data_filename,'r')
        
    info = speed_data_file.readline()
    speed_data_file.close()

    iterations,old_time = info.split('=')
    iterations = float(iterations); old_time=float(old_time)
    
    new_time = time_sim_run(script,iterations)

    percent_change = 100.0*(new_time-old_time)/old_time

    print "["+script+"]"+ '  Before: %2.1f s  Now: %2.1f s  (change=%2.1f s, %2.1f percent)'\
          %(old_time,new_time,new_time-old_time,percent_change)

    # CEBALERT: whatever compensations the python timing functions are supposed to make for CPU
    # activity, do they work well enough? If the processor is being used, these times jump all
    # over the place (i.e. vary by more than 10%).
    #assert percent_change<=5, "\nTime increase was greater than 5%"

