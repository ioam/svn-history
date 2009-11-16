# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --rcfile=doc/buildbot/pylintrc

PYCHECKER = bin/pychecker --config doc/buildbot/pycheckrc

RELEASE = 0.9.6

TEST_VERBOSITY = 1

# currently only applied to train-tests 
IMPORT_WEAVE = 1

# no. of decimal places to require for verifying a match in slow-tests
# (must match across platforms & for optimized vs unoptimized)
TESTDP = 7

# CEBALERT: tied to exact windows version!
ifeq ("$(shell uname -s)","MINGW32_NT-5.1")
	TIMER = 
else
	TIMER = time 
endif

XVFB = ${shell which xvfb-run}

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
default: win-msys-patch ext-packages topographica

all: default reference-manual doc tests examples 

clean: clean-doc clean-ext-packages clean-compiled 
	${RM} .??*~ *~ */*~ */.??*~ */*/*~ */*/.??*~ */*/*/*~ */*/*/.??*~ *.bak
	${RM} .#??*.* */.#??*.* */*/.#??*.* */*/*/.#??*.* current_profile ./topo/tests/testsnapshot.typ ./topo/tests/testplotfilesaver*.png
	${RM} -r bin include share lib man topographica ImageSaver*.jpeg python_topo

uninstall:
	make -C external uninstall


# Windows: to build topographica using msys, having already installed
# binary python, pil, jpeg
win-msys-patch:
ifeq ("$(shell uname -s)","MINGW32_NT-5.1")
	mkdir -p bin
	ln -f -s /c/Python25/python.exe bin/python
## prerequisites
	touch external/tcl external/tk external/blt external/python external/pil external/jpeg
## needed during the build process
# CEBALERT: shouldn't be required; why can't I get this to work as an
# option to setup.py? Use site.cfg?
	echo "[build]" > /c/Python25/Lib/distutils/distutils.cfg
	echo "compiler = mingw32" >> /c/Python25/Lib/distutils/distutils.cfg
## topographica.pth for Python to locate Topographica 
# CEBALERT: means there can only be one copy of Topographica on
# Windows.  Can't the topographica script modify sys.path at startup?
# Still, we'd need a way to have this work during the build process,
# too.

	bin/python external/msys_path.py /c/Python25/Lib/site-packages/topographica.pth ${PREFIX}/lib ${PREFIX}/lib/site-packages
	patch --force external/Makefile external/Makefile_win_msys.diff
	touch win-msys-patch
endif



win-msys-patch-uninstall:
	patch --force --reverse external/Makefile external/Makefile_win_msys.diff
	${RM} win-msys-patch
	${RM} /c/Python25/Lib/distutils.cfg
	${RM} /c/Python25/Lib/site-packages/topographica.pth
# CEBALERT: incomplete


# Mac OS X: to build python with X11 Tkinter
#osx-x11-patch: 
#	patch --force external/Makefile external/Makefile_OSX_X11.diff
#	touch osx-x11-patch

#osx-x11-patch-uninstall:
#	patch --force --reverse external/Makefile external/Makefile_OSX_X11.diff
#	${RM} osx-x11-patch


saved-examples: 
	make -C examples saved-examples


FORCE:

# To get more information about which tests are being run, do:
# make TEST_VERBOSITY=2 tests
tests: FORCE
	${XVFB} ./topographica -c "import topo.tests; t=topo.tests.run(verbosity=${TEST_VERBOSITY}); import sys; sys.exit(len(t.failures+t.errors))"

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

# CB: experimental
topographicagui: 
	echo "import topo.tkgui;topo.tkgui.start(mainloop=False)" > _gui.py
	echo "${PREFIX}bin/idle -n -t 'Topographica shell' -r _gui.py" > topographicagui
	echo "" >> topographicagui
	chmod a+x ${PREFIX}topographicagui


check:
	${PYCHECKER} topo/*.py topo/*/*.py

