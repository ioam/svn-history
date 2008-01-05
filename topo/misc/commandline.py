"""
Support functions for parsing command-line arguments and providing
the Topographica command prompt.  Typically called from the
'./topographica' script, but can be called directly if using
Topographica files within a separate Python.

$Id$
"""
__version__='$Revision$'


from optparse import OptionParser

import sys, __main__, math, os, re, traceback

import topo


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
    basic_format   = '"Topographica>>> "'
    simtime_format = '"Topographica_t%g>>> " % topo.sim.time()'
    ansi_format    = '"\x1b[32;40;1mTopographica\x1b[33;40;1m_t%g>>>\x1b[m " % topo.sim.time()'

    # Select from one of the predefined alternatives (or any other format):
    format = simtime_format

    def __str__(self): return str(eval(self.format,__main__.__dict__))
    def split(self,*args):
        return str(self).split(*args)

class CommandPrompt2(CommandPrompt):
    """
    Provides a dynamically updated command prompt for sys.ps2.

    This function uses the exact same prompt strings that are defined in
    CommandPrompt (above), but it replaces any occurrances of the substring '>>>'
    with '...'.
    """

    def __str__(self): return str(eval(self.format.replace('>>>','...'),__main__.__dict__))



# Use to define global constants
global_constants = {'pi':math.pi}

# Create the topographica parser.
usage = "usage: topographica ([<option>]:[<filename>])*\n\
where any combination of options and Python script filenames will be\n\
processed in order left to right."
topo_parser = OptionParser(usage=usage)


def sim_name_from_filename(filename):
    """
    Set the simulation title from the given filename, if none has been
    set already.
    """
    if topo.sim.name is None:
        topo.sim.name=re.sub('.ty$','',os.path.basename(filename))


def boolean_option_action(option,opt_str,value,parser):
    """Callback function for boolean-valued options that apply to the entire run.""" 
    #print "Processing %s" % (opt_str)
    setattr(parser.values,option.dest,True)


# CB: note that topographica should stay open if an error occurs
# anywhere after a -i (i.e. in a -c command or script)
def i_action(option,opt_str,value,parser):
    """Callback function for the -i option."""
    boolean_option_action(option,opt_str,value,parser)
    os.environ['PYTHONINSPECT'] = '1' # Provide Python prompt even after execution completes
    print BANNER

topo_parser.add_option("-i","--interactive",action="callback",callback=i_action,
                       dest="interactive",default=False,
                       help="provide an interactive prompt even if stdin does not appear to be a terminal.")

def gui():
    """Start the GUI as if -g were supplied in the command used to launch Topographica."""
    auto_import_commands()
    import topo.tkgui
    topo.tkgui.start()

# Topographica stays open if an error occurs after -g
# (see comment by i_action)
def g_action(option,opt_str,value,parser):
    """Callback function for the -g option."""
    boolean_option_action(option,opt_str,value,parser)
    os.environ['PYTHONINSPECT'] = '1'
    gui()
    
topo_parser.add_option("-g","--gui",action="callback",callback=g_action,dest="gui",default=False,help="""\
launch an interactive graphical user interface; \
equivalent to -c 'from topo.misc.commandline import gui ; gui()'. \
Implies -a.""")


# Keeps track of whether something has been performed, when deciding whether to assume -i
something_executed=False

def c_action(option,opt_str,value,parser):
    """Callback function for the -c option."""
    #print "Processing %s '%s'" % (opt_str,value)
    exec value in __main__.__dict__
    global something_executed
    something_executed=True
            
topo_parser.add_option("-c","--command",action = "callback",callback=c_action,type="string",
		       default=[],dest="commands",metavar="\"<command>\"",
		       help="string of arbitrary Python code to be executed in the main namespace.")



def auto_import_commands():
    """Import the contents of all files in the topo/commands/ directory."""
    import re,os
    from filepaths import application_path
    import __main__

    for f in os.listdir(os.path.join(application_path,"topo/commands")):
        if re.match('^[^_].*\.py$',f):
            modulename = re.sub('\.py$','',f)
            exec "from topo.commands."+modulename+" import *" in __main__.__dict__
    
