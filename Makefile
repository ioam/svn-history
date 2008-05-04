# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --rcfile=doc/buildbot/pylintrc

PYCHECKER = bin/pychecker --config doc/buildbot/pycheckrc

RELEASE = 0.9.4
RELEASE_TAG = release_0_9_4

TEST_VERBOSITY = 1

# currently only applied to train-tests 
IMPORT_WEAVE = 1

# no. of decimal places to require for verifying a match in slow-tests
TESTDP = 14


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

clean: clean-doc clean-ext-packages clean-compiled 
	${RM} .??*~ *~ */*~ */.??*~ */*/*~ */*/.??*~ */*/*/*~ */*/*/.??*~ *.bak
	${RM} .#??*.* */.#??*.* */*/.#??*.* */*/*/.#??*.* current_profile ./topo/tests/testsnapshot.typ ./topo/tests/testplotfilesaver*.png
	${RM} -r bin include share lib man topographica ImageSaver*.jpeg python_topo

uninstall:
	make -C external uninstall

# Mac OS X: to build python with X11 Tkinter
osx-x11-patch: 
	patch --force external/Makefile external/Makefile_OSX_X11.diff
	touch osx-x11-patch

osx-x11-patch-uninstall:
	patch --force --reverse external/Makefile external/Makefile_OSX_X11.diff
	${RM} osx-x11-patch


saved-examples: 
	make -C examples saved-examples


FORCE:

# To get more information about which tests are being run, do:
# make TEST_VERBOSITY=2 tests
tests: FORCE
	./topographica -c "import topo.tests; t=topo.tests.run(verbosity=${TEST_VERBOSITY}); import sys; sys.exit(len(t.failures+t.errors))"

examples: FORCE
	make -C examples

ext-packages:
	make -C external

clean-ext-packages: 
	make -C external clean
	make -C external uninstall


# Build the Python startup script.  Rebuilt whenever a file changes in
# topo/ or examples, to make sure that topo.version is up to date.
topographica: external Makefile topo/*/*.py examples/*.ty
	echo "#!${PREFIX}bin/python" > topographica
	echo "# Startup script for Topographica" >> topographica
	echo "" >> topographica
	echo "import topo" >> topographica
	echo "topo.release='${RELEASE}'" >> topographica
	echo "topo.version='${shell svnversion}'" >> topographica
	echo "" >> topographica
	echo "# Process the command-line arguments" >> topographica
	echo "from sys import argv" >> topographica
	echo "from topo.misc.commandline import process_argv" >> topographica
	echo "process_argv(argv[1:])" >> topographica
	echo "" >> topographica
	chmod a+x ${PREFIX}topographica


check:
	${PYCHECKER} topo/*.py topo/*/*.py

