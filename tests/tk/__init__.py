import os,unittest

import testpropertiesframe
import testtopoconsole
import testplotpanel

suite = unittest.TestSuite()

display_loc = os.getenv('DISPLAY')
for key,val in locals().items():
    if type(val) == type(unittest) and not val in (unittest, os):
        try:
            print 'Checking module tk.%s for test suite...' % key,
            new_test = getattr(val,'suite')
            if hasattr(new_test,'requires_display') and not display_loc:
                print 'skipped: No $DISPLAY.'
            else:
                print 'found.'
                suite.addTest(new_test)
        except AttributeError,err:
            print err

