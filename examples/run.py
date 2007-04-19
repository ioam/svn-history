"""
Commands for running the examples files in various ways.

Like a Makefile: contains a list of targets (and groups of targets)
that specify various commands to run.

E.g.
 ./topographica examples/run.py saved_examples

$Id$
"""

__version__='$Revision$'



# CB: Not yet fully tested.

### NOTES
#
# - Tricky to get this to work on Windows because of problems
#   with quotes, spaces, and so on in cmd.exe:
#   http://mail.python.org/pipermail/python-bugs-list/2002-March/010393.html
#   http://support.microsoft.com/kb/191495
#   So, currently have to take care over where this script is run from
#   (covered by an assertion statement), and how to pass in commands
#   (e.g. strings for printing - see trickysyntax target).
#
# - has none of the Makefile's dependency processing, so just does
#  what you tell it (i.e. over-writes existing files - which might be
#  behavior we actually want).

import platform 
from os import system
from sys import argv, executable
from os.path import join, dirname

## location of topographica main directory
# (same ALERT as in Filename parameter)
topographica_path = dirname(dirname(executable))

## location of the topographica script
topographica = join(topographica_path,"topographica")

## location of the examples directory
# CEBALERT: problem with paths on windows for passing in the script name to
# run; should be:
#  examples = join(topographica_path,"examples")
examples = "examples"
# temporary (I hope) test to ensure script is run from the topographica main directory
from os import getcwd; assert topographica_path==getcwd(), "Must be run from main topographica directory."


# (arg 0 is topographica, arg 1 is this script name)
command_names = argv[2:len(argv)]


### Convenience functions
def snapshot(filename):
    """Return a command for saving a snapshot named filename."""
    return "from topo.commands.basic import save_snapshot ; save_snapshot('"+join(examples,filename)+"')"
    
def or_analysis():
    """Return a command for orientation analysis."""
    return "from topo.commands.analysis import measure_or_pref,measure_position_pref,measure_cog,measure_or_tuning_fullfield; \
measure_or_pref(); \
#measure_position_pref(); \
measure_cog(); \
#measure_or_tuning_fullfield()"

def retinotopy_analysis():
    """Return a command for retinotopy analysis."""
    return "from topo.commands.analysis import measure_position_pref,measure_cog ;\
measure_position_pref(); \
measure_cog()"
###


def run(script_name,density=4,commands=["topo.sim.run(1)"]):
    """
    Return a complete command for running the given topographica
    example script (i.e. a script in the examples/ directory) at the
    given density, along with any additional commands.
    """
    cmds = ' -c "default_density='+`density`+'"'

    for c in commands:
        cmds+=' -c "'+c+'"'

    script = join(examples,script_name)

    if platform.system()=="Windows":
        # CB: extra leading "
        c = '""'+topographica+'" "'+script+'"'+cmds
    else:
        c = topographica+" "+script+' '+cmds

    return c




# shortcuts for executing multiple targets
group_targets = dict( all_quick=["hierarchical","cfsom_or","som_retinotopy","lissom_oo_or"],
                      all_long=["lissom_oo_or_10000.typ","som_retinotopy_40000.typ",
                                "lissom_or_10000.typ","lissom_fsa_10000.typ"],
                      saved_examples=["lissom_oo_or_10000.typ"])



targets = {
    "cfsom_or":       run("cfsom_or.ty"),
    "hierarchical":   run("hierarchical.ty"),
    "lissom_or":      run("lissom_or.ty"),
    "lissom_oo_or":   run("lissom_oo_or.ty"),
    "som_retinotopy": run("som_retinotopy.ty"),

    "trickysyntax":run("hierarchical.ty",commands=["topo.sim.run(1)",
                                                   "print 'printing a string'"]),

    "lissom_oo_or_10000.typ":run("lissom_oo_or.ty",
                                 commands=["topo.sim.run(10000)",
                                           or_analysis(),
                                           snapshot("lissom_oo_or_10000.typ")]),
    

    "lissom_or_10000.typ":run("lissom_or.ty",
                              commands=["topo.sim.run(10000)",
                                        or_analysis(),
                                        snapshot("lissom_or_10000.typ")]),
    
    "lissom_fsa_10000.typ":run("lissom_fsa.ty",
                               commands=["topo.sim.run(10000)",
                                         snapshot("lissom_fsa_10000.typ")]),
    
    "obermayer_pnas90_40000.typ":run("obermayer_pnas90_40000.ty",
                                     commands=["topo.sim.run(40000)",
                                               or_analysis(),
                                               snapshot("obermayer_pnas90_30000.typ")]),
    
    "som_retinotopy_40000.typ":run("som_retinotopy.ty",
                                   commands=["topo.sim.run(40000)",
                                             retinotopy_analysis(),
                                             snapshot("som_retinotopy_40000.typ")])
                              
    }



### Create the list of commands to execute either by getting the
### command labels from a target, or by inserting the command label
# CB: I don't know any string methods; I'm sure this can
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
    c = targets[cmd]
    print c
    system(c)
    
