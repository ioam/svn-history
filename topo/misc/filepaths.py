"""
Functions and classes to simplify dealing with paths.

For portable code:
  - specify paths in unix (rather than Windows) style;
  - use resolve_path() for paths to existing files to be read, 
    and normalize_path() for paths to new files to be written.

The location in which new files are created by default can be
controlled by the output_path module attribute, which applies
whenever a particular location is not specified explicitly.

$Id$
"""
__version__='$Revision$'

import os.path
import sys

from topo.base.parameterizedobject import Parameter, Parameterized


class Filename(Parameter):
    """
    Filename is a Parameter that can be set to a string specifying the
    path of a file (in unix style), and returns it in the format of
    the user's operating system.  Additionally, the specified path can
    be absolute or relative to:
    
    * any of the paths specified in the search_paths attribute;

    * any of the paths searched by resolve_path() (see doc for that
      function).
    """
    __slots__ = ['search_paths'] 

    def __init__(self,default=None,search_paths=[],**params):
        self.search_paths = search_paths
        super(Filename,self).__init__(default,**params)

        
    def __set__(self,obj,val):
        """
        Call Parameter's __set__, but warn if the file cannot be found.
        """
        try:
            resolve_path(val,self.search_paths)
        except IOError, e:
            Parameterized(name="%s.%s"%(str(obj),self.attrib_name(obj))).warning('%s'%(e.args[0]))

        super(Filename,self).__set__(obj,val)
        
    def __get__(self,obj,objtype):
        """
        Return an absolute, normalized path (see resolve_path).
        """
        raw_path = super(Filename,self).__get__(obj,objtype)
        return resolve_path(raw_path,self.search_paths)

    def __getstate__(self):
        # don't want to pickle the search_paths        
        state = super(Filename,self).__getstate__()
        # CBALERT: uncommenting gives an error on make tests (testsnapshots.py).
        # Testsnapshots.py runs fine on its own, and the snapshot-tests pass.
        # Must be a test interaction? Needs investigating.
        #del state['search_paths']
        return state


# Is there a more obvious way of getting this path?
# (Needs to work on unix and windows.)
# the application base directory
application_path = os.path.split(os.path.split(sys.executable)[0])[0]

# Location in which to create files; defaults to application_path
output_path = application_path

def resolve_path(path,search_paths=[]):
    """
    Find the path to an existing file, searching in the specified
    search paths if the filename is not absolute, and converting a
    UNIX-style path to the current OS's format if necessary.

    To turn a supplied relative path into an absolute one, the path is
    appended to each path in (search_paths+the current working
    directory+the application's base path), in that order, until the
    file is found.

    (Similar to Python's os.path.abspath(), except more search paths
    than just os.getcwd() can be used, and the file must exist.)
    
    An IOError is raised if the file is not found anywhere.
    """
    path = os.path.normpath(path)

    if os.path.isabs(path): return path

    all_search_paths = search_paths + [os.getcwd()] + [application_path]

    paths_tried = []
    for prefix in set(all_search_paths): # does set() keep order?            
        try_path = os.path.join(os.path.normpath(prefix),path)
        if os.path.isfile(try_path): return try_path
        paths_tried.append(try_path)

    raise IOError('File "'+os.path.split(path)[1]+'" was not found in the following place(s): '+str(paths_tried)+'.')


def normalize_path(path="",prefix=None):
    """
    Convert a UNIX-style path to the current OS's format,
    typically for creating a new file or directory.

    If the path is not already absolute, it will be made
    absolute (using the specified prefix, which defaults
    to filepaths.output_path) in the process.

    (Should do the same as Python's os.path.abspath(), except
    using the specified prefix rather than os.getcwd().)
    """
    if not prefix:
        prefix = output_path
        
    if not os.path.isabs(path):
        path = os.path.join(os.path.normpath(prefix),path)

    return os.path.normpath(path)
