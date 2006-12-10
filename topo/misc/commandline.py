"""
Support functions for parsing command-line arguments and providing
the Topographica command prompt.  Typically called from the
'./topographica' script, but can be called directly if using
Topographica files within a separate Python.

$Id$
"""
__version__='$Revision$'


import sys, __main__, math, os

from optparse import OptionParser
from inlinec import import_weave


BANNER = """
Welcome to Topographica!

Type help() for interactive help with python, help(topo) for general
information about Topographica, help(commandname) for info on a
specific command, or topo.about() for info on this release, including
licensing information.
"""

# CB: this one gives "topographica-t0.0000> "
# prompt = '"topographica-t"+str(topo.sim.time())+"> "'   
prompt = '"Topographica> "'

class CommandPrompt(object):
    """
    Object whose __str__ method returns str() of the 
    topo.misc.commandline.prompt variable eval()'d in __main__.

    Set topo.misc.commandline.prompt to something that can be
    eval()'d in __main__ to have that expression appear as the
    prompt. E.g.
    topo.misc.commandline.prompt = '"Topographica> "'
    sets the prompt to 'Topographica> '.
    """
    # If Python's sys.ps1 is set to a non-string object, then that object's
    # str() method is called before displaying the prompt. 
    def __str__(self): return str(eval(prompt,__main__.__dict__))


# Use to define global constants
global_constants = {'pi':math.pi}

# Create the topographica parser.
usage = "usage: topographica ([<option>]:[<filename>])*\n\
where any combination of options and Python script filenames will be\n\
processed in order left to right."
topo_parser = OptionParser(usage=usage)

### Define option processing


### JABALERT: It might be possible to eliminate this; how it is used seems clunky.
def get_filenames(parser):
    """
    Sub-function used to catch any filenames following any options.
    """
    list_command=getattr(parser.values,"commands")
    rargs = parser.rargs
    while rargs:
	arg = rargs[0]
	if ((arg[:2] == "--" and len(arg) > 2) or
            (arg[:1] == "-" and len(arg) > 1 and arg[1] != "-")):
            break
	else:
	    list_command = list_command +  ['execfile(' + repr(os.path.abspath(arg)) + ')']
	    del rargs[0]
    setattr(parser.values,"commands",list_command) 


def boolean_option_action(option,opt_str,value,parser):
    """Callback function for boolean-valued options that apply to the entire run.""" 
    setattr(parser.values,option.dest,True) 
    get_filenames(parser)


topo_parser.add_option("-g","--gui",action="callback",callback=boolean_option_action,dest="gui",
		       default=False,help="launch an interactive graphical user interface.")
topo_parser.add_option("-i","--interactive",action="callback",callback=boolean_option_action,
                       dest="interactive",default=False,
                       help="provide an interactive prompt even if stdin does not appear to be a terminal.")



def c_action(option,opt_str,value,parser):
    """Callback function for the -c option.""" 
    list_command=getattr(parser.values,option.dest)
    list_command +=  [value]
    setattr(parser.values,option.dest,list_command) 
    get_filenames(parser)

topo_parser.add_option("-c","--command",action = "callback",callback = c_action,type="string",
		       default=[],dest="commands",metavar="\"<command>\"",
		       help="commands passed in as a string and followed by files to be executed.")



### Execute what is specified by the options.

def process_argv(argv):
    """
    Process command-line arguments (minus argv[0]!), rearrange and execute.
    """
    (option,args) = topo_parser.parse_args(argv)

    # If no scripts and no commands were given, pretend -i was given.
    if len(args)==0 and len(option.commands)==0:
        option.interactive=True
        
    # JBDALERT: (As of 12/2005) With Python 2.4 compiled and run on
    # Windows XP, trying to import Weave after starting the topo
    # command-line will generate a serious system error.  However,
    # importing weave first does not cause problems.
    if import_weave: exec "import weave" in __main__.__dict__    

    sys.ps1 = CommandPrompt() 
    for (k,v) in global_constants.items():
        exec '%s = %s' % (k,v) in __main__.__dict__

    # if -i is on, or no scripts were given and no commands were given
    if option.interactive:
	os.environ["PYTHONINSPECT"] = "1"
	print BANNER
        try:
            import readline
        except ImportError:
            print "Module readline not available.\nHistory and completion support disabled."
        else:
            #set up command completion
            import rlcompleter
            readline.parse_and_bind("tab: complete")
    
    # if -g is on
    # Not sure why we need that here, but it doesn't work when it is at the top of the file.
    import topo
    if option.gui:
	import topo.tkgui
	topo.gui_cmdline_flag = True
	topo.tkgui.start() 
	os.environ["PYTHONINSPECT"] = "1"
    else:
	topo.gui_cmdline_flag = False 

     # catch the first filenames arguments (before any options) and execute them.
    filename_arg = topo_parser.largs

    for filename in filename_arg:
        # CB: this is going to need converting too, I don't know when it's used yet.
        # JABALERT: What do you mean?  It looks fine to me.
	execfile(filename,__main__.__dict__)

    # execute remaining commands.
    for cmd in option.commands:
	exec cmd in __main__.__dict__
    


	
