"""
Unit tests for Topographica

$Id$
"""

import unittest
import testboundingregion
import testdummy
import testbitmap
import testsheet
import testsheetview
import testhistogram
import testplot
import testplotengine
import testsimulator
import testpalette
import testgui
import testpropertiesframe

suite = unittest.TestSuite()

for key,val in locals().items():
    if type(val) == type(unittest) and val != unittest:
        try:
            print 'Checking module %s for test suite...' % key,
            suite.addTest(getattr(val,'suite'))
            print 'found.'
        except AttributeError,err:
            print err

