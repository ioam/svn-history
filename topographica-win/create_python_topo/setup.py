# Topographica Installation Script for Windows
# $Id$
#
# This should only be called by the setup.bat file in the root
# directory.  You may be able to call it directly by running the
# commands "python setup.py configure" which will check to make sure
# the right version of python is installed, then "python setup.py
# install" to do the different package installations but the 'install'
# flag does not check to make sure the right version of python is
# running.
#
# 'setup.py install' does the following (in no particular order):
#    *  Call the Numeric-24 Installer
#    *  Call the PIL Installer  
#    *  Call the MatPlotLib Installer
#    *  Unpack and copy ..\PMW.tgz to Pythons \Lib\site-packages\Pmw
#    1. Locate the default install directory for new programs
#    2. Copy over Topographica files into new install directory
#    3. Associate Topographica File extensions
#    4. Construct and Log a Windows Registry command for the Topo Extension
#    5. Create a topographica.bat wrapper to preserve the Topographica output
#    6. Give Topographica Files a pretty icon
#    7. Move the generic topographica_script.py to the one Windows will use
#    8. Create a Desktop CMD file to open the Install location of Topographica
#    9. Open up the newly installed directory

import sys, os
from _winreg import *

# Change this from the empty string if you do not want the Windows
# default install location.  Typically "C:\Program Files"
# For example: BASE_INSTALL_PATH = 'D:'
BASE_INSTALL_PATH = ''

instgroup = 0
PYTH = 2
PACK = 3
TOPO_VERSION = 2.4

# Set the run-state.  This is not a normal Python config file.
if len(sys.argv) > 1:
    if sys.argv[1] == 'configure':
	instgroup = PYTH
    elif sys.argv[1] == 'install':
	instgroup = PACK
	if len(sys.argv) > 2:
	    BASE_INSTALL_PATH = sys.argv[2]
else:
    print 'Run: "python setup.py configure" or "python setup.py install"'
    sys.exit(1)
    
#  Pass in 'configure' on the command line to check and install Python 2.4.
#  The setup.bat file should call this file as needed, but this might
#  work in isolation as well since it will install the needed files
#  and associations
if instgroup == PYTH:
    # Get the running version and compare it with the version
    # Topographica wants
    run_tup = sys.version_info[0:2]
    run_version = run_tup[0] + run_tup[1]/10.0
    print 'Python run version', run_version
    if run_version > TOPO_VERSION:
        print 'Newer version of Python already installed:', run_version
        print 'Topographica has been tested with Python 2.4.2 and cannot guarantee'
        print 'operation.  "external/win32" contains version 2.4.2 if you wish to install it.'
    elif run_version < TOPO_VERSION:
        print 'Old version of Python detected.'
        print 'Topographica requires Python 2.4.2  Installing...'
        os.system('python-2.4.2.msi')    
    else:
        print 'Python version 2.4 found.  Excellent.'
    if (sys.argv) == 1:
        print "Rerun setup.py with 'install' parameter to install req. packages."


#  Just install the dependent packs.  The file is split because an old version
#  of python may have been used to install the new python and the interpreter
#  may need to be switched.
if instgroup == PACK:

    # Numeric, PIL, MatPlotLib (and Jpeg?)
    packfiles = ['Numeric-24.2.win32-py2.4.exe',
                 'PIL-1.1.5.win32-py2.4.exe',
                 'matplotlib-0.81.win32-py2.4.exe']
    for each in packfiles:
        os.system('chmod u+x ' + each)
        os.system(each)
    # Jpeg-6b only needed to build PIL on Linux?
    # os.system('jpeg-6b-3.exe')

    # PMW (Python Mega Widgets)  No install, need to copy correctly.
    pmw_cmd = 'xcopy /E /I /Y Pmw "' + sys.prefix + '\\Lib\\site-packages\\Pmw"'
    # Prepare and use pmw_cmd to install PMW
    os.system('util\\gunzip -f ..\\Pmw.tgz')
    os.system('util\\tar xvf ..\\Pmw.tar')
    os.system(pmw_cmd)

    # FixedPoint.  For a new number class to use instead of floats.
    # We are trying to duplicate the install process in external/Makefile
    # A _patched.tgz file is created from the Unix version to make the
    # Windows install easier.
    fixedpt = "fixedpoint-0.1.2"
    fp_cmd = 'xcopy /E /I /Y ' + fixedpt + '_patched "' + sys.prefix + '\\Lib\\site-packages\\' + fixedpt + '"'
    os.system('util\\gunzip -f ' + fixedpt + '_patched.tgz')
    os.system('util\\tar xvf ' + fixedpt + '_patched.tar')
    os.system(fp_cmd)
    os.system(fixedpt + '_patched\\setup.bat')

    ##########################################################################
    ##### Fun with the Windows Registry!!!
    ##########################################################################
    # Tasks (in no particular order):
    # 1. Associate Topographica File extensions
    # 2. Construct and Set a Topographica run command for the Topo Files
    # 3. Give Topographica Files a pretty icon
    # 4. Locate the default install location for new programs
    # 5. Copy over Topo files for the install.
    # 6. Create a topographica.bat wrapper to auto-run.
    # 7. Create topographica script to the one that system will use
    # 8. Create a Desktop CMD file to open the Install location of Topo.
    ##########################################################################
    
    # Get the default location for new Programs.  Usually "C:\Program Files"
    # Topographica will install there automatically
    winpathkey = OpenKey(HKEY_LOCAL_MACHINE,'SOFTWARE\\Microsoft\\Windows\\CurrentVersion')
    if BASE_INSTALL_PATH:
	basepath = BASE_INSTALL_PATH
    else:
        basepath = QueryValueEx(winpathkey,'ProgramFilesDir')[0]
    CloseKey(winpathkey)
    
    # Create the Installation directory if not already there.
    if not os.access(basepath + '\\Topographica',os.X_OK):
        os.mkdir(basepath + '\\Topographica')

    
    # TOPOGRAPHICA.BAT
    # We've already verified that Python is installed: Take the python command
    # from the registry; add the Topographica script between the exe and the
    # params: and voila the new command to run when clicking on .ty files.
    pythcomkey = OpenKey(HKEY_CLASSES_ROOT,'Python.File\\shell\\open\\command')
    pythoncom = QueryValueEx(pythcomkey,None)[0]
    CloseKey(pythcomkey)
    # Construct the Topographica command that will call Python
    i = pythoncom.index(' ')
