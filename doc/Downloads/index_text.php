<H2><A NAME="installing-topographica">Installing Topographica</A></H2>

<P>Topographica is developed under Linux, and is also supported for
Windows and Mac OS X.  It should work on non-Linux versions of UNIX as
well, as long as standard GNU tools like make and GCC are installed.

<P>Whatever platform you use, there are two ways to obtain
Topographica.  The first, recommended for most users, is to download
one of our installation packages. The second is to
use <A HREF="http://subversion.tigris.org/">Subversion</A> (SVN). This
is recommended for users who want more frequent updates, or who need
to modify the source code.

<P>The following sections describe how to obtain, build (if
necessary), and run Topographica
on <A HREF="#win">Windows</A>, <A HREF="#mac">OS X</A>,
and <A HREF="#lin">Linux/UNIX</A>.


<H3><A NAME="win">Windows</A></H3>

<P>Windows users will generally want to use the installation program we
provide, but if you want to develop Topographica on Windows, you will
need instead to follow the instructions on building from source. 

<H4>Installation program</H4>

<P>The easiest way to install Topographica is to download and run the
self-installing
<a href="https://sourceforge.net/project/platformdownload.php?group_id=53602&sel_platform=6233">.exe</a> file. Once you have done this, you can skip straight to the 
<A HREF="#running-topographica">Running Topographica</A> instructions
below.

<H4>Build from source</H4>

<P>If you want frequent updates or you want to modify the source,
first follow our <A HREF="cvs.html">SVN instructions</A>. Having
installed the software recommended there (including MSYS/MinGW), you
can open an MSYS terminal by double clicking the icon on your
desktop. From there, change to the directory where you downloaded
Topographica (e.g. <code> cd /c/topographica/</code>) and
type <code>make win-msys-patch</code>.  Once that command has
completed, you can follow the <A HREF="#building-topographica">linux
build</A> instructions below.



<H3><A NAME="mac">Mac OS X</A></H3>

<P>Although we plan to offer a binary installer for OS X, none is yet
available. Fortunately, building Topographica on OS X is
straightforward. The instructions here assume you are using OS X 10.5
(Leopard), but should work on any version with minor alterations to
provide the required libraries.

<H4><A NAME="mac-prerequisites">Prerequisites</A></H4>

<!-- CEBALERT: need to run through these on a fresh OS X 10.5 machine 
Particularly, try with latest Xcode.-->

<P>If your system does not already have Apple's Xcode installed,
download <A HREF="http://developer.apple.com/tools/xcode/">Xcode
3.0</A> from the Apple developer web site. Xcode provides the required
GCC C/C++ compiler (among other development utilities). Other versions
should also work, but have not necessarily been tested.

<P>Now it is necessary to install two third-party support libraries
(libpng and freetype) if your system does not already have them. These
can be installed however you wish; you can download binaries, or, if
you have a package manager such
as <A HREF="http://www.finkproject.org/">Fink</A>
or <A HREF="http://www.macports.org/">MacPorts</A>, you can use it to
obtain and install them. We have used Fink successfully:
<ul>
<li>Download and install the <A
HREF="http://www.finkproject.org/download/">Fink 0.9.0 Binary
Installer</A> package. Again, other versions should work, but have not
necessarily been tested.
<li> Start the Terminal application (usually found in the Utilities folder
in the Applications section of Finder) and enter the following command:
<code>fink install libpng3 freetype219</code>. (These packages
provide, respectively, the Subversion program required to access the
Topographica code repository, the PNG format handling, and the font
handling for the matplotlib library used by Topographica.)

<!--
 <li> If you want to compile a local copy of the documentation
(e.g. for online help), use Fink to get imagemagick, transfig, php,
and m4 (if these are not already installed): <code>fink install
php4 m4 tetex imagemagick transfig</code>.
-->
<!-- with fink for os x 10.5 (i.e. not binary fink), this command 
takes at least 6 hours to run on sake...and then it finishes with:
Failed: Fink::SysState: Could not resolve inconsistent dependencies-->
<!--above comment might be out of date now because there's binary fink 
for 10.5 -->

