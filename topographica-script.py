import sys,os,code,copy
import traceback
import __main__
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

opts, args = getopt(sys.argv[1:],'i')

opts = dict(opts)


def topo_interact(banner = ''):
    """
    The Python InteractiveConsole() was not really running commands
    within the __main__ namespace, nor would it allow us to change the
    package name that the commands were being executed in.  To
    maintain control, this short event loop was created.  It's goal
    was to duplicate the Python command-line, but we can no longer say
    it behaves identically, particularly with exceptions, and with
    multi-line commands--which are supported.
    """
    if banner != '':
        print banner
    loc = copy.copy(locals())
    console = code.InteractiveConsole(loc)
    while True:
        Command = None
        complete_command = ''

        # The line needs to be added together, until there is a full
        # command.  This is when compile_command returns non-None.
        while Command == None:
            try:
                if complete_command == '':
                    next_line = console.raw_input('Topographica> ') + '\n'
                else:
                    next_line = console.raw_input('... ') + '\n'
                complete_command = complete_command + next_line
            except EOFError:       # Ctrl-D from the input.
                print "Goodbye!"
                sys.exit()

            # If a single line, or blank line after multi-line.
            if complete_command == next_line or next_line == '\n':
                try:
                    # Compile the line into a command.  Don't
                    # exit if the line is bad, just print error
                    # and reset.
                    Command = code.compile_command(complete_command)
                except (SyntaxError, OverflowError, ValueError):
                    print 'Command: ', complete_command[0:-1] 
                    traceback.print_exc()
                    complete_command = ''    # Reset.

        try:
            # Run the compiled command in the g environment.  Many
            # errors can result.  Catch all of them so Topographica
            # doesn't crash out to the shell.  
            g = __main__.__dict__
            exec Command in g  
        except:
            print 'Command: ', complete_command[0:-1] 
            traceback.print_exc()


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
    # Because python may be called twice: Once to set env vars, and second to start
    # interacting, only display the banner if it's time to interact.
    if 'topographica-script.py' in sys.argv[0]:
        topo_interact(banner)
    else:
        topo_interact('')
