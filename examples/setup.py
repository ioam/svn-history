"""
Commands for running the examples files.
"""

# CEBHACKALERT! Still being written!
# Not sure "setup.py" is the right name - maybe run.py?
#
# Just translating the Makefile for now...but we definitely have
# topographica by now so we could do this differently.
#
# Has none of the Makefile's dependency processing, so just does
# what you tell it (i.e. over-writes existing files).



from os import spawnv, P_WAIT
from sys import argv, executable
from os.path import join, split

# (same ALERT as in Filename parameter)
topographica_path = split(split(executable)[0])[0]

# location of the topographica script
topographica = join(topographica_path,"topographica")

# location of examples dir
examples = join(topographica_path,"examples")

# first arg is script name
command_names = argv[1:len(argv)]


### Convenience functions
def snapshot(filename):
    """Return a command for saving a snapshot named filename."""
    return "from topo.commands.basic import save_snapshot ; save_snapshot('"+join(examples,filename)+"')"
    
def or_analysis():
    """Return a command for orientation analysis."""
    return "from topo.commands.analysis import measure_or_pref,measure_position_pref,measure_cog,measure_or_tuning_fullfield; \
measure_or_pref(); \
measure_position_pref(); \
measure_cog(); \
measure_or_tuning_fullfield()"

def retinotopy_analysis():
    """Return a command for retinotopy analysis."""
    return "from topo.commands.analysis import measure_position_pref,measure_cog ;\
measure_position_pref(); \
measure_cog()"
###


def run(name,density=4,commands=["topo.sim.run(1)"]):
    """
    Return a command formatted in a suitable way for input to spawnv.
    """
    cmd_list = ["topographica"]
    cmd_list.append("-c")
    cmd_list.append("default_density=%d"%density)

    cmd_list.append(join(examples,name))
    
    for c in commands:
        cmd_list.append("-c")
        cmd_list.append(c)

    return tuple(cmd_list)




# shortcuts for executing multiple targets
group_targets = dict( all_quick=["hierarchical","cfsom_or","som_retinotopy","lissom_oo_or"],
                      all_long=["lissom_oo_or_10000.typ","som_retinotopy_40000.typ",
                                "lissom_or_10000.typ","lissom_fsa_10000.typ"],
                      saved_examples=["lissom_oo_or_10000.typ"])


# update the times!
targets = {
    "cfsom_or":run("cfsom_or.ty"),
    "hierarchical":run("hierarchical.ty"),
    "lissom_or":run("lissom_or.ty"),
    "lissom_oo_or":run("lissom_oo_or.ty"),
    "som_retinotopy":run("som_retinotopy.ty"),
    "lissom_oo_or_10000.typ":run("lissom_oo_or.ty",
                                 commands=["topo.sim.run(1)",
                                           or_analysis(),
                                           snapshot("lissom_oo_or_10000.typ")]),
    "lissom_or_10000.typ":run("lissom_or.ty",
                              commands=["topo.sim.run(1)",
                                        or_analysis(),
                                        snapshot("lissom_or_10000.typ")]),
    "lissom_fsa_10000.typ":run("lissom_fsa.ty",
                               commands=["topo.sim.run(1)",
                                         or_analysis(),
                                         snapshot("lissom_fsa_10000.typ")]),
    "obermayer_pnas90_30000.typ":run("obermayer_pnas90_30000.ty",
                                     commands=["topo.sim.run(1)",
                                               or_analysis(),
                                               snapshot("obermayer_pnas90_30000.typ")]),
    "som_retinotopy_40000.typ":run("som_retinotopy.ty",
                                   commands=["topo.sim.run(1)",
                                             retinotopy_analysis(),
                                             snapshot("som_retinotopy_40000.typ")])
                              
    }







### Create the list of commands to execute either by getting the
### command labels from a target, or by inserting the command label
# CEBALERT: I don't know any string methods; I'm sure this can
# be simplified!
command_labels=[]
for a in command_names:
    if a in group_targets:
        for X in group_targets[a]:
            command_labels.append(X)
    else:
        command_labels.append(a)

### Execute the commands
for cmd in command_labels:
	# CB: spawnv gives us new process,
	# P_WAIT means the script waits until new process returns
        print targets[cmd]
	spawnv(P_WAIT,topographica,targets[cmd])

print "(done)"
