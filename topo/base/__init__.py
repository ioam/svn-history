"""
Basic files needed by all Topographica programs.

This package should be self-contained, i.e., should not refer to any
other part of Topographica other than ..param.  For instance, no file
may include an import statement like 'from topo.package.module import'
or 'import topo.package.module'; the only external reference allowed
is to ..param.  This policy ensures that all of the packages outside
of this one and params are optional.

$Id$
"""
__version__='$Revision$'

__all__ = ['arrayutils','boundingregion','cf','functionfamilies','patterngenerator','projection','sheet','sheetcoords','sheetview','simulation']



