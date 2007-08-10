"""
Tests for the tkParameterizedObject classes.

$Id$
"""
__version__='$Revision$'


import unittest
from Tkinter import Frame,Toplevel

from topo.base.simulation import Simulation
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import BooleanParameter,Number,Parameter,ObjectSelectorParameter
from topo.patterns.basic import Gaussian        
from topo.outputfns.basic import PiecewiseLinear

from topo.tkgui.tkparameterizedobject import TkParameterizedObject


class SomeFrame(TkParameterizedObject,Frame):
    k = BooleanParameter(default=True)
    r = ObjectSelectorParameter()

    def __init__(self,master,extraPO=None,**params):
        TkParameterizedObject.__init__(self,master,extraPO=extraPO,**params)
        Frame.__init__(self,master)
        self.kcount=0

    def upkcount(self):
        self.kcount+=1

class OverlapPO(ParameterizedObject):
    x = Number(0.0)
    size = Number(1.0)
    notoverlap = Number(0.4)




class SometkPO(TkParameterizedObject,Frame):

    x = ObjectSelectorParameter(default="the")
    y = ObjectSelectorParameter(default="jane")
    z = Number(default=3)


### Temporaray, I hope, like the parameter.
## class TestObjectSelectorParameter(unittest.TestCase):

##     def test_basic(self):

##         k = SometkPO(Toplevel())
##         k.x = "cat"
##         k.z = 9

##         y_param = k.params()['y']
##         y_param.range = ["fred","jane","phil"]
##         #y_param.default = "phil"

##         self.assertEqual(k.z,9) 
##         self.assertEqual(k.x,"cat")
##         #self.assertEqual(k.y,"phil")

##         x_param = k.params()['x']
##         x_param.range = ["the","cat","sat"]
##         #x_param.default = "sat"
        
##         self.assertEqual(y_param.range,["fred","jane","phil"])
##         self.assertEqual(x_param.range,["the","cat","sat"])

##         #self.assertEqual(x_param.default,"sat")
##         #self.assertEqual(y_param.default,"phil")
        

##     def test_more(self):

##         k = SometkPO(Toplevel())

##         x_param = k.params()['x']
##         y_param = k.params()['y']

##         # need to reset parameter defaults
##         x_param.range = []
##         y_param.range = []
        
##         k.x = "cat" #x_param.default = '1'
##         k.y = "phil" #y_param.default = '2'

##         k.initialize_ranged_parameter('x',range_=["the","cat","sat"])
##         k.initialize_ranged_parameter('y',range_=["fred","jane","phil"])

##         self.assertNotEqual(id(x_param.range),id(y_param.range))

##         self.assertEqual(k.x,"cat")
##         self.assertEqual(k.y,"phil")

##         self.assertEqual(x_param.range,["the","cat","sat"])
##         self.assertEqual(y_param.range,["fred","jane","phil"])

##         k.pack_param('x')
##         k.pack_param('y')

##         self.assertEqual(x_param.range,["the","cat","sat"])
##         self.assertEqual(y_param.range,["fred","jane","phil"])

##         x=k.get_parameter('x')
##         y=k.get_parameter('y')

