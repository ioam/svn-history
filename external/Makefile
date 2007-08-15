PREFIX = ${dir ${CURDIR}}
CC = gcc

default: python jpeg pil numpy pmw matplotlib weave fixedpoint pychecker common pylint epydoc docutils gnosis

all: default pyaudiolab mlabwrap scipy ipython pyrex pytables psyco

clean: python-clean jpeg-clean pil-clean numeric-clean numpy-clean pmw-clean tk-clean tcl-clean matplotlib-clean weave-clean fixedpoint-clean pychecker-clean common-clean pylint-clean epydoc-clean docutils-clean gnosis-clean scipy-clean mlabwrap-clean ipython-clean libsndfile-clean ctypes-clean pyaudiolab-clean tile-clean tilewrapper-clean bwidget-clean psyco-clean pyrex-clean hdf5-clean pytables-clean

uninstall: python-uninstall jpeg-uninstall pil-uninstall numeric-uninstall numpy-uninstall pmw-uninstall tk-uninstall tcl-uninstall matplotlib-uninstall fixedpoint-uninstall weave-uninstall pychecker-uninstall common-uninstall pylint-uninstall epydoc-uninstall docutils-uninstall gnosis-uninstall scipy-uninstall mlabwrap-uninstall ipython-uninstall libsndfile-uninstall ctypes-uninstall pyaudiolab-uninstall tile-uninstall tilewrapper-clean bwidget-uninstall psyco-uninstall pyrex-uninstall hdf5-uninstall pytables-uninstall

##############################################################
# Python (interpreted language)
#
PYTHON = Python-2.4.4

PYTHON_LIB  = lib/python2.4
PYTHON_INC  = include/python2.4
PYTHON_CONF = lib/python2.4/config

PYTHON_UNINSTALL += bin/idle bin/python bin/pydoc bin/python2.4 
PYTHON_UNINSTALL += ${PYTHON_LIB} man/man1/python.1 include/python2.4


# LDFLAGS sets ${PREFIX}/lib as the LD_LIBRARY in the binary
# CB: rpath is ignored on OS X (so where are the library files taken from?). 
python: ${PYTHON}.tgz tk
	echo ${PREFIX}
	tar xzf ${PYTHON}.tgz
	cd ${PYTHON}; ./configure --prefix=${PREFIX} LDFLAGS=-Wl,-rpath,${PREFIX}/lib
	cd ${PYTHON}; env PREFIX=${PREFIX} make 
	cd ${PYTHON}; env PREFIX=${PREFIX} make install
	touch python

python-clean:
	rm -rf  ${PYTHON} 
python-uninstall:
	rm -rf python ${foreach f,${PYTHON_UNINSTALL}, ${PREFIX}/${f}}

##############################################################
# Tcl (required by Tk GUI toolkit)
#
TCL = tcl8.4.13
TCL_UNINSTALL += bin/tclsh8.4 bin/wish8.4 lib/tclConfig.sh
TCL_UNINSTALL += lib/tcl8.4 lib.tclConfig.sh lib/libtcl8.4.so lib/libtclstub8.4.a
TCL_UNINSTALL += include/tcl*.h man/man*

tcl: ${TCL}-src.tar.gz
	tar xzf ${TCL}-src.tar.gz
	cd ${TCL}/unix; ./configure --prefix=${PREFIX}
	make -C ${TCL}/unix install
	touch tcl

tcl-clean:
	rm -rf  ${TCL} 
