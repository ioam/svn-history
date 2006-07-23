# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --parseable=yes --required-attributes=__version__ --min-name-length=1 --notes=FIXME,XXX,TODO,ALERT --max-line-length=200 --disable-msg=C0324
PYCHECKER = bin/pychecker

DOC = doc/Reference_Manual

RELEASE = 0.9.1
RELEASE_TAG = release_0_9_1

TEST_VERBOSITY = 1


# Commands needed to build a public distribution

COMPRESS_ARCHIVE           = gzip
MAKE_ARCHIVE               = tar -cf -
MAKE_ZIP                   = zip -r -q
MKDIR                      = mkdir -p
SED			   = sed
RM                         = rm -f
CD                         = cd
CP                         = cp
MV                         = mv
MAKE                       = make

# Definitions for public distributions
PROGRAM                    = topographica
DIST_TMPDIR                = ../distributions
DIST_DIRNAME               = ${PROGRAM}-${RELEASE}
DIST_DIR                   = ${DIST_TMPDIR}/${DIST_DIRNAME}
DIST_ARCHIVE               = ${DIST_DIRNAME}.tar.gz
DIST_ZIP                   = ${DIST_DIRNAME}.zip



# Default does not include doc, in case user lacks PHP
default: ext-packages topographica reference-manual

all: default doc tests examples

clean: clean-doc clean-ext-packages clean-pyc
	${RM} .??*~ *~ */*~ */.??*~ */*/*~ */*/.??*~ */*/*/*~ */*/*/.??*~ *.bak
	${RM} .#??*.* */.#??*.* */*/.#??*.* */*/*/.#??*.*
	${RM} -r bin include share lib man topographica ImageSaver*.jpeg python_topo

saved-examples: 
	make -C examples saved-examples


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
	echo "import topo" >> topographica
	echo "topo.release='${RELEASE}'" >> topographica
	echo "" >> topographica
	echo "# Process the command-line arguments" >> topographica
	echo "from sys import argv" >> topographica
	echo "from topo.misc.commandline import process_argv" >> topographica
	echo "process_argv(argv[1:])" >> topographica

	chmod a+x ${PREFIX}topographica


check:
	${PYCHECKER} topo/*.py topo/*/*.py

lint:
	${PYLINT} topo/*.py topo/*/*.py


clean-pyc:
	rm -f topo/*.pyc topo/*/*.pyc topo/*/*/*.pyc

clean-doc:
	make -C doc clean

# Auto-generated source code documentation
# Uses an integrated python script named gendocs.py
reference-manual: topo/*.py topo/*/*.py doc/Reference_Manual
	mkdir -p ${DOC}
	./topographica topo/misc/gendocs.py

doc: FORCE
	make -C doc/



#############################################################################
# For maintainer only; be careful with these commands

## Code releases, currently handled via CVS.
## Run these from a relatively clean copy of the topographica directory 
## (without stray files, especially in doc/).

cvs-release: LATEST_STABLE sf-web-site

# Update any files that keep track of the version number
new-version: FORCE
	mv external/mswin/for_binaries/topographica.iss external/mswin/for_binaries/topographica.iss~
	sed -e 's/AppVerName=Topographica.*/AppVerName=Topographica '"${RELEASE}"'/g' external/mswin/for_binaries/topographica.iss~ > external/mswin/for_binaries/topographica.iss
	mv external/mswin/setup.py external/mswin/setup.py~
	sed -e "s/topo.release='.*'/topo.release='${RELEASE}'"'/g' external/mswin/setup.py~ > external/mswin/setup.py


# Make a new LATEST_STABLE on the web, using the currently checked-out version
LATEST_STABLE:
	cvs rtag -d LATEST_STABLE topographica
	cvs tag -F -c LATEST_STABLE
	cvs tag -F -c ${RELEASE_TAG}

# Update Topographica.org web site
sf-web-site: reference-manual doc
	rsync -v -arHz -e ssh doc/. topographica.sf.net:/home/groups/t/to/topographica/htdocs/.


# Clear out everything not intended for the public distribution
#
# This is ordinarily commented out in the CVS version for safety, 
# but it is enabled when the distribution directory is created.
#
#@@distclean: FORCE clean
#@@	   ${RM} .#* */.#* */*/.#* */*~ .cvsignore ChangeLog.txt */.cvsignore */*/.cvsignore
#@@	   ${RM} etc/topographica.elc ImageSaver*.ppm countalerts* annotate.out
#@@	   ${RM} examples/disparity_energy.ty
#@@	   ${RM} examples/homeostatic.ty
#@@	   ${RM} examples/joublin_bc96.ty
#@@	   ${RM} examples/laminar.ty*
#@@	   ${RM} examples/laminar_lissom.ty
#@@	   ${RM} examples/laminar_nolearning.ty
#@@	   ${RM} examples/leaky_lissom_or.ty
#@@	   ${RM} examples/lissom_or_sf.ty
#@@	   ${RM} examples/tiny.ty
#@@	   ${RM} -r external/mswin external/win32 setup.bat topographica.ico
#@@	   ${RM} -r tmp/
#@@	   ${RM} -r CVS */CVS */*/CVS */*/*/CVS


# Make public distribution archive
distarc: FORCE distclean 
	${CD} .. ; ${MAKE_ARCHIVE} ${DIST_DIRNAME} | ${COMPRESS_ARCHIVE} > ${DIST_ARCHIVE}
	${CD} .. ; ${RM} -f ${DIST_ZIP} ; ${MAKE_ZIP} ${DIST_ZIP} ${DIST_DIRNAME} 

# Create public distribution subdirectory
distdir: FORCE
	${RM} -r ${DIST_DIR}
	${MKDIR} ${DIST_DIR}
	${CP} -r -d . ${DIST_DIR}
	${RM} ${DIST_DIR}/Makefile 
	${SED} \
	-e 's|^#@@||' \
	Makefile > ${DIST_DIR}/Makefile 

# Create public distribution subdirectory and archive
dist: doc distdir reference-manual FORCE
	${CD} ${DIST_DIR}; ${MAKE} distarc

ChangeLog.txt: FORCE
	mv ChangeLog.txt ChangeLog
	`locate rcs2log | grep /emacs` -v > ChangeLog.new
	cat ChangeLog.new ChangeLog > ChangeLog.txt
	rm -f ChangeLog ChangeLog.new



