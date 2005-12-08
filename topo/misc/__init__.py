"""
Miscellaneous functions used by Topographica files outside topo.base

This package should be self-contained, i.e., should not refer to any
other part of Topographica.  For instance, no file may include an
import statement like 'from topo.package.module import' or 'import
topo.package.module'.  

$Id$
"""
__version__='$Revision$'

__all__ = ['distribution','inlinec','patternfns','commandline','gendocs','keyedlist','tyimputil']