#    topocommand = pythoncom[0:i] + ' "' + basepath + '\\Topographica\\topographica.py" %*'
    topocommand = 'start "Topographica" /B /WAIT "' + basepath + \
                  '\\Topographica\\topographica.py" -g %*'

    # This is the script to use for double-clicking on items, or
    # starting by directly running the batch file itself.  when
    # debugging code.  The bat file will be logged in the System
    # Registry later.
    f = open(basepath + '\\Topographica\\topographica.bat','w')
    f.write('cd "' + basepath + '\\Topographica"\n')
    f.write(topocommand)
    f.write('\nrem @pause')
    f.close()

    
    # Copy all Topographica system files to new location.  Exclude
    # installation files that are listed in noinstall.txt
    print 'Installing to', basepath + '\\Topographica'
    inst_cmd = 'xcopy /E /Y /EXCLUDE:util\\noinstall.txt ..\..\. "' + basepath + '\\Topographica"'
    os.system(inst_cmd)
    # Remove copied setup.py file, since it's not used in the program.
    os.system('del "' + basepath + '\\Topographica\\setup.bat"')

    
    # Link file extension to new File Type.  Shell commands are easier, and 
    # will allow double-clicking on .ty files.  This depends on a properly
    # working Topographica/topographica.bat file
    os.system('assoc .ty=Topographica.File')
    os.system('ftype Topographica.File="' + basepath + '\\Topographica\\topographica.bat" -i "%1" %*')
    
    # Add the Topographica Icon to the Registry.  Non-critical, but pretty.
    namepathkey = OpenKey(HKEY_CLASSES_ROOT,'Topographica.File',0,KEY_SET_VALUE)
    SetValue(namepathkey,None,REG_SZ,'Topographica File')
    SetValue(namepathkey,'DefaultIcon',REG_SZ, basepath + '\\Topographica\\topographica.ico')

    # TOPOGRAPHICA.PY
    # The startup script that sets some variables, command-line
    # arguments, and then dois a spawn to a new Python shell.  This
    # script is similar to, but different than, the version that is
    # built by Makefile under Linux.  Linux can use the execv() call,
    # but Windows behaves better with os.spawnv()
    target = '"' + basepath + '\\Topographica\\topographica.py"'
    os.system("echo import os,sys,topographica_script > " + target)
    os.system("echo cmd = " + pythoncom[0:i] + " >> " + target)
    os.system("echo args = topographica_script.generate_params(sys.argv[1:]) >> " + target)
    os.system("echo os.spawnv(os.P_WAIT,cmd,[cmd] + args) >> " + target)


    # Add to the desktop a .CMD file that will open the Topographica
    # root directory
    deskkey = OpenKey(HKEY_CURRENT_USER,'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders')
    deskpath = QueryValueEx(deskkey,'Desktop')[0]
    CloseKey(deskkey)
    f = open(deskpath + '\\Topographica.cmd','w')
    f.write('explorer "' + basepath + '\\Topographica"')
    f.close()


    # EXIT
    # Open the newly installed Topographica directory, and print info
    # that there is now a Desktop icon.
    os.system('explorer "' + basepath + '\\Topographica"')
    print 'An icon to the Topographica directory has been added to your desktop.'
    os.system('pause')

