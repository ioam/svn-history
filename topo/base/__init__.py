"""
Basic files needed by all Topographica programs.

This package should be self-contained, i.e., should not refer to any
other part of Topographica other than ..params.  For instance, no file
may include an import statement like 'from topo.package.module import'
or 'import topo.package.module'; the only external reference allowed
is to ..params.  This policy ensures that all of the packages outside
of this one and params are optional.

$Id$
"""
__version__='$Revision$'

__all__ = ['arrayutils','boundingregion','cf','functionfamilies','parameterclasses','parameterizedobject','patterngenerator','projection','sheet','sheetcoords','sheetview','simulation']


def _numpy_ufunc_pickle_support():
    """
    Allow instances of numpy.ufunc to pickle.

    Remove this when numpy.ufuncs themselves support pickling.
    See http://news.gmane.org/find-root.php?group=gmane.comp.python.numeric.general&article=13400
    """
    # Code from Robert Kern
    from numpy import ufunc
    import copy_reg

    def ufunc_pickler(ufunc):
        """Return the ufunc's name"""
        return ufunc.__name__

    copy_reg.pickle(ufunc,ufunc_pickler)

_numpy_ufunc_pickle_support()
del _numpy_ufunc_pickle_support

