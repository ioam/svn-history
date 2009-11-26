#!/usr/bin/env python

# should probably think of something better than this
# name, and than having it in the root topo dir

import sys
import os

def write(python_bin,release,version):
    script = """#!%s
# Startup script for Topographica

import topo
topo.release='%s'
topo.version='%s'

# Process the command-line arguments
from sys import argv
from topo.misc.commandline import process_argv
process_argv(argv[1:])
"""%(python_bin,release,version)
    
    # CEBALERT: assumes we're in the root topographica dir
    f = open('topographica','w')
    f.write(script)
    f.close()
    os.system('chmod +x topographica')


if __name__=='__main__':
    print "creating topographica script..."

    try:
        python_bin = sys.argv[1]
    except:
        python_bin = "/usr/bin/env python"

    print "python: %s"%python_bin

    try:
        release = sys.argv[2]
    except:
        release = None

    print "release: %s"%release

    try:
        version = sys.argv[3]
    except:
        version = None

    print "version: %s"%version

    write(python_bin,release,version)

