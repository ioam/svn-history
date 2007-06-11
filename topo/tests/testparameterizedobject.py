"""
Unit test for ParameterizedObject.


$Id$
"""
__version__='$Revision$'

import unittest

from topo.base.parameterizedobject import ParameterizedObject, Parameter


# CEBALERT: not anything like a complete test of ParameterizedObject!

class TestPO(ParameterizedObject):
    inst = Parameter(default=[1,2,3],instantiate=True)
    notinst = Parameter(default=[1,2,3],instantiate=False)


class AnotherTestPO(ParameterizedObject):
    instPO = Parameter(default=TestPO(),instantiate=True)
    notinstPO = Parameter(default=TestPO(),instantiate=False)

class TestParameterizedObject(unittest.TestCase):


    def test_basic_instantiation(self):

        testpo = TestPO()

        self.assertEqual(testpo.inst,TestPO.inst)
        self.assertEqual(testpo.notinst,TestPO.notinst)

        TestPO.inst[1]=7
        TestPO.notinst[1]=7
        
        self.assertEqual(testpo.notinst,[1,7,3])
        self.assertEqual(testpo.inst,[1,2,3])


    def test_more_instantiation(self):

        anothertestpo = AnotherTestPO()

        ### CB: AnotherTestPO.instPO is instantiated, but
        ### TestPO.notinst is not instantiated - so notinst is still
        ### shared, even by instantiated parameters of AnotherTestPO.
        ### Seems like this behavior of ParameterizedObject could be
        ### confusing, so maybe mention it in documentation somewhere.
        TestPO.notinst[1]=7
        # (if you thought your instPO was completely an independent object, you
        # might be expecting [1,2,3] here)
        self.assertEqual(anothertestpo.instPO.notinst,[1,7,3]) 
        

suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestParameterizedObject))
