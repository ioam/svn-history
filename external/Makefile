PREFIX = ${dir ${CURDIR}}
CC = gcc

# Options to pass to all setup.py install commands.
# (Allows us to control installation location even when not using our
# own Python, e.g. on Windows.)
PYSETUP_OPT = --prefix=${PREFIX}

default: platform-skip python jpeg pil numpy matplotlib weave fixedpoint pychecker common pylint epydoc docutils gnosis ipython gmpy scrodget tooltip

# uses touch -a to avoid changing modification dates
platform-skip:
# avoid building blt, tcl, and tk on OS X
ifeq ("$(shell uname -s)","Darwin")
	touch -a blt
	touch -a tcl
	touch -a tk
endif
ifeq ("$(shell uname -s)","MINGW32_NT-5.1")
	touch -a blt
	touch -a tcl
	touch -a tk
	touch -a python
	touch -a jpeg
	touch -a pil
endif


all: default pyaudiolab mlabwrap scipy ipython pyrex pytables psyco gnuplotpy

dist: bluesphere

clean: python-clean jpeg-clean pil-clean numpy-clean tk-clean tcl-clean matplotlib-clean weave-clean fixedpoint-clean pychecker-clean common-clean pylint-clean epydoc-clean docutils-clean gnosis-clean scipy-clean mlabwrap-clean ipython-clean libsndfile-clean pyaudiolab-clean psyco-clean pyrex-clean hdf5-clean pytables-clean gnuplotpy-clean bluesphere-clean player-clean progressbar-clean stage-clean gmp-clean mxnumber-clean gmpy-clean scrodget-clean tooltip-clean snit-clean svn2cl-clean readline-clean termcap-clean guppy-clean ipythontk-clean

uninstall: python-uninstall jpeg-uninstall pil-uninstall numpy-uninstall tk-uninstall tcl-uninstall matplotlib-uninstall fixedpoint-uninstall weave-uninstall pychecker-uninstall common-uninstall pylint-uninstall epydoc-uninstall docutils-uninstall gnosis-uninstall scipy-uninstall mlabwrap-uninstall ipython-uninstall libsndfile-uninstall pyaudiolab-uninstall psyco-uninstall pyrex-uninstall hdf5-uninstall pytables-uninstall gnuplotpy-uninstall player-uninstall progressbar-uninstall stage-uninstall gmp-uninstall mxnumber-uninstall gmpy-uninstall scrodget-uninstall tooltip-uninstall snit-uninstall svn2cl-uninstall readline-uninstall termcap-uninstall guppy-uninstall ipythontk-clean



##############################################################
# libblt: already available on nearly all systems, but some systems
# have a version incompatible with tkinter (and Tcl/Tk?), so we build
# our own version. If there are any problems building this, just do
# 'make blt-uninstall' followed by 'touch blt' (or remove python's blt
# dependency below), and it should still nearly always be fine.
#
BLT = blt2.4z
BLT_UNINSTALL += lib/libBLT24.so

blt: ${BLT}.tar.gz
	tar xzf ${BLT}.tar.gz
	cd ${BLT}; ./configure --prefix=${PREFIX}
	make -i -C ${BLT} install
	touch blt

blt-clean:
	rm -rf ${BLT}
