"""
Tests for the tkParameterizedObject classes.

$Id$
"""
__version__='$Revision$'


## CB: add test for change of po


import __main__
import unittest
from Tkinter import Frame,Toplevel

from topo.base.simulation import Simulation
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import BooleanParameter,Number,Parameter, \
                                       ObjectSelectorParameter,ClassSelectorParameter, \
                                       StringParameter
from topo.base.patterngenerator import PatternGenerator
import topo.patterns.basic
from topo.patterns.basic import Gaussian        
from topo.outputfns.basic import PiecewiseLinear

from topo.tkgui.tkparameterizedobject import TkParameterizedObject


# CEBALERT: can't have this code present when doing "make tests" - why?
## # In case this test is run alone, start tkgui
## # (otherwise simulation of gui set()s and get()s doesn't work)
## if not hasattr(topo,'guimain'):
##     import topo.tkgui; topo.tkgui.start()


class SomeFrame(TkParameterizedObject,Frame):
    boo = BooleanParameter(default=True)
    osp = ObjectSelectorParameter()
    csp = ClassSelectorParameter(class_=PatternGenerator)
    const = Parameter(1.0,constant=True)
    pa = Parameter(default="test")
    nu = Number(default=1.0,bounds=(-1,1))
    st = StringParameter("string1")

    def __init__(self,master,extraPO=None,**params):
        TkParameterizedObject.__init__(self,master,extraPO=extraPO,**params)
        Frame.__init__(self,master)
        self.boocount=0

    def upboocount(self):
        self.boocount+=1



class TestTkParameterizedObject(unittest.TestCase):


    def setUp(self):
        pass

    def test_basic(self):
        """
        Check basic setting and getting of attributes (via
        object.attribute and GUI set()/get()).
        """
        f = SomeFrame(Toplevel())
        f.pack()

        f.pack_param('const')
        
        f.pack_param('boo',on_change=f.upboocount)

        self.assertEqual(f.boo,True); self.assertEqual(f.boocount,0)

        f.boo = False
        self.assertEqual(f.boocount,1) # check that on_change was called
        self.assertEqual(f.boo,False)  # check that f.boo was set
        self.assertEqual(f._tk_vars['boo'].get(),False) # simulate GUI get & check result


        f._tk_vars['boo'].set(True) # simulate GUI set
        self.assertEqual(f.boocount,2) # check that on_change was called
        self.assertEqual(f.boo,True) # check that f.boo was actually set
        self.assertEqual(f._tk_vars['boo'].get(),True) # simulate GUI get

          
        
    def test_basic_shadow(self):
        """
        Check shadowing of a PO's parameters.
        """
        g = Gaussian()
        f = SomeFrame(Toplevel(),extraPO=g)
        f.pack()

        f.pack_param('x') # (from the Gaussian)

        # (just so we know g.x doesn't start equal to 0.75)
        g.x=0.1 
        f.x=0.75
        # test that setting f.x (where x is shadow of g.x) actually sets g.x
        self.assertEqual(g.x,0.75) 

        # simulate a GUI set & then and check g.x is set
        f._tk_vars['x'].set(0.9)
        self.assertEqual(g.x,0.9) 

        # check that up-to-date value is returned when g got changed elsewhere
        g.x=0.3
        self.assertEqual(f.x,0.3) 

        # simulate a GUI get & check up-to-date value returned
        g.x=0.4
        self.assertEqual(f._tk_vars['x'].get(),0.4) 

        # check that a method of this object can be called by on_change
        self.z = 0
        f.pack_param('boo',on_change=self.upzcount)
        f.boo=True
        self.assertEqual(self.z,1) 

    def upzcount(self): self.z+=1  # minor helper method



#### REMOVE ##############################################################################
    def test_more_shadow(self):
        """
        Check shadowing of multiple POs' parameters.

        Includes tests for handling of non-existent attributes.
        """
        g = Gaussian()
        #p = PiecewiseLinear()
        #o = OverlapPO()
        
        f = SomeFrame(Toplevel(),extraPO=g)  #  =[g,p,o]) # i.e. precedence is f,g,p,o
        f.pack()

##         f.pack_param('x') # from the Gaussian
##         f.pack_param('size') # from the Gaussian
##         f.pack_param('upper_bound') # from the PiecewiseLinear
##         f.pack_param('notoverlap') # from the OverlapPO

