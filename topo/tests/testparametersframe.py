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



    def test_initial_update_parameters(self):
        """
        Checking for specific bug: quotation marks being
        added to displayed values.

        (Only time should get quotation marks is when
        editing a Parameter and trying to create an instance
        of a class that hasn't been imported: then string is
        assumed, and quotes are added - since it's not a
        StringParameter.)
        """

        ## check that update doesn't affect the variable values
        orig_values = {}
        for param_name,tkvar in self.f._tk_vars.items():
            orig_values[param_name] = tkvar._original_get()

        self.f.update_parameters()

        for param_name,val in orig_values.items():
            self.assertEqual(self.f._tk_vars[param_name].get(),val)


        ## check that *displayed* values don't change 
        orig_values = {}
        for param_name,representation in self.f.representations.items():
            widget = representation['widget']

            # (not possible to get value from these widgets)
            if widget.__class__ is not Tkinter.Button and \
               widget.__class__ is not Tkinter.OptionMenu and \
               widget.__class__ is not Tkinter.Checkbutton:

                orig_values[param_name] = widget.get()
        
        self.f.update_parameters()

        for param_name,val in orig_values.items():
            widget = self.f.representations[param_name]['widget']
            self.assertEqual(widget.get(),val)
                             
            

    
        



###########################################################

cases = [TestParametersFrame]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])
suite.requires_display = True

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

