<!-- CB: maybe shouldn't be called 'external' packages, since
to the user they are part of topographica. users might think this
is just a list of packages they can get from somewhere if they 
are interested. -->

<H1>External Packages</H1>

<P>Packages available for use in Topographica...

<!--maybe make this a contents page w/ little blurb
and link out, depending on how much text these need.-->


<H2>mlabwrap: high-level Python-to-Matlab bridge</H2>

<P>Allows Matlab to look like a normal Python library.
For example:

<PRE>
from mlabwrap import mlab

mlab.plot([1,2,3],'-o')
</PRE>

The first line starts a Matlab session; the second
illustrates a command.

<P>See mlabwrap.sourceforge.net [add link] for more
information.

<P>To use this package, you need to build the 
external 'all' target etc, or 
<code>cd external; make mlabwrap</code>.
When you do this, if the matlab libraries are not in your PATH,
there wil be a note telling you 
to add something to your path with a command like:

<pre>
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/matlab-7.2/bin/glnx86
</pre>

Either add that permanently to your path, or do it before using malbwrap
			   each time. (You must have the matlab
				       binary in your path too.)