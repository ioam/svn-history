# $Id$

RM                              = rm -f
PHP                             = php -q
SED                             = sed
LN                              = ln -s

PHPBASE = ${wildcard */text.php}
PHPHTML = ${subst text.php,index.html,${PHPBASE}}


# General rule based only on target filename and location
# Hack: uses complicated path to index.php to declare this 
# directory for _SERVER[PHP_SELF]
%/index.html : %/text.php shared/*.php shared/*.css
	cd $* ; ${PHP} ../$*/../shared/index.php > index.html

# Generate HTML files from source versions
default: all
all: ${PHPHTML}

clean:
	${RM} ${PHPHTML}

.PHONY: default all clean
