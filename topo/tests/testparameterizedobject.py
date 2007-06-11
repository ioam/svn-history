"""
Unit test for ParameterizedObject.


$Id$
"""
__version__='$Revision$'

import unittest

from topo.base.parameterizedobject import ParameterizedObject, Parameter

from topo.outputfns.basic import PiecewiseLinear

# CEBALERT: not anything like a complete test of ParameterizedObject!

class TestPO(ParameterizedObject):
    inst = Parameter(default=[1,2,3],instantiate=True)
    notinst = Parameter(default=[1,2,3],instantiate=False)


class TestParameterizedObject(unittest.TestCase):


    def test_basic_instantiation(self):

        testpo = TestPO()

        self.assertEqual(testpo.inst,TestPO.inst)
        self.assertEqual(testpo.notinst,TestPO.notinst)

        TestPO.inst[1]=7
        TestPO.notinst[1]=7
        
        self.assertEqual(testpo.notinst,[1,7,3])
        self.assertEqual(testpo.inst,[1,2,3])


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestParameterizedObject))
