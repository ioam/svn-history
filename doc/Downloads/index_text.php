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

<P>To get started, first change to a directory to which you have write
access with sufficient space available, i.e., about 400 megabytes as
of 2/2006. There are two ways to get your own local copy of the CVS
files, depending on whether or not you are an official Topographica
developer. Non-developers can check out a read-only version of the
repository, while developers have read/write access so that they can
make changes that become a permanent part of the project
repository. Please follow the appropriate set of instructions below.

<H3>Read-only access</H3>

<P>For read-only access from UNIX, Mac, or
<A HREF="http://www.cygwin.com/">Cygwin</a> (Windows with Unix
commands installed), log in to the CVS server using the command:

<pre>
  cvs -d :pserver:anonymous@cvs.sf.net:/cvsroot/topographica login
</pre>

When a password is requested, just press return.  Then change to
wherever you want the files to be stored, and use the command:

<pre>
  cvs -d :pserver:anonymous@cvs.sf.net:/cvsroot/topographica
  checkout -P -r LATEST_STABLE topographica
</pre>

(where the entire command should be on a single line, even though it
is broken into two lines above).  This process will likely take
several minutes (probably appearing to hang at certain points), as
there are some extremely large files involved.  The <code>-r
LATEST_STABLE</code> option selects the version that has most recently
been declared to pass all tests.  That option can be omitted if you
want the absolutely most up-to-date version, which may not always be
usable due to work in progress.

<P>In Windows without Cygwin, you can retrieve the files using
<A HREF="http://www.tortoisecvs.org/">TortoiseCVS</A> (tested 2/2006
using TortoiseCVS 1.8.25).  After installing TortoiseCVS, open the
Windows directory where you want the files to be located on your
machine, right click, select "CVS Checkout", fill in CVSROOT as
<code>:pserver:anonymous@cvs.sf.net:/cvsroot/topographica</code>, and
type in <code>topographica</code> for the module name.  Before
clicking OK, select the "Revision" tab and select "Choose branch or
tag", filling in "LATEST_STABLE" as the tag name (unless you want the
latest bleeding-edge development version).  When you click OK, the
files should be downloaded for you (though it may take some time).

<H3>Read/write access</H3>

For developers wanting read/write access, no login step is needed.
However, you may need to tell CVS to use <code>ssh</code>, because
most systems default to rsh, yet rsh is almost never supported in practice.
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

<P>Windows users can use the read-only procedure described
for TortoiseCVS above, replacing CVSROOT with
<code>:ext:<i>uname</i>@cvs.sourceforge.net:/cvsroot/topographica</code>.
You will typically need to have an SSH client installed for this to
work, such as
<A HREF="http://www.chiark.greenend.org.uk/~sgtatham/putty/">PuTTY</A>.

<P>Note that anyone interested in Topographica is welcome to join as a
Topographica developer to get read/write access, so that your changes
can become part of the main distribution.  Just email
<A HREF="mailto:&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107?subject=Request%20to%20be%20a%20Topographica%20developer">Jim</a>
and describe what you want to do, and he'll tell you what to do from there.

<H3>Building Topographica</H3>

The <code>topographica</code> directory you have now checked out
includes the files necessary to build Topographica on most platforms.
To make the build process simpler for developers using multiple
platforms, source code versions of the libraries needed are included,
and are created as part of the build process.  This approach makes the
initial compilation time longer and the simulator directory larger,
but it minimizes the changes necessary for specific platforms and
operating system versions.

<P><B>Linux:</B>
To build Topographica under Linux, just type <code>make</code> from
within the <code>topographica/</code> directory.  The build process
will take a while to complete (e.g. about 5-10 minutes on a 1.5GHz
Pentium IV machine with a local disk).  If you have PHP installed, you
can also make local copies of the HTML documentation from the web
site; to do so, type "make all" instead of (or after) "make".  "make
all" will also run the regression tests and example files, to ensure
that everything is functioning properly on your system.  At the
moment, be sure that you do this compilation on a machine with a
functioning DISPLAY, i.e., not a remote text-only session, or there
will be some warnings involving Tk.  

<P>If all goes well, a script named <code>topographica</code> will be
created in the <code>topographica/</code> directory; you can use this
to start Topographica as described in the <A
HREF="../Tutorials/index.html">Tutorials</A>.  If you have problems,
try adding <code>-k</code> to the <code>make</code> command, which
will allow the make process to skip any components that do not build
properly on your machine. Topographica is highly modular, and most
functionality should be accessible even without some of those
components.

<P><B>UNIX:</B>
Topographica is developed under Linux, but should work on other
versions of UNIX as well, as long as they have standard GNU tools like
make and GCC installed.  Just follow the Linux instructions, replacing
<code>make</code> with <code>gmake</code> if that's the name of GNU make on your system.

