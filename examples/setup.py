# Commands for running the examples files.
# CEBHACKALERT! Still being written!
# Not sure "setup.py" is the right name.
# Just translating the Makefile...but we definitely have topographica
# by now so we could do this completely differently.


from os import system, spawnv, P_WAIT, getcwd
from sys import argv,exit,exec_prefix
from os.path import join

# pretend we got these args...
args = ["all_quick","saved_examples","hierarchical"]  #(argv[1], argv[2])


targets = dict( all_quick=["hierarchical","cfsom_or"],
		saved_examples=["lissom_oo_or_20000.typ"]
		)


# location of the topographica script
topographica = join(exec_prefix,"topographica")

# location of examples dir
examples = join(exec_prefix,"examples")


SNAPSHOT = "from topo.commands.basic import save_snapshot ; save_snapshot"

OR_ANALYSIS = "from topo.commands.analysis import measure_or_pref,measure_position_pref,measure_cog,measure_or_tuning_fullfield; \
measure_or_pref(); \
measure_position_pref(); \
measure_cog(); \
measure_or_tuning_fullfield(); \
"

RETINOTOPY_ANALYSIS = "from topo.commands.analysis import measure_position_pref,measure_cog ;\
measure_position_pref(); \
measure_cog(); \
"



commands = {
    "cfsom_or":("topographica",
                '-c',"default_density=4",join(examples,"cfsom_or.ty"),
                '-c','topo.sim.run(1)'),
    
    "hierarchical":("topographica",
                    '-c',"default_density=4",join(examples,"hierarchical.ty"),
                    '-c','topo.sim.run(1)'),
    
    "lissom_or":("topographica",
                 '-c',"default_density=4",join(examples,"lissom_or.ty"),
                 '-c','topo.sim.run(1)'),
    
    "lissom_oo_or":("topographica",
                    '-c',"default_density=4",join(examples,"lissom_oo_or.ty"),
                    '-c','topo.sim.run(1)'),
    
    "som_retinotopy":("topographica",
                      '-c',"default_density=4",join(examples,"som_retinotopy.ty"),
                      '-c','topo.sim.run(1)'),
    
    "lissom_oo_or_20000.typ":("topographica",
                              '-c',"default_density=4",join(examples,"lissom_oo_or.ty"),
                              '-c','topo.sim.run(2)',
                              '-c',SNAPSHOT+"('"+join(examples,'lissom_oo_or_20000.typ')+"')")
    }


# Create the list of commands to execute either by getting the
# command labels from a target, or by inserting the command label
# CEBALERT: I don't know any string methods; I'm sure this can
# be simplified.
command_labels=[]
for a in args:
    if a in targets:
        for X in targets[a]:
            command_labels.append(X)
    else:
        command_labels.append(a)


for cmd in command_labels:
	# CB: spawnv gives us new process,
	# P_WAIT means the script waits until new process returns
        print commands[cmd]
	spawnv(P_WAIT,topographica,commands[cmd])

print "(done)"
