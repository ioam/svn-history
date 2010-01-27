"""
Required Dependencies
=====================

Below are the requirements for Topographica. Packages are listed with
the version we normally use, followed by other versions we expect
would work (but have not necessarily tested).

* Python 2.6 (with Tkinter to get the GUI)
Python 2.5 

* NumPy 1.3
NumPy>=1.0

* Matplotlib 0.99 (with support for Tkinter for GUI)
Matplotlib 0.91

* Imaging (PIL) (with support for Tkinter for GUI)
PIL>=1.1.4

* SciPy 0.7
SciPy>=0.3 (must be compatible with NumPy version)

* IPython 0.10
IPython>0.8

* gmpy >=1.01 OR * fixedpoint 0.1.2



Ubuntu 9.04
-----------

$ sudo apt-get install python python-dev python-numpy python-gmpy python-matplotlib python-scipy ipython python-tk python-imaging python-imaging-tk


MacPorts on Mac OS X 10.6
-------------------------

$ sudo port install python26 py26-numpy py26-matplotlib py26-pil py26-scipy py26-ipython gmp python_select
$ sudo port python_select python26
$ curl http://gmpy.googlecode.com/files/gmpy-1.10.zip > gmpy-1.10.zip
$ open gmpy-1.10.zip; rm gmpy-1.10.zip
$ cd gmpy-1.10/; sudo python setup.py install



"""

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

