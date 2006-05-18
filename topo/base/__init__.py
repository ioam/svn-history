"""
Basic files needed by all Topographica programs.

This package should be self-contained, i.e., should not refer to any
other part of Topographica.  For instance, no file may include an
import statement like 'from topo.package.module import' or 'import
topo.package.module'.  This ensures that all of the packages outside
of this one are optional.

$Id$
"""
__version__='$Revision$'

__all__ = ['arrayutils','boundingregion','cf','functionfamilies','parameterclasses','parameterizedobject','patterngenerator','projection','sheet','sheetcoords','sheetview','simulation']


