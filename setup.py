#!/usr/bin/env python

# CB: work in progress.

# As of 2009/10/03, tested successfully on:
# Ubuntu 9.04  
# Mac OS X 10.6 with MacPorts

# See _setup.py for list of dependencies, then:
# sudo python setup.py install
# (or alternative, such as "python setup.py install --prefix=...")

from distutils.core import setup

import _setup

_setup.create_topographica_script()
setup(**_setup.common)

