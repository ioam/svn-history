#!/usr/bin/env python

# should probably think of something better than this
# name, and than having it in the root topo dir

import sys
import os

DEFAULTS = dict(python_bin="/usr/bin/env python",
                release = None,
                version = None)

def write(python_bin=None,release=None,version=None):

    python_bin = python_bin or DEFAULTS['python_bin']
    release = release or DEFAULTS['release']
    version = version or DEFAULTS['version']

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

    python_bin = DEFAULTS['python_bin']
    release = DEFAULTS['release']
    version = DEFAULTS['version']

    args = sys.argv[1::]
    assert len(args)==3, "Pass python_bin, release, version (any of which may be None)"
    python_bin,release,version = args

    print "python: %s"%python_bin
    print "release: %s"%release
    print "version: %s"%version

    write(python_bin,release,version)


