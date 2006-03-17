<H1>Optimization</H1>

<P>According to Knuth, "Premature optimization is the root of all
evil".  Although the performance of Topographica is critically
important, the way to achieve high performance is by spending <i>all</i> of
our optimization efforts on the very small portion of the code that
accounts for nearly all of the run time, i.e., the bottlenecks.  The
overall architecture of Topographica is designed explicitly to
localize those bottlenecks into specific functions and objects that
can then be heavily optimized without affecting any of the rest of the
code.  Only in such small, local regions, behind well-defined modules
with clear semantics, is it possible to optimize effectively in a way
that can be maintained in the long run.  If it is precisely clear what
the module is supposed to do, then the implementation can be polished
to achieve that, while reasoning only about the behavior of that one
specific module.

<P>Conversely, finding that good performance requires adding special
hacks in the largest-scale, general-purpose parts of the overall
Topographica architecture means that the architecture is flawed and
needs to be re-thought.  For instance, please do not add any special
checks scattered through the code testing for specific
PatternGenerator or Sheet objects, substituting a quicker version of
some operation but falling back to the general case for others.  Such
code is impossible to understand and maintain, because changes to the
specific object implementations will not have any effect.  Instead, we
can optimize the individual PatternGenerator or Sheet object heavily.
If some special hack needs to be done at a high level, e.g. at the
base Sheet class level, we can add a method there that then gets
overridden in the base class with the special purpose code.  That way
all optimization will be local (and thus maintainable).  If it's not
clear how to optimize something cleanly, first do it uncleanly to see
if it will have any effect, but don't check it in to CVS.  If it looks
like the optimization is worthwhile, brainstorm with other team
members to figure out a way to do it cleanly and check in the clean
version instead.


<H2>Providing optimized versions of Topographica objects</H2>

<P>Where possible, Python components can be implemented with high
performance using
<A href="http://numeric.scipy.org/numpydoc/numdoc.htm">Numeric</A>
matrix operations.  This should be the first approach when optimizing
any component, and indeed when writing the component for the first
time (because the Numeric primitives are much easier to use and
maintain than e.g. explicitly writing <code>for</code> loops.
However, there are certain cases where the performance of Numeric is
not sufficient, or where Numeric is unsuitable (for example, many
Numeric operations do not act in-place on arrays).  Other components
may be able to be implemented much more quickly if certain assumptions
are made about the nature of their arguments, or the types of
computations that can be performed.

<P>In the cases mentioned above, it is worthwhile to have a reference
version of the object that is simple to understand and does not make
any special assumptions. Then, an optimized version can be offered as
an alternative. The convention we use is to add the suffix
<code>_optN</code> to the optimized version, where <code>N</code> is a
number that allows to distinguish between differently optimized
versions. This is helpful both for understanding and for ensuring
correctness.

<P>For example, consider <code>CFDotProduct</code>, from
<code>topo.responsefns.basic</code>. If users wish to use a version
optimized by having been written in C, they can instead import
<code>CFDotProduct_opt1</code> from
<code>topo.responsefns.optimized</code>. We use
<code>CFDotProduct_opt1</code> as standard in our code because it's
much faster than --- but otherwise identical to --- the unoptimized
version. However, because <code>CFDotProduct_opt1</code> relies on a
more complex setup (having the weave module installed, as well as a
correctly configured C++ compiler), we cannot assume all users will
have access to it. It is also extremely difficult to read and
understand. Therefore, we provide an automatic fall-back to the
unoptimized version (see <code>topo/responsefns/optimized.py</code>
for an example of how to do this).

<P>The non-optimized version also acts as a simple specification of
exactly what the optimized version is supposed to do, apart from any
optimizations.  The optimized versions are often nearly unreadable, so
having the simple version available is very helpful for understanding
and debugging.  The expectation is that the simple (slow) versions
will rarely change, but the optimized ones will get faster and faster
over time, while preserving the same user-visible behavior.
