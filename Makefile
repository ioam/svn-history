# $Id$

all: ext-packages topographica docs

clean: cleandocs clean-ext-packages

topographica: topographica-script.py Makefile
	make -C external startscript

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

