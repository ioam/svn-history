import sys,os,code,copy
import traceback
from getopt import getopt,GetoptError
from pprint import pprint
if __name__ == '__main__':       # Don't import if this is not the main code,
    from topo import *           # since the env vars will not be set yet.


# set the prompt
sys.ps1        = 'Topographica> '
VALID_OPTS     = 'ic:dEhOQ:StuvVW:xm:'  # All valid Python 2.4 args
COMMAND_PREFIX = 'execfile("topographica_script.py");'
BANNER         = """
Welcome to Topographica!

Type help() for interactive help, or help(commandname) for info on a
specific command.
"""

def generate_params(argv):
    """
    Read in argv, and rearrange for re-execution.  Pass along all
    existing flags as well as possible.  If no -c, peel off an
    argument as the file to evaluate.  If no args, and no -c, enter
    interactive mode by adding a possibly redundant '-i'.
    """
    c_flag = False
    in_opts, in_args = getopt(argv,VALID_OPTS)  

    #print 'in_opts:', in_opts, ' in_args:', in_args

    opts = list()                      # Preserve order in a list.
    for (key, val) in in_opts:
        if key == '-c':                # Add prefix string to start of a '-c' 
            c_flag = True
            val = COMMAND_PREFIX + val
        opts.append((key,val))

    if not c_flag:                     # Create the '-c' on arg 1 or go interactive.
        if len(in_args) >= 1:
            key, val = '-c', COMMAND_PREFIX + 'execfile("' + in_args[0] + '");'
            opts.append((key,val))
            in_args = in_args[1:]
        else:                          # Std Interactive mode
            opts.append(('-i',''))     # Add an '-i' even if it's already there.
            opts.append(('-c',COMMAND_PREFIX))
            print BANNER

    args = []
    for each in opts:
        args.append(each[0])
        if each[1] != '': args.append(each[1])
    args = args + in_args
    return args


def topo_interact(banner = ''):
    """
    The Python InteractiveConsole() was not really running commands
    within the __main__ namespace, nor would it allow us to change the
    package name that the commands were being executed in.  To
    maintain control, this short event loop was created.  It's goal
    was to duplicate the Python command-line, but we can no longer prove
    it behaves identically, particularly with exceptions, and with
    multi-line commands--which are supported.

    Currently 02/2005 not used.  The Python main loop is being used
    instead, and topographica_script.py is being called as a header to
    Topographica files.
    """
    if banner != '':
        print banner
    loc = locals()
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


# See if we should load the readline modules.
opts, args = getopt(sys.argv[1:],VALID_OPTS)
opts = dict(opts)

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

