"""
Miscellaneous functions used by Topographica files outside topo.base.

This package is intended to be self-contained, i.e., should not refer to any
other part of Topographica.  For instance, files should not generally include an
import statement like 'from topo.package.module import' or 'import
topo.package.module'.  Those that follow this convention will be
easily available for anyone to copy and use in their own unrelated
projects; they are not specific to Topographica in any way.

$Id: __init__.py 6876 2007-10-19 00:29:50Z jbednar $
"""
__version__='$Revision: 6876 $'

__all__=['commandline','distribution','filepaths','gendocs','inlinec','keyedlist','numbergenerators','patternfns','traces','utils']