check-base:
	${PYCHECKER} topo/base/*.py 

lint:
	${PYLINT} topo

lint-base:
	${PYLINT} topo.base


# Compare topographica and C++ lissom output
or_comparisons:
	./topographica -c "from topo.tests.test_script import run_multiple_density_comparisons;nerr=run_multiple_density_comparisons('lissom_or_reference.ty'); import sys;sys.exit(nerr)"

oo_or_comparisons:
	./topographica -c "from topo.tests.test_script import run_multiple_density_comparisons;nerr=run_multiple_density_comparisons('lissom_oo_or_reference.ty'); import sys;sys.exit(nerr)"


# Test that the specified scripts haven't changed in results or speed.
#SCRIPTS=^lissom_oo_or.ty ^som_retinotopy.ty
SCRIPTS= ^hierarchical.ty ^lissom_or.ty ^lissom_oo_or.ty ^som_retinotopy.ty ^sullivan_neurocomputing04.ty ^lissom.ty ^lissom_fsa.ty ^gca_lissom.ty #^lissom_whisker_barrels.ty
# CEB: tests on these scripts temporarily suspended (SF.net #2053538)
# ^lissom_oo_or_homeostatic.ty ^lissom_oo_or_homeostatic_tracked.ty
# ^lissom_or_noshrinking.ty  - only matches to 4 dp with IMPORT_WEAVE=0 

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
	./topographica -c "from topo.command.basic import load_snapshot; load_snapshot('topo/tests/lissom_oo_or.ty_pickle_test.typ')" -c "topo.sim.run(1)"


# Test that simulations give the same results whether run straight
# through or run part way, saved, reloaded, and run on to the same
# point.
# CEBALERT: please make this work for som_retinotopy as well as lissom_oo_or
simulation-snapshot-tests:
	./topographica -c 'from topo.tests.test_script import compare_with_and_without_snapshot_NoSnapshot as A; A(script="examples/lissom_oo_or.ty")'
	./topographica -c 'from topo.tests.test_script import compare_with_and_without_snapshot_CreateSnapshot as B; B(script="examples/lissom_oo_or.ty")'
	./topographica -c 'from topo.tests.test_script import compare_with_and_without_snapshot_LoadSnapshot as C; C(script="examples/lissom_oo_or.ty")'
	rm -f examples/lissom_oo_or.ty_PICKLETEST*


snapshot-tests: simulation-snapshot-tests snapshot-compatibility-tests script-repr-tests

print-info:
	@echo Running at ${shell date +%s}
	@echo svnversion ${shell svnversion}

# CB: snapshot-tests is not part of slow-tests for the moment
# (until slow-tests split up on buildbot).
slow-tests: print-info train-tests all-speed-tests map-tests
#snapshot-tests 

# CB: add notes somewhere about...
# - making sure weave compilation has already occurred before running speed tests
# - when to delete data files (i.e. when to generate new data)

# General rules for generating test data and running the tests
%_DATA:
	./topographica -c 'from topo.tests.test_script import generate_data; generate_data(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_DATA",run_for=[1,99,150],look_at="V1",cortex_density=8,retina_density=24,lgn_density=24)'

%_TEST: %_DATA
	${TIMER}./topographica -c 'import_weave=${IMPORT_WEAVE}' -c 'from topo.tests.test_script import TestScript; TestScript(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_DATA",decimal=${TESTDP})'
# CB: Beyond 14 dp, the results of the current tests do not match on
# ppc64 and i686 (using linux).  In the future, decimal=14 might have
# to be reduced (if the tests change, or to accommodate other
# processors/platforms).

v_lissom:
	make -C topo/tests/reference/	
	${TIMER}./topographica -c "profiling=True;iterations=20000" topo/tests/reference/lissom_oo_or_reference.ty


%_SPEEDDATA:
	${TIMER}./topographica -c 'from topo.tests.test_script import generate_speed_data; generate_speed_data(script="examples/${notdir $*}",iterations=250,data_filename="topo/tests/${notdir $*}_SPEEDDATA")'

%_SPEEDTEST: %_SPEEDDATA
	${TIMER}./topographica -c 'from topo.tests.test_script import compare_speed_data; compare_speed_data(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_SPEEDDATA")'


%_STARTUPSPEEDDATA:
	${TIMER}./topographica -c 'from topo.tests.test_script import generate_startup_speed_data; generate_startup_speed_data(script="examples/${notdir $*}",density=48,data_filename="topo/tests/${notdir $*}_STARTUPSPEEDDATA")'

%_STARTUPSPEEDTEST: %_STARTUPSPEEDDATA
	${TIMER}./topographica -c 'from topo.tests.test_script import compare_startup_speed_data; compare_startup_speed_data(script="examples/${notdir $*}",data_filename="topo/tests/${notdir $*}_STARTUPSPEEDDATA")'

.SECONDARY: ${SPEEDDATA} ${TRAINDATA} ${STARTUPSPEEDDATA} # Make sure that *_*DATA is kept around


# Special versions for specific scripts:
topo/tests/lissom.ty_DATA:
	./topographica -c 'from topo.tests.test_script import generate_data; generate_data(script="examples/lissom.ty",data_filename="topo/tests/lissom.ty_DATA",run_for=[1,99,150],look_at="V1",cortex_density=8,retina_density=6,lgn_density=6,dims=["or","od","dr","dy","cr","sf"])'

topo/tests/lissom.ty_SPEEDDATA:
	./topographica -c 'from topo.tests.test_script import generate_speed_data; generate_speed_data(script="examples/lissom.ty",data_filename="topo/tests/lissom.ty_SPEEDDATA",iterations=250,cortex_density=8,retina_density=6,lgn_density=6,dims=["or","od","dr","dy","cr","sf"])'

topo/tests/lissom_fsa.ty_DATA:
	./topographica -c 'from topo.tests.test_script import generate_data; generate_data(script="examples/lissom_fsa.ty",data_filename="topo/tests/lissom_fsa.ty_DATA",run_for=[1,99,150],look_at="FSA",cortex_density=8,retina_density=24,lgn_density=24)'

topo/tests/lissom_whisker_barrels.ty_DATA:
	./topographica -c 'from topo.tests.test_script import generate_data; generate_data(script="examples/lissom_whisker_barrels.ty",data_filename="topo/tests/lissom_whisker_barrels.ty_DATA",run_for=[1,99,150],look_at="S1")'



# pass a list of plotgroup names to test() instead of plotgroups_to_test to restrict the tests
map-tests:
	./topographica -c "cortex_density=8" examples/lissom_oo_or.ty -c "topo.sim.run(100);from topo.tests.test_map_measurement import *; test(plotgroups_to_test)" 

generate-map-tests-data:
	./topographica -c "cortex_density=8" examples/lissom_oo_or.ty -c "topo.sim.run(100);from topo.tests.test_map_measurement import *; generate(plotgroups_to_test)" 

script-repr-tests:
	./topographica examples/hierarchical.ty -a -c "save_script_repr('topo/tests/script_repr_test.ty')"
	./topographica topo/tests/script_repr_test.ty
	rm topo/tests/script_repr_test.ty

gui-tests: basic-gui-tests detailed-gui-tests

basic-gui-tests:
	${XVFB} ./topographica -g -c "from topo.tests.gui_tests import run_basic; nerr=run_basic(); topo.guimain.quit_topographica(check=False,exit_status=nerr)"

detailed-gui-tests:
	${XVFB} ./topographica -g -c "from topo.tests.gui_tests import run_detailed; nerr=run_detailed(); topo.guimain.quit_topographica(check=False,exit_status=nerr)"


clean-compiled: clean-weave clean-pyc

clean-weave:
	rm -rf ~/.python2*_compiled/ | cat

clean-pyc:
	rm -f *.pyc param/*.pyc topo/*.pyc topo/*/*.pyc topo/*/*/*.pyc examples/*.pyc contrib/*.pyc

clean-doc:
	make -C doc clean

reference-manual: 
	make -C doc reference-manual

doc: FORCE
	make -C doc/


# CB: work in progress (to be run on windows, for creating exe)
build-win-exe: topographica
	bin/python win_build_exe.py py2exe

#############################################################################
# For maintainer only; be careful with these commands

## Subversion-only code release, without making new binaries
## Run these from a relatively clean copy of the topographica directory 
## (without stray files, especially in doc/).

svn-release: LATEST_STABLE tag-release sf-web-site 

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
	svn copy ${TOPOROOT}/trunk ${TOPOROOT}/tags/LATEST_STABLE -m "Update LATEST_STABLE."

tag-release: 
	svn copy ${TOPOROOT}/trunk ${TOPOROOT}/releases/${RELEASE} -m "Create release ${RELEASE}"

# Update Topographica.org web site
sf-web-site: reference-manual doc
	rsync -v -arHz --rsh=ssh doc/. web.sf.net:/home/groups/t/to/topographica/htdocs/.


SCRIPTS_TO_KEEP_IN_DIST= ^goodhill_network90.ty ^hierarchical.ty ^leaky_lissom_or.ty ^lissom_fsa.ty ^lissom_oo_or.ty ^lissom_or_movie.ty ^lissom_or.ty ^lissom.ty ^lissom_whisker_barrels.ty ^obermayer_pnas90.ty ^som_retinotopy.ty ^sullivan_neurocomputing04.ty ^tiny.ty ^gca_lissom.ty


# Clear out everything not intended for the public distribution
#
# This is ordinarily commented out in the SVN version for safety, 
# but it is enabled when the distribution directory is created.
#
#@@distclean: FORCE clean
#@@	   ${RM} .#* */.#* */*/.#* */*~ 
#@@	   ${RM} etc/topographica.elc ImageSaver*.ppm countalerts* annotate.out emacslog
#@@	   ${RM} current_profile ./topo/tests/testsnapshot.typ script ./topo/tests/*.ty_*DATA timing* ./topo/tests/testplotfilesaver*.png
#@@	   ${RM} examples/*.typ
#@@	   ${RM} -r Output
#@@	   -mv images/ellen_arthur.pgm ./TMPellen_arthur.pgm
#@@	   ${RM} -r images
#@@	   ${RM} -r info
#@@	   mkdir images; mv ./TMPellen_arthur.pgm images/ellen_arthur.pgm
#@@	   ${RM} -r setup.py setup_ez.py setup_app.py setup_exe.py _setup.py
#@@	   ${RM} -r tmp/
#@@	   ${RM} -r contrib/
#@@	   ${RM} -r .svn */.svn */*/.svn */*/*/.svn */*/*/*/.svn
#@@	   ${CD} topo/tests/reference ; make clean
#@@	   ${RM} -r doc/buildbot/
#@@	   ${RM} -r debian/
#@@	   find examples/*.ty -maxdepth 1 ${subst ^,! -name ,${SCRIPTS_TO_KEEP_IN_DIST}} -exec rm {} \;
#@@ifeq ("$(shell uname -s)","MINGW32_NT-5.1")
#@@else
#@@	   	${RM} -r topographica-win 
#@@endif

