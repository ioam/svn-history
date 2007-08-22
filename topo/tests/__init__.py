"""
Unit tests for Topographica.

Sets up all tests in any file in this directory whose name begins with
'test' and ends '.py', if it define the 'suite' attribute.

Use the 'run' function to run the tests.


$Id$
"""
__version__='$Revision$'

# CEBALERT: It might be good if tests/ were a directory at the top
# level, with a subdirectory structure mirroring that of topo/. Then
# it is more likely we'd have a separate test file for each module,
# and we could also simply name the files the same as what they are
# testing, which could make it simpler to find the right test file.


# CEBALERT: the tests need to be cleaned up. In each test file,
# setup() is to setup something that a series of tests can then all use.
# That saves on duplication, etc.
# We should at least start doing it right from now, or this problem
# is going to grow.
#
# Additionally, tests often affect each other. Instead of creating
# independent objects, they often share them (in particular, they
# often share topo.sim). 



import unittest,doctest,os,re,fnmatch

# Automatically discover all test*.py files in this directory
__all__ = [re.sub('\.py$','',f)
           for f in fnmatch.filter(os.listdir(__path__[0]),'test*.py')]

all_doctest = sorted(fnmatch.filter(os.listdir(__path__[0]),'test*.txt'))


# Remove any test that for now we don't want to run with the others
__all__.remove('test_script')   # this is a slower test & should have a different
                                # calling mechanism (see Future_Work/current)


__all__.sort()


def all_suite():
    """
    For each test module that defines a 'suite' attribute, add its tests.
    Only adds tests requiring a display if the DISPLAY environment
    variable is set.
    """
    suite = unittest.TestSuite()
    display_loc = os.getenv('DISPLAY')    
    for test_name in __all__:
        # import the module
        exec 'import '+test_name

        test_module = locals()[test_name]
        try:        
            print 'Checking module %s for test suite...' % test_name,
            new_test = getattr(test_module,'suite')

            if hasattr(new_test,'requires_display') and not display_loc:
                print 'skipped: No $DISPLAY.'
            else:
                print 'found.'
                suite.addTest(new_test)
        except AttributeError,err:
            print err

    for filename in all_doctest:
        print 'Loading doctest file', filename
        suite.addTest(doctest.DocFileSuite(filename))
    return suite


def run(verbosity=1,test_modules=None):
    """
    By default, run all tests in any file in this directory whose name
    begins with 'test' and ends '.py', if it define the 'suite'
    attribute.

    Example usage:
      ./topographica -c 'import topo.tests; topo.tests.run()'

    
    verbosity specifies the level of information printed during the
    tests (see unittest.TextTestRunner).

    To run only a subset of the tests, specify the module names in
    test_modules. For example:
    
      ./topographica -c 'import topo.tests.testimage; topo.tests.run(test_modules=[topo.tests.testimage])'    
    """

    import types
    
    suite = None
    
    if not test_modules:
        suite = all_suite()
    else:
        assert isinstance(test_modules,list), 'test_modules argument must be a list of test modules or doctest filenames.'
        
        suite = unittest.TestSuite()
        for test_module in test_modules:
            if isinstance(test_module,types.ModuleType):
                suite.addTest(getattr(test_module,'suite'))
            elif isinstance(test_module,str):
                if test_module in all_doctest:
                    suite.addTest(doctest.DocFileSuite(test_module))
                elif test_module+'.txt' in all_doctest:
                    suite.addTest(doctest.DocFileSuite(test_module+'.txt'))
                else:
                    raise ValueError, '"%s" is not an available doctest file.' % test_module
            else:
                raise ValueError, '%s is not a valid test module' % str(test_module)
                                 

    return unittest.TextTestRunner(verbosity=verbosity).run(suite)

