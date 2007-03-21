"""
Test that the results of a particular script have not changed.

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

$Id$
"""
__version__='$Revision$'


import pickle, copy, __main__

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
        if (decimal == None):
            assert_array_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                           err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())
        else:
            assert_array_almost_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                           decimal,err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())

    print "\nResults from " + script + " have not changed."
    if (decimal != None): print "(to %d decimal places)" % (decimal)



# CB: currently working on these!

def generate_speed_data(script="examples/lissom_oo_or.ty"):


    # I'm sure there is a function that simply does timing, so I can avoid 90 % of this stuff.

    
    filename = script+'_SPEEDDATA' 

    from topo.misc.utils import profile
    import sys
    f = open('temp','w') # how do I have a temporary file? This might write over someone's stuff
    old_stdout=sys.stdout
    sys.stdout = f
    profile('execfile("'+script+'");topo.sim.run(10)',n=0)
    sys.stdout = old_stdout
    f.close()

    speed_data = open('temp','r')
    perf = speed_data.readline()
    speed_data.close()



    # Should be replaced with a regular expression (by someone who knows them...)
    # perf looks like:
    #"         172124 function calls (169542 primitive calls) in 1.689 CPU seconds"    
    perf= perf[perf.find("in ")+3:perf.find("CPU")-1]
    speed_data = open(filename,'w')
    speed_data.write(perf)
    speed_data.close()


def compare_speed_data(script="examples/lissom_oo_or.ty"):

    filename = script+'_SPEEDDATA' 

    from topo.misc.utils import profile
    import sys
    f = open('temp','w') # how do I have a temporary file? This might write over someone's stuff
    old_stdout=sys.stdout
    sys.stdout = f
    profile('execfile("'+script+'");topo.sim.run(10)',n=0)
    sys.stdout = old_stdout
    f.close()

    speed_data = open('temp','r')
    perf = speed_data.readline()
    speed_data.close()

    # Should be replaced with a regular expression (by someone who knows them...)
    # perf looks like:
    #"         172124 function calls (169542 primitive calls) in 1.689 CPU seconds"    
    perf= float(perf[perf.find("in ")+3:perf.find("CPU")-1])


    old = open(filename,'r')
    old_speed_data = float(old.readline())
    old.close()


    print "["+script+"]"+ " Before: %f s   Now: %f s  (change=%f s, %f percent)"%(old_speed_data,perf,perf-old_speed_data,100.0*(perf-old_speed_data)/old_speed_data)