tcl-uninstall:
	rm -rf tcl ${foreach f,${TCL_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# Tk (GUI toolkit)
#
TK = tk8.4.13

TK_UNINSTALL += lib/tk8.4 lib/libtk8.4.so lib/libtkstub8.4.a
TK_UNINSTALL += include/tk*.h lib/tkConfig.sh

tk: ${TK}-src.tar.gz tcl
	tar xzf ${TK}-src.tar.gz
	cd ${TK}/unix; ./configure --prefix=${PREFIX}
	make -C ${TK}/unix install
	touch tk

tk-clean:
	rm -rf  ${TK} 
tk-uninstall:
	rm -rf tk ${foreach f,${TK_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# ipython (improved interactive prompt)
#
IPYTHON = ipython-0.7.3
IPYTHON_UNINSTALL =  ${PYTHON_LIB}/site-packages/IPython

ipython: ${IPYTHON}.tar.gz python 
	tar xzf ${IPYTHON}.tar.gz
	cd ${IPYTHON}; ${PREFIX}/bin/python setup.py install
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
	tar xzf ${JPEG}.tgz
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
PIL = Imaging-1.1.5
PIL_UNINSTALL = ${PYTHON_LIB}/site-packages/PIL

pil: ${PIL}.tgz jpeg python
	tar xzf ${PIL}.tgz
#	cd ${PIL}/libImaging; ./configure --prefix=${PREFIX} --with-jpeg=${PREFIX}/lib
#	make -C ${PIL}/libImaging
#
#       Apply patch for 64-bit machines; helps prevent "encoder zip not available" problems
ifeq ("$(shell uname -m)","x86_64")
	cd ${PIL}; patch < ../Imaging.diff
endif
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py build_ext -i
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python selftest.py
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch pil

pil-clean:
	rm -rf ${PIL} 
pil-uninstall:
	rm -rf pil $(foreach f, ${PIL_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# Numeric (matrix library)
# CB: will remove this section shortly...
NUMERIC = Numeric-24.0
NUMERIC_UNINSTALL =  ${PYTHON_LIB}/site-packages/Numeric

numeric-clean:
	rm -rf ${NUMERIC} 
numeric-uninstall:
	rm -rf numeric $(foreach f, ${NUMERIC_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# numpy (matrix library)
#
NUMPY = numpy-1.0.2
NUMPY_UNINSTALL =  ${PYTHON_LIB}/site-packages/numpy

numpy: ${NUMPY}.tar.gz python numpy.diff
	tar xzf ${NUMPY}.tar.gz
	cd ${NUMPY}; patch -p0 < ../numpy.diff
	cd ${NUMPY}; ${PREFIX}/bin/python setup.py install
	touch numpy

numpy-clean:
	rm -rf ${NUMPY} 
numpy-uninstall:
	rm -rf numpy $(foreach f, ${NUMPY_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# MatPlotLib (plotting library)
#
MATPLOTLIB = matplotlib-0.90.0
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
	tar xzf ${MATPLOTLIB}.tar.gz
	cd ${MATPLOTLIB}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${MATPLOTLIB_DISPLAY} ${PREFIX}/bin/python setup.py build
	cd ${MATPLOTLIB}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${MATPLOTLIB_DISPLAY} ${PREFIX}/bin/python setup.py install
	touch matplotlib

matplotlib-clean:
	rm -rf ${MATPLOTLIB} 
matplotlib-uninstall:
	rm -rf matplotlib ${MATPLOTLIB} $(foreach f, ${MATPLOTLIB_UNINSTALL}, ${PREFIX}/${f})


##############################################################
# PMW (graphical toolkit)
#
PMW = Pmw
PMW_UNINSTALL = ${PYTHON_LIB}/site-packages/Pmw

pmw: ${PMW}.tgz python
	tar xzf ${PMW}.tgz
	cp -r ${PMW} ${PREFIX}/${PYTHON_LIB}/site-packages/Pmw
	touch pmw

pmw-clean:
	rm -rf ${PMW} 
pmw-uninstall:
	rm -rf pmw ${PREFIX}/${PMW_UNINSTALL}


##############################################################
# Weave (on its own apart from Scipy)
#
WEAVE = scipy-0.5.2
WEAVE_UNINSTALL = ${PYTHON_LIB}/site-packages/weave external/weave

# Forces removal of weave version used with Numeric
weave: ${WEAVE}.tar.gz python
	rm -rf Scipy_core-0.3.0_108.1820
	rm -f ${PYTHON_LIB}/site-packages/weave external/weave
	tar xzf ${WEAVE}.tar.gz
	cd ${WEAVE}/Lib/weave/; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch weave

weave-clean:
	rm -rf ${WEAVE} 
weave-uninstall:
	rm -rf weave ${WEAVE} $(foreach f, ${WEAVE_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# Scipy
#
SCIPY = scipy-0.5.2
SCIPY_UNINSTALL = ${PYTHON_LIB}/site-packages/scipy external/scipy

# Forces removal of scipy version used with Numeric
scipy: ${SCIPY}.tar.gz python
	rm -f ${PYTHON_LIB}/site-packages/scipy external/scipy
	tar xzf ${SCIPY}.tar.gz
	cd ${SCIPY}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
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
	tar xzf ${FIXEDPT}.tgz
	mv fixedpoint ${FIXEDPT}
	cp fixedpoint.diff ${FIXEDPT}
	cp fixedpoint_setup.py ${FIXEDPT}/setup.py
	cd ${FIXEDPT}; patch < fixedpoint.diff; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch fixedpoint

fixedpoint-clean:
	rm -rf ${FIXEDPT}
fixedpoint-uninstall:
	rm -rf fixedpoint ${FIXEDPT} ${FIXEDPT_UNINSTALL}/fixedpoint.*



##############################################################
# pychecker (optional source code checker)
#
PYCHECKER = pychecker-0.8.16
PYCHECKER_UNINSTALL = ${PYTHON_LIB}/site-packages/pychecker

pychecker: ${PYCHECKER}.tar.gz python
	tar xzf ${PYCHECKER}.tar.gz
	cd ${PYCHECKER}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch pychecker

pychecker-clean:
	rm -rf ${PYCHECKER} 
pychecker-uninstall:
	rm -rf pychecker ${PYCHECKER} $(foreach f, ${PYCHECKER_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# logilab common files, required for pylint (but should be 
# removed if pylint is removed)
#
COMMON = common-0.12.0
COMMON_UNINSTALL = ${PYTHON_LIB}/site-packages/logilab/common

common: ${COMMON}.tar.gz python
	tar xzf ${COMMON}.tar.gz
	cd ${COMMON}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch common

common-clean:
	rm -rf ${COMMON} 
common-uninstall:
	rm -rf common ${COMMON} $(foreach f, ${COMMON_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# pylint (optional source-code checker)
#
PYLINT = pylint-0.7.0
PYLINT_UNINSTALL = ${PYTHON_LIB}/site-packages/pylint

pylint: ${PYLINT}.tar.gz python common
	tar xzf ${PYLINT}.tar.gz
	cd ${PYLINT}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch pylint

pylint-clean:
	rm -rf ${PYLINT} 
pylint-uninstall:
	rm -rf pylint ${PYLINT} $(foreach f, ${PYLINT_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# epydoc (Automatic Reference_Manual generator)
#
EPYDOC = epydoc-3.0beta1
EPYDOC_UNINSTALL = ${PYTHON_LIB}/site-packages/epydoc

epydoc: ${EPYDOC}.tar.gz python common
	tar xzf ${EPYDOC}.tar.gz
	cd ${EPYDOC}; cd epydoc ; patch -p0 < ../../epydoc.diff; cd .. ; ${PREFIX}/bin/python setup.py install
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

docutils: ${DOCUTILS}.tar.gz python common
	tar xzf ${DOCUTILS}.tar.gz
	cd ${DOCUTILS}; ${PREFIX}/bin/python setup.py install
	touch docutils

docutils-clean:
	rm -rf ${DOCUTILS} 
docutils-uninstall:
	rm -rf docutils ${DOCUTILS} $(foreach f, ${DOCUTILS_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# gnosis (xml tools)
#
GNOSIS = Gnosis_Utils-1.2.1
GNOSIS_UNINSTALL =  ${PYTHON_LIB}/site-packages/gnosis

gnosis: ${GNOSIS}.tar.gz python
	tar xzf ${GNOSIS}.tar.gz
	cd ${GNOSIS}; ${PREFIX}/bin/python setup.py install
	touch gnosis

gnosis-clean:
	rm -rf ${GNOSIS} 
gnosis-uninstall:
	rm -rf gnosis $(foreach f, ${GNOSIS_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# ctypes (used by pyaudiolab)
#

# CBALERT: ctypes is present in Python 2.5, so remove it
# if python is updated!
CTYPES = ctypes-1.0.1
CTYPES_UNINSTALL =  ${PYTHON_LIB}/site-packages/ctypes
CTYPES_UNINSTALL += ${PYTHON_LIB}/_ctypes.so ${PYTHON_LIB}/_ctypes_test.so

ctypes: ${CTYPES}.tar.gz python
	tar xzf ${CTYPES}.tar.gz
	cd ${CTYPES}; ${PREFIX}/bin/python setup.py build
	cd ${CTYPES}; ${PREFIX}/bin/python setup.py install
	touch ctypes

ctypes-clean:
	rm -rf ${CTYPES}
ctypes-uninstall:
	rm -rf ctypes ${CTYPES} $(foreach f, ${CTYPES_UNINSTALL}, ${PREFIX}/${f})




##############################################################
# libsndfile (used by pyaudiolab)
#
LIBSNDFILE = libsndfile-1.0.17

LIBSNDFILE_UNINSTALL += bin/sndfile-* 
LIBSNDFILE_UNINSTALL += lib/libsndfile.*

libsndfile: ${LIBSNDFILE}.tar.gz
	tar xzf ${LIBSNDFILE}.tar.gz
	cd ${LIBSNDFILE}; ./configure --prefix=${PREFIX}
	cd ${LIBSNDFILE}; make 
	cd ${LIBSNDFILE}; make install
	touch libsndfile

libsndfile-clean:
	rm -rf  ${LIBSNDFILE} 
libsndfile-uninstall:
	rm -rf libsndfile ${foreach f,${LIBSNDFILE_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# pyaudiolab (sound file reading)
#
PYAUDIOLAB = pyaudiolab-0.6.6
PYAUDIOLAB_UNINSTALL =  ${PYTHON_LIB}/site-packages/pyaudiolab

pyaudiolab: ${PYAUDIOLAB}.tar.gz python libsndfile ctypes
	tar xzf ${PYAUDIOLAB}.tar.gz
	cd ${PYAUDIOLAB}; ${PREFIX}/bin/python setup.py install
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
	tar xzf ${MLABWRAP}.tar.gz
	cd ${MLABWRAP}; ${PREFIX}/bin/python setup.py install
	touch mlabwrap

mlabwrap-clean:
	rm -rf ${MLABWRAP} 
mlabwrap-uninstall:
	rm -rf mlabwrap ${MLABWRAP} $(foreach f, ${MLABWRAP_UNINSTALL}, ${PREFIX}/${f})




##############################################################
# TILE (extension to tk; actually a part of tk 8.5)
#
TILE = tile-0.7.8

TILE_UNINSTALL += lib/tile0.7.8 lib/libttkstub.a
TILE_UNINSTALL += include/ttk*.h

tile: ${TILE}.tar.gz tk
	tar xzf ${TILE}.tar.gz
	cd ${TILE}/generic; ./configure --prefix=${PREFIX}
	make -C ${TILE}/generic install
	touch tile

tile-clean:
	rm -rf  ${TILE} 
tile-uninstall:
	rm -rf tile ${foreach f,${TILE_UNINSTALL}, ${PREFIX}/${f}}


##############################################################
# TILEWRAPPER (makes tile easy to use from tkinter)
#
TILEWRAPPER = Tile

TILEWRAPPER_UNINSTALL += ${PYTHON_LIB}/site-packages/Tile.py*

# CB: I've made a bit of a meal out of simply copying
# Tile.py to the site-packages directory!
tilewrapper: ${TILEWRAPPER}.py.gz tile
	gzip -dc ${TILEWRAPPER}.py.gz > ${TILEWRAPPER}.py
	cp ${TILEWRAPPER}.py ${PREFIX}/${PYTHON_LIB}/site-packages/
	touch tilewrapper

tilewrapper-clean:
	rm -rf  ${TILEWRAPPER}.py 
tilewrapper-uninstall:
	rm -rf tilewrapper ${foreach f,${TILEWRAPPER_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# BWIDGET
#
BWIDGET = pybwidget-0.1.2_1.7.0

BWIDGET_UNINSTALL += share/pybwidget 
BWIDGET_UNINSTALL += ${PYTHON_LIB}/site-packages/bwidget

bwidget: ${BWIDGET}.tar.gz python tcl tk
	tar xzf ${BWIDGET}.tar.gz
	cd ${BWIDGET}; ${PREFIX}/bin/python setup.py install
	touch bwidget

bwidget-clean:
	rm -rf  ${BWIDGET} 
bwidget-uninstall:
	rm -rf bwidget ${foreach f,${BWIDGET_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# PSYCO
#
PSYCO = psyco-dist

PSYCO_UNINSTALL += ${PYTHON_LIB}/site-packages/psyco

psyco: ${PSYCO}-svn42201.tar.gz python
	tar xzf ${PSYCO}-svn42201.tar.gz
	cd ${PSYCO}; ${PREFIX}/bin/python setup.py install
	touch psyco

psyco-clean:
	rm -rf  ${PSYCO} 
psyco-uninstall:
	rm -rf psyco ${foreach f,${PSYCO_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# Pyrex (required by PyTables)
#
PYREX = Pyrex-0.9.5.1a

PYREX_UNINSTALL += ${PYTHON_LIB}/site-packages/Pyrex

pyrex: ${PYREX}.tar.gz python
	tar xzf ${PYREX}.tar.gz
	cd ${PYREX}; ${PREFIX}/bin/python setup.py install
	touch pyrex

pyrex-clean:
	rm -rf ${PYREX}
pyrex-uninstall:
	rm -rf pyrex ${foreach f,${PYREX_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# HDF5 library (required by PyTables)
#
HDF5 = hdf5-1.6.5

HDF5_UNINSTALL += 

hdf5: ${HDF5}.tar.gz
	tar xzf ${HDF5}.tar.gz
	cd ${HDF5}; ./configure --prefix=${PREFIX}
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
	tar xzf ${PYTABLES}-20070518.tar.gz
	cd ${PYTABLES}; ${PREFIX}/bin/python setup.py install
	touch pytables

pytables-clean:
	rm -rf ${PYTABLES}
pytables-uninstall:
	rm -rf pytables ${foreach f,${PYTABLES_UNINSTALL}, ${PREFIX}/${f}}
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
