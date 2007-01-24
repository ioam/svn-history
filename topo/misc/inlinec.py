"""
Interface class for inline C/C++ functions.  Based on the SciPy Weave package.

Weave (from SciPy) allows programmers to implement Python methods or
functions using C code written as a string in the Python file.  This
is generally done to speed up code that would be slow if written
directly in Python.  Because not all users can be assumed to have a
working C/C++ compiler, it is crucial for such optimizations to be
optional.  This file provides an interface for processing the inline
C/C++ code in a way that can gracefully revert back to the
unoptimized version when Weave is not available.

The fallback is implemented by making use of the way Python allows
function names to be overwritten, as in these simple examples:

  def x(y = 5): return y
  def x2(y = 6): return y*y
  print 'x:', x(), 'x2:', x2()  # Result -- x: 5 x2: 36
  x = x2
  print 'x:', x(), 'x2:', x2()  # Result -- x: 36 x2: 36

In this file, inline() is overwritten to call inline_weave() if Weave
is available.  If Weave is not available, inline() will raise a
NotImplementedError exception.  For a program to be usable without
Weave, just test inlinec.optimized after defining each optimized
component, replacing it with a non-optimized equivalent if
inlinec.optimized is False.

For more information on weave, see:
http://old.scipy.org/documentation/weave/weaveusersguide.html

$Id$
"""


import os
from copy import copy

# If true, will attempt to import weave.  Set this to False if you want
# to avoid weave altogether, e.g. if your installation is broken.
import_weave = True

# Variable that will be used to report whether weave was successfully
# imported (below).
weave_imported = False


def inline(*params,**nparams): raise NotImplementedError


try:
    if import_weave:
        import weave
        weave_imported = True

    # Default parameters to add to the inline_weave() call.
    inline_named_params = {
        'extra_compile_args':['-O2','-fomit-frame-pointer','-funroll-loops'],
        'extra_link_args':['-lstdc++'],
        'compiler':'gcc',
        'verbose':0}

    def inline_weave(*params,**nparams):
        named_params = copy(inline_named_params) # Make copy of defaults.
        named_params.update(nparams)             # Add newly passed named parameters.
        weave.inline(*params,**named_params)
        
    # Overwrites stub definition with full Weave definition
    inline = inline_weave

except ImportError:
    print 'Caution: Unable to import Weave.  Will use non-optimized versions of most components.'


# Flag available for all to use to test whether to use the inline
# versions or not.
optimized = weave_imported

def provide_unoptimized_equivalent(optimized_name, unoptimized_name, local_dict):
    """
    If not using optimization, replace the optimized component with its unoptimized equivalent.
    
    The objects named by optimized_name and unoptimized_name should be
    plug-compatible.  The local_dict argument should be given the
    contents of locals(), so that this function can replace the
    optimized version with the unoptimized one in the namespace from
    which it has been called.

    As an example, calling this function as::
    
      provide_unoptimized_equivalent("sort_opt","sort",locals())

    is equivalent to putting the following code directly into the
    calling location::
    
      if not optimized:
        sort_opt = sort
        print 'module: Inline-optimized components not available; using sort instead of sort_opt.'
    """
    if not optimized:
        local_dict[optimized_name] = local_dict[unoptimized_name]
        print '%s: Inline-optimized components not available; using %s instead of %s.' \
              % (local_dict['__name__'], optimized_name, unoptimized_name)


# Simple test
if __name__ == '__main__':
    inline('printf("Hello World!!\\n");')

