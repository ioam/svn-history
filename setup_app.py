"""
py2app build script for Topographica.

Work in progress

Usage:
    python setup.py py2app
"""
from setuptools import setup
setup(
    app=["topographica"],
    setup_requires=["py2app"],
)
