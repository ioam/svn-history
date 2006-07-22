# CEBHACKALERT: this directory is going to contain 
# a script to create a working Python installation suitable
# for Topographica (i.e. the script run by a developer to
# create the python_topo/ directory). 
# ** The script already present will not work **


Windows Installer Binary Files Directory
$Id$

This directory contains files that are used by the Windows Install.
There are two other files in the root Topographica directory that 
are also part of the Win32 system: topographica.ico, and setup.bat

setup.bat changes to this directory and runs:
python setup.py configure - Verifies Python 2.4 is installed
python setup.py install   - Installs the required packs and does
                            things to the Windows Registry.

The .\util directory contains:

tar.exe       - Windows does not have this.
gunzip.exe    - Needed to unpack binaries.
gzip.exe      - Just in case.
Y_OR_N.COM    - Utility to verify installation is desired in setup.bat
noinstall.txt - Used by setup.py and xcopy.exe to avoid copying the 
		external directories into the installation directory.
