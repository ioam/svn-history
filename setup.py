#!/usr/bin/env python

# CB: work in progress

# To install topo package and topographica script, assuming all
# dependencies are satisfied (as given in _setup.py):
# python setup.py install

from distutils.core import setup

import _setup

_setup.create_topographica_script()
setup(**_setup.common)