def a_action(option,opt_str,value,parser):
    """Callback function for the -a option."""
    auto_import_commands()
    
topo_parser.add_option("-a","--auto-import-commands",action="callback",callback=a_action,help="""\
import everything from commands/*.py into the main namespace, for convenience; \
equivalent to -c 'from topo.misc.commandline import auto_import_commands ; auto_import_commands()'.""")



def exec_startup_files():
    """
    Execute startup files, looking at appropriate locations for many different platforms.
    """
    home = os.path.expanduser("~")  # dotfiles on unix
    appdata = os.path.expandvars("$APPDATA") # application data on windows
    appsupport = os.path.join(home,"Library","Application Support") # application support on OS X  

    rcpath = os.path.join(home,'.topographicarc')
    inipath = os.path.join(appdata,'Topographica','topographica.ini')
    configpath = os.path.join(appsupport,'Topographica','topographica.config')

    for startup_file in (rcpath,configpath,inipath):
        if os.path.exists(startup_file):
            print "Executing user startup file %s" % (startup_file)
            execfile(startup_file,__main__.__dict__)
                

    ### Notes about choices for topographica.rc equivalents on different platforms
    #
    ## Windows:
    # Location --  Most programs use the registry or a folder in %appdata% (which is typically
    #  ~\Application Data). The registry is not easily accessible for users, and %appdata% is
    # a hidden folder, which means it doesn't appear in Explorer (or file-open dialogs).
    # Most programs do not have any user-editable configuration files, so this does not matter
    # to them. Maybe we should just use ~\topographica.ini?
    # 
    # Name -- Considered topographica.rc, topographica.dat, topographica.cfg, topographica.ini.
    #  Of those, only .ini is registered as standard in Windows. According to Winows Explorer:
    #  "Files with extension 'INI' are of type 'Configuration Settings'"
    #  Importantly, this means they are already setup to be editable by notepad by default, so
    #  they can be double clicked.
    #
    # http://mail.python.org/pipermail/python-list/2005-September/341702.html
    #
    ## Mac OS:
    # Location -- Seems like programs use either ~/Library/AppName or (more commonly)
    # ~/Library/Application Support/AppName (CEBALERT: is there a var. for that on OS X?).
    # 
    # Name -- there are many different extensions (e.g. dat, config, cfg, ini), none of which
    # opens with any application by default. Some applications use xml.




### Execute what is specified by the options.

def process_argv(argv):
    """
    Process command-line arguments (minus argv[0]!), rearrange and execute.
    """

    # Initial preparation
    for (k,v) in global_constants.items():
        exec '%s = %s' % (k,v) in __main__.__dict__

    sys.ps1 = CommandPrompt()
    sys.ps2 = CommandPrompt2()
    
    exec_startup_files()

    # Repeatedly process options, if any, followed by filenames, if any, until nothing is left
    topo_parser.disable_interspersed_args()
    args=argv
    option=None
    global something_executed
    while True:
        # Process options up until the first filename
        (option,args) = topo_parser.parse_args(args,option)

        # Handle filename
        if args:
            filename=args.pop(0)
            #print "Executing %s" % (filename)
            filedir = os.path.dirname(os.path.abspath(filename))
            sys.path.insert(0,filedir) # Allow imports relative to this file's path
            sim_name_from_filename(filename) # Default value of topo.sim.name

            execfile(filename,__main__.__dict__)
            something_executed=True
            
        if not args:
            break

        
    # If no scripts and no commands were given, pretend -i was given.
    if not something_executed:
        option.interactive=True
        
    if option.interactive or option.gui or os.environ.get('PYTHONINSPECT'):
        # Use readline if available
        try:
            import readline
        except ImportError:
            print "Module readline not available.\nHistory and completion support disabled."
        else:
            #set up command completion
            import rlcompleter
            readline.parse_and_bind("tab: complete")
    else:
        # IPython (unlike Python) stays open no matter what interactive is set to,
        # so we need to call exit
        sys.exit()

    if option.gui:
        topo.guimain.title(topo.sim.name)

    
        
