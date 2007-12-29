"""

$Id$
"""
__version__='$Revision$'

# temp

# this kind of thing is done all over the tests;
# could change to use this function (if the test
# actually needs a new simulation).

def new_simulation():

    from topo.base.simulation import Simulation
    from topo.base.cf import CFSheet,CFProjection
    from topo.sheets.generatorsheet import GeneratorSheet

    sim=Simulation(register=True)
    sim['GS']=GeneratorSheet(nominal_density=2)
    sim['GS2']=GeneratorSheet(nominal_density=2)
    sim['S'] = CFSheet(nominal_density=2)
    sim['S2'] = CFSheet(nominal_density=2)
    sim.connect('GS','S',connection_type=CFProjection,delay=0.05)
    sim.connect('GS','S2',connection_type=CFProjection,delay=0.05)
    sim.connect('GS2','S2',connection_type=CFProjection,delay=0.05)


# move to utils
from numpy.testing import assert_array_equal
def assert_array_not_equal(a1,a2,msg=""):
    try:
        assert_array_equal(a1,a2)
    except AssertionError:
        pass
    else:
        raise AssertionError(msg)


    
