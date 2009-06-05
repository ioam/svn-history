#!/usr/bin/env python

# CB: work in progress. 

from setuptools import setup#,find_packages

install_requires=[
    "numpy >= 1.0",
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
    ]

setup(name='Topographica',
      version='0.9.6',
      description='Topographica is a general-purpose neural simulator focusing on topographic maps.',
      maintainer='Topographica Developers',
      maintainer_email='developers[at]topographica[dot]org',
      url='http://topographica.org/',
      # CEBALERT: do I have to list these? if I do, can I generate the list automatically?
#      packages=find_packages(),
      packages=['topo',
                'topo.analysis',
                'topo.base',
                'topo.command',
                'topo.coordmapper',
                'topo.ep',
                'topo.ipythonTk',
                'topo.learningfn',
                'topo.misc',
                'topo.numbergen',
                'topo.transferfn',
                'topo.param',
                'topo.pattern',
                'topo.plotting',
                'topo.projection',
                'topo.responsefn',
                'topo.sheet',
                'topo.tests',
                'topo.tkgui'],
      package_data={'topo.tkgui': ['icons/*.*'],
                    'topo.command':['*.png','*.pdf'],
                    'topo.tests':['*.txt','*.jpg','*.pgm']},
      scripts = ['topographica'],
      install_requires=install_requires,
      dependency_links=['http://www.pythonware.com/products/pil/']
     )
