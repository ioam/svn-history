import unittest
import numpy

from topo.base.simulation import Simulation
from topo.base.boundingregion import BoundingBox
from topo.base.cf import CFIter,MaskedCFIter,ResizableCFProjection,CFSheet

class TestIter(unittest.TestCase):

    def setUp(self):

        self.sim = Simulation()

        self.sim['Dest'] = CFSheet(nominal_density=10,nominal_bounds=BoundingBox(radius=0.5))
        self.sim['Src'] = CFSheet(nominal_density=10,nominal_bounds=BoundingBox(radius=0.5))

        self.sim.connect('Src','Dest',
                         connection_type = ResizableCFProjection,
                         )

    def test_iterate_all(self):
        """
        Test to make sure the iterator hits every CF
        """
        total = 0
        dest = self.sim['Dest']
        proj = dest.projections()['SrcToDest']
        for cf,r,c in self.iter_type(proj)():
            total += 1
            self.failUnless(0 <= r < 10, "CFIter generated bogus CF row index")
            self.failUnless(0 <= c < 10, "CFIter generated bogus CF col index")
            cfxy = (proj.X_cf[r,c],proj.Y_cf[r,c])
            self.failUnlessEqual(cfxy,dest.matrixidx2sheet(r,c))
        self.failUnlessEqual(total,100)


    def test_iterate_some_nil(self):
        """
        Test to make sure iterator skips nil CFs (i.e cf == None)
        """
        dest = self.sim['Dest']
        proj = dest.projections()['SrcToDest']
        total = 0
        proj.cfs[5,5] = None
        for cf,r,c in self.iter_type(proj)():
            total += 1
            self.failIfEqual((r,c),(5,5))
        self.failUnlessEqual(total,99)

class TestCFIter(TestIter):

    iter_type = CFIter

class TestMaskedCFIter(TestIter):

    iter_type = MaskedCFIter

    def test_iterate_masked(self):
        """
        Test if iterator skips masked CFs
        """
        total = 0
        dest = self.sim['Dest']
        proj = dest.projections()['SrcToDest']
        dest.mask.data = numpy.zeros(dest.activity.shape)
        dest.mask.data[5,5] = 1
        for cf,r,c in self.iter_type(proj)():
            total += 1
            self.failUnlessEqual((r,c),(5,5))
            self.failUnless(cf is proj.cfs[5,5])
        self.failUnlessEqual(total,1)
        


####
cases = [TestCFIter, TestMaskedCFIter]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