<li>If you have trouble running <code>fink</code>, make sure the Fink
installation is actually in your path (the default Fink path is
<code>/sw/bin/</code>; the installer should have set this up for
you). Also, if you prefer not to use the commandline, you can install
<a href="http://finkcommander.sourceforge.net/">FinkCommander</a>, a
GUI for Fink that allows you to search for the packages above and
click to install them.
</ul>


<P>Finally, if you do not already have Tcl/Tk version 8.5 or later
installed on your system, you will need to install it to use the
Topographica GUI. The easiest method is to
install <A HREF="http://www.activestate.com/Products/activetcl/">ActiveTcl</A>,
although any Framework build of Tcl/Tk 8.5 should work.

<P>Having obtained these prerequisites, you can now download Topographica.


<H4>Obtaining Topographica</H4>
 
<!--Might be better just to duplicate linux section here-->
<P>After opening a Terminal (usually found in the Utilities folder in
the Applications section of Finder), please follow the instructions
for <A HREF="#linux-obtaining">obtaining Topographica in
linux</A>. Once you have followed that section, you can proceed to build
Topographica as described below.

<H4>Building Topographica</H4>

<P>Again using the Terminal, enter the <code>topographica</code>
directory and type <code>make osx-tk-patch</code> (this allows
Python to find the correct version of Tcl/Tk). Having done this,
please now follow the instructions for <A HREF="#building-topographica">building
Topographica on linux</A>.


<H3><A NAME="lin">Linux/UNIX</A></H3>

<P>Currently, we do not offer binary installers for Linux, so it is
necessary to build Topographica after obtaining it. This is usually
straightforward.

<H4><A NAME="linux-prerequisites">Prerequisites</A></H4>

<P>Most Linux systems will already have the required libraries
installed, so usually no action will be required here. 

<P>On some Linux
distributions that start with a minimal set of packages included, such
as Ubuntu or the various "live CD" systems, you may need to specify
explicitly that some standard libraries be installed in your system,
such as
<code>libfreetype</code>,
<code>libfreetype-dev</code>,
<code>libpng</code>,
<code>libpng-dev</code>,
<code>libx11-dev</code>, and
<code>zlib</code>,
before <code>make</code> will succeed.  On some systems the
<code>-dev</code> packages are called <code>-devel</code>, and
sometimes specific versions must be specified (e.g.
<code>libpng12-dev</code>,
<code>libfreetype6-dev</code>).  Example for Ubuntu 7.10:
<blockquote><code>sudo apt-get install  libfreetype6 libfreetype6-dev libpng12-0 libpng12-dev libx11-dev zlib1g</code></blockquote>

<P>Once these libraries are installed, you can proceed to obtain Topographica.



<H4><A NAME="linux-obtaining">Obtaining Topographica</A></H4>

<P>If you want frequent updates, or you want to modify the source
code, please first follow our <A HREF="cvs.html">SVN
instructions</A>. Otherwise, download either the <code>.zip</code>
or <code>.tar.gz</code> archive package from our
<A HREF="http://sourceforge.net/project/showfiles.php?group_id=53602">downloads</A>
page, and then unpack it. You will need to do this in a writable
directory with approximately 500 megabytes of spaces available (as of
10/2007).

<H4><A NAME="building-topographica">Building Topographica</A></H4>

<!--
Once you have obtained the <code>topographica</code> directory, you
are ready to build Topographica.  This directory contains the files
making up Topographica itself, plus source code versions of most of the
various external libraries needed by Topographica.  At present, the
libraries are included in source code form to minimize
platform-specific modifications needed for different systems, although
this approach does increase the disk space and compile time
requirements.
-->