check-base:
	${PYCHECKER} topo/base/*.py 

lint:
	${PYLINT} topo

lint-base:
	${PYLINT} topo.base


# Compare topographica and C++ lissom output
# (needs cleanup+doc)
COMPARE_BASERN=24
COMPARE_BASEN=24
compare_or: 
	make -C topo/tests/reference/
	./topographica -c "BaseRN=${COMPARE_BASERN}; BaseN=${COMPARE_BASEN}; comparisons=True" topo/tests/reference/lissom_or_reference.ty 

or_comparisons:
	./topographica -c "from topo.tests.test_script import run_multiple_density_comparisons;nerr=run_multiple_density_comparisons('lissom_or_reference.ty'); import sys;sys.exit(nerr)"

# will change to use new script (+BaseRN,BaseN ignored right now)
compare_oo_or: 
	make -C topo/tests/reference/fixed_params/
	./topographica -c "BaseRN=${COMPARE_BASERN}; BaseN=${COMPARE_BASEN}; comparisons=True" topo/tests/reference/fixed_params/lissom_oo_or_reference_fixed.ty 

oo_or_comparisons:
	./topographica -c "from topo.tests.test_script import run_multiple_density_comparisons;nerr=run_multiple_density_comparisons('lissom_oo_or_reference.ty'); import sys;sys.exit(nerr)"


# Test that the specified scripts haven't changed in results or speed.
#SCRIPTS=^cfsom_or.ty ^lissom_oo_or.ty ^som_retinotopy.ty
# ^lissom_or_noshrinking.ty  - only matches to 4 dp with IMPORT_WEAVE=0 
SCRIPTS= ^cfsom_or.ty ^hierarchical.ty ^lissom_or.ty ^lissom_oo_or.ty ^lissom_oo_or_dy.ty ^lissom_oo_od.ty ^lissom_photo_or.ty ^som_retinotopy.ty ^sullivan_neurocomputing04.ty ^sullivan_nn06.ty

TRAINSCRIPTS=${SCRIPTS}
TRAINDATA =${subst ^,topo/tests/,${subst .ty,.ty_DATA,${TRAINSCRIPTS}}}
TRAINTESTS=${subst ^,topo/tests/,${subst .ty,.ty_TEST,${TRAINSCRIPTS}}}

SPEEDSCRIPTS=${SCRIPTS}
SPEEDDATA =${subst ^,topo/tests/,${subst .ty,.ty_SPEEDDATA,${SPEEDSCRIPTS}}}
SPEEDTESTS=${subst ^,topo/tests/,${subst .ty,.ty_SPEEDTEST,${SPEEDSCRIPTS}}}

STARTUPSPEEDSCRIPTS= ^lissom_oo_or.ty ^lissom_or.ty  
STARTUPSPEEDDATA =${subst ^,topo/tests/,${subst .ty,.ty_STARTUPSPEEDDATA,${STARTUPSPEEDSCRIPTS}}}
STARTUPSPEEDTESTS=${subst ^,topo/tests/,${subst .ty,.ty_STARTUPSPEEDTEST,${STARTUPSPEEDSCRIPTS}}}


# CB: when changing the various targets, don't forget about buildbot. 

train-tests: ${TRAINTESTS}
speed-tests: ${SPEEDTESTS}
startup-speed-tests: ${STARTUPSPEEDTESTS}

all-speed-tests: speed-tests startup-speed-tests

snapshot-compatibility-tests: 
	./topographica -c "from topo.commands.basic import load_snapshot; load_snapshot('topo/tests/lissom_oo_or.ty_pickle_test.typ')" -c "topo.sim.run(1)"


# Test that simulations give the same results whether run straight
# through or run part way, saved, reloaded, and run on to the same
# point.
# CEBALERT: please make this work for som_retinotopy as well as lissom_oo_or
simulation-snapshot-tests:
	./topographica -c 'from topo.tests.test_script import compare_with_and_without_snapshot_NoSnapshot as A; A(script="examples/lissom_oo_or.ty")'
	./topographica -c 'from topo.tests.test_script import compare_with_and_without_snapshot_CreateSnapshot as B; B(script="examples/lissom_oo_or.ty")'
	./topographica -c 'from topo.tests.test_script import compare_with_and_without_snapshot_LoadSnapshot as C; C(script="examples/lissom_oo_or.ty")'
	rm -f examples/lissom_oo_or.ty_PICKLETEST*


snapshot-tests: simulation-snapshot-tests snapshot-compatibility-tests

print-info:
	@echo Running at ${shell date +%s}
	@echo svnversion ${shell svnversion}

# CB: snapshot-tests is not part of slow-tests for the moment
# (until slow-tests split up on buildbot).
slow-tests: print-info train-tests all-speed-tests 
#snapshot-tests 

# CB: add notes somewhere about...
# - making sure weave compilation has already occurred before running speed tests
# - when to delete data files (i.e. when to generate new data)

# General rules for generating test data and running the tests
%_DATA:
	./topographica -c 'from topo.tests.test_script import GenerateData; GenerateData(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_DATA",density=8,run_for=[1,99,150])'

%_TEST: %_DATA
	time ./topographica -c 'import_weave=${IMPORT_WEAVE}' -c 'from topo.tests.test_script import TestScript; TestScript(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_DATA",decimal=${TESTDP})'
# CB: Beyond 14 dp, the results of the current tests do not match on ppc64 and i686 (using linux).
# In the future, decimal=14 might have to be reduced (if the tests change, or to accommodate other
# processors/platforms).


v_lissom:
	make -C topo/tests/reference/	
	time ./topographica -c "profiling=True;iterations=20000" topo/tests/reference/lissom_oo_or_reference.ty


%_SPEEDDATA:
	time ./topographica -c 'from topo.tests.test_script import generate_speed_data; generate_speed_data(script="examples/${notdir $*}",iterations=250,data_filename="topo/tests/${notdir $*}_SPEEDDATA")'

%_SPEEDTEST: %_SPEEDDATA
	time ./topographica -c 'from topo.tests.test_script import compare_speed_data; compare_speed_data(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_SPEEDDATA")'


%_STARTUPSPEEDDATA:
	time ./topographica -c 'from topo.tests.test_script import generate_startup_speed_data; generate_startup_speed_data(script="examples/${notdir $*}",density=48,data_filename="topo/tests/${notdir $*}_STARTUPSPEEDDATA")'

%_STARTUPSPEEDTEST: %_STARTUPSPEEDDATA
	time ./topographica -c 'from topo.tests.test_script import compare_startup_speed_data; compare_startup_speed_data(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_STARTUPSPEEDDATA")'

.SECONDARY: ${SPEEDDATA} ${TRAINDATA} ${STARTUPSPEEDDATA} # Make sure that *_*DATA is kept around




gui-tests: basic-gui-tests detailed-gui-tests

basic-gui-tests:
	./topographica -g -c "from topo.tests.gui_tests import run_basic; nerr=run_basic(); import sys; sys.exit(nerr)"

detailed-gui-tests:
	./topographica -g -c "from topo.tests.gui_tests import run_detailed; nerr=run_detailed(); import sys; sys.exit(nerr)"


clean-compiled: clean-weave clean-pyc

clean-weave:
	rm -rf ~/.python2*_compiled/ | cat

clean-pyc:
	rm -f topo/*.pyc topo/*/*.pyc topo/*/*/*.pyc examples/*.pyc

clean-doc:
	make -C doc clean

reference-manual: 
	make -C doc reference-manual

doc: FORCE
	make -C doc/



#############################################################################
# For maintainer only; be careful with these commands

## Subversion-only code release, without making new binaries
## Run these from a relatively clean copy of the topographica directory 
## (without stray files, especially in doc/).

svn-release: LATEST_STABLE sf-web-site

# Update any topographica-win files that keep track of the version number
# CEBALERT: maintainer must have checked out topographica-win
new-version: FORCE
	mv topographica-win/create_installer/topographica.iss topographica-win/create_installer/topographica.iss~
	sed -e 's/AppVerName=Topographica.*/AppVerName=Topographica '"${RELEASE}"'/g' topographica-win/create_installer/topographica.iss~ > topographica-win/create_installer/topographica.iss
	mv topographica-win/common/setup.py topographica-win/common/setup.py~
	sed -e "s/topo.release='.*'/topo.release='${RELEASE}'"'/g' topographica-win/common/setup.py~ > topographica-win/common/setup.py


