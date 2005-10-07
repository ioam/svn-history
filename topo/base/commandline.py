import sys, __main__, math
"""
$Id$
"""


BANNER         = """
Welcome to Topographica!

Type help() for interactive help with python, help(topo) for general
information about about Topographica, help(commandname) for info on a
specific command, or topo.about() for info on this release, including
licensing information.
"""

global_constants = {'PI':math.pi, 'pi':math.pi, 'Pi':math.pi}

def start(interactive=True):
    """
    Function that will display a banner, import topo into main,
    and change the prompt display.  Since this is part of the topo
    package, the topo.__init__ will already be evaluated when this
    file is imported.
    """
    sys.ps1        = 'Topographica> '
    
    for (k,v) in global_constants.items():
        exec '%s = %s' % (k,v) in __main__.__dict__
        
    if interactive:
        print BANNER
        try:
            import readline
        except ImportError:
            print "Module readline not available.\nHistory and completion support disabled."
        else:
        #set up command completion
            import rlcompleter
            readline.parse_and_bind("tab: complete")

