"""
py2app build script for Topographica.

** Work in progress **

"""
from setuptools import setup

# Two options: try to build app from OS X Topographica build,
# or use macports.
#
#
# USING TOPOGRAPHICA BUILD
# ========================
#
# $ cd ~/topographica
# $ bin/python setup_app.py py2app
# (fails)
#
#
# USING MACPORTS
# ==============
#
# Dependencies
# ------------
#
# (1) see those listed in _setup.py
#
# Building .app
# -------------
#
# $ cd ~/topographica
# $ python setup_app.py py2app 
# (fails)



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