# need to make sure python_topo isn't cleaned away on Windows
win-distclean:
	-mv python_topo TMPpython_topo
	make distclean
	mv TMPpython_topo python_topo


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

# CEBALERT: should make this use different path? Or sneakily combine
# with dist somehow? Tradeoff: avoiding interference/surprise vs
# saving time and hard disks...
#
# Create public distribution suitable for python setup.py install, as
# well as examples and doc archives
dist-setup.py: doc distdir reference-manual FORCE
# clean dir but keep setup.py-related files
	${CD} ${DIST_DIR}; ${MV} setup.py TMPsetup.py
	${CD} ${DIST_DIR}; ${MV} _setup.py TMP_setup.py
	${CD} ${DIST_DIR}; make distclean
	${CD} ${DIST_DIR}; ${MV} TMPsetup.py setup.py
	${CD} ${DIST_DIR}; ${MV} TMP_setup.py _setup.py
# won't need to build this copy
	${RM} ${DIST_DIR}/Makefile 
	${RM} -r ${DIST_DIR}/external
# create archives
	${CD} ${DIST_TMPDIR} ; ${MAKE_ARCHIVE} ${DIST_DIRNAME} | ${COMPRESS_ARCHIVE} > ${DIST_ARCHIVE}


# Note that the output needs to be appended to a copy of the old file,
# to keep old fixes to formatting. The 9000:HEAD can be omitted to get
# the full list, but this is faster.
ChangeLog.txt: FORCE
	make -C external svn2cl
	external/svn2cl -r HEAD:9000 --include-rev --group-by-day --separate-daylogs --break-before-msg --stdout https://topographica.svn.sourceforge.net/svnroot/topographica/ | sed -e 's|/trunk/topographica/||g' > ChangeLog.txt



