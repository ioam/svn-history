"""
Test directory for the tkgui package in topo/tkgui.

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
