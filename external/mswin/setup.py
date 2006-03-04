# Creates topographica.py script

import sys
import os

path = os.path.normpath(sys.argv[1])

f = open(os.path.join(path,'topographica.py'),'w')
f.write('import os\n')
f.write("os.environ['TOPOGRAPHICAPATH']='"+path+"'\n")
f.write("os.environ['TOPORELEASE']='0.8.2'\n")
f.write('from sys import argv\n')
f.write('from topo.misc.commandline import process_argv\n')
f.write('process_argv(argv[1:])\n')
f.close()