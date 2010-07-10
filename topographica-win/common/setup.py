# Create 'topographica' script and topographica.bat batch file.  (Note
# that on Windows the batch file is necessary for executing commands
# at all.)
#
# The first argument (required) is the Topographica root directory.  A
# second optional argument "create_associations" may be passed to have
# this script create file associations and shortcuts (used when
# setting up a cvs-controlled copy of topographica).
#
#
# Examples:
#
# To have this script simply make the script and batch file:
#    setup.py "d:\program files\topographica"
# (This is what the binary installation procedure uses.)
#
# To have this script additionally create file associations and shortcuts,
# it might be invoked as:
#    setup.py "d:\program files\topographica" "create_associations"
# (This is how a cvs-controlled copy is setup.)

import sys
import os

create_associations=False
compiler_path = "python_topo\\mingw\\bin"
# following required for non-admin vista users?
cc1plus_path = "python_topo\\mingw\\libexec\\gcc\\mingw32\\3.4.2" 


# CEBHACKALERT: should check it's valid, etc.
# Should check arguments, and so on.
path = os.path.abspath(sys.argv[1])

if len(sys.argv)>2:
    if sys.argv[2]=="create_associations":
        create_associations=True


# CEBHACKALERT: it's like the Makefile here; can't it be the same?


# topographica script
f = open(os.path.join(path,"topographica"),'w')

f.write("#! python_topo/python.exe\n")
f.write("# Startup script for Topographica\n")
f.write("\n")
f.write("# for gcc compiler\n")
# Should keep current path, too? Or work out how to set gcc compiler path directly.
f.write("from os import environ\n")
f.write("environ['PATH']="+repr(os.path.join(path,compiler_path)+ ";"+os.path.join(path,cc1plus_path))+"\n")
f.write("\n")
f.write('import topo'+'\n')
# CEBHACKALERT: This is hard-coded twice: should be read from somewhere.
f.write("topo.release='0.9.7'\n")
f.write("\n")
f.write("# Process the command-line arguments\n")
f.write('from sys import argv\n')
f.write('from topo.misc.commandline import process_argv\n')
f.write('process_argv(argv[1:])\n')
f.close()

# topographica.bat
f = open(os.path.join(path,'topographica.bat'),'w')
f.write("""@echo off"""+'\n')
# store the original path so we can put the shell back after
f.write("""set startdir=%cd%"""+'\n')
f.write('cd "' + path + '"\n')
f.write("""python_topo\python.exe topographica %*"""+'\n')
f.write("""cd %startdir%"""+'\n')
f.write("""@echo on"""+'\n')
f.close()


from _winreg import *
if create_associations:
    # Link '.ty' file extension to  "topographica.bat -g"
    bat_path = os.path.join(path,'topographica.bat')
    ico_path = os.path.join(path,'topographica.ico')
    
    os.system('assoc .ty=Topographica.Script')
    os.system('ftype Topographica.Script="' + bat_path + '" -g "%1"')
    
    # and add the Topographica icon to the registry.
    namepathkey = OpenKey(HKEY_CLASSES_ROOT,'Topographica.Script',0,KEY_SET_VALUE)
    SetValue(namepathkey,None,REG_SZ,'Topographica Script')
    SetValue(namepathkey,'DefaultIcon',REG_SZ, ico_path)
    
    # and create a desktop shortcut
    # by calling a windows scripting file
    os.system('wscript create_shortcut.vbs "' + path + '"')
