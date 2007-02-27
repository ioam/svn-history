# Commands for running the examples files.
# CEBHACKALERT! Still being written!
# Not sure "setup.py" is the right name.
# Just translating the Makefile...but we definitely have topographica
# by now so we could do this completely differently.
# The spawn commands in here show what commands in the main Makefile
# could be replaced with (once python itself has been built).

# currently run from the examples directory like this:
# ../bin/python setup.py X
# where X is all_quick or saved_examples

from os import system, spawnv, P_WAIT, getcwd
from sys import argv,exit,exec_prefix
from os.path import join

def usage():
    print """
instructions for running...
"""
# CEBALERT: replace all this with some kind of option parsing
if len(argv)< 2:
    usage()
    exit(-1)
arg = argv[1]

targets = dict( all_quick=("hierarchical","cfsom_or"),
		saved_examples=("lissom_oo_or_20000.typ",)
		)



# location of the topographica script
topographica = join(exec_prefix,"topographica")

# location of examples dir
# CBALERT: won't work in general, use one reliable way to get
# the topographica path and build the others from that.
examples = getcwd()


SNAPSHOT = "from topo.commands.basic import save_snapshot ; save_snapshot"


commands = {
	"cfsom_or":("topographica",
		    '-c',"default_density=4",join(examples,"cfsom_or.ty"),
		    '-c','topo.sim.run(1)',
		    '-c','print "cf"'),

	"hierarchical":("topographica",
		    '-c',"default_density=4",join(examples,"hierarchical.ty"),
		    '-c','topo.sim.run(1)',
		    '-c','print "h"'),

	"lissom_oo_or_20000.typ":("topographica",
				  '-c',"default_density=4",join(examples,"lissom_oo_or.ty"),
				  '-c','topo.sim.run(2)',
				  '-c',SNAPSHOT+"('"+join(examples,'lissom_oo_or_20000.typ')+"')")
	}



# CB: temp.
for t in targets[arg]:
	# CB: spawnv gives us new process,
	# P_WAIT means the script waits until new process returns
	spawnv(P_WAIT,topographica,commands[t])

print "(done)"
