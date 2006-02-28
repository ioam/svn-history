"""
To start Topographica, run './topographica' and not this file.  This
file is used to support that file.

./topographica is generated by the Makefile so we keep as much code
outside so the Makefile remains readable, and changes are easier to
implement.

$Id$
"""

__version__='$Revision$'

import sys, __main__, math

import os
from optparse import OptionParser
from topo.misc.inlinec import import_weave

BANNER         = """
Welcome to Topographica!

Type help() for interactive help with python, help(topo) for general
information about Topographica, help(commandname) for info on a
specific command, or topo.about() for info on this release, including
licensing information.
"""

### JABALERT: Should pick just one of these, presumably pi
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



# Create the parser.
usage = "usage: topographica ([<option>]:[<filename>])*\n\
where <option> can be one of the following:\n\
-c \"<command>\"\n\
-g\n\
-i\n\
-v\n\
"

topo_parser = OptionParser(usage=usage)

# Defining the options 

def getting_filenames(parser):
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
	    list_command = list_command +  'execfile(\'' + arg + '\');'
	    del rargs[0]
    setattr(parser.values,"commands",list_command) 


def g_i_action(option,opt_str,value,parser):
    """callback function for the -g and -i option.""" 
    setattr(parser.values,option.dest,True) 
    getting_filenames(parser)


topo_parser.add_option("-g","--gui",action="callback",callback=g_i_action,dest="gui",default=False,help="enter GUI mode.")
topo_parser.add_option( "-i",action="callback",callback=g_i_action,dest="interactive",default=False,
			help="inspect interactively after running script, and force prompts,\
even if stdin does not appear to be a terminal.")


def c_action(option,opt_str,value,parser):
    """callback function for the -c option.""" 
    list_command=getattr(parser.values,option.dest)
    list_command +=  value + ";"
    setattr(parser.values,option.dest,list_command) 
    getting_filenames(parser)

topo_parser.add_option("-c",action = "callback",callback = c_action,type="string",default='',dest="commands",
		       metavar="\"<command>\"",help="commands passed in as a string and followed by files to be executed.")


def append_to_option_list(option,opt_str,value,parser):
    """callback function for all option without argument."""
    option_list=getattr(parser.values,option.dest)
    option_list.append(opt_str)
    getting_filenames(parser)

topo_parser.add_option("-v","--verbose",action="callback",callback = append_to_option_list,
		       nargs=0, dest="list_option", default = [],help="verbose.")


def generate_params(argv):
    """
    Read in argv (minus argv[0]!), and rearrange for re-execution.
    """

    (option,args) = topo_parser.parse_args(argv)

    # catch the first filenames arguments
    filename_arg = topo_parser.largs
    list_filename = ''
    for filename in filename_arg:
	list_filename +=  'execfile(\'' + filename + '\');'
    
    # generates the prefixes of cmd and option_list
    cmd, option_list = generate_prefixes(option.gui,option.interactive) 
    # add the lists of non-arg options (recognized by python)
    option_list += option.list_option

    # cmd is the command line executed by python
    # option_list is the option without arguments that are recognized by Python
  
    cmd += list_filename
    cmd += option.commands
    # To deal with a need to double-quote under Windows
    if os.name == 'nt': cmd += '"'
    option_list.append('-c')
    return (option_list + [cmd])



def generate_prefixes(gui,interactive):
    """
    Generate start-up command and options.
    """
    option_list = []
     # To deal with a need to double-quote under Windows
    if os.name == 'nt': cmd = '"'
    else: cmd = ''

    # (As of 12/2005) With Python 2.4 compiled and run on Windows XP,
    # trying to import Weave after starting the topo command-line will
    # generate a serious system error.  However, importing weave first
    # does not cause problems.  
    try:
        if import_weave:
            import weave    
            cmd += 'import weave; '
    except:
        pass
    
    cmd += 'import topo.misc.commandline; topo.misc.commandline.start(' \
           + str(interactive) + ');'
    
    # if -g is on
    if gui:
	cmd += ' topo.gui_cmdline_flag = True; import topo.tkgui; topo.tkgui.start();'
	option_list += ['-i']
    else:
        cmd += ' topo.gui_cmdline_flag = False;'
     
    # if -i is on
    if interactive:
	option_list += ['-i']

    return cmd, option_list
