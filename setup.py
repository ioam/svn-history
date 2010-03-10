#!/usr/bin/env python

import sys
from distutils.core import setup

### TOPOGRAPHICA DEPENDENCIES ########################################
required = {'PIL':">=1.1.6",
            'numpy':">=1.0"} 

recommended = {'gmpy':'>=1.0', 
               'matplotlib':'>=0.8',
               'weave':'>=0.1'}

optional = {'scipy':'>=0.5','ipython':">=0.7"}
            
# for easy_install
packages_to_install = [required,recommended]

# for pypi/distutils
packages_to_state = [required]
######################################################################

setup_args = {}


if 'setuptools' in sys.modules:
    # support easy_install without depending on setuptools
    install_requires = []
    for package_list in packages_to_install:
        install_requires+=["%s%s"%(package,version) for package,version in package_list.items()]
    setup_args['install_requires']=install_requires
    setup_args['dependency_links']=["http://buildbot.topographica.org/extra/"]
    setup_args['zip_safe']=False

for package_list in packages_to_state:
    requires = []
    requires+=["%s (%s)"%(package,version) for package,version in package_list.items()]
    setup_args['requires']=requires


_topographica_devs='Topographica Developers'
_topographica_devs_email='developers[at]topographica[dot]org' 


setup_args.update(dict(
    name='topographica',

    version='0.9.7a',

    description='A general-purpose neural simulator focusing on topographic maps.',

    long_description="""
`Topographica`_ is a software package for computational modeling of neural maps. The goal is to help researchers understand brain function at the level of the topographic maps that make up sensory and motor systems.

Most users will want to download an official release from http://topographica.org/.

Installation
============

If you have `easy_install`_ or `pip`_, you could use one of these to
install Topographica and its dependencies automatically
(e.g. ``easy_install topographica``).

Alternatively, you can install Topographica with a command like
``python setup.py install --user`` (or ``sudo python setup.py
install`` for a site-wide installation). You will need install at
least `NumPy`_ and `PIL`_ before running Topographica. We also
strongly recommend that you install `MatPlotLib`_ so you can access
all Topographica's plots, as well as `Gmpy`_ and Weave (available as
part of `SciPy`_) for optimum performance.

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
.. _easy_install:
   http://peak.telecommunity.com/DevCenter/EasyInstall
.. _pip:
   http://pip.openplans.org/

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

    scripts = ['topographica']))



setup(**setup_args)
