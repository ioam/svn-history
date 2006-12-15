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


# Startup banner
BANNER = """
Welcome to Topographica!

Type help() for interactive help with python, help(topo) for general
information about Topographica, help(commandname) for info on a
specific command, or topo.about() for info on this release, including
licensing information.
"""

class CommandPrompt(object):
    """
    Provides a dynamically updated command prompt.

    The variable sys.ps1 controls Python's command prompt.  If that
    variable is set to a non-string object, then the object's
    __str__() method is called before displaying the prompt.  This
    class provides a __str__() method that evaluates this class's
    'format' variable in __main__, and then returns the result.  To
    use this, just set sys.ps1 to an instance of this class.

    The prompt is then controlled by the class attribute 'format'.
    Several predefined formats are provided, and any of these (or any
    arbitrary string) can be used by setting the class attribute
    'format' to their values.  For example, user code can turn on ANSI
    colors using:
    
      CommandPrompt.format=CommandPrompt.ansi_format
    """

    # For portable ANSI output, could use TerminalController from:
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475116
    # (or other such solutions)
    # Predefined alternatives
    basic_format   = '"Topographica> "'
    simtime_format = '"Topographica_t%g> " % topo.sim.time()'
    ansi_format    = '"\x1b[32;40;1mTopographica\x1b[33;40;1m_t%g>\x1b[m " % topo.sim.time()'

    # Select from one of the predefined alternatives (or any other format):
    format = simtime_format
    
    def __str__(self): return str(eval(self.format,__main__.__dict__))


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
    


	
