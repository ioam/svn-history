# $Id$

all: topographica ext-packages  docs

clean: cleandocs clean-ext-packages

topographica: topographica-script.py Makefile
	echo "#!/usr/bin/env" ${PWD}/bin/python > topographica
	cat topographica-script.py >> topographica 
	chmod a+x topographica

ext-packages:
	make -C external

clean-ext-packages: 
	make -C external clean
	make -C external uninstall

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

