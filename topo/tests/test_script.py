"""
Test that the results of a particular script have not changed.

The current results from running x are checked against the results
stored in x_DATA, where x is the path of the script.

You can run the test like this:
  ./topographica -c 'from topo.tests.test_script import TestScript; TestScript(x)'

You can specify which sheet to look at, its density, and the number of iterations.


You can generate a new data file like this:
  ./topographica -c 'from topo.tests.test_script import GenerateData; GenerateData(x)'


The script x is assumed to support 'default_density' (see e.g. examples/lissom_oo_or.ty)



$Id$
"""
__version__='$Revision$'


import pickle, copy, __main__

import topo

from topo.tests.utils import assert_array_equal


# CBALERT: will these 'script="examples..."' paths work on Windows?


def GenerateData(script="examples/lissom_oo_or.ty",look_at='V1',density=4,run_for=[1,99,150]):
    """
    Run script (with the sheet look_at set to the specified density) for the times in run_for;
    after each run_for time the activity of look_at is saved.

    Saves the resulting data to the pickle script_DATA
    """
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
    
    pickle.dump(data,open(script+'_DATA','wb'),2)



def TestScript(script="examples/lissom_oo_or.ty"):
    """
    Run script with the parameters specified when its DATA file was generated, and check
    for changes.
    """
    try:
        data_filename = script+'_DATA'
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
        assert_array_equal(data[topo.sim.time()],topo.sim[look_at].activity,
                           err_msg="\nAt topo.sim.time()=%d"%topo.sim.time())

    print "\nResults from " + script + " have not changed."