# CREATING .DEB FOR UBUNTU
#
# https://wiki.ubuntu.com/PackagingGuide/Complete
#
# - need to add steps at beginning to get suitable dir
# - need to change upload location to a topographica ppa
# - need to add .desktop
#
# $ export DEBFULLNAME='C. E. Ball'
# $ export DEBEMAIL='ceball@gmail.com'
# set up GPG key, sign various ubuntu agreements on launchpad, ...
# $ export GPGKEY=4275E3C7
#
# ceball@fiver:~/working/topographica3$ make dist-setup.py
#
# ceball@fiver:~/pkg$ ls
# topographica-0.9.6  topographica_0.9.6.orig.tar.gz
#
# ceball@fiver:~/pkg/topographica-0.9.6$ ls
# ChangeLog.txt  debian  images      _setup.py  topo
# COPYING.txt    etc     README.txt  setup.py   topographica
#
# ceball@fiver:~/pkg/topographica-0.9.6$ ls debian/
# changelog  python-scrodget.debhelper.log
# compat     python-scrodget.postinst.debhelper
# control    python-scrodget.preinst.debhelper
# copyright  python-scrodget.prerm.debhelper
# docs       python-scrodget.substvars
# pycompat   rules
# 
#
# ceball@fiver:~/pkg/topographica-0.9.6$ dch -i
#
# ceball@fiver:~/pkg/topographica-0.9.6$ debuild -S -sa
#
# * Test it builds
# 
# Not sure, something like this...
# set up (first time only):
# $ sudo pbuilder create --distribution jaunty  
# then for testing:
# $ sudo pbuilder build topographica_0.9.6-0ubuntu2.dsc
#
#
# * Upload to PPA
# 
# ceball@fiver:~/pkg$ dput ppa:ceball/ppa topographica_0.9.6-0ubuntu3_source.changes



