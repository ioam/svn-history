<H1>Importing external files and functions</H1>

<P>When at all possible, use a Python standard library function
instead of writing your own code or downloading a separate package.
The standard library functions are available to all Python platforms
without any maintenance work from us, they will be more readable to
Python programmers (who might just recognize the name instead of
having to study the semantics), and those functions are much less
likely to contain bugs than our own code is because the library
functions have been tested by more people on more tasks.

<P>Non-standard external Python libraries should be used where
appropriate, i.e. for anything reasonably substantial like plotting or
matrix manipulation. The core external libraries of Topographica are
NumPy and PIL (Imaging); you can assume that these will always exist
for any Topographica installation. Other external packages, while
often very useful, should be considered optional (and their absence
should be handled gracefully).

<P>Including an external package adds an approximately fixed cost of
tracking future updates and changes to it, handling its licensing
issues, increasing the size of our download, restricting the number of
supported platforms, etc.  Including an external package just for one
or two small, simple functions probably doesn't make sense, but
including it for non-trivial items like plot generation or matrix
handling does make sense.  The key question to answer for any external
package is "would the code I'm using from the external package be
easier to maintain on its own, or is it easier to just include the
external package?".  If it's easier just to add those couple of
functions, just copy them (if the licensing terms allow it); otherwise
add the external package.

<P>When importing code, whether from standard libraries or external
functions, always import only the functions and classes that you are
actually using.  As an example that has already occurred, please do
NOT do anything like <CODE>from MLab import *</CODE>, because of the
huge potential for name clashes resulting in strange, hard-to-track
bugs.  For that particular example, python has a built-in function
named max(), but this function is replaced with a matrix-specific
version by <CODE>from MLab import *</CODE>:

<PRE>
  $ bin/python
  &gt;&gt;&gt; max(1.2,0)
  1.2
  &gt;&gt;&gt; from MLab import *
  &gt;&gt;&gt; max(1.2,0)
  Traceback (most recent call last):
    File "&lt;stdin&gt;", line 1, in ?
    File "/lib/python2.4/site-packages/Numeric/MLab.py", line 146, in max
      return maximum.reduce(m,axis)
  ValueError: dimension not in array
  &gt;&gt;&gt; 
</PRE>

<P>Please try to avoid such problems by importing only the specific
functions and classes you need, or (where practical) by importing the
package only and then using the fully qualified name
(e.g. <CODE>import MLab ; MLab.max()</CODE>).

<P>If you find that you need to change any file in an external
package, please <EM>DO NOT</EM> change that file, wrap it up into a .tar or
.zip archive, and put it back into the Topographica repository.  Doing
so is a very bad idea, because it prevents us from upgrading that
package in the future.  Instead, keep the original archive intact as
distributed, but then have the <CODE>external/Makefile</CODE> patch it
automatically to change the specific items that need editing.  When
the package is updated, the same patch can often be applied as-is to
the new package, and in any case it will be clear exactly where to
look in the package to make the necessary change.

<P>As a convention, we arrange the imports in each Python file in
order from most general to most specific:

<OL>
<LI>Python standard library items (such as <CODE>math</CODE>, <CODE>sys</CODE>, <CODE>os</CODE>)
<LI>Core external packages (<CODE>numpy</CODE> and <CODE>Imaging</CODE>)
<LI>Other external packages (such as <CODE>matplotlib</CODE>)
<LI>Topographica files not in the current package<BR>
      (with absolute paths like <CODE>topo.base.sheet</CODE>)
<LI>Topographica files in the current package<BR>
      (usually with relative paths like <CODE>sheet</CODE>)
</OL>

<P>A blank line separates each of these sections, and items in the
sections are typically ordered alphabetically (at least if there is a
long list).  For example:

<PRE>
  import types
  from math import pi
  
  from numpy import transpose, array
  
  from topo.base.connectionfield import CFSheet
  from topo.base.functionfamily import TransferFn
  from topo.misc.util import flatten, cross_product
  
  from plot import Plot
  import bitmap
</PRE>   


