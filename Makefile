# $Id$

all: topographica ext-packages docs

topographica: topographica-script.py Makefile
	echo "#!/usr/bin/env" ${PWD}/bin/python > topographica
	cat topographica-script.py >> topographica 
	chmod a+x topographica

ext-packages:
	make -C external


##############################################################
# Auto-generated Source Documentation
# Uses a partially integrated python script named gendocs.py
#
GENDOC = ./topographica topo/gendocs.py -w 

cleandocs:
	rm -r docs

docs: topo/*.py
	mkdir -p docs
	${GENDOC} topo
	mv topo.html docs/index.html
	${GENDOC} topo/

