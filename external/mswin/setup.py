# Create topographica.py script and topographica.bat batch file.

# CEBHACKALERT: it's like the Makefile; can't it be the same?

import sys
import os

path = os.path.abspath(sys.argv[1])
compiler_path = "python_topo\\mingw\\bin"

# topographica.ty
f = open(os.path.join(path,"topographica.py"),'w')
f.write('import os'+'\n')
f.write("os.environ['PATH']='"+repr(os.path.join(path,compiler_path))+";'\n")
### should keep current path, too
f.write("""os.environ['TOPORELEASE']='0.8.2'"""+'\n')
f.write('from sys import argv\n')
f.write('from topo.misc.commandline import process_argv\n')
f.write('process_argv(argv[1:])\n')
f.close()

# topographica.bat
f = open(os.path.join(path,'topographica.bat'),'w')
f.write("""@echo off"""+'\n')
f.write("""python_topo\python.exe topographica.py %*"""+'\n')
f.write("""@echo on"""+'\n')
f.close()