##         g.x = 0.1
##         f.x = 0.7
##         self.assertEqual(g.x,0.7) # test setting g.x via f.x 

##         g.size=0.151515
##         self.assertNotEqual(g.size,f.size) # because Frame has size attribute, g.size isn't accessible as f.size 

##         f._tk_vars['size'].set(0.5)
##         self.assertEqual(g.size,0.5) # GUI setting should be fine

##         f.size=0.7
##         self.assertEqual(g.size,0.7) # as in Python, a mistaken f.size=0.7 overwrites the method with a value


##         f.notoverlap = 9
##         self.assertEqual(o.x,0.0) # shouldn't have been set
##         self.assertEqual(o.size,1.0) # shouldn't have been set
##         self.assertEqual(o.notoverlap,9) # should have been set


        # CEB: the following doesn't work:
        #  self.assertRaises(AttributeError,f.does_not_exist)
        # An AttributeError *is* raised, but it doesn't seem to be caught by testing mechanism!
        # Below is equivalent test...
        try:
            f.does_not_exist
        except AttributeError:
            pass
        else:
            raise("Failed to raise AttributeError on looking up non-existent attribute 'does_not_exist'")
            
        f.did_not_exist = 9
        assert 'did_not_exist' in f.__dict__ # check that new attribute added to f's dict...
        self.assertEqual(f.did_not_exist,9)  # ...and that it was set
#### REMOVE ##############################################################################

        


    def test_direct_getting_and_setting(self):
        """
        Test the methods used to set and get Parameter values.
        """
        
        g = Gaussian()
        f = SomeFrame(Toplevel(),extraPO=g) 

        g.size=0.95
        self.assertNotEqual(f.size,g.size)
        self.assertEqual(f.get_parameter_value('size'),g.size)

        f.set_parameter_value('size',0.23)
        self.assertEqual(g.size,0.23)

        try:
            f.set_parameter_value('does_not_exist',100)
        except AttributeError:
            pass
        else:
            raise("Failed to raise AttributeError on setting non-existent *Parameter* 'does_not_exist'")

        try:
            f.get_parameter_value('does_not_exist')
        except AttributeError:
            pass
        else:
            raise("Failed to raise AttributeError on getting non-existent *Parameter* 'does_not_exist'")



class TestParameterTypeRepresentations(unittest.TestCase):


##         In the GUI, objects must sometimes be represented by strings (e.g. for an OptionMenu):
##         test that such conversion is handled correctly


    def setUp(self):
        self.f = SomeFrame(Toplevel())


    def test_number_parameter(self):
        nu_param = self.f.get_parameter_object('nu')
        nu_tkvar = self.f._tk_vars['nu']
        
        self.f.pack_param('nu')

        # check gui setting
        self.f.nu = 0.1
        nu_tkvar.set(0.4)
        self.assertEqual(self.f.nu,0.4)

        # check gui getting
        self.f.nu = 0.2
        self.assertEqual(nu_tkvar.get(),0.2)

        # try to gui set beyond the 1 upper bound
        nu_tkvar.set(40.0)
        self.assertEqual(self.f.nu,1)

        # check actual typing
        w = self.f.representations['nu']['widget'].tag
        w.delete(0,"end")
        w.insert(0,0.005)
        self.assertEqual(self.f.nu,0.005)

        # check we can retrieve a value from main
        __main__.__dict__['testA'] = 0.075
        w.delete(0,"end")
        w.insert(0,"testA")
        self.assertEqual(self.f.nu,0.075)

        # check we can do some basic maths
        exec "from math import sin,pi" in __main__.__dict__
        w.delete(0,"end")
        w.insert(0,"sin(pi)")
        from math import sin,pi
        self.assertAlmostEqual(self.f.nu,sin(pi))
        
        

    def test_object_selector_parameter(self):
        """
        Test that ObjectSelectorParameter representation works.        
        """
        some_pos = [ParameterizedObject(name='cat'),
                    ParameterizedObject(name='rat'),
                    ParameterizedObject(name='bat')]
        osp_param = self.f.get_parameter('osp')
        osp_param.Arange = some_pos
        #self.f.r.default = some_pos[0]

        self.f.pack_param('osp')  # have to pack AFTER populating range for OptionMenu widget to work (see ALERT in tkparameterizedobject.py)

        # after packing, the value of r should not be its original
        # value (None) since that's not in the range
        self.assertNotEqual(self.f.osp,None)
        # should be: self.assertEqual(f.r,some_pos[0])
        # but order not currently kept.
        
        # (otherwise, could do the following:
