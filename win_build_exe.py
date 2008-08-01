# CB: work in progress
# Create exe in Windows

from distutils.core import setup
import py2exe

setup(console=['topographica'])
# (we won't want console eventually - use windows= instead)
