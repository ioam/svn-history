"""
Some Topographica specific changes to the standard pydoc command.
Moves generated pydoc HTML files to the docs directory after they are
created by pydoc.  To be used with MAKE, and only from the base
Topographica directory.

The generated index.html file is for the topo/__init__.py file which
does not necessarily catalog topo/*.py.  To see all files, select
the 'index' link at the top of one of the html docs.

To generate Documentation, enter 'make docs' from the base Topographica
directory which will call this file on the Topographica sources.

From the Makefile (Tabs have been stripped):
    cleandocs:
        - rm -r docs
        
    docs: topo/*.py
        mkdir -p docs
        ./topographica topo/gendocs.py
        mv docs/topo.__init__.html docs/index.html

$Id$
"""

import pydoc, glob, sys, os

TOPO = 'topo'   # Subdirectory with Topographica source
DOCS = 'docs'   # Subdirectory to place Docs
pydoc.writing = 1

os.system('rm -rf ' + DOCS + '/*')

# Generate the files once.  Skip if already generated.
filelist = glob.glob(TOPO + '/*.py')
for i in filelist:
    if not glob.glob(DOCS + '/' + TOPO + '.' + i[len(TOPO)+1:-3] + '.html'):
        pydoc.writedoc('topo.' + i[len(TOPO)+1:-3])
    if glob.glob(TOPO + '.' + i[len(TOPO)+1:-3] + '.html'):
        cline = 'mv -f ' + TOPO + '.' + i[len(TOPO)+1:-3] + '.html ' + DOCS + '/'
        os.system(cline)
    else:                   
        filelist.remove(i)  

