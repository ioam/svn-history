"""
Tests for the ParametersFrameWithApply classes.

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

from topo.tkgui.parametersframe import ParametersFrameWithApply


# CEBALERT: can't have this code present when doing "make tests" - why?
## # In case this test is run alone, start tkgui
## # (otherwise simulation of gui set()s and get()s doesn't work)
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


cannot_get_value = [Tkinter.OptionMenu] #OptionMenu has no get()    


class TestParametersFrameWithApply(unittest.TestCase):


    def setUp(self):

        self.some_pos = [ParameterizedObject(),ParameterizedObject(),
                         ParameterizedObject()]
        
        self.testpo1 = TestPO()
        self.testpo1.params()['osp'].objects = self.some_pos

        self.testpo2 = TestPO()
        self.testpo1.params()['osp'].objects = self.some_pos
        
        self.toplevel = Tkinter.Toplevel()
        self.f = ParametersFrameWithApply(self.toplevel,self.testpo1)



    def test_set_PO(self):
        self.assertEqual(self.f._extraPO,self.testpo1)
        self.f.set_PO(self.testpo2)
        self.assertEqual(self.f._extraPO,self.testpo2)
        


    def test_apply_button_1(self):
        """
        Check:
          when pressing apply after no changes, objects should remain
          unchanged, and should still be displayed the same as before.
        """
        ## check that update doesn't affect the variable values
        orig_values = {}
        for param_name,tkvar in self.f._tk_vars.items():
            orig_values[param_name] = tkvar._original_get()

        self.f.Apply()

        for param_name,val in orig_values.items():
            self.assertEqual(self.f._tk_vars[param_name].get(),val)

        ## and check that *displayed* values don't change 
        orig_values = {}
        for param_name,representation in self.f.representations.items():
            widget = representation['widget']
            
            # button-type widgets don't have a value
            widget_has_value = not 'command' in widget.config()
                            
            if widget.__class__ not in cannot_get_value and widget_has_value:
                orig_values[param_name] = widget.get()
        
        self.f.Apply()

        for param_name,val in orig_values.items():
            widget = self.f.representations[param_name]['widget']
            self.assertEqual(widget.get(),val)


    def test_apply_button_2(self):
        """
        Check:
          When code to instantiate an object is typed into the entry
          representing a Parameter, if that object exists in main it
          should be instantiated. Further, the display should NOT then
          include quote marks.

          (Only time should get quotation marks is when editing a
          Parameter and trying to create an instance of a class that
          hasn't been imported: then string is assumed, and quotes are
          added - since it's not a StringParameter.)

          Finally, check that when the string remains the same in a box
          that a new object is not instantiated each time Apply is pressed.
        """
        exec "from topo.tests.testparametersframe import TestPO" in __main__.__dict__
        w = self.f.representations['pa']['widget']
        w.delete(0,"end")
        w.insert(0,"TestPO()")
        self.f.Apply()
        content = w.get()
        self.assertEqual(type(self.f.pa),TestPO) # get the object?
        self.assertEqual(content[0:7],"TestPO(") # object displayed right?

        # Now check that pressing apply over and over does not
        # create a new object each time when the same string remains
        # in the widget 
        testpo_id = id(self.f.pa)
        self.f.Apply()
        self.assertEqual(id(self.f.pa),testpo_id)
        # ...but that we do get a new object when the string really changes
        w.delete(0,"end")
        w.insert(0,"TestPO(name='fred')")
        self.f.Apply()
        self.assertNotEqual(id(self.f.pa),testpo_id)
        

# CEBALERT: need test for defaults button. Check that works ok
# for non-instantiated params etc

            

    
        



###########################################################

cases = [TestParametersFrameWithApply]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])
suite.requires_display = True

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

