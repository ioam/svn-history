# $Id$
PREFIX =  ${CURDIR}/

all:  topographica docs

clean: cleandocs clean-ext-packages


ext-packages:
	make -C external

clean-ext-packages: 
	make -C external clean
	make -C external uninstall


##############################################################
# Startup Script sh version.  
#
topographica_old: ext-packages
	echo "#!/bin/sh" > ${PREFIX}topographica
	echo 'export DISLIN="${PREFIX}${DISLIN_UNINSTALL}"' >> ${PREFIX}topographica
	echo 'export PYTHONPATH="$$PYTHONPATH:${PREFIX}${DISLIN_UNINSTALL}/python"' >> ${PREFIX}topographica
	echo 'export LD_LIBRARY_PATH="${PREFIX}lib:${PREFIX}${DISLIN_UNINSTALL}:$$LD_LIBRARY_PATH"' >> ${PREFIX}topographica
	echo -e "/usr/bin/env ${PREFIX}/bin/python ${PREFIX}/topographica-script.py \044\100" >> ${PREFIX}topographica
	chmod a+x ${PREFIX}topographica


##############################################################
# Startup Script Python Version -- Not working
# It sets all the environment variables and even calls exec
# but it can't find Dislin afterwards.  Don't know what's wrong.
#
topographica: ext-packages
	echo "#!${PREFIX}/bin/python" > topographica
	echo "#  wrapper.py test wrapper for setting environment" >> topographica
	echo "import os,sys" >> topographica
	echo "" >> topographica
	echo "TOPO = '${PREFIX}'" >> topographica
	echo "DISLIN = os.path.join(TOPO,'lib/dislin')" >> topographica
	echo "" >> topographica
	echo "os.putenv('DISLIN',DISLIN)" >> topographica
	echo "os.putenv('LD_LIBRARY_PATH'," >> topographica
	echo "          ':'.join((os.path.join(TOPO,'lib'),DISLIN,os.getenv('LD_LIBRARY_PATH'))))" >> topographica
	echo "os.putenv('PYTHONPATH',os.path.join(DISLIN,'python')+':'+os.getenv('PYTHONPATH'))" >> topographica
	echo "" >> topographica
	echo "" >> topographica
	echo "# exec" >> topographica
	echo "os.execv(os.path.join(TOPO,'bin/python')," >> topographica
	echo "         [os.path.join(TOPO,'topographica')," >> topographica
	echo "          'topographica-script.py'] + sys.argv[1:])" >> topographica

	chmod a+x ${PREFIX}topographica




##############################################################
# Auto-generated Source Documentation
# Uses an integrated python script named gendocs.py
#
cleandocs:
	- rm -r docs

docs: topo/*.py
	mkdir -p docs
	./topographica topo/gendocs.py
	mv docs/topo.__init__.html docs/index.html

