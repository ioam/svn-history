common = dict(

    name='Topographica',

    version='0.9.6' ,

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


# CEBALERT: duplicates Makefile. Could we have a python script to do
# this, called by both Makefile and setup.py? 
def create_topographica_script(python_bin='/usr/bin/python',release=None,version=None):

    script = """#!%s
# Startup script for Topographica

import topo
topo.release='%s'
topo.version='%s'

# Process the command-line arguments
from sys import argv
from topo.misc.commandline import process_argv
process_argv(argv[1:])
"""%(python_bin,release,version)
    f = open('topographica','w')
    f.write(script)
    f.close()

