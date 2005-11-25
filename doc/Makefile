# Makefile for doc directory
# Does not currently make the reference manual, so that
# the documentation can be compiled even if the code won't.

# $Id$

RM                              = rm -f
PHP                             = php -q
SED                             = sed
LN                              = ln -s

PHPBASE = ${wildcard */*_text.php}
PHPHTML = ${subst _text.php,.html,${PHPBASE}}


# General rule based only on target filename and location

# Old version: worked only for text.php -> index.html
#%/index.html : %/text.php shared/*.php shared/*.css
#	cd $* ; ${PHP} ../shared/index.php > index.html

# Works for any *_text.php -> *.html
# Hack: passes in text filename in an arbitrary php.ini option named
# 'sendmail_from', because it's not clear how to pass in 
# a user-defined variable value
%.html : %_text.php shared/*.php shared/*.css
	cd ${dir $@} ; ${PHP} -d sendmail_from=${notdir $<} ../shared/index.php > $(subst _text.php,.html,${notdir $<})

# Generate HTML files from source versions
default: all
all: ${PHPHTML}

clean:
	${RM} Reference_Manual/topo*.html

# Not removed by default, for people who do not have PHP locally
clean_php:
	${RM} ${PHPHTML}

.PHONY: default all clean clean-php

