"""
easy_install build script for Topographica.

(eventually "easy_install topographica")

Work in progress: currently missing weave, and still have to get some
prerequisites manually.


Usage:
    python setup_ez.py develop
or
    python setup_ez.py install
"""

# prerequisites:
#
# * python (with Tkinter for the GUI: also tcllib and tklib for GUI)
# * GMP (if using a package manager, also get -dev version. E.g. "sudo apt-get install libgmp3c2 libgmp3-dev")
# * numpy (e.g. "sudo easy_install numpy")

from setuptools import setup

import _setup

_setup.create_topographica_script()

setup(
      #parsed in reverse order?
      install_requires=[
                        "gmpy==1.04",
                        "matplotlib>=0.99",
# CEBALERT: need to do something about weave
#                        "scipy >= 0.3.0",
                        "ipython>=0.8",
                        "PIL==1.1.6",
# CEBALERT:"sudo easy_install numpy" works, but numpy doesn't work as dependency (numerous bug reports about this?)
#                        "numpy >= 1.1.0",
                        ],
            
      dependency_links=[# pil pypi links are broken (last checked Sep 09)
                        'http://doozy.inf.ed.ac.uk:8010/extra/PIL-1.1.6.tar.gz'
                        # otherwise can't get 0.99 (previous ones fail to build) 
                        'http://doozy.inf.ed.ac.uk:8010/extra/matplotlib-0.99.0.tar.gz',
                        # otherwise can't get 1.04 (previous ones fail to build)
                        'http://gmpy.googlecode.com/files/gmpy-1.04.zip'
                        ],
      **_setup.common
     )
