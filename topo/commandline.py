import sys

BANNER         = """
Welcome to Topographica!

Type help() for interactive help, or help(commandname) for info on a
specific command.
"""

def start(interactive=True):
    """
    Function that will display a banner, import topo into main,
    and change the prompt display.  Since this is part of the topo
    package, the topo.__init__ will already be evaluated when this
    file is imported.
    """
    sys.ps1        = 'Topographica> '
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

