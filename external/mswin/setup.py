# Create topographica.py script and topographica.bat batch file.

# CEBHACKALERT: it's like the Makefile; can't it be the same?

import sys
import os

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
f.write("""python_topo\python.exe topographica %*"""+'\n')
f.write("""@echo on"""+'\n')
f.close()
