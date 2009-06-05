#!/usr/bin/env python

# CB: work in progress. 

from setuptools import setup#,find_packages
# consider using packages=find_packages()?

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
      # pil pypi entry seems is broken?
      dependency_links=['http://www.pythonware.com/products/pil/'],
      **common
     )
