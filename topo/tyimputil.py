"""
Extends, but technically doesn't subclass, the imputil.py script
which allows changes to the Python 'import' command.

Upon importing, automatically calls installTYExtensions(), which will
make 'import' treat files with the .ty extension as Python source
files which means loading and compiling the code to .tyc or .tyo
depending on the optimization flag.  If the source .ty files are not
available, existing .tyc or .tyo (depending) will still import
properly like traditional Python files.  Note: No guarantees about
Pythonesque behavior if source and binaries with the same name are
scattered in different directories.

NOTE: Because the module auto-loads through a test of the __name__
variable, proper placement of the 'import' is important.  In the topo
__init__.py file, placing it at the end seems to do the trick.

Original version by Judah on June 30, 2004

$Id$
"""

import imp
import struct
import marshal
from imputil import *
from imputil import _timestamp, _compile, _suffix_char, DynLoadSuffixImporter

# byte-compiled file suffix
_ty_suffix = '.ty' + _suffix_char


def ty_suffix_importer(filename, finfo, fqname):
    """
    Importer function for .TY A minor change on the py_suffix_importer
    from imputil.py.  Will generate the compiled code for .ty files too.
    """
    file = filename[:-3] + _ty_suffix
    t_py = long(finfo[8])
    t_pyc = _timestamp(file)

    code = None
    if t_pyc is not None and t_pyc >= t_py:
        f = open(file, 'rb')
        if f.read(4) == imp.get_magic():
            t = struct.unpack('<I', f.read(4))[0]
            if t == t_py:
                code = marshal.load(f)
        f.close()
    if code is None:
        file = filename
        code = _compile(file, t_py)

    return 0, code, { '__file__' : file }


def installTYExtensions():
    """
    Will log the .ty, and .tyc or .tyo (depending) into the import
    command of Python.  If the .ty files are not found, it will still
    attempt to load the compiled files directly, so the source is not
    necessary.
    """
    n = ImportManager()
    n.add_suffix('.ty',ty_suffix_importer)
    desc = (_ty_suffix,'rb',imp.PY_COMPILED)
    n.add_suffix(_ty_suffix,DynLoadSuffixImporter(desc).import_file)
    n.install()


# Nifty, but causes issues in nested imports
#if __name__ != '__main__':
#    installTYExtensions()


def tests():
    "Test sequences, assumes a helloworld.ty"
    installTYExtensions()
    import helloworld     # helloworld.ty
    helloworld.test()     # Print a Hello World
