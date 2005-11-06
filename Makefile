# $Id$
PREFIX =  ${CURDIR}/
PYLINT = bin/pylint --parseable=yes --required-attributes=__version__ --min-name-length=1 --notes=FIXME,XXX,TODO,ALERT --max-line-length=200 --disable-msg=C0324
PYCHECKER = bin/pychecker

DOC    = doc/Reference_Manual


all:  ext-packages topographica doc

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
	echo "#  Wrapper for setting environment vars and execing commands" >> topographica
	echo "import os,sys,topographica_script" >> topographica
	echo "" >> topographica
	echo "TOPO = '${PREFIX}'" >> topographica
	echo "DISLIN = os.path.join(TOPO,'lib/dislin')" >> topographica
	echo "" >> topographica
	echo "os.putenv('DISLIN',DISLIN)" >> topographica
	echo "os.putenv('LD_LIBRARY_PATH'," >> topographica
	echo "          ':'.join((os.path.join(TOPO,'lib'),DISLIN,os.getenv('LD_LIBRARY_PATH',''))))" >> topographica
	echo "os.putenv('PYTHONPATH',TOPO+':'+os.path.join(DISLIN,'python')+':'+os.getenv('PYTHONPATH',''))" >> topographica
	echo "" >> topographica
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

# Auto-generated Source Documentation
# Uses an integrated python script named gendocs.py
doc: topo/*.py topo/*/*.py
	mkdir -p ${DOC}
	./topographica topo/base/gendocs.py
