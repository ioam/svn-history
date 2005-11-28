"""
Interface class for inline C functions in the SciPy Weave package.

Weave is used for writing inline C code for code speedups.  It is
possible to run Topographica without having initially installed Weave,
such as on a Windows platform.  Using this file as an interface,
fallback non-optimized functions will be transparently called if Weave
is not installed.

The transparency is possible by the way Python allows function names
to be overwritten.  For example:

def x(y = 5): return y
def x2(y = 6): return y*y
print 'x:', x(), 'x2:', x2()  # x: 5 x2: 36
x = x2
print 'Overwritten.'
print 'x:', x(), 'x2:', x2()  # x: 36 x2: 36

Then, when this file is imported, a dictionary is accessed that
replaces the non-Weave functions with the Weave optimized functions.
For example inline() would be overwritten to call inline_weave()
instead.  This will require a non-optimized function assignment for
each optimized function, even if that function is a message stating
that the function is a stub.


$Id$
"""

weave_imported = False

def inline(*params): print "inline() not implemented."

try:
    import weave
    weave_imported = True

    def inline_weave(*params):
        weave.inline(*params)
    inline = inline_weave

except ImportError:
    print 'Caution: Unable to import Weave.  Some functionality may be disabled.'

inline('printf("Hello World!");')

