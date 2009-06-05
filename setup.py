#!/usr/bin/env python

# CB: work in progress. Current issues:
#
# (1) why does topo end up in /usr/local/lib/python2.6/dist-packages/
#     rather than site-packages?
# Maybe it's supposed to? E.g. https://bugs.launchpad.net/ubuntu/+source/python2.6/+bug/362570

from distutils.core import setup

setup(name='Topographica',
      version='0.9.6',
      description='Topographica is a general-purpose neural simulator focusing on topographic maps.',
      maintainer='Topographica Developers',
      maintainer_email='developers[at]topographica[dot]org',
      url='http://topographica.org/',
      # CEBALERT: do I have to list these? if I do, can I generate the list automatically?
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
      scripts = ['topographica']
     )
