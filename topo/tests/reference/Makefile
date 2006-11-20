# $Id$

GZCAT = gzip -c
RM    = rm -f

FILESTOUNZIP  = ${wildcard *.gz}
UNZIPPEDFILES = ${patsubst %.gz,%,${FILESTOUNZIP}}

# Rule for updating from gzipped files
% : %.gz
	${GZCAT} $< > $@

all: ${UNZIPPEDFILES}

clean: 
	${RM} ${UNZIPPEDFILES}
