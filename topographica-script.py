
import sys,os,code,copy
import traceback
from getopt import getopt,GetoptError
from pprint import pprint
from topo import *


# set the prompt and banner
sys.ps1 = 'Topographica> '

banner = """
Welcome to Topographica!

Type help() for interactive help, or help(commandname) for info on a
specific command.
"""

opts,args = getopt(sys.argv[1:],'i')

opts = dict(opts)


#start the intepreter
#
# NOTE: From here on, Topo interpeter's locals have "forked"
# from the locals of this script
#
interpreter_locals = copy.copy(locals())
interpreter = code.InteractiveConsole(interpreter_locals)



if args:
    # if there's a file argument, load it.
    try:
        f = open(args[0],'r')
        sys.argv = args
        if interpreter.runsource(f.read(),args[0],'exec'):
            print "Input file '%s' is incomplete." % filename
        f.close()
    except:
        traceback.print_exc()


if '-i' in opts or len(args) == 0:
    # ...then we're running interactively...
    # set up readline
    try:
        import readline
    except ImportError:
        print "Module readline not available.\nHistory and completion support disabled."
    else:
        #set up command completion
        import rlcompleter
        readline.parse_and_bind("tab: complete")

    # start interacting
    interpreter.interact(banner)