# Make a new LATEST_STABLE on the web, using the currently checked-out version
TOPOROOT=https://topographica.svn.sourceforge.net/svnroot/topographica
LATEST_STABLE:
	svn delete -m "Updating LATEST_STABLE."  $TOPOROOT/tags/LATEST_STABLE
	svn copy $TOPOROOT/trunk $TOPOROOT/tags/LATEST_STABLE -m "Updating LATEST_STABLE."


# Update Topographica.org web site
sf-web-site: reference-manual doc
	rsync -v -arHz -e ssh doc/. topographica.sf.net:/home/groups/t/to/topographica/htdocs/.


# Clear out everything not intended for the public distribution
#
# This is ordinarily commented out in the SVN version for safety, 
# but it is enabled when the distribution directory is created.
#
#@@distclean: FORCE clean
#@@	   ${RM} .#* */.#* */*/.#* */*~ .cvsignore ChangeLog.txt */.cvsignore */*/.cvsignore */*/*/.cvsignore
#@@	   ${RM} etc/topographica.elc ImageSaver*.ppm countalerts* annotate.out emacslog
#@@	   ${RM} current_profile ./topo/tests/testsnapshot.typ script ./topo/tests/*.ty_*DATA timing* ./topo/tests/testplotfilesaver*.png
#@@	   ${RM} examples/disparity_energy.ty
#@@	   ${RM} examples/face_space.ty
#@@	   ${RM} examples/goodhill_network90.ty
#@@	   ${RM} examples/homeostatic.ty
#@@	   ${RM} examples/joublin_bc96.ty
#@@	   ${RM} examples/laminar.ty
#@@	   ${RM} examples/laminar_or.ty
#@@	   ${RM} examples/laminar_lissom.ty
#@@	   ${RM} examples/laminar_nolearning.ty
#@@	   ${RM} examples/laminar_oo_or.ty*
#@@	   ${RM} examples/leaky_lissom_or.ty
#@@	   ${RM} examples/lgn_lateral.ty*
#@@	   ${RM} examples/lissom_oo_od.ty
#@@	   ${RM} examples/lissom_oo_or_dy_photo.ty
#@@	   ${RM} examples/lissom_oo_or_homeomaxent.ty
#@@	   ${RM} examples/lissom_oo_or_noshrinking_adapthomeo.ty
#@@	   ${RM} examples/lissom_oo_or_noshrinking_latswitch.ty
#@@	   ${RM} examples/lissom_or_homeomaxent.ty
#@@	   ${RM} examples/lissom_or_homeoscale.ty
#@@	   ${RM} examples/lissom_or_noshrinking.ty
#@@	   ${RM} examples/lissom_or_noshrinking_latswitch.ty
#@@	   ${RM} examples/lissom_or_sf.ty
#@@	   ${RM} examples/ohzawa_science90.ty
#@@	   ${RM} examples/saccade_demo.ty
#@@	   ${RM} examples/sullivan_neurocomputing04.ty
#@@	   ${RM} examples/sullivan_nn06.ty
#@@	   ${RM} examples/*.typ
#@@	   ${RM} -r Output
#@@	   ${RM} -r images
#@@	   ${RM} -r topographica-win
#@@	   ${RM} -r tmp/
#@@	   ${RM} -r .svn */.svn */*/.svn */*/*/.svn
#@@	   ${CD} topo/tests/reference ; make clean

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



