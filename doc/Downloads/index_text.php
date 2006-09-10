<H3><A NAME="installing-topographica">Installing Topographica</A></H3>

<P>Topographica is developed under Linux, and is also supported for
Windows and Mac OS X.  It should work on non-Linux versions of UNIX as
well, as long as standard GNU tools like make and GCC are installed.
You will need a writable directory with a large amount of space
available, about 400 megabytes as of 6/2006.

<P>There are two ways to obtain Topographica: as downloadable
installation packages, or via
<A HREF="http://www.nongnu.org/cvs/">CVS</A>.  Most users should
download the installation packages at our Sourceforge
<A HREF="http://sourceforge.net/project/showfiles.php?group_id=53602">downloads</A>
page. Linux, Unix, and Mac OS X users can download either the
<code>.zip</code> or <code>.tar.gz</code> archive package, unpack it,
and then follow the <A HREF="#building-topographica">'Building
Topographica'</A> instructions below.  Depending on your setup, Mac
users may find that you  need to install some of the programs specified in the
<A HREF="cvs.html#osx">Mac CVS instructions</A>.  Windows users can download and
run the self-installing <code>.exe</code> file, and can then skip to
the <A HREF="#running-topographica">'Running Topographica'</A>
instructions below.  Users who want more frequent updates, or who need
to modify the source code, should <A HREF="cvs.html">obtain
Topographica using CVS</A> instead.

<H3><A NAME="building-topographica">Building Topographica</A></H3>

Once you have obtained the <code>topographica</code> directory, you
are ready to build Topographica.  This directory contains the files
making up Topographica itself, plus source code versions of the
various external libraries needed by Topographica.  At present, the
libraries are included in source code form to minimize
platform-specific modifications needed for different systems, although
this approach does increase the disk space and compile time
requirements.

<P>On Windows, no build step is necessary if you downloaded the
self-installing .exe file.  Windows CVS users should just double click
on setup.bat in the 
<code>topographica\topographica-win\setup_cvs_copy\</code>
directory after checking out the code.

<P>On other systems, just type <code>make</code> (which may be called
<code>gmake</code> on some systems) from within the
<code>topographica/</code> directory.  The build process will take a
while to complete (e.g. about 5-10 minutes on a 1.5GHz Pentium IV
machine with a local disk).  If you have PHP, m4, and fig2dev
installed, you can also make local copies of the HTML documentation
from the web site; to do so, type <code>make all</code> instead of (or
after) <code>make</code>.  <code>make all</code> will
also run the regression tests and example files, to ensure that
everything is functioning properly on your system.  (Note that if you
do the tests on a machine without a functioning DISPLAY, such as a
remote text-only session, there will be some warnings about GUI tests
being skipped.)

<P>On some Linux distributions that start with a minimal set of
packages included, such as Ubuntu or the various "live CD" systems,
you may need to specify explicitly that some standard libraries be
installed in your system, such as <t>libfreetype</t>, <t>libpng</t>,
<t>libx11-dev</t>, and <t>zlib</t>, before <code>make</code> will
succeed.

<P>If all goes well, a script named <code>topographica</code> or
<code>topographica.bat</code> will be created in the
<code>topographica/</code> directory; you can use this to start
Topographica as described in the <A HREF="#running-topographica">'Running
Topographica'</A> section below.  If you have problems,
try adding <code>-k</code> to the <code>make</code> command, which
will allow the make process to skip any components that do not build
properly on your machine. Topographica is highly modular, and most
functionality should be accessible even without some of those
components.  

<H3><A NAME="running-topographica">Running Topographica</A></H3>

Once you have the program installed and built, you can run
Topographica on the example models.  On most systems (including Linux,
Unix, and Mac), just open a terminal window, go to your topographica/
directory, and type e.g.:

<pre>
  ./topographica -g examples/cfsom_or.ty
</pre>

or

<pre>
  ./topographica -g examples/hierarchical.ty
</pre>

or

<pre>
  ./topographica -g examples/som_retinotopy.ty
</pre>

or

<pre>
  ./topographica -g examples/lissom_oo_or.ty
</pre>

Windows users can type similar commands at a Windows command prompt,
but should omit the initial '<code>./</code>' and should replace the
second forward slash '<code>/</code>' with a backslash
'<code>\</code>'.  Alternatively, Windows users can double click on
one of the <code>.ty</code> scripts in the examples directory;
<code>.ty</code> files are associated with Topographica.

<P>Note that the first time Topographica is run on a given example,
there may be a short pause while the program compiles some of the
optimized components used in that example.  (Some components,
generally those with <code>_opt</code> in their names, use code
written in C++ internally for speed, and this code must be compiled.)
The compiled versions are stored in <code>~/.python24_compiled/</code>
on most systems (or in the system temporary directory on Windows), and
they will be reused on the next run unless the source files have
changed.  Thus you should only notice such pauses the first time you
use a particular component, at which time you may also notice various
inscrutable messages from the compiler (which may generally be ignored).

<P>In any case, a good way to get started with these examples is to
work through  
the <A HREF="../Tutorials/som_retinotopy.html">SOM</A> or 
<A HREF="../Tutorials/lissom_oo_or.html">LISSOM</A> tutorials.
Have fun with Topographica, and be sure to subscribe to the 
<A
HREF="https://lists.sourceforge.net/lists/listinfo/topographica-announce">topographica-announce</A>
mailing list to hear about future updates!


