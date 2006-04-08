"""
Unit tests for Topographica.

Runs all tests in every file in this directory and the tkgui/
subdirectory whose name begins with 'test' and ends '.py',
if they define the 'suite' attribute.

$Id$
"""
__version__='$Revision$'

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
    

def run(verbosity=1):
    unittest.TextTestRunner(verbosity=verbosity).run(suite)

