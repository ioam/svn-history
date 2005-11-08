"""
Unit tests for Topographica

$Id$
"""
__version__='$Revision $'

### JABALERT!
###
### Should change this to be like topo/patterns/__init__.py, i.e.
### to automatically discover the test files.  That way new tests
### can be just dropped in.

import unittest, os
import testboundingregion
import testdummy
import testbitmap
import testsheet
import testsheetview
import testhistogram
import testplot
import testplotgroup
import testplotengine
import testplotfilesaver
import testsimulator
import testpalette
import testcfsom
import testpatterngenerator
import testmatplotlib
import testpatternpresent
import testdistribution
import testfeaturemap


# tkgui import calls tkgui/__init__.py, which should contain other test
# imports for that directory.
import tkgui

suite = unittest.TestSuite()

display_loc = os.getenv('DISPLAY')
for key,val in locals().items():
    if type(val) == type(unittest) and not val in (unittest, os):
        try:
            print 'Checking module %s for test suite...' % key,
            new_test = getattr(val,'suite')
            if hasattr(new_test,'requires_display') and not display_loc:
                print 'skipped: No $DISPLAY.'
            else:
                print 'found.'
                suite.addTest(new_test)
        except AttributeError,err:
            print err


