
all: topographica ext-packages

topographica: topographica-script.py Makefile
	echo "#!"${PWD}/bin/python > topographica
	cat topographica-script.py >> topographica 
	chmod a+x topographica

ext-packages:
	make -C external