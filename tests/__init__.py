"""
Unit tests for Topographica

$Id$
"""

import unittest
import testboundingregion
import testdummy
import testsheet
import testbitmap
import testplot

suite = unittest.TestSuite()

for key,val in locals().items():
    if type(val) == type(unittest) and val != unittest:
        try:
            print 'Checking module %s for test suite...' % key,
            suite.addTest(getattr(val,'suite'))
            print 'found.'
        except AttributeError,err:
            print err