##         self.assertEqual(x,x_param)
##         self.assertEqual(y,y_param)
        


        



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
        f.pack_param('k',on_change=f.upkcount)

        self.assertEqual(f.k,True); self.assertEqual(f.kcount,0)

        f.k = False
        self.assertEqual(f.kcount,1) # check that on_change was called
        self.assertEqual(f.k,False)  # check that f.k was set
        self.assertEqual(f._tk_vars['k'].get(),False) # simulate GUI get & check result


        f._tk_vars['k'].set(True) # simulate GUI set
        self.assertEqual(f.kcount,2) # check that on_change was called
        self.assertEqual(f.k,True) # check that f.k was actually set
        self.assertEqual(f._tk_vars['k'].get(),True) # simulate GUI get

          
        
    def test_basic_shadow(self):
        """
        Check shadowing of a PO's parameters.
        """
        g = Gaussian()
        f = SomeFrame(Toplevel(),extraPO=g)
        f.pack()

        f.pack_param('x') # (from the Gaussian)

        g.x = 0.1 # (just so we know g.x doesn't start equal to 0.75)
        f.x=0.75
        self.assertEqual(g.x,0.75) # test that setting f.x (where x is shadow of g.x) actually sets g.x

        f._tk_vars['x'].set(0.9)
        self.assertEqual(g.x,0.9) # simulate a GUI set & then and check g.x is set

        g.x=0.3
        self.assertEqual(f.x,0.3) # check that up-to-date value is returned when g got changed elsewhere

        g.x=0.4
        self.assertEqual(f._tk_vars['x'].get(),0.4) # simulate a GUI get & check up-to-date value returned

        self.z = 0
        f.pack_param('k',on_change=self.upzcount)
        f.k=True
        self.assertEqual(self.z,1) # check that a method of this object can be called by on_change

    def upzcount(self): self.z+=1  # minor helper method


    def test_more_shadow(self):
        """
        Check shadowing of multiple POs' parameters.

        Includes tests for handling of non-existant attributes.
        """
        g = Gaussian()
        p = PiecewiseLinear()
        o = OverlapPO()
        
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
            raise("Failed to raise AttributeError on looking up non-existant attribute 'does_not_exist'")
            
        f.did_not_exist = 9
        assert 'did_not_exist' in f.__dict__ # check that new attribute added to f's dict...
        self.assertEqual(f.did_not_exist,9)  # ...and that it was set



    def test_direct_getting_and_setting(self):
        
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
            raise("Failed to raise AttributeError on setting non-existant *Parameter* 'does_not_exist'")

        try:
            f.get_parameter_value('does_not_exist')
        except AttributeError:
            pass
        else:
            raise("Failed to raise AttributeError on getting non-existant *Parameter* 'does_not_exist'")


    # CB: will need to be updated once ClassSelectorParam/ObjectSelectorParam are finished.
    def test_translation(self):
        """
        In the GUI, objects must sometimes be represented by strings (e.g. for an OptionMenu):
        test that such conversion is handled correctly
        """
        f = SomeFrame(Toplevel())

        some_pos = [ParameterizedObject(name='cat'),ParameterizedObject(name='rat'),ParameterizedObject(name='bat')]
        r = f.get_parameter('r')
        r.Arange = some_pos
        #f.r.default = some_pos[0]

        f.pack_param('r')  # have to pack AFTER populating range for OptionMenu widget to work (see tkparameterizedobject.py)

        # after packing, the value of r should not be its original value (None) since that's not in the range
        self.assertNotEqual(f.r,None)
        # should be: self.assertEqual(f.r,some_pos[0])
        # but order not currently kept.

        
        # (otherwise, could do the following:
##         f = SomeFrame(Toplevel())
##         f.pack_param('r')
##         f.initialize_ranged_parameter('r',
##                                       [ParameterizedObject(name='cat'),ParameterizedObject(name='rat'),ParameterizedObject(name='bat')])

        # tests converta()
        self.assertEqual(f.translators['r']['cat'],some_pos[0])
        self.assertEqual(f.translators['r']['rat'],some_pos[1])
        self.assertEqual(f.translators['r']['bat'],some_pos[2])

        gnat = ParameterizedObject(name='gnat')
        r.Arange.append(gnat)
        f.pack_param('r') # again, note the need to pack after updating range.
##         f.initialize_ranged_parameter('r',ParameterizedObject)
        self.assertEqual(f.translators['r']['gnat'],gnat)


        self.assertEqual(f.atrevnoc('r',some_pos[0]),'cat')
        self.assertEqual(f.atrevnoc('r',some_pos[1]),'rat')
        self.assertEqual(f.atrevnoc('r',some_pos[2]),'bat') 




###########################################################


cases = [TestTkParameterizedObject] #,TestObjectSelectorParameter]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])
suite.requires_display = True

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