blt-uninstall:
	rm -rf blt ${foreach f,${BLT_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# Python (interpreted language)
#
PYTHON = Python-2.5.1

PYTHON_LIB  = lib/python2.5
PYTHON_INC  = include/python2.5
PYTHON_CONF = lib/python2.5/config

PYTHON_UNINSTALL += bin/idle bin/python bin/pydoc bin/python2.5 
PYTHON_UNINSTALL += ${PYTHON_LIB} man/man1/python.1 include/python2.5


# LDFLAGS sets ${PREFIX}/lib as the LD_LIBRARY in the binary
# CB: rpath is ignored on OS X (so where are the library files taken from?). 
python: ${PYTHON}.tgz tk blt readline
	echo ${PREFIX}
	tar -xzf ${PYTHON}.tgz
# 32-bit/64-bit snapshot patch: topo SF.net #2119256
	patch -p0 < Python_64bit_pickle.diff
# Tkinter: support None in BooleanVar
	patch -p0 < Tkinter_bool_none.diff
# IDLE: work with tk 8.5 (see http://bugs.python.org/issue2693).
	patch -p0 < idle_tk8.5.patch
# Configure for specific operating system versions
ifeq ("$(shell uname -s)","Darwin")
	patch -p0 < Python_OSX_tk.diff # build python with tcl/tk from /Library/Frameworks
ifeq ("$(shell uname -r | cut -d . -f 1)","9") # Darwin 9.x == Mac OS X 10.5 (Leopard)
	cd ${PYTHON}; ./configure --prefix=${PREFIX} MACOSX_DEPLOYMENT_TARGET=10.5
else
	cd ${PYTHON}; ./configure --prefix=${PREFIX}
endif
else
	cd ${PYTHON}; ./configure --prefix=${PREFIX} LDFLAGS=-Wl,-rpath,${PREFIX}/lib
endif
	cd ${PYTHON}; env PREFIX=${PREFIX} make EXTRA_CFLAGS=-I${PREFIX}/include
	cd ${PYTHON}; env PREFIX=${PREFIX} make install
	touch python

python-clean: blt-clean
	rm -rf ${PYTHON} Python-2.4*/

python-uninstall: blt-uninstall
	rm -rf python ${foreach f,${PYTHON_UNINSTALL}, ${PREFIX}/${f}} Python-2.4*/

##############################################################
# Tcl (required by Tk GUI toolkit)
#
TCL = tcl8.5.5
TCL_UNINSTALL += bin/tclsh8.5 bin/wish8.5 lib/tclConfig.sh
TCL_UNINSTALL += lib/tcl8.5 lib.tclConfig.sh lib/libtcl8.5.so lib/libtclstub8.5.a
TCL_UNINSTALL += include/tcl*.h man/man*

tcl: ${TCL}-src.tar.gz
	tar -xzf ${TCL}-src.tar.gz
	cd ${TCL}/unix; ./configure --prefix=${PREFIX}
	make -C ${TCL}/unix install
	touch tcl

tcl-clean:
	rm -rf ${TCL} tcl8*/
tcl-uninstall:
	rm -rf tcl ${foreach f,${TCL_UNINSTALL}, ${PREFIX}/${f}} tcl8*/



##############################################################
# Tk (GUI toolkit)
#
TK = tk8.5.5

TK_UNINSTALL += lib/tk8.5 lib/libtk8.5.so lib/libtkstub8.5.a
TK_UNINSTALL += include/tk*.h lib/tkConfig.sh

tk: ${TK}-src.tar.gz tcl
	tar -xzf ${TK}-src.tar.gz
	cd ${TK}/unix; ./configure --prefix=${PREFIX} --enable-xft
	make -C ${TK}/unix install
	touch tk

tk-clean:
	rm -rf ${TK} tk8*/
tk-uninstall:
	rm -rf tk ${foreach f,${TK_UNINSTALL}, ${PREFIX}/${f}} tk8*/



##############################################################
# ipython (improved interactive prompt)
#
IPYTHON = ipython-0.8.4
IPYTHON_UNINSTALL =  ${PYTHON_LIB}/site-packages/IPython

ipython: ${IPYTHON}.tar.gz python 
	tar -xzf ${IPYTHON}.tar.gz
	cd ${IPYTHON}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch ipython

ipython-clean:
	rm -rf ${IPYTHON} 
ipython-uninstall:
	rm -rf ipython ${IPYTHON} $(foreach f, ${IPYTHON_UNINSTALL}, ${PREFIX}/${f})




#############################################################
# jpeg (JPEG image library)

JPEG = jpeg-6b

JPEG_UNINSTALL += bin/cjpeg bin/djpeg bin/jpegtran bin/rdjpgcom bin/wrjpgcom
JPEG_UNINSTALL += lib/libjpeg.* 
JPEG_UNINSTALL += man/man1/cjpeg.1 man/man1/djpeg.1 man/man1/jpegtran.1
JPEG_UNINSTALL += man/man1/rdjpgcom.1 man/man1/wrjpgcom.1
JPEG_UNINSTALL += include/jconfig.h include/jerror.h include/jmorecfg.h include/jpeglib.h


jpeg: ${JPEG}.tgz
	tar -xzf ${JPEG}.tgz
	cd ${JPEG}; ./configure --prefix=${PREFIX} --enable-shared --enable-static
	make -C ${JPEG}
	make -C ${JPEG} test
	make -C ${JPEG} install
	touch jpeg

jpeg-clean: 
	rm -rf ${JPEG} 
jpeg-uninstall:
	rm -rf jpeg $(foreach f, ${JPEG_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# PIL (bitmap image library)
#
PIL = Imaging-1.1.6
PIL_UNINSTALL = ${PYTHON_LIB}/site-packages/PIL

pil: ${PIL}.tgz jpeg python
	tar -xzf ${PIL}.tgz
#	cd ${PIL}/libImaging; ./configure --prefix=${PREFIX} --with-jpeg=${PREFIX}/lib
#	make -C ${PIL}/libImaging
#
# Apply OS-specific patches:
ifeq ("$(shell uname -m)","x86_64")
#       # Tell 64-bit Linux machines where to find zlib, to prevent "encoder zip not available" problems
	cd ${PIL}; patch < ../Imaging.diff
endif
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py build_ext -i
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python selftest.py
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch pil

pil-clean:
	rm -rf ${PIL} 
pil-uninstall:
	rm -rf pil $(foreach f, ${PIL_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# numpy (matrix library)
#
NUMPY = numpy-1.2.1
NUMPY_UNINSTALL =  ${PYTHON_LIB}/site-packages/numpy

numpy: ${NUMPY}.tar.gz python
	tar -xzf ${NUMPY}.tar.gz
	cd ${NUMPY}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch numpy

numpy-clean:
	rm -rf ${NUMPY} 
numpy-uninstall:
	rm -rf numpy $(foreach f, ${NUMPY_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# MatPlotLib (plotting library)
#
MATPLOTLIB = matplotlib-0.99.1.1
MATPLOTLIB_UNINSTALL =  ${PYTHON_LIB}/site-packages/matplotlib

# Workaround to allow MATPLOTLIB to compile on a remote session.
#
# Forces the DISPLAY variable to be set, if only to a guess at the
# correct value.  If DISPLAY is set incorrectly, matplotlib may not be
# able to find the right Tcl/Tk libraries.
ifeq ($(strip $(DISPLAY)),)
  MATPLOTLIB_DISPLAY="DISPLAY=:0"
else
  MATPLOTLIB_DISPLAY=
endif

matplotlib: ${MATPLOTLIB}.tar.gz python
	tar -xzf ${MATPLOTLIB}.tar.gz
# mistakenly included in matplotlib distribution?
	cd ${MATPLOTLIB}; rm setup.cfg
# otherwise can't find our tk while building tkagg
	cd ${MATPLOTLIB}; ${PREFIX}/bin/python setup.py build_ext -L${PREFIX}/lib/
	cd ${MATPLOTLIB}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${MATPLOTLIB_DISPLAY} ${PREFIX}/bin/python setup.py build
	cd ${MATPLOTLIB}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${MATPLOTLIB_DISPLAY} ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch matplotlib

matplotlib-clean:
	rm -rf ${MATPLOTLIB} matplotlib-0.90*/
matplotlib-uninstall:
	rm -rf matplotlib ${MATPLOTLIB} $(foreach f, ${MATPLOTLIB_UNINSTALL}, ${PREFIX}/${f}) matplotlib-0.90*/



##############################################################
# Weave (on its own apart from Scipy)
#
WEAVE = scipy-0.7.1
WEAVE_UNINSTALL = ${PYTHON_LIB}/site-packages/weave external/weave

# Forces removal of weave version used with Numeric
weave: ${WEAVE}.tar.gz python
	rm -rf Scipy_core-0.3.0_108.1820
	rm -f ${PYTHON_LIB}/site-packages/weave external/weave
	tar -xzf ${WEAVE}.tar.gz
# we make weave not depend on scipy
	patch -p0 < weave.diff
	cp ${WEAVE}/scipy/io/dumb_shelve.py ${WEAVE}/scipy/weave/
	cp ${WEAVE}/scipy/io/dumbdbm_patched.py ${WEAVE}/scipy/weave
	cd ${WEAVE}/scipy/weave/; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch weave

weave-clean:
	rm -rf ${WEAVE} weave-3852
weave-uninstall:
	rm -rf weave ${WEAVE} $(foreach f, ${WEAVE_UNINSTALL}, ${PREFIX}/${f}) weave-3852



##############################################################
# Scipy
#
SCIPY = scipy-0.7.1
SCIPY_UNINSTALL = ${PYTHON_LIB}/site-packages/scipy external/scipy

# Forces removal of scipy version used with Numeric
scipy: ${SCIPY}.tar.gz python
	rm -f ${PYTHON_LIB}/site-packages/scipy external/scipy
	tar -xzf ${SCIPY}.tar.gz
	cp scipy-site.cfg ${SCIPY}/site.cfg
	cd ${SCIPY}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch scipy

scipy-clean:
	rm -rf ${SCIPY} 
scipy-uninstall:
	rm -rf scipy ${SCIPY} $(foreach f, ${SCIPY_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# Fixed-Point package
#
FIXEDPT = fixedpoint-0.1.2
FIXEDPT_UNINSTALL = ${PYTHON_LIB}/site-packages

fixedpoint: ${FIXEDPT}.tgz python fixedpoint.diff fixedpoint_setup.py
	rm -rf ${FIXEDPT}
	tar -xzf ${FIXEDPT}.tgz
	mv fixedpoint ${FIXEDPT}
	cp fixedpoint.diff ${FIXEDPT}
	cp fixedpoint_setup.py ${FIXEDPT}/setup.py
	cd ${FIXEDPT}; patch < fixedpoint.diff; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch fixedpoint

fixedpoint-clean:
	rm -rf ${FIXEDPT}
fixedpoint-uninstall:
	rm -rf fixedpoint ${FIXEDPT} ${FIXEDPT_UNINSTALL}/fixedpoint.*



##############################################################
# pychecker (optional source code checker)
#
PYCHECKER = pychecker-0.8.18-CVS-200712061936
PYCHECKER_UNINSTALL = ${PYTHON_LIB}/site-packages/pychecker

pychecker: ${PYCHECKER}.tar.gz python
	tar -xzf ${PYCHECKER}.tar.gz
	cd ${PYCHECKER}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch pychecker

pychecker-clean:
	rm -rf ${PYCHECKER} 
pychecker-uninstall:
	rm -rf pychecker ${PYCHECKER} $(foreach f, ${PYCHECKER_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# logilab common files, required for pylint (but should be 
# removed if pylint is removed)
#
COMMON = logilab-common-0.41.0
COMMON_UNINSTALL = ${PYTHON_LIB}/site-packages/logilab/common

common: ${COMMON}.tar.gz python
	tar -xzf ${COMMON}.tar.gz
	cd ${COMMON}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch common

common-clean:
	rm -rf ${COMMON} 
common-uninstall:
	rm -rf common ${COMMON} $(foreach f, ${COMMON_UNINSTALL}, ${PREFIX}/${f})



################################################################
# logilab astng, required for pylint (but should be 
# removed if pylint is removed)
ASTNG = logilab-astng-0.19.0
ASTNG_UNINSTALL = ${PYTHON_LIB}/site-packages/logilab/astng

astng: ${ASTNG}.tar.gz python
	tar -xzf ${ASTNG}.tar.gz
	cd ${ASTNG}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch astng

astng-clean:
	rm -rf ${ASTNG} logilab-astng-0.*/
astng-uninstall:
	rm -rf astng ${ASTNG} $(foreach f, ${ASTNG_UNINSTALL}, ${PREFIX}/${f}) logilab-astng-0.*/



##############################################################
# pylint (optional source-code checker)
#
PYLINT = pylint-0.18.0
PYLINT_UNINSTALL = ${PYTHON_LIB}/site-packages/pylint

pylint: ${PYLINT}.tar.gz python common astng
	tar -xzf ${PYLINT}.tar.gz
	cd ${PYLINT}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch pylint

pylint-clean: astng-clean common-clean
	rm -rf ${PYLINT} pylint-0.*/
pylint-uninstall: astng-uninstall common-uninstall
	rm -rf pylint ${PYLINT} $(foreach f, ${PYLINT_UNINSTALL}, ${PREFIX}/${f}) pylint-0.*/



##############################################################
# epydoc (Automatic Reference_Manual generator)
#
EPYDOC = epydoc-3.0.1
EPYDOC_UNINSTALL = ${PYTHON_LIB}/site-packages/epydoc

epydoc: ${EPYDOC}.tar.gz python
	tar -xzf ${EPYDOC}.tar.gz
	cd ${EPYDOC}; cd epydoc ; patch -p0 < ../../epydoc.diff; cd .. ; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch epydoc

epydoc-clean:
	rm -rf ${EPYDOC} 
epydoc-uninstall:
	rm -rf epydoc ${EPYDOC} $(foreach f, ${EPYDOC_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# docutils (used by epydoc)
#
DOCUTILS = docutils-0.4
DOCUTILS_UNINSTALL = ${PYTHON_LIB}/site-packages/docutils

docutils: ${DOCUTILS}.tar.gz python
	tar -xzf ${DOCUTILS}.tar.gz
	cd ${DOCUTILS}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch docutils

docutils-clean:
	rm -rf ${DOCUTILS} 
docutils-uninstall:
	rm -rf docutils ${DOCUTILS} $(foreach f, ${DOCUTILS_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# gnosis (xml tools: we use for xml pickle)
#
GNOSIS = Gnosis_Utils-1.3.0-alpha-7
GNOSIS_UNINSTALL =  ${PYTHON_LIB}/site-packages/gnosis

# uninstalls previous version first (could i just call 'gnosis-uninstall'?)
gnosis: ${GNOSIS}.tar.gz python
	rm -rf $(foreach f, ${GNOSIS_UNINSTALL}, ${PREFIX}/${f})
	tar -xzf ${GNOSIS}.tar.gz
	cd ${GNOSIS}; patch -p0 < ../Gnosis_Utils.diff
	cd ${GNOSIS}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch gnosis

gnosis-clean:
	rm -rf ${GNOSIS} 
gnosis-uninstall:
	rm -rf gnosis $(foreach f, ${GNOSIS_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# libsndfile (used by pyaudiolab)
#
LIBSNDFILE = libsndfile-1.0.17

LIBSNDFILE_UNINSTALL += bin/sndfile-* 
LIBSNDFILE_UNINSTALL += lib/libsndfile.*

libsndfile: ${LIBSNDFILE}.tar.gz
	tar -xzf ${LIBSNDFILE}.tar.gz
	cd ${LIBSNDFILE}; ./configure --prefix=${PREFIX}
	cd ${LIBSNDFILE}; make 
	cd ${LIBSNDFILE}; make install
	touch libsndfile

libsndfile-clean:
	rm -rf ${LIBSNDFILE} 
libsndfile-uninstall:
	rm -rf libsndfile ${foreach f,${LIBSNDFILE_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# pyaudiolab (sound file reading)
#
PYAUDIOLAB = pyaudiolab-0.6.6
PYAUDIOLAB_UNINSTALL =  ${PYTHON_LIB}/site-packages/pyaudiolab

pyaudiolab: ${PYAUDIOLAB}.tar.gz python libsndfile 
	tar -xzf ${PYAUDIOLAB}.tar.gz
	cd ${PYAUDIOLAB}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch pyaudiolab

pyaudiolab-clean:
	rm -rf ${PYAUDIOLAB} 
pyaudiolab-uninstall:
	rm -rf pyaudiolab ${PYAUDIOLAB} $(foreach f, ${PYAUDIOLAB_UNINSTALL}, ${PREFIX}/${f})




##############################################################
# mlabwrap (high level python to matlab bridge)
#
MLABWRAP = mlabwrap-1.0
MLABWRAP_UNINSTALL =  ${PYTHON_LIB}/site-packages/mlabwrap.py*
MLABWRAP_UNINSTALL += ${PYTHON_LIB}/site-packages/mlabrawmodule.so

mlabwrap: ${MLABWRAP}.tar.gz python 
	tar -xzf ${MLABWRAP}.tar.gz
	cd ${MLABWRAP}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch mlabwrap

mlabwrap-clean:
	rm -rf ${MLABWRAP} 
mlabwrap-uninstall:
	rm -rf mlabwrap ${MLABWRAP} $(foreach f, ${MLABWRAP_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# SCRODGET  (provides decent scrollbars)
#
SCRODGET = pyscrodget-0.0.2_2.1

SCRODGET_UNINSTALL += share/pyscrodget
SCRODGET_UNINSTALL += ${PYTHON_LIB}/site-packages/pyscrodget

scrodget: ${SCRODGET}.tar.gz python snit
	tar -xzf ${SCRODGET}.tar.gz
	cd ${SCRODGET}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch scrodget

scrodget-clean:
	rm -rf  ${SCRODGET} 
scrodget-uninstall:
	rm -rf scrodget ${foreach f,${SCRODGET_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# SNIT (module from tklib; used by scrodget)
#
SNIT = snit-2.2.1

SNIT_UNINSTALL += lib/${SNIT}

snit: ${SNIT}.tar.gz
	tar -xzf ${SNIT}.tar.gz
	cp -R ${SNIT} ${PREFIX}/lib/${SNIT}
	touch snit

snit-clean:
	rm -rf  ${SNIT} 
snit-uninstall:
	rm -rf snit ${foreach f,${SNIT_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# TOOLTIP (module from tcllib; used for help balloons)
#
TOOLTIP = tooltip-1.4

TOOLTIP_UNINSTALL += lib/${TOOLTIP}

tooltip: ${TOOLTIP}.tar.gz 
	tar -xzf ${TOOLTIP}.tar.gz
	cp -R ${TOOLTIP} ${PREFIX}/lib/${TOOLTIP}
	touch tooltip

tooltip-clean:
	rm -rf  ${TOOLTIP} 
tooltip-uninstall:
	rm -rf tooltip ${foreach f,${TOOLTIP_UNINSTALL}, ${PREFIX}/${f}}





##############################################################
# PSYCO
#
PSYCO = psyco-dist

PSYCO_UNINSTALL += ${PYTHON_LIB}/site-packages/psyco

psyco: ${PSYCO}-svn56930.tar.gz python
	tar -xzf ${PSYCO}-svn56930.tar.gz
	cd ${PSYCO}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch psyco

psyco-clean:
	rm -rf ${PSYCO} 
psyco-uninstall:
	rm -rf psyco ${foreach f,${PSYCO_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# Pyrex (required by PyTables)
#
PYREX = Pyrex-0.9.5.1a

PYREX_UNINSTALL += ${PYTHON_LIB}/site-packages/Pyrex

pyrex: ${PYREX}.tar.gz python
	tar -xzf ${PYREX}.tar.gz
	cd ${PYREX}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch pyrex

pyrex-clean:
	rm -rf ${PYREX}
pyrex-uninstall:
	rm -rf pyrex ${foreach f,${PYREX_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# HDF5 library (required by PyTables)
#
HDF5 = hdf5-1.6.6

HDF5_UNINSTALL += 

hdf5: ${HDF5}.tar.gz
	tar -xzf ${HDF5}.tar.gz
	cd ${HDF5}; ./configure --enable-cxx --prefix=${PREFIX}
	make -C ${HDF5} install
	touch hdf5

hdf5-clean:
	rm -rf ${HDF5} 
hdf5-uninstall:
	rm -rf hdf5 ${foreach f,${HDF5_UNINSTALL}, ${PREFIX}/${f}}


##############################################################
# PyTables
#
PYTABLES = pytables

PYTABLES_UNINSTALL += ${PYTHON_LIB}/site-packages/tables

pytables: ${PYTABLES}-20070518.tar.gz pyrex hdf5
	tar -xzf ${PYTABLES}-20070518.tar.gz
	cd ${PYTABLES}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT} --hdf5=${PREFIX}
	touch pytables

pytables-clean:
	rm -rf ${PYTABLES}
pytables-uninstall:
	rm -rf pytables ${foreach f,${PYTABLES_UNINSTALL}, ${PREFIX}/${f}}

##############################################################
# BlueSphere
# Only needs to be updated when the choice of icons changes, as the results 
# are ordinarily checked in under topo/tkgui/icons/.
# 
BLUESPHERE = BlueSphere-SVG-snapshot-Nov-29-2002

BLUESPHERE_UNINSTALL += topo/tkgui/icons/*.png

bluesphere: ${BLUESPHERE}.tar.gz
	rm -rf ${BLUESPHERE}
	mkdir ${BLUESPHERE}
	cd ${BLUESPHERE}; tar -xzf ../${BLUESPHERE}.tar.gz
	cp ${BLUESPHERE}_Makefile ${BLUESPHERE}/Makefile
	cd ${BLUESPHERE}; make
	cp ${BLUESPHERE}/*.png ../topo/tkgui/icons/
	touch bluesphere

bluesphere-clean:
	rm -rf ${BLUESPHERE}
bluesphere-uninstall:
	rm -rf bluesphere ${foreach f,${BLUESPHERE_UNINSTALL}, ${PREFIX}/${f}}

##############################################################
# Gnuplotpy
#
GNUPLOTPY = gnuplot-py-1.7

GNUPLOTPY_UNINSTALL += ${PYTHON_LIB}/site-packages/Gnuplot

gnuplotpy: ${GNUPLOTPY}.tar.gz
	tar -xzf ${GNUPLOTPY}.tar.gz
	cd ${GNUPLOTPY}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch gnuplotpy

gnuplotpy-clean:
	rm -rf ${GNUPLOTPY}
gnuplotpy-uninstall:
	rm -rf gnuplotpy ${foreach f,${GNUPLOTPY_UNINSTALL}, ${PREFIX}/${f}}

##############################################################
# Player
#
# ALERT: Not fully tested yet; may need more attention
PLAYER = player-2.1.0rc1

PLAYER_UNINSTALL += ${PYTHON_LIB}/site-packages/playerc* ${PYTHON_LIB}/site-packages/_playerc.so ${PYTHON_LIB}/../libplayer*

player: ${PLAYER}.tar.bz2
	tar -xjf ${PLAYER}.tar.bz2
	cd ${PLAYER}; ./configure --prefix=${PREFIX} ${PLAYER_FLAGS}
	make -C ${PLAYER} install
	make -C ${PLAYER}/client_libs/libplayerc/bindings/python
	cd ${PLAYER}/client_libs/libplayerc/bindings/python ; ${PREFIX}/bin/python ./setup.py install ${PYSETUP_OPT} 
	touch player

player-clean:
	rm -rf ${PLAYER}
player-uninstall:
	rm -rf player ${foreach f,${PLAYER_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# Stage
#
# ALERT: Not fully tested yet; may need more attention
STAGE = stage-2.1.0rc1

STAGE_UNINSTALL += ${PYTHON_LIB}/../libstage*

stage: ${STAGE}.tar.bz2
	tar -xjf ${STAGE}.tar.bz2
	cd ${STAGE}; ./configure --prefix=${PREFIX}
	make -C ${STAGE} install
	touch stage

stage-clean:
	rm -rf ${STAGE}
stage-uninstall:
	rm -rf stage ${foreach f,${STAGE_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# progressbar
#
PROGRESSBAR = progressbar-2.2

PROGRESSBAR_UNINSTALL += ${PYTHON_LIB}/site-packages/progressbar.py

progressbar: ${PROGRESSBAR}.tar.gz python
	tar -xzf ${PROGRESSBAR}.tar.gz
	cd ${PROGRESSBAR}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch progressbar

progressbar-clean:
	rm -rf ${PROGRESSBAR}
progressbar-uninstall:
	rm -rf progressbar ${foreach f,${PROGRESSBAR_UNINSTALL}, ${PREFIX}/${f}}



#############################################################
# GNU MP
GMP = gmp-4.3.1

GMP_UNINSTALL += lib/libgmp.* 
GMP_UNINSTALL += include/gmp.h


gmp: ${GMP}.tar.gz
	tar -xzf ${GMP}.tar.gz
	cd ${GMP}; ./configure --prefix=${PREFIX} 
	make -C ${GMP}
	make -C ${GMP} check
	make -C ${GMP} install
	touch gmp

gmp-clean: 
	rm -rf ${GMP} 
gmp-uninstall:
	rm -rf gmp $(foreach f, ${GMP_UNINSTALL}, ${PREFIX}/${f})


# CBALERT: there are probably other packages for which we should remove .egg-info?

# CB: mxnumber will be removed

##############################################################
# eGenix mx Experimental (for mxNumber)
#
MXNUMBER = egenix-mx-experimental-3.0.0

MXNUMBER_UNINSTALL += ${PYTHON_LIB}/site-packages/mx/
MXNUMBER_UNINSTALL += ${PYTHON_LIB}/site-packages/egenix_mx_experimental-3.0.0-py2.5.egg-info

mxnumber: ${MXNUMBER}.tar.gz python gmp
	tar -xzf ${MXNUMBER}.tar.gz
	cd ${MXNUMBER}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch mxnumber

mxnumber-clean:
	rm -rf ${MXNUMBER}
mxnumber-uninstall:
	rm -rf mxnumber ${foreach f,${MXNUMBER_UNINSTALL}, ${PREFIX}/${f}}


##############################################################
# wraps GMP
#
GMPY = gmpy-sources-101

GMPY_UNINSTALL += ${PYTHON_LIB}/site-packages/gmpy-1.01-py2.5.egg-info
GMPY_UNINSTALL += ${PYTHON_LIB}/site-packages/gmpy.so

gmpy: ${GMPY}.tar.gz python gmp
	tar -xzf ${GMPY}.tar.gz
	cd ${GMPY}; ${PREFIX}/bin/python setup.py build_ext --include-dirs='${PREFIX}/include' --library-dirs='${PREFIX}/lib'; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch gmpy

gmpy-clean:
	rm -rf ${GMPY}
gmpy-uninstall:
	rm -rf gmpy ${foreach f,${GMPY_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# processing (improved interactive prompt)
#
PROCESSING = processing-0.51
PROCESSING_UNINSTALL =  ${PYTHON_LIB}/site-packages/processing
PROCESSING_UNINSTALL += ${PYTHON_LIB}/site-packages/processing-0.51-py2.5.egg-info

processing: ${PROCESSING}.tar.gz python 
	tar -xzf ${PROCESSING}.tar.gz
	cd ${PROCESSING}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch processing

processing-clean:
	rm -rf ${PROCESSING} 
processing-uninstall:
	rm -rf processing ${PROCESSING} $(foreach f, ${PROCESSING_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# svn2cl (Only used for generating the ChangeLog)
#
SVN2CL = svn2cl-0.10

svn2cl: ${SVN2CL}.tar.gz
	tar -xzf ${SVN2CL}.tar.gz
	ln -sf ${SVN2CL}/svn2cl.sh svn2cl

svn2cl-clean:

svn2cl-uninstall:
	rm -rf svn2cl ${SVN2CL}


##############################################################
# pyttk (CB: currently unused - will replace Tile.py)
#
PYTTK = pyttk-0.2.6

PYTTK_UNINSTALL += ${PYTHON_LIB}/site-packages/pyttk.py

pyttk: ${PYTTK}.tar.gz python
	tar -xzf ${PYTTK}.tar.gz
	cd ${PYTTK}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch pyttk

pyttk-clean:
	rm -rf ${PYTTK}
pyttk-uninstall:
	rm -rf pyttk ${foreach f,${PYTTK_UNINSTALL}, ${PREFIX}/${f}}


#############################################################
# GNU READLINE
READLINE = readline-5.2

READLINE_UNINSTALL += lib/libreadline.* 
READLINE_UNINSTALL += include/readline.h

readline: ${READLINE}.tar.gz termcap
	tar -xzf ${READLINE}.tar.gz
	cd ${READLINE}; ./configure --prefix=${PREFIX} 
	make -C ${READLINE}
	make -C ${READLINE} install
	touch readline

readline-clean: 
	rm -rf ${READLINE} 
readline-uninstall:
	rm -rf readline $(foreach f, ${READLINE_UNINSTALL}, ${PREFIX}/${f})


#############################################################
# GNU TERMCAP
TERMCAP = termcap-1.3.1

TERMCAP_UNINSTALL += lib/libtermcap.* 
TERMCAP_UNINSTALL += include/termcap.h

termcap: ${TERMCAP}.tar.gz
	tar -xzf ${TERMCAP}.tar.gz
	cd ${TERMCAP}; ./configure --prefix=${PREFIX} 
	make -C ${TERMCAP}
	make -C ${TERMCAP} install
	touch termcap

termcap-clean: 
	rm -rf ${TERMCAP} 
termcap-uninstall:
	rm -rf termcap $(foreach f, ${TERMCAP_UNINSTALL}, ${PREFIX}/${f})




#############################################################
# CYTHON
CYTHON = Cython-0.9.8.1.1

CYTHON_UNINSTALL += ${PYTHON_LIB}/site-packages/Cython*
CYTHON_UNINSTALL += ${PYTHON_LIB}/site-packages/pyximport
CYTHON_UNINSTALL += bin/cython

cython: ${CYTHON}.tar.gz
	tar -xzf ${CYTHON}.tar.gz
	cd ${CYTHON}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch cython

cython-clean: 
	rm -rf ${CYTHON} 
cython-uninstall:
	rm -rf cython $(foreach f, ${CYTHON_UNINSTALL}, ${PREFIX}/${f})


#############################################################
# LINE_PROFILER
LINE_PROFILER = line_profiler-582df342463a

LINE_PROFILER_UNINSTALL += ${PYTHON_LIB}/site-packages/line_profiler*
LINE_PROFILER_UNINSTALL += bin/kernprof.py

line_profiler: ${LINE_PROFILER}.tar.gz cython
	tar -xzf ${LINE_PROFILER}.tar.gz
	cd ${LINE_PROFILER}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch line_profiler

line_profiler-clean: 
	rm -rf ${LINE_PROFILER} 
line_profiler-uninstall:
	rm -rf line_profiler $(foreach f, ${LINE_PROFILER_UNINSTALL}, ${PREFIX}/${f})


#############################################################
# guppy: provides heapy, a memory profiler
GUPPY = guppy-r70

GUPPY_UNINSTALL += ${PYTHON_LIB}/site-packages/guppy
GUPPY_UNINSTALL += ${PYTHON_LIB}/site-packages/guppy*.egg*

guppy: ${GUPPY}.tar.gz python
	tar -xzf ${GUPPY}.tar.gz
	cd ${GUPPY}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch guppy

guppy-clean: 
	rm -rf ${GUPPY} 
guppy-uninstall:
	rm -rf guppy $(foreach f, ${GUPPY_UNINSTALL}, ${PREFIX}/${f})


#############################################################
# ipythontk: provides IPython console in Tkinter
IPYTHONTK = ipythonTk

IPYTHONTK_UNINSTALL += ${PYTHON_LIB}/site-packages/ipythonTk*.egg*
IPYTHONTK_UNINSTALL += ${PYTHON_LIB}/site-packages/ipythonTk

ipythontk: ${IPYTHONTK}.tar.gz python
	tar -xzf ${IPYTHONTK}.tar.gz
	cd ${IPYTHONTK}; patch -p0 ipythonTk/ipythonTk.py < ../ipythonTk.diff
	cd ${IPYTHONTK}; patch -p0 ipythonTk/ipython_view.py < ../ipython_view.diff
	cd ${IPYTHONTK}; ${PREFIX}/bin/python setup.py install ${PYSETUP_OPT}
	touch ipythontk

ipythontk-clean: 
	rm -rf ${IPYTHONTK} 
ipythontk-uninstall:
	rm -rf ipythontk $(foreach f, ${IPYTHONTK_UNINSTALL}, ${PREFIX}/${f})


#############################################################################
#   Generic targets added for migration from Sourceforge to GitHub.         #
#   These targets download the necessary files from external-full-history   #
#   on Sourceforge where the binaries historically used by Topographica     #
#   are currently stored.                                                   #
#                                                                           #
#   These targets has been appended in September 2012 and should work for   #
#   all correctly written targets: targets that list the required source    #
#   archive(s) as necessary dependencies.                                   #
#############################################################################

%.tgz:
	wget --no-check-certificate https://sourceforge.net/projects/topographica/files/external-full-history/$@

%.py.gz:
	wget --no-check-certificate https://sourceforge.net/projects/topographica/files/external-full-history/$@

%.tar.gz:
	wget --no-check-certificate https://sourceforge.net/projects/topographica/files/external-full-history/$@

%.tar.bz2:
	wget --no-check-certificate https://sourceforge.net/projects/topographica/files/external-full-history/$@
