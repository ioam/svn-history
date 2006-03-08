# Create topographica.py script and topographica.bat batch file.

# CEBHACKALERT: it's like the Makefile; can't it be the same?

import sys
import os

from _winreg import *

# argument comes from setup.bat
path = os.path.abspath(sys.argv[1])

compiler_path = "python_topo\\mingw\\bin"

# topographica script
f = open(os.path.join(path,"topographica"),'w')

f.write("# Startup script for Topographica\n")
f.write("\n")
f.write("# for gcc compiler\n")
# Should keep current path, too? Or work out how to set gcc compiler path directly.
f.write("from os import environ\n")
f.write("environ['PATH']="+repr(os.path.join(path,compiler_path))+"\n")
f.write("\n")
f.write('import topo'+'\n')
# This is hard-coded twice: should be read from somewhere.
f.write("topo.release='0.8.2'\n")
f.write("\n")
f.write("# Process the command-line arguments\n")
f.write('from sys import argv\n')
f.write('from topo.misc.commandline import process_argv\n')
f.write('process_argv(argv[1:])\n')
f.close()

# topographica.bat
f = open(os.path.join(path,'topographica.bat'),'w')
f.write("""@echo off"""+'\n')
f.write('cd "' + path + '"\n')
f.write("""python_topo\python.exe topographica %*"""+'\n')
f.write("""@echo on"""+'\n')
f.close()



# Link '.ty' file extension to  "topographica.bat -g"
bat_path = os.path.join(path,'topographica.bat')
ico_path = os.path.join(path,'topographica.ico')

os.system('assoc .ty=Topographica.Script')
os.system('ftype Topographica.Script="' + bat_path + '" -g "%1"')
    
# and add the Topographica icon to the registry.
namepathkey = OpenKey(HKEY_CLASSES_ROOT,'Topographica.Script',0,KEY_SET_VALUE)
SetValue(namepathkey,None,REG_SZ,'Topographica Script')
SetValue(namepathkey,'DefaultIcon',REG_SZ, ico_path)


