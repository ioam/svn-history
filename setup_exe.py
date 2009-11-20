"""
py2exe build script for Topographica.

Work in progress

Usage:
    python setup.py py2exe
"""

from distutils.core import setup
import py2exe

import create_topographica_script
create_topographica_script.write()


setup(console=['topographica'])
# (we won't want console eventually - use windows= instead)
