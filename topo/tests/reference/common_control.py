### This file can't be used on its own (see e.g. lissom_or_reference)

### NOTE: c++ lissom does not output unsituated weights, so a function
### in lissom_log_parser guesses how to unsituate the weights. If your
### weights contains rows or columns of zeros, this guessing will fail.

from topo.tests.reference.lissom_log_parser import check_weights,check_activities

def _check_proj(s,p,N):
    # we might consider skipping every other one, or something like that!
    try:
        for i in range(N):
            for j in range(N):
                check_weights(s,p,(i,j),display=verbose)
        return 0
    except AssertionError, st:
        return "%s: %s\n"%(s,st)
        

def check_all_weights():
    print "t=%s: Checking all weights..."%topo.sim.time()

    e = ""
    for proj in prjns_to_check:
        o =_check_proj('Primary',proj,BaseN)
        if o!=0:e+=o
    if len(e)>0:
        raise AssertionError("The following weights did not match:\n%s"%e)


def check_all_activities():
    print "t=%s: Checking all activities..."%topo.sim.time()
    check_activities('Eye0',display=verbose)
    check_activities('Primary',display=verbose)


# hack
L = locals()

def run_comparisons(l):

    L.update(l)

    ### Check initial weights
    check_all_weights()

    ### Check initial patterns are ok on Eye0 and Primary
    for i in range(5):
        topo.sim.run(1)
        check_all_activities()
        check_all_weights()
    
    topo.sim.run(5)
    check_all_activities()

    topo.sim.run(10)
    check_all_activities()

    topo.sim.run(80)
    check_all_activities();check_all_weights()

    topo.sim.run(100)
    check_all_activities() #200
    
    topo.sim.run(400)
    check_all_activities() #600
    
    topo.sim.run(300)
    check_all_activities() #900
    
    topo.sim.run(100) # to 1000
    check_all_activities();check_all_weights()

    if not stop_at_1000:

        for i in range(8): # to 9000
            topo.sim.run(1000)
            check_all_activities()


        topo.sim.run(3000) # 12000
        check_all_activities();check_all_weights()

        topo.sim.run(3000)
        check_all_activities()

        topo.sim.run(5000)
        check_all_activities();check_all_weights()



