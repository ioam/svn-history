"""
Commands for running the examples files in various ways.

Like a Makefile: contains a list of targets (and groups of targets)
that specify various commands to run.

E.g.

  topographica -c 'from topo.misc.genexamples import generate; generate(targets=["all_quick","saved_examples"])' 

Runs the 'all_quick' target if called without any arguments: 

  topographica -c 'from topo.misc.genexamples import generate; generate()'

To add new single targets, add to the targets dictionary;
for groups of targets, add to the group_targets dictionary.


$Id$
"""

__version__='$Revision$'


# Note: has none of the Makefile's dependency processing, so just does
# what you tell it (i.e. over-writes existing files - which might be
# behavior we actually want).


# CB: need to investigate the situation on Windows; old comment:
#
#   Tricky to get this to work on Windows because of problems
#   with quotes, spaces, and so on in cmd.exe:
#   http://mail.python.org/pipermail/python-bugs-list/2002-March/010393.html
#   http://support.microsoft.com/kb/191495
#   So, currently have to take care over where this script is run from
#   (covered by an assertion statement), and how to pass in commands
#   (e.g. strings for printing - see trickysyntax target).
#   I might have become confused by all this, so there's likely to be
#   something simpler we could do - this script contains the history of
#   its production in the code (e.g. I probably don't need the full
#   path to the topographica script in here anymore.)


import platform 
import sys
import os.path

from os import system
from os.path import join


## location of the topographica script
topographica = sys.argv[0]

import param
from param import ParamOverrides

### Convenience functions
def snapshot(filename):
    """Return a command for saving a snapshot named filename."""
    return "from topo.command.basic import save_snapshot ; save_snapshot(filename)"
    
def or_analysis():
    """Return a command for orientation analysis."""
    return """
from topo.command.analysis import measure_or_pref; \
from topo.command.pylabplot import measure_position_pref,measure_cog,measure_or_tuning_fullfield; \
measure_or_pref(); \
#measure_position_pref(); \
measure_cog(); \
#measure_or_tuning_fullfield()
"""

def retinotopy_analysis():
    """Return a command for retinotopy analysis."""
    return "from topo.command.pylabplot import measure_position_pref,measure_cog ;\
measure_position_pref(); \
measure_cog()"
###



def run(examples,script_name,density=None,commands=["topo.sim.run(1)"]):
    """
    Return a complete command for running the given topographica
    example script (i.e. a script in the examples/ directory) at the
    given density, along with any additional commands.
    """
    
    if density:
        density_cmd = ' -c "default_density='+`density`+'" '
    else:
        density_cmd = " "

    cmds = ""
    for c in commands:
        cmds+=' -c "'+c+'"'

    script = os.path.join(examples,script_name)

    if platform.system()=="Windows":
        # CB: extra leading " required!
        c = '""'+topographica+density_cmd+script+'"'+cmds
    else:
        c = topographica+density_cmd+script+' '+cmds

    return c



scripts = {
    'hierarchical':'hierarchical.ty',
    'lissom_or'   :'lissom_or.ty',
    'lissom_oo_or':'lissom_oo_or.ty',
    'som_retinotopy':'som_retinotopy.ty',
    'trickysyntax':'hierarchical.ty',
    'obermayer_pnas90':'obermayer_pnas90.ty',
    'lissom_fsa':'lissom_fsa.ty',
    'gca_lissom':'gca_lissom.ty',
    'lissom_oo_or_10000.typ':'lissom_oo_or.ty',
    'lissom_fsa_10000.typ':'obermayer_pnas90.ty',
    'obermayer_pnas90_40000.typ':'obermayer_pnas90.ty',
    'som_retinotopy_40000.typ':'som_retinotopy.ty',
    'gca_lissom_10000.typ':'gca_lissom.ty'}


def copy_examples():
# topographica -c "from topo.misc.genexamples import copy_examples; copy_examples()"
    examples = find_examples()
    locn = os.path.join(param.normalize_path.prefix,"examples")
    if os.path.exists(locn):
        print "%s already exists; delete or rename it if you want to re-copy the examples."%locn
        return
    else:
        print "Creating %s"%locn
        import shutil
        print "Copying %s to %s"%(examples,locn)
        shutil.copytree(examples,locn)


