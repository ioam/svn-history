#!/usr/bin/env python

from distutils.core import setup

setup(name='Topographica',
      version='0.9.6',
      description='Topographica is a general-purpose neural simulator focusing on topographic maps.',
      maintainer='Topographica Developers',
      maintainer_email='developers[at]topographica[dot]org',
      url='http://topographica.org/',
      # CEBALERT: do I have to list these?
      packages=['topo',
                'topo.analysis',
                'topo.base',
                'topo.command',
                'topo.coordmapper',
                'topo.ep',
                'topo.learningfn',
                'topo.misc',
                'topo.transferfn',
                'topo.param',
                'topo.pattern',
                'topo.plotting',
                'topo.projection',
                'topo.responsefn',
                'topo.sheet',
                'topo.tests',
                'topo.tkgui']
     )
