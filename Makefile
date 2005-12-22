# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --parseable=yes --required-attributes=__version__ --min-name-length=1 --notes=FIXME,XXX,TODO,ALERT --max-line-length=200 --disable-msg=C0324
PYCHECKER = bin/pychecker

DOC    = doc/Reference_Manual

RELEASE = 0.8.1
RELEASE_TAG = release_0_8_1

# Default does not include doc, in case user lacks PHP
default: ext-packages topographica reference-manual

all: default doc tests examples

clean: cleandoc clean-ext-packages

FORCE:

tests: FORCE
	./topographica runtests

examples: FORCE
	make -C examples

ext-packages:
	make -C external

clean-ext-packages: 
	make -C external clean
	make -C external uninstall


# Startup Script, in Python
topographica: external Makefile
	echo "#!${PREFIX}/bin/python" > topographica
	echo "#  Wrapper for setting environment vars and exec-ing commands" >> topographica
	echo "import os,sys,topographica_script" >> topographica
	echo "" >> topographica
	echo "TOPO = '${PREFIX}'" >> topographica
	echo "os.putenv('LD_LIBRARY_PATH'," >> topographica
	echo "          ':'.join((os.path.join(TOPO,'lib'),os.getenv('LD_LIBRARY_PATH',''))))" >> topographica
	echo "os.putenv('PYTHONPATH',TOPO+':'+':'+os.getenv('PYTHONPATH',''))" >> topographica
	echo "os.putenv('TOPORELEASE','${RELEASE}')" >> topographica
	echo "" >> topographica
	echo "# exec" >> topographica
	echo "cmd = os.path.join(TOPO,'bin/python')" >> topographica
	echo "args = topographica_script.generate_params(sys.argv[1:])" >> topographica
	echo "os.execv(cmd,[cmd] + args)" >> topographica

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
	cvs tag -F -c LATEST_STABLE
	cvs tag -F -c ${RELEASE_TAG}

# Update Topographica.org web site
sf-web-site: reference-manual doc
	rsync -v -arHz -e ssh doc/. topographica.sf.net:/home/groups/t/to/topographica/htdocs/.

