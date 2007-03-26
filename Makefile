# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --parseable=yes --required-attributes=__version__ --min-name-length=1 --notes=FIXME,XXX,TODO,ALERT --max-line-length=200 --disable-msg=C0324
PYCHECKER = bin/pychecker

RELEASE = 0.9.2
RELEASE_TAG = release_0_9_2

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
default: ext-packages topographica

all: default reference-manual doc tests examples 

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


# Compare topographica and C++ lissom output
compare_or: 
	make -C topo/tests/reference/
	./topographica -c "comparisons=True" topo/tests/reference/lissom_or_reference.ty 

compare_oo_or: 
	make -C topo/tests/reference/
	./topographica -c "comparisons=True" topo/tests/reference/lissom_oo_or_reference.ty 

# Test that the specified scripts haven't changed in results or speed.
#SCRIPTS=^cfsom_or.ty ^lissom_oo_or.ty ^som_retinotopy.ty
SCRIPTS= ^cfsom_or.ty ^hierarchical.ty ^lissom_or.ty ^lissom_oo_or.ty ^lissom_oo_or_dy.ty ^lissom_oo_od.ty ^lissom_oo_or_homeomaxent.ty ^lissom_or_homeomaxent.ty ^lissom_or_homeoscale.ty ^lissom_or_noshrinking.ty ^som_retinotopy.ty ^sullivan_neurocomputing04.ty ^sullivan_nn06.ty
# ^lissom_photo_or.ty # Omitted because photos are not always installed


TRAINSCRIPTS=${SCRIPTS}
TRAINDATA =${subst ^,topo/tests/,${subst .ty,.ty_DATA,${TRAINSCRIPTS}}}
TRAINTESTS=${subst ^,topo/tests/,${subst .ty,.ty_TEST,${TRAINSCRIPTS}}}

SPEEDSCRIPTS=${SCRIPTS}
SPEEDDATA =${subst ^,topo/tests/,${subst .ty,.ty_SPEEDDATA,${SPEEDSCRIPTS}}}
SPEEDTESTS=${subst ^,topo/tests/,${subst .ty,.ty_SPEEDTEST,${SPEEDSCRIPTS}}}

train-tests: ${TRAINTESTS}
speed-tests: ${SPEEDTESTS}

slow-tests: train-tests snapshot-tests speed-tests


# General rules for generating test data and running the tests
%_DATA:
	./topographica -c 'from topo.tests.test_script import GenerateData; GenerateData(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_DATA",density=8,run_for=[1,99,150])'

%_TEST: %_DATA
	./topographica -c 'from topo.tests.test_script import TestScript; TestScript(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_DATA")'

%_SPEEDDATA:
	./topographica -c 'from topo.tests.test_script import generate_speed_data; generate_speed_data(script="examples/${notdir $*}",iterations=250,data_filename="topo/tests/${notdir $*}_SPEEDDATA")'

%_SPEEDTEST: %_SPEEDDATA
	./topographica -c 'from topo.tests.test_script import compare_speed_data; compare_speed_data(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_SPEEDDATA")'

.SECONDARY: ${SPEEDDATA} ${TRAINDATA} # Make sure that *_*DATA is kept around


snapshot-tests:
	./topographica -c "default_density=4" examples/lissom_oo_or.ty -c "topo.sim.run(1)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('snapshot-tests.typ')"
	./topographica -c "from topo.commands.basic import load_snapshot ; load_snapshot('snapshot-tests.typ')"
	./topographica -c "default_density=4" examples/som_retinotopy.ty -c "topo.sim.run(1)" -c "from topo.commands.basic import save_snapshot ; save_snapshot('snapshot-tests.typ')"
	./topographica -c "default_density=4" examples/som_retinotopy.ty -c "from topo.commands.basic import load_snapshot ; load_snapshot('snapshot-tests.typ')"
	rm -f 'snapshot-tests.typ'


clean-pyc:
	rm -f topo/*.pyc topo/*/*.pyc topo/*/*/*.pyc

clean-doc:
	make -C doc clean

reference-manual: 
	make -C doc reference-manual

doc: FORCE
	make -C doc/



#############################################################################
# For maintainer only; be careful with these commands

## Code releases, currently handled via CVS.
## Run these from a relatively clean copy of the topographica directory 
## (without stray files, especially in doc/).

cvs-release: LATEST_STABLE sf-web-site

# Update any topographica-win files that keep track of the version number
# CEBALERT: maintainer must have checked out topographica-win
new-version: FORCE
	mv topographica-win/create_installer/topographica.iss topographica-win/create_installer/topographica.iss~
	sed -e 's/AppVerName=Topographica.*/AppVerName=Topographica '"${RELEASE}"'/g' topographica-win/create_installer/topographica.iss~ > topographica-win/create_installer/topographica.iss
	mv topographica-win/common/setup.py topographica-win/common/setup.py~
	sed -e "s/topo.release='.*'/topo.release='${RELEASE}'"'/g' topographica-win/common/setup.py~ > topographica-win/common/setup.py


# Make a new LATEST_STABLE on the web, using the currently checked-out version
LATEST_STABLE:
	cvs rtag -d LATEST_STABLE topographica
	cvs rtag -d LATEST_STABLE topographica-win
	cvs tag  -F -c LATEST_STABLE
	cvs tag  -F -c ${RELEASE_TAG}
	cvs rtag -F LATEST_STABLE  topographica-win
	cvs rtag -F ${RELEASE_TAG} topographica-win

# Update Topographica.org web site
sf-web-site: reference-manual doc
	rsync -v -arHz -e ssh doc/. topographica.sf.net:/home/groups/t/to/topographica/htdocs/.


# Clear out everything not intended for the public distribution
#
# This is ordinarily commented out in the CVS version for safety, 
# but it is enabled when the distribution directory is created.
#
#@@distclean: FORCE clean
#@@	   ${RM} .#* */.#* */*/.#* */*~ .cvsignore ChangeLog.txt */.cvsignore */*/.cvsignore */*/*/.cvsignore
#@@	   ${RM} etc/topographica.elc ImageSaver*.ppm countalerts* annotate.out
#@@	   ${RM} examples/disparity_energy.ty
#@@	   ${RM} examples/homeostatic.ty
#@@	   ${RM} examples/joublin_bc96.ty
#@@	   ${RM} examples/laminar.ty
#@@	   ${RM} examples/laminar_lissom.ty
#@@	   ${RM} examples/laminar_nolearning.ty
#@@	   ${RM} examples/leaky_lissom_or.ty
#@@	   ${RM} examples/lissom_oo_od.ty
#@@	   ${RM} examples/lissom_oo_or_dy_photo.ty
#@@	   ${RM} examples/lissom_oo_or_homeomaxent.ty
#@@	   ${RM} examples/lissom_or_homeomaxent.ty
#@@	   ${RM} examples/lissom_or_homeoscale.ty
#@@	   ${RM} examples/lissom_or_noshrinking.ty
#@@	   ${RM} examples/lissom_or_noshrinking_latswitch.ty
#@@	   ${RM} examples/lissom_or_sf.ty
#@@	   ${RM} examples/ohzawa_science90.ty
#@@	   ${RM} examples/sullivan_neurocomputing04.ty
#@@	   ${RM} examples/sullivan_nn06.ty
#@@	   ${RM} -r topographica-win
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