# .deb of svn 
# 
# ceball@fiver:~/working/topographica3$ nice make dist-setup.py
# ceball@fiver:~/working/topographica3$ cd ../distributions/
# ceball@fiver:~/working/distributions$ ls
# topographica-0.9.6  topographica-0.9.6.tar.gz
# ceball@fiver:~/working/distributions$ mv topographica-0.9.6.tar.gz topographica_0.9.6+r10621.orig.tar.gz 
# ceball@fiver:~/working/distributions$ mv topographica-0.9.6/ topographica-0.9.6+r10621
# ceball@fiver:~/working/distributions$ cp -R ../topographica3/debian topographica-0.9.6+r10621/debian
# ceball@fiver:~/working/distributions$ rm -rf topographica-0.9.6+r10621/debian/.svn
# ceball@fiver:~/working/distributions$ cd topographica-0.9.6+r10621/
# use ~rXXXXX to indicate pre e.g. 0.9.7~r10600; then skip rm debian/changelog and dch --create
# ceball@fiver:~/working/distributions/topographica-0.9.6+r10621$ rm debian/changelog
# ceball@fiver:~/working/distributions/topographica-0.9.6+r10621$ dch --create
# ceball@fiver:~/working/distributions/topographica-0.9.6+r10621$ dch -i
# ceball@fiver:~/working/distributions/topographica-0.9.6+r10621$ debuild -S -sa
# ceball@fiver:~/working/distributions$ ls
# topographica-0.9.6+r10621
# topographica_0.9.6+r10621-0ubuntu1.diff.gz
# topographica_0.9.6+r10621-0ubuntu1.dsc
# topographica_0.9.6+r10621-0ubuntu1_source.build
# topographica_0.9.6+r10621-0ubuntu1_source.changes
# topographica_0.9.6+r10621.orig.tar.gz
# ceball@fiver:~/working/distributions$ sudo pbuilder build topographica_0.9.6+r10621-0ubuntu1.dsc 
# ceball@fiver:~/working/distributions$ dput ppa:ceball/ppa topographica_0.9.6+r10621-0ubuntu1_source.changes

# after debuild to get deb, can get rpm by doing 
# $ sudo alien -r topographica_0.9.6+r10624-0ubuntu1_all.deb