def print_examples_dir(**kw):
    examples = find_examples(**kw)
    if examples:
        print "Found examples in %s"%examples

def find_examples(specified_examples=None,dirs=None):
    import topo

    if not specified_examples:
        # CEBALERT: hack!
        specified_examples = ["hierarchical","lissom_oo_or","som_retinotopy"]
        

    if not dirs:
        candidate_example_dirs = [
            os.path.join(os.path.expanduser("~"),'topographica/examples'),
            # version-controlled topographica dir
            os.path.join(topo._package_path,"../examples"),
            # package installed at <some path>/lib/python2.X/site-packages/topo
            os.path.join(topo._package_path,"../../../share/topographica/examples")]
    else:
        candidate_example_dirs = dirs

    # CEBALERT: horrible way to find directory that contains all the
    # examples specified.
    examples = None
    for d in candidate_example_dirs:
        if not examples:
            for cmd in specified_examples:
                if os.path.isfile(os.path.join(d,scripts[cmd])):
                    examples = d
                else:
                    examples = False

                if examples is False:
                    break

    return os.path.normpath(examples)




# CEBALERT: should be rewritten!

def _stuff(specified_targets):

    # shortcuts for executing multiple targets
    group_targets = dict( all_quick=["hierarchical","som_retinotopy","lissom_oo_or"],
                          all_long=["lissom_oo_or_10000.typ","som_retinotopy_40000.typ",
                                    "lissom_or_10000.typ","lissom_fsa_10000.typ"],
                          saved_examples=["lissom_oo_or_10000.typ"])

    ### Create the list of commands to execute either by getting the
    ### command labels from a target, or by inserting the command label
    # CB: I don't know any string methods; I'm sure this can
    # be simplified!
    command_labels=[]


    for a in specified_targets:
        if a in group_targets:
            command_labels+=group_targets[a]
        else:
            command_labels.append(a)    

    examples = find_examples(specified_examples=command_labels)

    if not examples:
        raise IOError("Could not find examples in %s"%candidate_example_dirs)
    else:
        print "Found examples in %s"%examples

    # CB: so much repeated typing...

    available_targets = {
        "hierarchical":   run(examples,scripts["hierarchical"],density=4),
        "lissom_or":      run(examples,scripts["lissom_or"],density=4),
        "lissom_oo_or":   run(examples,scripts["lissom_oo_or"],density=4),
        "som_retinotopy": run(examples,scripts["som_retinotopy"],density=4),

        "trickysyntax":run(examples,scripts["hierarchical"],commands=["topo.sim.run(1)",
                                                       "print 'printing a string'"]),

        "lissom_oo_or_10000.typ":run(examples,scripts["lissom_oo_or"],
                                     commands=["topo.sim.run(10000)",
                                               or_analysis(),
                                               snapshot("lissom_oo_or_10000.typ")]),


        "lissom_or_10000.typ":run(examples,scripts["lissom_or"],
                                  commands=["topo.sim.run(10000)",
                                            or_analysis(),
                                            snapshot("lissom_or_10000.typ")]),

        "lissom_fsa_10000.typ":run(examples,scripts["lissom_fsa"],
                                   commands=["topo.sim.run(10000)",
                                             snapshot("lissom_fsa_10000.typ")]),

        "obermayer_pnas90_40000.typ":run(examples,scripts["obermayer_pnas90"],
                                         commands=["topo.sim.run(40000)",
                                                   or_analysis(),
                                                   snapshot("obermayer_pnas90_30000.typ")]),

        "som_retinotopy_40000.typ":run(examples,scripts["som_retinotopy"],
                                       commands=["topo.sim.run(40000)",
                                                 retinotopy_analysis(),
                                                 snapshot("som_retinotopy_40000.typ")]),

        "gca_lissom_10000.typ":run(examples,scripts["gca_lissom"],
                                   commands=["topo.sim.run(10000)",
                                             or_analysis(),
                                             snapshot("gca_lissom_10000.typ")])

        }

    return command_labels,available_targets


class generate(param.ParameterizedFunction):

    targets = param.List(default=['all_quick'])

    def __call__(self,**params):
        p = ParamOverrides(self,params)

        command_labels,available_targets = _stuff(p.targets)
        for cmd in command_labels:
            c = available_targets[cmd]
            print c
            system(c)
        
