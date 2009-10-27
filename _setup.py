## Dependencies for Ubuntu 9.04
## ============================
##
## $ sudo apt-get install python python-dev python-numpy python-gmpy python-matplotlib python-scipy ipython python-tk python-imaging python-imaging-tk
## 
##
## Dependencies for MacPorts on OS X 10.6
## ======================================
## 
## $ sudo port install python25 py25-tkinter py25-numpy py25-matplotlib py25-pil py25-scipy py25-ipython
## $ sudo port install python_select
## $ sudo port python_select python25

_topographica_devs='Topographica Developers'
_topographica_devs_email='developers[at]topographica[dot]org'
 
common = dict(

    name='Topographica',

    version='0.9.6' ,

    description='[NOTE: PACKAGING UNDER DEVELOPEMT] A general-purpose neural simulator focusing on topographic maps.',

    long_description="Topographica is a software package for computational modeling of neural maps. The goal is to help researchers understand brain function at the level of the topographic maps that make up sensory and motor systems.",

    author= _topographica_devs,
    author_email= _topographica_devs_email,
    maintainer= _topographica_devs,
    maintainer_email= _topographica_devs_email,

    url='http://topographica.org/',

    classifiers = [
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: OS Independent"],

    requires = ["PIL",         # Can't seem to specify versions. This is like 
                "numpy",       # install_requires for setuptools 
                "matplotlib",  # But they all seem to be ignored!
                "ipython",
                "scipy"],

    # CEBALERT: do I have to list these? if I do, can I generate the list automatically?
    packages=['topo',
              'param',
              'topo.analysis',
              'topo.base',
              'topo.command',
              'topo.coordmapper',
              'topo.ep',
              'topo.learningfn',
              'topo.misc',
              'topo.numbergen',
              'topo.transferfn',
              'topo.pattern',
              'topo.plotting',
              'topo.projection',
              'topo.responsefn',
              'topo.sheet',
              'topo.tests',
              'topo.tkgui'],

    package_data={
        # These things are not data. I'm not sure how else to do
        # this - I couldn't find documentation.
        'param': ['externaltk/snit-2.2.1/*.tcl',
                  'externaltk/scrodget-2.1/*.tcl',
                  'externaltk/tooltip-1.4/*.tcl'],

        'topo.tkgui': ['icons/*.*'],
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

