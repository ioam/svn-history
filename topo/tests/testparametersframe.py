"""
Tests for the ParametersFrame classes.

$Id$
"""
__version__='$Revision$'


import __main__
import unittest
import Tkinter

from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import BooleanParameter,Number,Parameter, \
                                       ObjectSelectorParameter,ClassSelectorParameter, \
                                       StringParameter

from topo.base.patterngenerator import PatternGenerator

from topo.tkgui.parametersframe import ParametersFrame



# CEBALERT: can't have this code present when doing "make tests" - why?
## # In case this test is run alone, start tkgui
## # (otherwise simulation of gui set()s and get()s doesn't work)
## import topo
## if not hasattr(topo,'guimain'):
##     import topo.tkgui; topo.tkgui.start()


class TestPO(ParameterizedObject):
    boo = BooleanParameter(default=True)
    osp = ObjectSelectorParameter()
    csp = ClassSelectorParameter(class_=PatternGenerator)
    const = Parameter(1.0,constant=True)
    pa = Parameter(default="test")
    nu = Number(default=1.0,bounds=(-1,1))
    st = StringParameter("string1")


class TestParametersFrame(unittest.TestCase):


    def setUp(self):

        self.some_pos = [ParameterizedObject(),ParameterizedObject(),
                         ParameterizedObject()]
        
        self.testpo1 = TestPO()
        self.testpo1.params()['osp'].Arange = self.some_pos

        self.testpo2 = TestPO()
        self.testpo1.params()['osp'].Arange = self.some_pos
        
        self.toplevel = Tkinter.Toplevel()
        self.f = ParametersFrame(self.toplevel,self.testpo1)


    def test_set_PO(self):
        self.assertEqual(self.f._extraPO,self.testpo1)
        self.f.set_PO(self.testpo2)
        self.assertEqual(self.f._extraPO,self.testpo2)
        



###########################################################

cases = [TestParametersFrame]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])
suite.requires_display = True

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

