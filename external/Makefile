PREFIX = ${dir ${CURDIR}}
CC = gcc

all: python jpeg pil numeric pmw matplotlib dislin  dislinpy weave fixedpoint

clean: python-clean jpeg-clean pil-clean numeric-clean pmw-clean tk-clean tcl-clean matplotlib-clean dislin-clean dislinpy-clean fixedpoint-clean

uninstall: python-uninstall jpeg-uninstall pil-uninstall numeric-uninstall pmw-uninstall tk-uninstall tcl-uninstall matplotlib-uninstall dislin-uninstall dislinpy-uninstall fixedpoint-uninstall

##############################################################
# Python
#
PYTHON = Python-2.4

PYTHON_LIB  = lib/python2.4
PYTHON_INC  = include/python2.4
PYTHON_CONF = lib/python2.4/config

PYTHON_UNINSTALL += bin/idle bin/python bin/pydoc bin/python2.4 
PYTHON_UNINSTALL += ${PYTHON_LIB} man/man1/python.1 include/python2.4


python: ${PYTHON}.tgz tk
	tar xzf ${PYTHON}.tgz
	cd ${PYTHON}; ./configure --prefix=${PREFIX}
	env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib make -C ${PYTHON} install
	touch python

python-clean:
	rm -rf  ${PYTHON} 
python-uninstall:
	rm -rf python ${foreach f,${PYTHON_UNINSTALL}, ${PREFIX}/${f}}

##############################################################
# Tcl
#
# Jeff says that these flags, passed to the linker
# should make the need to add the path to LD_LIBRARY_PATH
# unnecessary   -Wl,-rpath -Wl,/home/jp/research/topographica/lib
TCL = tcl8.4.9
TCL_UNINSTALL += bin/tclsh8.4 bin/wish8.4 lib/tclConfig.sh
TCL_UNINSTALL += lib/tcl8.4 lib.tclConfig.sh lib/libtcl8.4.so lib/libtclstub8.4.a
TCL_UNINSTALL += include/tcl*.h man/man*

tcl: ${TCL}.tgz 
	tar xzf ${TCL}.tgz
	cd ${TCL}/unix; ./configure --prefix=${PREFIX}
	make -C ${TCL}/unix install
	touch tcl

tcl-clean:
	rm -rf  ${TCL} 
tcl-uninstall:
	rm -rf tcl ${foreach f,${TCL_UNINSTALL}, ${PREFIX}/${f}}



##############################################################
# Tk
#
# Jeff says that these flags, passed to the linker
# should make the need to add the path to LD_LIBRARY_PATH
# unnecessary   -Wl,-rpath -Wl,/home/jp/research/topographica/lib
TK = tk8.4.9

TK_UNINSTALL += lib/tk8.4 lib/libtk8.4.so lib/libtkstub8.4.a
TK_UNINSTALL += include/tk*.h lib/tkConfig.sh

tk: ${TK}.tgz tcl
	tar xzf ${TK}.tgz
	cd ${TK}/unix; ./configure --prefix=${PREFIX}
	make -C ${TK}/unix install
	touch tk

tk-clean:
	rm -rf  ${TK} 
tk-uninstall:
	rm -rf tk ${foreach f,${TK_UNINSTALL}, ${PREFIX}/${f}}



#############################################################
# jpeg

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
# PIL
#
PIL = Imaging-1.1.5
PIL_UNINSTALL = ${PYTHON_LIB}/site-packages/PIL

pil: ${PIL}.tgz jpeg python
	tar xzf ${PIL}.tgz
#	cd ${PIL}/libImaging; ./configure --prefix=${PREFIX} --with-jpeg=${PREFIX}/lib
#	make -C ${PIL}/libImaging
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py build_ext -i
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python selftest.py
	cd ${PIL}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch pil

pil-clean:
	rm -rf ${PIL} 
pil-uninstall:
	rm -rf pil $(foreach f, ${PIL_UNINSTALL}, ${PREFIX}/${f})

##############################################################
# Numeric
#
NUMERIC = Numeric-23.0
NUMERIC_UNINSTALL =  ${PYTHON_LIB}/site-packages/Numeric

numeric: ${NUMERIC}.tgz python
	tar xzf ${NUMERIC}.tgz
	cd ${NUMERIC}; ${PREFIX}/bin/python setup.py install
	touch numeric

