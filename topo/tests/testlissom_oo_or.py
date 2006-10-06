"""
Slow test to check that the results of examples/lissom_oo_or.ty
have not changed.
"""

import pickle, unittest, copy

import topo

from topo.tests.utils import assert_array_equal


def GenerateData():
    execfile("examples/lissom_oo_or.ty")
    topo.sim.run(1)
    t1=copy.deepcopy(topo.sim['V1'].activity)
    topo.sim.run(1)
    t2=copy.deepcopy(topo.sim['V1'].activity)

    pickle.dump((t1,t2),open('topo/tests/testlissom_oo_or.data','wb'),2)


class Test_lissom_oo_or(unittest.TestCase):

    def test_activity(self):
        """
        
        ('true' means what it was last time GenerateData was called)
        """
        trueV1activities = pickle.load(open("topo/tests/testlissom_oo_or.data","r"))
        
        execfile("examples/lissom_oo_or.ty")
        
        topo.sim.run(1)
        # CEBHACKALERT: the single line below ought to work instead of
        # the 4 beneath it!
        #assert_array_equal(trueV1activities[0],topo.sim['V1'].activity)
        self.assertEqual(topo.sim['V1'].activity.shape,trueV1activities[0].shape)
        for i in range(topo.sim['V1'].activity.shape[0]):
            for j in range(topo.sim['V1'].activity.shape[1]):
                self.assertEqual(topo.sim['V1'].activity[i,j],trueV1activities[0][i,j])
        
        topo.sim.run(1)
        #assert_array_equal(trueV1activities[0],topo.sim['V1'].activity)
        self.assertEqual(topo.sim['V1'].activity.shape,trueV1activities[1].shape)
        for i in range(topo.sim['V1'].activity.shape[0]):
            for j in range(topo.sim['V1'].activity.shape[1]):
                self.assertEqual(topo.sim['V1'].activity[i,j],trueV1activities[1][i,j])

        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(Test_lissom_oo_or))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

