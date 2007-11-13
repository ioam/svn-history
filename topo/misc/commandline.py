"""
Support functions for parsing command-line arguments and providing
the Topographica command prompt.  Typically called from the
'./topographica' script, but can be called directly if using
Topographica files within a separate Python.

$Id$
"""
__version__='$Revision$'


from optparse import OptionParser
from inlinec import import_weave

import sys, __main__, math, os, re

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

def sim_title_from_filename(filename):
    """
    Set the simulation title from the given filename, if none has been
    set already.
    """
    if topo.sim.name is None:
        topo.sim.name=re.sub('.ty$','',os.path.basename(filename))


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
            # Adds commands for opening a script; also adds the location
            # of the file to sys.path so that imports relative to the
            # script's location will work
            abs_arg = os.path.abspath(arg)
	    list_command = list_command + ['import sys; sys.path.insert(0,"%s")'%os.path.dirname(abs_arg),
                                           'execfile(' + repr(abs_arg) + ')']

            sim_title_from_filename(arg)
            
	    del rargs[0]
    setattr(parser.values,"commands",list_command) 


def boolean_option_action(option,opt_str,value,parser):
    """Callback function for boolean-valued options that apply to the entire run.""" 
    setattr(parser.values,option.dest,True) 
    get_filenames(parser)


topo_parser.add_option("-i","--interactive",action="callback",callback=boolean_option_action,
                       dest="interactive",default=False,
                       help="provide an interactive prompt even if stdin does not appear to be a terminal.")


gui_started=False

def g_action(option,opt_str,value,parser):
    """Callback function for the -g option."""

    # The first time -g is encountered (only), adds a command to the -c list to start the GUI
    global gui_started
    if not gui_started:
        gui_started = True
        list_command=getattr(parser.values,"commands")
        list_command += ["print 'Launching GUI'; import topo.tkgui ; topo.tkgui.start()"]
        setattr(parser.values,"commands",list_command)

    boolean_option_action(option,opt_str,value,parser)
    a_action(option,opt_str,value,parser)
    
topo_parser.add_option("-g","--gui",action="callback",callback=g_action,dest="gui",default=False,help="""
    launch an interactive graphical user interface; \
    equivalent to -c 'import topo.tkgui ; topo.tkgui.start()'.\
    Implies -a.""")


def c_action(option,opt_str,value,parser):
    """Callback function for the -c option."""
    
    list_command=getattr(parser.values,option.dest)
    list_command += [value]
    setattr(parser.values,option.dest,list_command) 
    get_filenames(parser)

topo_parser.add_option("-c","--command",action = "callback",callback=c_action,type="string",
		       default=[],dest="commands",metavar="\"<command>\"",
		       help="commands passed in as a string and followed by files to be executed.")


def a_action(option,opt_str,value,parser):
    """Callback function for the -a option."""
    import re,os
    from filepaths import application_path
    import __main__

    for f in os.listdir(os.path.join(application_path,"topo/commands")):
        if re.match('^[^_].*\.py$',f):
            modulename = re.sub('\.py$','',f)
            exec "from topo.commands."+modulename+" import *" in __main__.__dict__
    
topo_parser.add_option("-a","--auto-import-commands",action="callback",callback=a_action,
		       help="import everything from commands/*.py into the main namespace, for convenience.")



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
    # CB: can we remove this ALERT? We want to import weave before
    # running a user's commands and scripts anyway. Plus, I can't
    # reproduce the error by doing the following:
    # - comment out code line below
    # - $ ./topographica
    # - $ import weave
    # (using both cygwin-compiled topographica and topographica from
    # binary packages).
    if import_weave: exec "import weave" in __main__.__dict__    

    sys.ps1 = CommandPrompt()
    sys.ps2 = CommandPrompt2()
    
    for (k,v) in global_constants.items():
        exec '%s = %s' % (k,v) in __main__.__dict__

    ### exec one or more (possibly platform-specific) startup files 
    home = os.path.expanduser("~")  # dotfiles on unix
    appdata = os.path.expandvars("$APPDATA") # application data on windows
    appsupport = os.path.join(home,"Library","Application Support") # application support on OS X  

    rcpath = os.path.join(home,'.topographicarc')
    inipath = os.path.join(appdata,'Topographica','topographica.ini')
    configpath = os.path.join(appsupport,'Topographica','topographica.config')

    startup_exceptions_found=False
    for startup_file in (rcpath,configpath,inipath):
        if os.path.exists(startup_file):
            if option.interactive or option.gui:
                print "Executing user startup file %s" % (startup_file)
            try:
                execfile(startup_file,__main__.__dict__)
            except:
                import traceback
                # print any exception raised in the init files, and continue
                print 'Exception executing startup file %s' % startup_file
                typ,val,tb = sys.exc_info()
                print traceback.print_tb(tb)
                print '%s: %s'%(typ.__name__, str(val))
                # JPALERT: Maybe instead of continuing, control should
                # go straight to the command line here for debugging,
                # skipping the rest of the startup process?
                startup_exceptions_found=True

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

    # Provide an interactive prompt unless running in batch mode
    if option.interactive:
        print BANNER

    if option.interactive or option.gui:
	os.environ["PYTHONINSPECT"] = "1"
        try:
            import readline
        except ImportError:
            print "Module readline not available.\nHistory and completion support disabled."
        else:
            #set up command completion
            import rlcompleter
            readline.parse_and_bind("tab: complete")

    if startup_exceptions_found:
        print "ERROR: Exceptions encountered when processing startup files; not executing any command-line arguments."
        return
    
     # catch the first filenames arguments (before any options) and execute them.
    filename_arg = topo_parser.largs

    for filename in filename_arg:
        # CB: this is going to need converting too, I don't know when it's used yet.
        # JABALERT: What do you mean?  It looks fine to me.
        # JPALERT: Because topo_parser.parse_args(argv) converts all the files on
        # the command line into execfile commands, there are no files left to
        # process here.  So this code is never called.  Still I updated it to add
        # the file directory to sys.path, just in case.
        #print "Note: Please send the command you used to start this run of Topographica to jbednar at inf.ed.ac.uk, showing how to reproduce this message, for debugging purposes."
        filedir = os.path.dirname(os.path.abspath(filename))
        sys.path.insert(0,filedir)
	execfile(filename,__main__.__dict__)
        

    # execute remaining commands.
    for cmd in option.commands:
	exec cmd in __main__.__dict__
    

    # if the gui is running, set the console name
    if gui_started: topo.guimain.title(topo.sim.name)