##         f = SomeFrame(Toplevel())
##         f.pack_param('r')
##         f.initialize_ranged_parameter('r',
##                                       [ParameterizedObject(name='cat'),ParameterizedObject(name='rat'),ParameterizedObject(name='bat')])

        self.assertEqual(self.f.translators['osp']['cat'],some_pos[0])
        self.assertEqual(self.f.translators['osp']['rat'],some_pos[1])
        self.assertEqual(self.f.translators['osp']['bat'],some_pos[2])

        gnat = ParameterizedObject(name='gnat')
        osp_param.Arange.append(gnat)
        self.f.pack_param('osp') # again, note the need to pack after updating range.
##         self.f.initialize_ranged_parameter('r',ParameterizedObject)
        self.assertEqual(self.f.translators['osp']['gnat'],gnat)

        self.assertEqual(self.f.object2string_ifrequired('osp',some_pos[0]),'cat')
        self.assertEqual(self.f.object2string_ifrequired('osp',some_pos[1]),'rat')
        self.assertEqual(self.f.object2string_ifrequired('osp',some_pos[2]),'bat')


        # Simulate a GUI set
        self.f._tk_vars['osp'].set('bat')
        self.assertEqual(self.f.osp,some_pos[2])

        # Test sorting
        # CB: add


    def test_class_selector_parameter(self):
        self.f.pack_param('csp')

        csp_param = self.f.get_parameter_object('csp')
        csp_tkvar = self.f._tk_vars['csp']

        # For class selector parameters, the tkpo should instantiate
        # all choices on pack()ing of the parameter and then maintain
        # the instances (allows persistence of edits to properties of
        # the classes during the lifetime of a window).
        csp_tkvar.set('Ring')
        self.assertEqual(type(self.f.csp),topo.patterns.basic.Ring)
        ring_id = id(self.f.csp)
        
        csp_tkvar.set('Rectangle')
        self.assertEqual(type(self.f.csp),topo.patterns.basic.Rectangle)
        rectangle_id = id(self.f.csp)
        
        csp_tkvar.set('Ring')
        self.assertEqual(id(self.f.csp),ring_id)
        csp_tkvar.set('Rectangle')
        self.assertEqual(id(self.f.csp),rectangle_id)
        
        # test sorting
        # CB: add


    def test_string_parameter(self):

        def test_fn(param_name):
            self.f.pack_param(param_name)
            w = self.f.representations[param_name]['widget']

            test_string = "new test string"
            w.delete(0,"end")
            w.insert(0,test_string)
            self.f._update_param(param_name,force=True)
            
            self.assertEqual(getattr(self.f,param_name),test_string)
            self.assertEqual(w.get(),test_string)

        # unlike when typed by a user, everything's immediate when simulating set()
        self.f.param_immediately_apply_change[StringParameter] = True
        test_fn('st')

        # and now check the test actually works by making sure
        # it doesn't work for a Parameter (there'll be an extra
        # pair of quotes, stopping a match)
        try:
            test_fn('pa')
        except AssertionError:
            pass
        else:
            raise("Test should fail for Parameter")

        


    def test_parameter(self):
        self.f.pack_param('pa')
        w = self.f.representations['pa']['widget']
        w.delete(0,"end")
        w.insert(0,"AnObjectNamedThisWillNotExist")
        self.f._update_param('pa',True)
        self.assertEqual(self.f.pa,"AnObjectNamedThisWillNotExist")

        # Check that we can create an object from a class in __main__
        exec "from topo.outputfns.basic import IdentityOF" in __main__.__dict__
        w.delete(0,"end")
        w.insert(0,"IdentityOF()")
        self.f._update_param('pa',force=True)
        import topo.outputfns.basic
        self.assertEqual(type(self.f.pa),topo.outputfns.basic.IdentityOF)




###########################################################


cases = [TestTkParameterizedObject,TestParameterTypeRepresentations]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])
suite.requires_display = True

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

