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


import unittest,re,os

# Automatically discover all test*.py files in this directory
# and import them. 
__all__ = [re.sub('\.py$','',f)
           for f in os.listdir(__path__[0])
           if re.match('^test.*\.py$',f)]

for test_name in __all__:
    exec 'import '+test_name


# For each test module that defines a 'suite' attribute, add its
# tests.
# Only adds tests requiring a display if the DISPLAY environment
# variable is set.
suite = unittest.TestSuite()
display_loc = os.getenv('DISPLAY')
for test_name in __all__:    
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

    if not test_modules:
        unittest.TextTestRunner(verbosity=verbosity).run(suite)
    else:
        new_suite = unittest.TestSuite()
        for test_module in test_modules:
            new_suite.addTest(getattr(test_module,'suite'))
        unittest.TextTestRunner(verbosity=verbosity).run(new_suite)