<P><B><A NAME="osx">Mac:</A></B>
Topographica builds only under Mac OS X or later.  Topographica
developers have only limited access to OS X machines, and so at any
time there may be some issues with the OS X version, although we do
try to minimize them.

<P>These instructions assume that you have an X server installed.  It
is also possible to build Topographica using a native (Aqua) version
of Python, which looks a bit nicer, but we have not yet documented how
to do that.

<P>To install under Mac OS X 10.4 (Tiger):

<ol>
<li> From the Apple developer web site, download 
<A HREF="http://developer.apple.com/tools/xcode/index.html">XCode_Tool2.2</a>
(among other development utilities, it provides the gcc C/C++
compiler for Topographica to use).
<li> Specify gcc 3.3 using: <code>sudo gcc_select 3.3</code>.  The
default 4.0 compiler is fine for most of the included packages, but
some people have reported that SciPy (weave) does not work with gcc 4.0.
<li> Download and install the <A HREF="http://fink.sourceforge.net/download/">Fink</a> package.
Also install the FinkCommander GUI, which makes finding and installing Unix software
more convenient.
<li> With Fink, find and install the following packages: <code>libpng</code> and 
<code>freetype219</code> (they provide, respectively, the PNG format
handling and the matplotlib library installation required to run
Topographica).
<li> If you want to compile the local copy of the documentation
(e.g. for online help), use Fink to get imagemagick, transfig, and m4,
plus php if it's not already installed.
<li> If CVS is not already installed on your Mac, find and install <code>cvsup</code>
(and the associated library and client) with Fink.
<li> Get, unpack, and make Topographica using CVS as described above.
</ol>

<P> Other OS X versions may require small changes to this procedure,
to make sure that compatible libraries are available.


<P><B>Windows:</B> The Topographica project is committed to supporting
Windows in the long term, but in the current stage of very active
development under Linux, the Windows version often lags behind and has
various minor quirks and installation difficulties.  Thus Windows
support should be considered experimental at this stage.

<P>In any case, there are two ways to build Topographica under
Windows: <A HREF="http://www.cygwin.com/">Cygwin</a> and Windows
native.  Cygwin offers a set of UNIX-compatible tools that make it
possible to compile UNIX-style programs under Windows, in which case
you can follow the generic Linux instructions above.  However, as of
1/2006 the library versions available on Cygwin are a bit out of date
and thus this process does not currently go smoothly.

<P>Instead of Cygwin, Topographica can also be configured to use
Win32-native versions of various support tools like Python.
However, there are again likely to be various problems related to
library versions at any given time, so installing the native version
is not necessarily straightforward.  <P>In any case, the basic steps
for building the native version are:

<ol>
<li> Double click on setup.bat 
<li> Follow the various installation prompts for the packages bundled with Topographica.
</ol>

<P>
If you do not wish to install to the default Windows program files
directory, you will instead need to run setup.bat from the command-line, with
the target base path as the first parameter.  For example, to install
to D:\Topographica, the command would be: "setup D:"

<P>
After installation you should now have an icon on your desktop that
opens the directory where Topographica is installed.  There will be a
new file association called ".ty"; these are scripts that the
Topographica program will execute when you double-click on them.

<P>You can now test the installation by double-clicking on the
topographica.bat file which will run the interactive Topographica
shell and give you a &quot;Topographica&gt;&quot; prompt.  You can
also double-click on some of the .ty files in the examples
directory.<P>If you experience any problems, or wish to install Weave
to enable the C-optimized functions, then please consult our detailed
<a href="win32.html">Windows installation/troubleshooting
instructions</a>.  Note that the performance of Topographica will be
extremely poor (i.e., slow) unless you do successfully install Weave.


<H3>Running Topographica</H3>

Once you have the code installed and built, go to your
topographica/ directory and type e.g.:

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
  ./topographica -g examples/lissom_or.ty
</pre>

For the latter two examples, a good way to get started is to work through 
the <A HREF="../Tutorials/som_retinotopy.html">SOM</A> or 
the <A HREF="../Tutorials/lissom_or.html">LISSOM</A> tutorials.

<H3>Updating Topographica</H3>

Once you have Topographica checked out, you can update to the latest
stable version at any time by doing:

<pre>
  cd topographica
  cvs update -d -P -r LATEST_STABLE
  make all
</pre>

<P>If you want the very most recent version, stable or not, replace
<code>-r LATEST_STABLE</code> with <code>-A</code> to force a complete
update. Under TortoiseCVS in Windows, you can right click in the
topographica directory and select CVS Update to get the new files.

<P>Note that updating the examples/ subdirectory sometimes takes
a long time, if the sample saved snapshot has been updated.
Similarly, updating the external/ subdirectory sometimes takes a long
time, if some of the external packages have been upgraded, and in that
case the "make all" can also take some time to build.