<P>Once you have satisfied the prerequisites and have downloaded and
extracted Topographica, just type
<code>make</code> (which may be called <code>gmake</code> on some
systems) from within the <code>topographica/</code> directory.  It is
best to do this as a regular user in the user's own directory, not as
a root user with special privileges, because Topographica does not
need any special access to your system.  You will currently (10/2007)
need to do this on a machine with a functioning DISPLAY, not on a
remote text-only windowless session, because of build requirements for
the MatPlotLib library.  (Note that many systems provide xfvb for this
very purpose, and in such cases you can simply type <code>xvfb-run
make</code> to build using a virtual display instead.)  The build
process will take a while to complete (e.g. about 5-10 minutes on a
1.5GHz Pentium IV machine with a local disk).

<P>If you have the php, m4, bibtex, convert,
and fig2dev commands installed, you can also make local copies of the
HTML documentation from the web site; to do so, type <code>make
all</code> instead of (or after) <code>make</code>.  (If you don't
have those commands, in most distributions you can get them by
installing the php, m4, tetex, imagemagick, and transfig packages).
<code>make all</code> will also run the regression tests and example
files, to ensure that everything is functioning properly on your
system.  If you do the tests on a machine without a functioning
DISPLAY, such as a remote text-only session, there will be some
warnings about GUI tests being skipped.

<P>If all goes well, a script named <code>topographica</code> will be created in the
<code>topographica/</code> directory; you can use this to start
Topographica as described in
the <A HREF="#running-topographica">Running Topographica</A> section
below.  If you have problems, try adding <code>-k</code> to
the <code>make</code> command, which will allow the make process to
skip any components that do not build properly on your
machine. Topographica is highly modular, and most functionality should
be accessible even without some of those components.



<H3><A NAME="running-topographica">Running Topographica</A></H3>

Once you have the program installed and built, you can run
Topographica on the example models.  On most systems (including Linux,
Unix, and Mac), just open a terminal window, go to your topographica/
directory, and type e.g.:

<pre title="Win: topographica -g examples\cfsom_or.ty">
  ./topographica -g examples/cfsom_or.ty
</pre>

or

<pre title="Win: topographica -g examples\hierarchical.ty">
  ./topographica -g examples/hierarchical.ty
</pre>

or

<pre title="Win: topographica -g examples\som_retinotopy.ty">
  ./topographica -g examples/som_retinotopy.ty
</pre>

or

<pre title="Win: topographica -g examples\lissom_oo_or.ty">
  ./topographica -g examples/lissom_oo_or.ty
</pre>

(Windows users can type similar commands at a Windows command prompt:
hold your mouse over a command above to see the Windows equivalent, or
see our note about <A
HREF="win32notes.html#unix-commands-on-win">translating Unix shell
commands to Windows</A>.  Alternatively, Windows users can double
click on one of the <code>.ty</code> scripts in the examples
directory; <code>.ty</code> files are associated with Topographica.)

<P>Note that the first time Topographica is run on a given example,
there may be a short pause while the program compiles some of the
optimized components used in that example.  (Some components,
generally those with <code>_opt</code> in their names, use code
written in C++ internally for speed, and this code must be compiled.)
The compiled versions are stored in <code>~/.python25_compiled/</code>
on most systems (or in the temporary directory
<code>%TEMP%\%USERNAME%</code> on Windows), and they will be reused on
the next run unless the source files have changed.  Thus you should
only notice such pauses the first time you use a particular component,
at which time you may also notice various inscrutable messages from
the compiler (which may generally be ignored).

<P>In any case, a good way to get started with these examples is to
work through  
the <A HREF="../Tutorials/som_retinotopy.html">SOM</A> or 
<A HREF="../Tutorials/lissom_oo_or.html">LISSOM</A> tutorials.
Have fun with Topographica, and be sure to subscribe to the 
<A
HREF="https://lists.sourceforge.net/lists/listinfo/topographica-announce">topographica-announce</A>
mailing list to hear about future updates!


