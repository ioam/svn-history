### This file can't be used on its own (see e.g. lissom_or_reference)

### NOTE: c++ lissom does not output unsituated weights, so a function
### in lissom_log_parser guesses how to unsituate the weights. If your
### weights contains rows or columns of zeros, this guessing will fail.

from topo.tests.reference.lissom_log_parser import check_weights,check_activities,check_size
from math import ceil

def _check_proj(s,p,N):

    # to match save_all_units.command
    step = int(ceil(N/20.0))
    if step>2 and step%2==1:
        step+=1

    # check all sizes
    try:
        for i in range(0,N,step):
            for j in range(0,N,step):
                check_size(s,p,(i,j),display=verbose)
    except AssertionError, st:
        return "%s: %s\n"%(s,st)

    
    try:
        for i in range(0,N,step):
            for j in range(0,N,step):
                check_weights(s,p,(i,j),display=verbose)
        return 0
    except AssertionError, st:
        return "%s: %s\n"%(s,st)
        

def check_all_weights():
    print "t=%s: Checking weights..."%topo.sim.time()

    e = ""
    # assumes 'Primary'
    for proj in topo.sim['Primary'].projections():
        print "...%s"%proj
        o =_check_proj('Primary',proj,BaseN)
        if o!=0:e+=o
    if len(e)>0:
        raise AssertionError("The following weights did not match:\n%s"%e)


def check_all_activities():
    print "t=%s: Checking activities..."%topo.sim.time()

    sheets = sorted(topo.sim.objects().values(), cmp=lambda x, y:
                    cmp(x.precedence,
                        y.precedence))
    for s in sheets:
        print "...%s"%s.name
        check_activities(s.name,display=verbose)

        
# hack
L = locals()

def run_comparisons(l):


    # there are weigts checks at the beginning and then
    # after every bounds change
    
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

    topo.sim.run(80) # 100
    check_all_weights(); check_all_activities()

    topo.sim.run(100)
    check_all_weights();check_all_activities() #200

    topo.sim.run(300)
    check_all_weights();check_all_activities() #500
    
    topo.sim.run(300)
    check_all_activities() #800
        
    topo.sim.run(200) # 1000
    check_all_weights();check_all_activities()

    if not stop_at_1000:

        for i in range(4): # to 5000
            topo.sim.run(1000)
            check_all_weights();check_all_activities()


        topo.sim.run(1500) # 6500
        check_all_weights();check_all_activities()

        topo.sim.run(1500) # 8000
        check_all_weights();check_all_activities()

        topo.sim.run(5000) # 13000
        check_all_activities()

        topo.sim.run(3000) # 16000
        check_all_activities()
        
        topo.sim.run(4000) # 20000
        check_all_weights; check_all_activities()
