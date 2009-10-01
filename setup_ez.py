"""
easy_install build script for Topographica.

(eventually "easy_install topographica")

Work in progress.

Usage:
    python setup_ez.py develop
or
    python setup_ez.py install
"""

# Required:
#
# * python, python-dev
# * GMP (if using a package manager, also get -dev version. E.g. "sudo apt-get install libgmp3c2 libgmp3-dev")
#
# Optional:
# 
# * GUI: tcl8.5,tcl8.5-dev,tk8.5,tk8.5-dev,tcllib,tklib,python-tk



from setuptools import setup

import _setup

_setup.create_topographica_script()

setup(
      #parsed in reverse order?
      install_requires=[
                        "weave==0.4.9",
                        "pyscrodget==0.0.2_2.1",
                        "gmpy==1.04",
                        "matplotlib>=0.99",
# CEBALERT: need to do something about weave
#                        "scipy >= 0.3.0",
                        "ipython>=0.8",
                        "numpy >= 1.2.0",
                        "PIL == 1.1.6", # error unless done before numpy!
                        ],

      # pil pypi links are broken (last checked Sep 09)
      # pil doesn't work with setuptools (Imaging vs PIL)
      # http://www.gossamer-threads.com/lists/python/python/772845
      # pil patched to find tk includes
      
      # matplotlib-0.99.1.1.tar.gz has stray setup.cfg in it
      # ...

      # numpy patched to work as dependency
      # (http://projects.scipy.org/numpy/ticket/999)            

      dependency_links=['http://doozy.inf.ed.ac.uk:8010/extra/',

                        # otherwise can't get 1.04 (previous ones fail to build)
                        'http://gmpy.googlecode.com/files/gmpy-1.04.zip'],
        
      **_setup.common
     )