numeric-clean:
	rm -rf ${NUMERIC} 
numeric-uninstall:
	rm -rf numeric $(foreach f, ${NUMERIC_UNINSTALL}, ${PREFIX}/${f})
##############################################################
# MatPlotLib
#
MATPLOTLIB = matplotlib-0.81
MATPLOTLIB_UNINSTALL =  ${PYTHON_LIB}/site-packages/matplotlib

matplotlib: ${MATPLOTLIB}.tgz
	tar xzf ${MATPLOTLIB}.tgz
	cd ${MATPLOTLIB}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py build
	cd ${MATPLOTLIB}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch matplotlib

matplotlib-clean:
	rm -rf ${MATPLOTLIB} 
matplotlib-uninstall:
	rm -rf ${MATPLOTLIB} $(foreach f, ${MATPLOTLIB_UNINSTALL}, ${PREFIX}/${f})
##############################################################
# PMW
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
# DISLIN
#
DISLIN = dislin-8.2
DISLIN_UNINSTALL = lib/dislin

dislin: ${DISLIN}.linux.tgz python
	tar xzf ${DISLIN}.linux.tgz
	mkdir -p ${PREFIX}/${DISLIN_UNINSTALL}
	cd ${DISLIN}; env DISLIN=${PREFIX}/${DISLIN_UNINSTALL} ./INSTALL
	touch dislin

dislin-clean:
	rm -rf ${DISLIN}
dislin-uninstall:
	rm -rf dislin ${DISLIN} ${PREFIX}/${DISLIN_UNINSTALL}


##############################################################
# Dislin/Pyton interface
# Modified from the sample make script in ${DISLIN}/python
#
DISLIN_PYTHON_DIR = ${PREFIX}${DISLIN_UNINSTALL}/python
DISLIN_PYTHON_SRC = ${DISLIN}.python.tar.gz
DISLINPY_BUILD =${CC} -c -O -I${PREFIX}/${PYTHON_INC} -I${PREFIX}/${PYTHON_CONF} dislinmodule.c
DISLINPY_LINK  = ${CC} -shared -Wl,-soname,dislinmodule.so -o dislinmodule.so *.o -L${PREFIX}/${DISLIN_UNINSTALL} -ldislnc

dislinpy: dislin 
	cd ${DISLIN_PYTHON_DIR}; tar xzf ${DISLIN_PYTHON_SRC}
	cd ${DISLIN_PYTHON_DIR}; ${DISLINPY_BUILD}
	cd ${DISLIN_PYTHON_DIR}; ${DISLINPY_LINK}
	touch dislinpy

dislinpy-clean:
	cd ${DISLIN_PYTHON_DIR}; rm -f make_py README.PY dislin.h dislinmodule.{h,c,o}

dislinpy-uninstall: dislinpy-clean
	rm -f dislinpy ${DISLIN_PYTHON_DIR}/dislinmodule.so

##############################################################
# Scipy (weave)
#
WEAVE = Scipy_core-0.3.0_108.1820
WEAVE_UNINSTALL = ${PYTHON_LIB}/site-packages/weave

weave: ${WEAVE}.tar.gz python
	tar xzf ${WEAVE}.tar.gz
	cd ${WEAVE}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch weave

weave-clean:
	rm -rf ${WEAVE} 
weave-uninstall:
	rm -rf ${WEAVE} $(foreach f, ${WEAVE_UNINSTALL}, ${PREFIX}/${f})



##############################################################
# Fixed-Point package
#
FIXEDPT = fixedpoint-0.1.2
FIXEDPT_UNINSTALL = ${PYTHON_LIB}/site-packages

fixedpoint: ${FIXEDPT}.tgz python
	tar xzf ${FIXEDPT}.tgz
	cd ${FIXEDPT}; env PREFIX=${PREFIX} LD_LIBRARY_PATH=${PREFIX}/lib ${PREFIX}/bin/python setup.py install
	touch fixedpoint

fixedpoint-clean:
	rm -rf ${FIXEDPT}
fixedpoint-uninstall:
	rm -rf ${FIXEDPT} ${FIXEDPT_UNINSTALL}/fixedpoint.*
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
