# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --parseable=yes --required-attributes=__version__ --min-name-length=1 --notes=FIXME,XXX,TODO,ALERT --max-line-length=200 --disable-msg=C0324
PYCHECKER = bin/pychecker

DOC    = doc/Reference_Manual

RELEASE = 0.8.2
RELEASE_TAG = release_0_8_2

TEST_VERBOSITY = 1


# Default does not include doc, in case user lacks PHP
default: ext-packages topographica reference-manual

all: default doc tests examples

clean: cleandoc clean-ext-packages

saved-examples: 
	make -C examples lissom_oo_or_20000.typ


FORCE:

# To get more information about which tests are being run, do:
# make TEST_VERBOSITY=2 tests
tests: FORCE
	./topographica -c "import topo.tests; topo.tests.run(verbosity=${TEST_VERBOSITY})"

examples: FORCE
	make -C examples

ext-packages:
	make -C external

clean-ext-packages: 
	make -C external clean
	make -C external uninstall


# Startup Script, in Python
topographica: external Makefile
	echo "#!${PREFIX}bin/python" > topographica
	echo "# Startup script for Topographica" >> topographica
	echo "" >> topographica
	echo "# Set os environment variables before importing anything else" >> topographica
	# CEBHACKALERT: Do we need any of these except toporelease? Why are
	# they environment variables in particular?
	echo "import os" >> topographica
	echo "os.environ['PYTHONPATH']='${PREFIX}'" >> topographica
	echo "os.environ['TOPORELEASE']='${RELEASE}'" >> topographica
	echo "" >> topographica
	echo "# Now process the command-line arguments and do Topographica-specific setup" >> topographica
	echo "from sys import argv" >> topographica
	echo "from topo.misc.commandline import process_argv" >> topographica
	echo "process_argv(argv[1:])" >> topographica

	chmod a+x ${PREFIX}topographica


check:
	${PYCHECKER} topo/*.py topo/*/*.py

lint:
	${PYLINT} topo/*.py topo/*/*.py


cleandoc:
	make -C doc clean

# Auto-generated source code documentation
# Uses an integrated python script named gendocs.py
reference-manual: topo/*.py topo/*/*.py doc/Reference_Manual
	mkdir -p ${DOC}
	./topographica topo/misc/gendocs.py

doc: FORCE
	make -C doc/



## Code releases, currently handled via CVS.
## Run these from a relatively clean copy of the topographica directory 
## (without stray files, especially in doc/).

cvs-release: LATEST_STABLE sf-web-site

# Make a new LATEST_STABLE on the web, using the currently checked-out version
LATEST_STABLE:
	cvs rtag -d LATEST_STABLE topographica
	cvs tag -F -c LATEST_STABLE
	cvs tag -F -c ${RELEASE_TAG}

# Update Topographica.org web site
sf-web-site: reference-manual doc
	rsync -v -arHz -e ssh doc/. topographica.sf.net:/home/groups/t/to/topographica/htdocs/.

