"""
Some Topographica specific changes to the standard pydoc command.
Moves generated pydoc HTML files to the docs directory after they are
created by pydoc.  To be used with MAKE, and only from the base
Topographica directory.

To generate Documentation, enter 'make docs' from the base Topographica
directory which will call this file on the Topographica sources.

From the Makefile (Tabs have been stripped):
    GENDOC = ./topographica topo/gendocs.py -w 
    docs: topo/*.py
	mkdir -p docs
	${GENDOC} topo/__init__.py
	mv docs/__init__.html docs/index.html
	${GENDOC} topo/

$Id$
"""

import pydoc, glob, sys, os

TOPO = 'topo'   # Subdirectory with Topographica source
DOCS = 'docs'   # Subdirectory to place Docs

sys.path.insert(1,TOPO + '/') 
pydoc.cli()

# Move those files which were generated to ./docs/
for i in glob.glob(TOPO + '/*.py'):
    cline = 'mv -f ' + i[len(TOPO)+1:-3] + '.html ' + DOCS + '/' + i[len(TOPO)+1:-3] + '.html'
    if glob.glob(i[len(TOPO)+1:-3] + '.html'):
        # print cline
        os.system(cline)

