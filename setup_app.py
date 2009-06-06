"""
py2app build script for Topographica.

Work in progress

Usage:
    python setup.py py2app
"""
from setuptools import setup

# Currently this doesn't work because Topographica doesn't build
# lib/libpython2.5.dylib.  Not sure what to do about that.

OPTIONS = {
    'packages': ['numpy','matplotlib','pil'] # ...more to go
    }

setup(
    app=["topographica.py"],
    setup_requires=["py2app"],
    options = {'py2app':OPTIONS}
)
