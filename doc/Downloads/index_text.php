<P>Topographica is currently under very active development, with many
changes made daily.  To simplify the process of frequent file
releases, it is currently distributed using
<A HREF="http://www.nongnu.org/cvs/">CVS</A>, the version control
system used for managing Topographica development.  Over the next few
months, installation packages will be built for Linux, Windows, and
Macintosh, which will speed up and simplify the process of
installation (at the cost of making it slightly more difficult to
upgrade to new versions).  If you prefer to wait for these packages,
just sign up for the
<A HREF="https://lists.sourceforge.net/lists/listinfo/topographica-announce">topographica-announce</A>
mailing list, where they will be announced when available.

<!-- They will be listed at http://sourceforge.net/project/showfiles.php?group_id=53602 -->

<H2>Installing using CVS</H2>

<P>Topographica is hosted by
<A HREF="http://sourceforge.net/projects/topographica">
SourceForge.net</A>, which maintains the CVS repository.  The
essentials for using CVS at SourceForge are described below; see the
<A HREF="http://sourceforge.net/docman/display_doc.php?docid=29894&group_id=1">
SourceForge documentation</A> for more details or if you have any
difficulties.

<P> To get started, first change to a directory to which you have
write access with sufficient space available, i.e., about 500
megabytes as of 11/2005.  There are two ways to get your own local
copy of the CVS files, depending on whether or not you are an official
Topographica developer.  Non-developers can check out a read-only
version of the repository, while developers have read/write access so
that they can make changes that become a permanent part of the project
repository.  Please follow the appropriate set of instructions below.

<H3>Read-only access</H3>

For read-only access, log in to the CVS server using the UNIX
command:

<pre>
  cvs -d :pserver:anonymous@cvs.sf.net:/cvsroot/topographica login
</pre>

When a password is requested, just press return.  Then change to
wherever you want the files to be stored, and use the command:

<pre>
  cvs -d :pserver:anonymous@cvs.sf.net:/cvsroot/topographica
  checkout -A -d -P -r LATEST_STABLE topographica
</pre>

(where the entire command should be on a single line, even though it
is broken into two lines above).  This process will likely take a few
minutes, as there are some large files involved.  The <code>-r
LATEST_STABLE</code> option selects the version that has most recently
been declared to pass all tests.  That option can be omitted if you
want the absolutely most up-to-date version, which may not always be
usable due to work in progress.


<H3>Read/write access</H3>

For developers wanting read/write access, no login step is needed.
However, you may need to tell CVS to use <code>ssh</code>, because
most systems default to rsh, which is almost never supported anymore.
Just type <code>export CVS_RSH=ssh</code> for <code>sh/bash</code> or
<code>setenv CVS_RSH ssh</code> for csh/tcsh; you may wish to put this
in your shell startup file.  The checkout command is then:

<pre>
  cvs -d ':ext:<i>uname</i>@cvs.sourceforge.net:/cvsroot/topographica' checkout topographica
</pre>

where <i>uname</i> should be replaced with your SourceForge.net
username.  You will be asked for your SourceForge.net password.  If
instead you get a message about rsh timing out, you have probably
forgotten to do the CVS_RSH command.  The LATEST_STABLE option can
also be provided as above, but developers will more likely want the
most up-to-date version for editing.


<H3>Building Topographica</H3>

The <code>topographica</code> directory you have now checked out
includes the files necessary to build Topographica on most platforms.
To make the build process simpler for developers using multiple of
platforms, source code versions of the libraries needed are included,
and are created as part of the build process.  This approach makes the
initial compilation time longer and the simulator directory larger,
but it minimizes the changes necessary for specific platforms and
operating system versions.

<P><B>Linux:</B>
To build Topographica under Linux, just type <code>make</code> from within the
<code>topographica/</code> directory.  The build process will take a

while to complete (e.g. about 5-10 minutes on a 1.5GHz Pentium IV
machine with a local disk).  If all goes well, a script named
<code>topographica</code> will be created in the
<code>topographica/</code> directory; you can use this to start
Topographica as described in the <A
HREF="../Tutorial/index.html">Tutorial</A>.  If you have PHP
installed, you call also make local copies of the HTML documentation;
to do so, type all" instead of (or after) "make".  "make all" will
also run the regression tests and example files, to ensure that
everything is functioning properly on your system.

<P><B>UNIX:</B>
Topographica is developed under Linux, but should work on other
versions of UNIX as well, as long as they have standard GNU tools like
make and GCC installed.  Just follow the Linux instructions, replacing
<code>make</code> with <code>gmake</code> if that's the name of GNU make on your system.

<P><B>Mac:</B>
Topographica builds only under Mac OS X or later.  Topographica
developers have only limited access to OS X machines, and so at any
time there are likely to be some issues with the OS X version,
although we do try to minimize them.  

If you have an X server installed, you can just build Topographica as
described for Linux.  It is also possible to build Topographica using
a native (Aqua) version of Python, which looks a bit nicer, but we
have not yet documented how to do that.  We have not necessarily
tested the most recent version on the Mac, so there may be some small
changes required.

<P><B>Windows:</B> It should be possible to build Topographica under
Windows just as is done under UNIX, if you first install <A
HREF="http://www.cygwin.com/">Cygwin</a>, although as of 11/2005 the
library versions available on Cygwin are a bit out of date.
Alternatively, nearly all of the features of Topographica are
available with a Win32-native Python, and if you choose this option
then Cygwin is optional.  The basic steps for building the native
version are:

<ol>
<li> Unpack the topographica archive into a temporary directory.
<li> Double click on setup.bat
<li> Follow the various installation prompts for the packages 
     bundled with Topographica.
</ol>

<P>
After installation you should now have an icon on your desktop that
opens the directory where Topographica is installed.  There will be a
new file association called ".ty" which are scripts that the
Topographica program will execute when you double-click on them.

<P>
You can now test the installation by double-clicking on the
topographica.bat file which will run the interactive Topographica
shell and give you a "Topographica>" prompt.

<P>If you experience the error:
<pre>
  File "C:\Python23\lib\string.py", line 220, in atoi 
    return _int(s, base)
TypeError: int() can't convert non-string with explicit base
</pre>

<p>Then you may be running an old version of Python.  Check your
Environment Variables in "My Computer -> Properties" to make sure you
don't have an old version of Python earlier in your path statement
that is running first.  If you still have troubles, see the 
WIN32_INSTALL.txt file included with the Topographica distribution.


<H3>Running Topographica</H3>

Once you have the code installed and built, go to your
topographica/ directory and type e.g.:

  ./topographica -g examples/cfsom_or.ty

or

  ./topographica -g examples/lissom_or.ty

If you use the latter, a good way to get started is to work through
the <A HREF="../Tutorial/index.html">LISSOM tutorial</A>.

<H3>Updating Topographica</H3>

Once you have Topographica checked out, you can update to the latest
stable version at any time by doing:

<pre>
  cd topographica
  cvs update -A -d -P -r LATEST_STABLE
</pre>

As before, '-r LATEST_STABLE' can be omitted to get the very most
recent version.
