PREFIX = ${dir ${CURDIR}}


all: python pil numeric pmw

clean: python-clean jpeg-clean pil-clean numeric-clean pmw-clean


##############################################################
# Python
#
PYTHON = Python-2.3.3

PYTHON_LIB = lib/python2.3

PYTHON_CLEAN += bin/idle bin/python bin/pydoc bin/python2.3 
PYTHON_CLEAN += ${PYTHON_LIB} man/man1/python.1 include/python2.3


python: ${PYTHON}.tgz
	tar xzf ${PYTHON}.tgz
	cd ${PYTHON}; ./configure --prefix=${PREFIX}
	make -C ${PYTHON} install
	touch python

python-clean:
	rm -rf python ${PYTHON} ${foreach f,${PYTHON_CLEAN}, ${PREFIX}/${f}}

#############################################################
# jpeg

JPEG = jpeg-6b

JPEG-CLEAN =  ${JPEG}
JPEG_CLEAN += bin/cjpeg bin/djpeg bin/jpegtran bin/rdjpgcom bin/wrjpgcom
JPEG_CLEAN += lib/libjpeg.* 
JPEG_CLEAN += man/man1/cjpeg.1 man/man1/djpeg.1 man/man1/jpegtran.1
JPEG_CLEAN += man/man1/rdjpgcom.1 man/man1/wrjpgcom.1
JPEG_CLEAN += include/jconfig.h include/jerror.h include/jmorecfg.h include/jpeglib.h


jpeg: ${JPEG}.tgz
	tar xzf ${JPEG}.tgz
	cd ${JPEG}; ./configure --prefix=${PREFIX} --enable-shared --enable-static
	make -C ${JPEG}
	make -C ${JPEG} test
	make -C ${JPEG} install
	touch jpeg

jpeg-clean: 
	rm -rf jpeg ${JPEG} $(foreach f, ${JPEG_CLEAN}, ${PREFIX}/${f})


##############################################################
# PIL
#
PIL = Imaging-1.1.4jp
PIL_CLEAN = ${PYTHON_LIB}/site-packages/PIL

pil: ${PIL}.tgz jpeg python
	tar xzf ${PIL}.tgz
	cd ${PIL}/libImaging; ./configure --prefix=${PREFIX} --with-jpeg=${PREFIX}/lib
	make -C ${PIL}/libImaging
	cd ${PIL}; ${PREFIX}/bin/python setup.py build
	cd ${PIL}; ${PREFIX}/bin/python setup.py install
	touch pil

pil-clean:
	rm -rf pil ${PIL} $(foreach f, ${PIL_CLEAN}, ${PREFIX}/${f})


##############################################################
# Numeric
#
NUMERIC = Numeric-23.0
NUMERIC_CLEAN =  ${PYTHON_LIB}/site-packages/Numeric

numeric: ${NUMERIC}.tgz python
	tar xzf ${NUMERIC}.tgz
	cd ${NUMERIC}; ${PREFIX}/bin/python setup.py install
	touch numeric

numeric-clean:
	rm -rf numeric ${NUMERIC} $(foreach f, ${NUMERIC_CLEAN}, ${PREFIX}/${f})

##############################################################
# PMW
#
PMW = Pmw
PMW_CLEAN = ${PYTHON_LIB}/site-packages/Pmw

pmw: ${PMW}.tgz python
	tar xzf ${PMW}.tgz
	cp -r ${PMW} ${PREFIX}/${PYTHON_LIB}/site-packages/Pmw
	touch pmw

pmw-clean:
	rm -rf ${PMW} pmw ${PREFIX}/${PMW_CLEAN}#############################################################################
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
