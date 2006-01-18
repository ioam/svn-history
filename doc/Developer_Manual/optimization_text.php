<H1>Optimization</H1>

<P>According to Knuth, "Premature optimization is the root of all
evil".  Although the performance of Topographica is critically
important, the way to achieve high performance is by spending *all* of
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
