"""
Tests for the tkParameterizedObject classes.

$Id$
"""
__version__='$Revision$'


import unittest
from Tkinter import Frame,Toplevel

from topo.base.simulation import Simulation
from topo.base.parameterizedobject import ParameterizedObject
from topo.base.parameterclasses import BooleanParameter,Number
from topo.patterns.basic import Gaussian        
from topo.outputfns.basic import PiecewiseLinear

from topo.tkgui.tkparameterizedobject import TkParameterizedObject



class SomeFrame(TkParameterizedObject,Frame):
    k = BooleanParameter(default=True)

    def __init__(self,master,extra_pos=[],**params):
        TkParameterizedObject.__init__(self,master,extra_pos=extra_pos,**params)
        Frame.__init__(self,master)
        self.kcount=0

    def upkcount(self):
        self.kcount+=1

class OverlapPO(ParameterizedObject):
    x = Number(0.0)
    size = Number(1.0)
    notoverlap = Number(0.4)



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
        f = SomeFrame(Toplevel(),extra_pos=[g])
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
        """
        g = Gaussian()
        p = PiecewiseLinear()
        o = OverlapPO()
        
        f = SomeFrame(Toplevel(),extra_pos=[g,p,o]) # i.e. precedence is f,g,p,o
        f.pack()

        f.pack_param('x') # from the Gaussian
        f.pack_param('size') # from the Gaussian
        f.pack_param('upper_bound') # from the PiecewiseLinear
        f.pack_param('notoverlap') # from the OverlapPO

        g.x = 0.1
        f.x = 0.7
        self.assertEqual(g.x,0.7) # test setting g.x via f.x 

        g.size=0.151515
        self.assertNotEqual(g.size,f.size) # because Frame has size attribute, g.size isn't accessible as f.size 

        f._tk_vars['size'].set(0.5)
        self.assertEqual(g.size,0.5) # GUI setting should be fine

        f.size=0.7
        self.assertEqual(g.size,0.7) # as in Python, a mistaken f.size=0.7 overwrites the method with a value


        f.notoverlap = 9
        self.assertEqual(o.x,0.0) # shouldn't have been set
        self.assertEqual(o.size,1.0) # shouldn't have been set
        self.assertEqual(o.notoverlap,9) # should've been set


##     def test_translation(self):
##         pass






###########################################################

cases = [TestTkParameterizedObject]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)

