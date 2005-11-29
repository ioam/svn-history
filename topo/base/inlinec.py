"""
Interface class for inline C functions in the SciPy Weave package.

Weave is used for writing inline C for code speedups.  Sometimes it is
possible to run Topographica without having initially installed Weave,
such as on Windows.  Using this file as an interface, non-optimized
functions will be transparently called as a fallback if Weave is not
installed.

This transparency is possible by making use of the way Python allows
function names to be overwritten.  For example:

def x(y = 5): return y
def x2(y = 6): return y*y
print 'x:', x(), 'x2:', x2()  # x: 5 x2: 36
x = x2
print 'Overwritten.'
print 'x:', x(), 'x2:', x2()  # x: 36 x2: 36

For example inline() will be overwritten to call inline_weave()
instead.  This requires a non-optimized function assignment for each
optimized function, even if that function is a message stating that
the function is a stub.


$Id$
"""

# In case an outside package wants to know
weave_imported = False

def inline(*params): raise NotImplementedError

try:
    import weave
    weave_imported = True

    def inline_weave(*params):
        weave.inline(*params)
    inline = inline_weave

except ImportError:
    print 'Caution: Unable to import Weave.  Will use non-optimized versions of most components.'

# Flag available for all to use to test whether to use the inline versions or not.
optimized = weave_imported

# Simple test
if __name__ == '__main__':
    inline('printf("Hello World!\\n");')

