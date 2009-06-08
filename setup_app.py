"""
py2app build script for Topographica.

Work in progress

Usage:
    python setup.py py2app
"""
from setuptools import setup

# Currently this script with topographica's python doesn't work
# because Topographica doesn't build lib/libpython2.5.dylib.  Not sure
# what to do about that.
# Turns out nobody else could get the .dylib file. Apparently fixed in
# python 2.6: http://bugs.python.org/issue4472.
#
# Using macports, can almost build .app file...
# $ sudo port install python25 py25-tkinter py25-numpy py25-matplotlib py25-pil py25-scipy
# $ #py25-ipython won't compile (and can't get ipython's setup.py to install ipython for python to find!)
# $ #no py25-gmpy (can use fixedpoint)
# $ sudo port install tcllib
# sudo port install python_select
# sudo port python_select python25
# $ # download tklib, install using provided ./install.tcl
# $ sudo python setup.py install for fixedpoint
# $ python setup_app.py py2app -A # builds + tests pass
# $ python setup_app.py py2app # builds successfully, but topographica.app can't find Image module


#Information about OS X & icons, from Kevin Walzer (www.codebykevin.com)
#
#The application icon is part of the application bundle structure. See
#the link below for some basic tips on how to create an icon and specify
#it in your application. (Note this article does not deal specifically
#with deploying Python applications, but the parts about the icon are
#applicable.)
#
#http://tk-components.sourceforge.net/tk-bundle-tutorial/index.html
#
#The easiest way to specify the icon with a Python application is part of
#the setup file you use with py2app (which wraps all Python packages into
#an application package on the Mac).  Here's a basic example:
#
#imagedir = (os.getcwd() + "/images")
#helpdir = (os.getcwd() + "/html")
#
#setup(
#    app = ['Phynchronicity.py'],
#    data_files = [imagedir, helpdir],
#    options=dict(py2app=
#                    dict(iconfile='Phynchronicity.icns',
#                    plist = 'Info.plist'),
#             ),
#    )
#

import _setup

_setup.create_topographica_script()

OPTIONS = {
    'packages': ['numpy','matplotlib','PIL'] # ...more to go
    }

setup(
    app=["topographica.py"],
    setup_requires=["py2app"],
    options = {'py2app':OPTIONS}
)
