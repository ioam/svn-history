"""
Slow test to check that the results of examples/lissom_oo_or.ty
have not changed.

The current simulation's results are checked against the results
stored in testlissom_oo_or.data.

You can run the test like this:
  ./topographica -c 'import topo.tests.testlissom_oo_or; topo.tests.run(test_modules=[topo.tests.testlissom_oo_or])'

You can generate a new testlissom_oo_or.data file with the following command:
  ./topographica -c "from topo.tests.testlissom_oo_or import GenerateData; GenerateData()"
"""

import pickle, unittest, copy, __main__

import topo

from topo.tests.utils import assert_array_equal


def GenerateData():

    #### call the lissom_oo_or.ty example with density 8
    default_density=8.0
    execfile("examples/lissom_oo_or.ty")        
    # CEBHACKALERT: I found the following line was necessary, so presumably
    # I'm doing something wrong with execfile and where it runs the script.
    exec "from topo.base.boundingregion import BoundingBox" in __main__.__dict__
    ####

    # t=1 to indicate likely activity calculation error
    # t=100 to indicate learning errors (e.g. rate)
    # t=210 to indicate bounds changing errors
    
    topo.sim.run(1)
    t1=copy.deepcopy(topo.sim['V1'].activity)
    topo.sim.run(99)
    t100=copy.deepcopy(topo.sim['V1'].activity)
    topo.sim.run(110)
    t210=copy.deepcopy(topo.sim['V1'].activity)

    pickle.dump((t1,t100,t210),open('topo/tests/testlissom_oo_or.data','wb'),2)


class Test_lissom_oo_or(unittest.TestCase):

    def test_activity(self):
        """
        Check that the current simulation's activity values match those from the last
        time GenerateData() was called.
        """        
        trueV1activities = pickle.load(open("topo/tests/testlissom_oo_or.data","r"))

        #### call the lissom_oo_or.ty example with density 8
        default_density=8.0
        execfile("examples/lissom_oo_or.ty")        
        # CEBHACKALERT: I found the following line was necessary, so presumably
        # I'm doing something wrong with execfile and where it runs the script.
        exec "from topo.base.boundingregion import BoundingBox" in __main__.__dict__
        ####

        topo.sim.run(1)
        assert_array_equal(trueV1activities[0],topo.sim['V1'].activity)

        topo.sim.run(99)
        assert_array_equal(trueV1activities[1],topo.sim['V1'].activity)

        topo.sim.run(110)
        assert_array_equal(trueV1activities[2],topo.sim['V1'].activity)

        
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(Test_lissom_oo_or))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

