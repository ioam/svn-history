"""
Unit test for Parameterized.


$Id$
"""
__version__='$Revision$'

import unittest

from .. import param

# CEBALERT: not anything like a complete test of Parameterized!

class TestPO(Parameterized):
    inst = Parameter(default=[1,2,3],instantiate=True)
    notinst = Parameter(default=[1,2,3],instantiate=False)
    const = Parameter(default=1,constant=True)
    ro = Parameter(default="Hello",readonly=True)
    ro2 = Parameter(default=object(),readonly=True,instantiate=True)

    dyn = param.Dynamic(default=1)

class AnotherTestPO(Parameterized):
    instPO = Parameter(default=TestPO(),instantiate=True)
    notinstPO = Parameter(default=TestPO(),instantiate=False)


class TestAbstractPO(Parameterized):
    __abstract = True


class TestParameterized(unittest.TestCase):

    def test_constant_parameter(self):
        """Test that you can't set a constant parameter after construction."""
        testpo = TestPO(const=17)
        self.assertEqual(testpo.const,17)
        self.assertRaises(TypeError,setattr,testpo,'const',10)

        # check you can set on class
        TestPO.const=9
        testpo = TestPO()
        self.assertEqual(testpo.const,9)

    def test_readonly_parameter(self):
        """Test that you can't set a read-only parameter on construction or as an attribute."""
        testpo = TestPO()
        self.assertEqual(testpo.ro,"Hello")

        # CB: couldn't figure out how to use assertRaises
        try:
            t = TestPO(ro=20)
        except TypeError:
            pass
        else:
            raise AssertionError("Read-only parameter was set!")

        t=TestPO()
        self.assertRaises(TypeError,setattr,t,'ro',10)

        # check you cannot set on class
        self.assertRaises(TypeError,setattr,TestPO,'ro',5)

        self.assertEqual(testpo.params()['ro'].constant,True)

        # check that instantiate was ignored for readonly
        self.assertEqual(testpo.params()['ro2'].instantiate,False)
        


    def test_basic_instantiation(self):
        """Check that instantiated parameters are copied into objects."""

        testpo = TestPO()

        self.assertEqual(testpo.inst,TestPO.inst)
        self.assertEqual(testpo.notinst,TestPO.notinst)

        TestPO.inst[1]=7
        TestPO.notinst[1]=7
        
        self.assertEqual(testpo.notinst,[1,7,3])
        self.assertEqual(testpo.inst,[1,2,3])


    def test_more_instantiation(self):
        """Show that objects in instantiated Parameters can still share data."""
        anothertestpo = AnotherTestPO()

        ### CB: AnotherTestPO.instPO is instantiated, but
        ### TestPO.notinst is not instantiated - so notinst is still
        ### shared, even by instantiated parameters of AnotherTestPO.
        ### Seems like this behavior of Parameterized could be
        ### confusing, so maybe mention it in documentation somewhere.
        TestPO.notinst[1]=7
        # (if you thought your instPO was completely an independent object, you
        # might be expecting [1,2,3] here)
        self.assertEqual(anothertestpo.instPO.notinst,[1,7,3])


    def test_abstract_class(self):
        """Check that a class declared abstract actually shows up as abstract."""
        self.assertEqual(TestAbstractPO.abstract,True)
        self.assertEqual(TestPO.abstract,False)


    def test_params(self):
        """Basic tests of params() method."""


        # CB: test not so good because it requires changes if params
        # of PO are changed
        assert 'name' in Parameterized.params()
        assert 'print_level' in Parameterized.params()
        assert len(Parameterized.params())==2

        ## check for bug where subclass Parameters were not showing up
        ## if params() already called on a super class.
        assert 'inst' in TestPO.params()
        assert 'notinst' in TestPO.params()

        ## check caching
        assert Parameterized.params() is Parameterized().params(), "Results of params() should be cached." # just for performance reasons


    def test_state_saving(self):
        from topo.misc.numbergenerators import UniformRandom
        t = TestPO(dyn=UniformRandom())
        g = t.get_value_generator('dyn')
        g._Dynamic_time_fn=None
        assert t.dyn!=t.dyn
        orig = t.dyn
        t.state_push()
        t.dyn
        assert t.inspect_value('dyn')!=orig
        t.state_pop()
        assert t.inspect_value('dyn')==orig
        
        


suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestParameterized))
