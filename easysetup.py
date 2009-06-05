#!/usr/bin/env python

# CB: work in progress. We need numpy, scipy, and pil to work with
# easy_install before we can make any more progress...

# Script to allow 'easy_install topographica'

from setuptools import setup

from _setup import common

setup(
      install_requires=["numpy >= 1.0",
                        "gmpy >= 1.0",
                        "matplotlib >= 0.91",
                        "scipy >= 0.3.0",
                        "ipython >= 0.8",
                        "imaging >= 1.1.6",
                        #
                        # python-imaging-tk 
                        # python-tk          
                        # tcllib
                        # tklib
                        ],
      # pil pypi links are broken?
      dependency_links=['http://www.pythonware.com/products/pil/'],
      **common
     )
