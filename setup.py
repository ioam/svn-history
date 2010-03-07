#!/usr/bin/env python

from distutils.core import setup

_topographica_devs='Topographica Developers'
_topographica_devs_email='developers[at]topographica[dot]org' 

setup(
    name='Topographica',

    version='0.9.7a',

    description='A general-purpose neural simulator focusing on topographic maps.',

    long_description="""
`Topographica`_ is a software package for computational modeling of neural maps. The goal is to help researchers understand brain function at the level of the topographic maps that make up sensory and motor systems.

Topographica's full documentation is available at http://topographica.org/.

Installation
============

Topographica requires `NumPy`_ and `PIL`_. We strongly recommend that you also install `MatPlotLib`_ so you can access all Topographica's plots, as well as `Gmpy`_ and Weave (available as part of `SciPy`_) for optimum performance.

Once you have the prerequisites, you should be able to install Topographica system-wide with a command like ``sudo python setup.py install``, or into your user directory with ``python setup.py install --user``.

Note that this package is not yet fully tested; please see http://topographica.org/Downloads for official releases.

.. _Topographica:
   http://topographica.org/Home/index.html
.. _NumPy: 
   http://pypi.python.org/pypi/numpy
.. _Gmpy: 
   http://pypi.python.org/pypi/gmpy
.. _SciPy: 
   http://pypi.python.org/pypi/scipy
.. _MatPlotLib: 
   http://pypi.python.org/pypi/matplotlib
.. _PIL: 
   http://pypi.python.org/pypi/PIL
""",

    author= _topographica_devs,
    author_email= _topographica_devs_email,
    maintainer= _topographica_devs,
    maintainer_email= _topographica_devs_email,
    platforms=['Windows', 'Mac OS X', 'Linux'],
    license='GPL',
    download_url='http://sourceforge.net/projects/topographica/files/',
    url='http://topographica.org/',

    classifiers = [
        "License :: OSI Approved :: GNU General Public License (GPL)",
# (until packaging tested)
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Education",
        "Topic :: Scientific/Engineering"],

    # Ignored by distutils! Useful only for documentation?
    requires = ["PIL (>=1.1.6)",          # >= 1.1.6     
                "NumPy (>=1.0)"],       # >= 1.1
    # CEBALERT: strongly recommended: gmpy, weave, matplotlib
    #                    recommended: ipython
    #                       optional: scipy

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
        # CEBALERT: These things are not data. Should be in
        # MANIFEST.in, but need to update deb packaging first.
        'param': ['externaltk/snit-2.2.1/*.tcl',
                  'externaltk/scrodget-2.1/*.tcl',
                  'externaltk/tooltip-1.4/*.tcl'],

        'topo.tkgui': ['icons/*.*'],
        'topo.command':['*.png','*.pdf'],
        'topo.tests':['*.txt','*.jpg','*.pgm']},

    scripts = ['topographica'])

