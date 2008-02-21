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
    const = Parameter(default=1,constant=True)
    ro = Parameter(default="Hello",readonly=True)
    ro2 = Parameter(default=object(),readonly=True,instantiate=True)

class AnotherTestPO(ParameterizedObject):
    instPO = Parameter(default=TestPO(),instantiate=True)
    notinstPO = Parameter(default=TestPO(),instantiate=False)


class TestAbstractPO(ParameterizedObject):
    __abstract = True


class TestParameterizedObject(unittest.TestCase):

    def test_constant_parameter(self):
        """Test taht you can't set a constant parameter after construction."""
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


    def test_abstract_class(self):
        """Check that a class declared abstract actually shows up as abstract."""
        self.assertEqual(TestAbstractPO.abstract,True)
        self.assertEqual(TestPO.abstract,False)


    def test_params(self):

        ## basic test
        # CB: test not so good because it requires changes if params of PO are changed
        assert 'name' in ParameterizedObject.params()
        assert 'print_level' in ParameterizedObject.params()
        assert len(ParameterizedObject.params())==2

        ## check for bug where subclass Parameters were not showing up if params() already
        # called on a super class.
        assert 'inst' in TestPO.params()
        assert 'notinst' in TestPO.params()

        ## check caching
        assert ParameterizedObject.params() is ParameterizedObject().params(), "Results of params() should be cached." # just for performance reasons




suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestParameterizedObject))
