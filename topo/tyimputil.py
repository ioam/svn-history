"""
Module that extends, but technically doesn't subclass, the
imputil.py script which allows changes to the Python 'import'
command.  This extension, when loaded and installed with
installTYExtensions(), will treat files with the .ty extension as
Python source files upon importing, compiling the code to .tyc or
.tyo depending on the optimization flag.  If the source .ty files
are not available, existing .tyc or .tyo (depending) will still
import properly like traditional Python files.  Note: No guarantees
about Pythonesque behavior if source and binaries with the same name
are scattered in different directories.

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


"""
A minor change on the py_suffix_importer from 
imputil.py.  Will generate the compiled
code.
"""
def ty_suffix_importer(filename, finfo, fqname):
    "Modified py_suffix_importer for .TY"
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


"""
Will log the .ty, and .tyc or .tyo (depending)
into the import command of Python.  If the .ty
files are not found, it will still attempt to
load the compiled files directly so the source
is not necessary.
"""
def installTYExtensions():
    "Install new ImportManager that handles .ty, .tyc, .tyo"
    n = ImportManager()
    n.add_suffix('.ty',ty_suffix_importer)
    desc = (_ty_suffix,'rb',imp.PY_COMPILED)
    n.add_suffix(_ty_suffix,DynLoadSuffixImporter(desc).import_file)
    n.install()


def main():
    "Test sequence"
    installTYExtensions()
    import t1     # t1.ty
    t1.test()     # Print a Hello World
