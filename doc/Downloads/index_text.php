<H2><A NAME="installing-topographica">Installing Topographica</A></H2>

<P>Topographica is developed under Linux, and is also supported for
Windows and Mac OS X.  It should work on non-Linux versions of UNIX as
well, as long as standard GNU tools like make and GCC are installed.

<P>Whatever platform you use, there are two ways to obtain
Topographica.  The first, described below and recommended for most
users, is to download one of our installation packages for official
releases. The second is to use Subversion (SVN), as described on a
<A HREF="cvs.html">separate page</A>, for users who want more frequent
updates, or who need to modify the source code.

<P>If you want to run large simulations (requiring more than about 3
GB of memory), you should build and run Topographica on a 64-bit
platform. No change to the installation procedure is necessary when
when using such a platform. <!--Tested only on 64-bit linux so
far. When there are binaries, will need to mention about selecting the
right one-->

<P>The following sections describe how to obtain Topographica and build it (if
necessary) 
on <A HREF="#win">Windows</A>, <A HREF="#mac">OS X</A>,
and <A HREF="#lin">Linux/UNIX</A>. 


<H3><A NAME="win">Windows</A></H3>

<P>Windows users will generally want to use the self-installing <a
href="https://sourceforge.net/project/platformdownload.php?group_id=53602&sel_platform=6233">.exe</a>
file we provide. Once you have installed it, you can skip straight to
the <A HREF="#postinstall">After Installation</A> section below.

<H4><A NAME="win-prerequisites">Build from source</H4>

<P>If instead you want to develop Topographica on Windows, or you want
frequent updates, you will probably need to install some additional
software on your machine.

<!--CB: I assume 32 bit win xp. Don't know how much that matters...-->

<P>We first recommend that you install a more convenient environment
for working at the command line than is provided by default. We
support building Topographica on Windows via <A
HREF="http://www.mingw.org/">MSYS/MinGW</A>. If your system does not
already have MSYS/MinGW, please install MSYS 1.0.11 and MingGW 5.1.4
(from the MinGW <A
HREF="http://sourceforge.net/project/showfiles.php?group_id=2435">download
page</A>). Other versions might work, but we have not tested them.

<!--CBENHANCEMENT: readymade MSYS/MinGW in topographica-win: move or doc-->

<P>In addition to MSYS, because we do not currently provide a method
to compile Python on Windows, it is also necessary to install Python
2.5 if your system does not already have it. An <A
HREF="http://python.org/ftp/python/2.5.2/python-2.5.2.msi">installer
package</A> is available from Python.org. Note that currently Python
must be installed to <code>c:\Python25\</code>.

<P>Having installed Python, you also need to install some 
extra packages that we do not yet support building from source:
<ul>
<li>Install <A HREF="http://effbot.org/downloads/PIL-1.1.5.win32-py2.5.exe">PIL 1.1.5</A> if your system does not already have it</li>
<!--CEBALERT: JPEG lib is included in pil binary, I think
<li>Install the GNU <A HREF="http://downloads.sourceforge.net/gnuwin32/jpeg-6b-4.exe">JPEG library</A> (again, if your system does not already have it).</li>
-->
<li>Download and extract <A HREF="http://sourceforge.net/project/showfiles.php?group_id=11464&package_id=107795&release_id=562098">tile082.zip</A>; put the <code>tile0.8.2/</code> directory into your <code>topographica/Lib/</code> directory.
</ul>

<P>

<P>Once these requirements are all present, you can follow the <A
HREF="#common-obtain">common instructions</A> below by using an MSYS
terminal (double click on the MSYS icon on your desktop; note that
while using an MSYS terminal, you can enter commands as given for
Linux/UNIX rather than any alternative that might be given for
Windows).


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

<P>Now it is necessary to install two third-party support libraries -
libpng and freetype - if your system does not already have them. These
provide the PNG format handling and the font handling for the
matplotlib library used by Topographica, and can be installed however
you wish: you can download binaries, or, if you have a package manager
such as <A HREF="http://www.finkproject.org/">Fink</A>
or <A HREF="http://www.macports.org/">MacPorts</A>, you can use it to
obtain and install them. We have used Fink successfully:
<!--CB: maybe we should consider using macports instead?
https://sourceforge.net/forum/message.php?msg_id=7426788-->
<ul>
<li>Download and install the <A
HREF="http://www.finkproject.org/download/">Fink 0.9.0 Binary
Installer</A> package. Again, other versions should work, but have not
necessarily been tested.
<li> Start the Terminal application (usually found in the Utilities
folder in the Applications section of Finder) and enter the following
command:
<code>fink install libpng3 freetype219</code>. 
<!--libpng might already be present on macs...--> 

<li> <em>Optional</em>: If you want to compile a local copy of the documentation
(e.g. for online help), use Fink to get imagemagick, transfig, php,
and m4 (if these are not already installed): <code>fink install
php5-cli m4 tetex imagemagick transfig</code>.  However, this takes
about half a day to run (as it needs to compile everything from
source), and you first have to set fink to its <a href="http://www.finkproject.org/faq/usage-fink.php?phpLang=en#unstable">unstable branch</a>.

</ul>

<P>If you have trouble running <code>fink</code>, make sure the Fink
installation is actually in your path (the default Fink path is
<code>/sw/bin/</code>; the installer should have set this up for
you). Also, if you prefer not to use the commandline, you can install
<a href="http://finkcommander.sourceforge.net/">FinkCommander</a>, a
GUI for Fink that allows you to search for the packages above and
click to install them.

<P>Finally, if you do not already have Tcl/Tk version 8.5 or later
installed on your system, you will need to install it to use the
Topographica GUI. The easiest method is to
install <A HREF="http://www.activestate.com/Products/activetcl/">ActiveTcl</A>,
although any Framework build of Tcl/Tk 8.5 should work.

<P>Having satisfied these prerequisites, you can follow the
instructions for <A HREF="#common">obtaining and building</A>
Topographica.


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
<code>libx11-dev</code>, 
<code>libxft-dev</code> <!--for antialiased fonts-->, and 
<code>zlib</code>,
before <code>make</code> will succeed.  On some systems the
<code>-dev</code> packages are called <code>-devel</code>, and
sometimes specific versions must be specified (e.g.
<code>libpng12-dev</code>,
<code>libfreetype6-dev</code>).  Example for Ubuntu 7.0 or 8.04.1:
<blockquote><code>sudo apt-get install  libfreetype6 libfreetype6-dev libpng12-0 libpng12-dev libx11-dev libxft-dev zlib1g m4</code></blockquote>

<P>Once these libraries are installed, you can proceed to
the <A HREF="#common-obtain">common instructions</A> for all
platforms.


<H3><A NAME="common">All platforms</A></H3>

<P>The instructions below assume you have followed any necessary
platform-specific instructions described above.

<H4><A NAME="common-obtain">Obtaining Topographica</A></H4>

<P>If you want frequent updates, or you want to modify the source
code, please first follow our <A HREF="cvs.html">SVN
instructions</A>. Otherwise, download either the <code>.zip</code>
or <code>.tar.gz</code> archive package from our
<A HREF="http://sourceforge.net/project/showfiles.php?group_id=53602">downloads</A>
page, and then unpack it. You will need to do this in a writable
directory with approximately 800 megabytes of spaces available (as of
2/2009).

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

<P>Once you have satisfied the prerequisites for your platform and
have downloaded and extracted Topographica, type
<code>make</code> (which may be called <code>gmake</code> on some
systems) from within the <code>topographica/</code> directory.  It is
best to do this as a regular user in the user's own directory, not as
a root user with special privileges, because Topographica does not
need any special access to your system.  The build
process will take a while to complete (e.g. about 5-10 minutes on a
1.5GHz Pentium IV machine with a local disk).

<P>If all goes well, a script named <code>topographica</code> will be
created in the <code>topographica/</code> directory. If you have
problems during the build process, try adding <code>-k</code> to the
<code>make</code> command, which will allow the make process to skip
any components that do not build properly on your
machine. Topographica is highly modular, and most functionality should
be accessible even without some of those components. If you do
experience problems during the installation or subsequent use of
Topographica on your platform, please check our <A
HREF="../FAQ/index.html#plat">platform-specific FAQ</A>.

<P>If desired, you can also make local copies of the HTML
documentation from the web site. To do so, you must have the php, m4,
bibtex, convert, and fig2dev commands installed; type <code>make
all</code> instead of (or after) <code>make</code>.  (If you don't
have those commands, in most distributions you can get them by
installing the php5-cli, m4, tetex, imagemagick, and transfig
<!--CEBALERT: tetex not in ubuntu 9.04; not sure what the new package is-->
packages).  <code>make all</code> will also run the regression tests
and example files, to ensure that everything is functioning properly
on your system.  If you do the tests on a machine without a
functioning DISPLAY, such as a remote text-only session, there will be
some warnings about GUI tests being skipped.


<H3><A NAME="postinstall">After installation</A></H3>

<P>Linux, Mac, and Windows MSYS users can use the
<code>topographica</code> script to start Topographica. Windows users
who installed the .exe can double click on the Topographica icon on
the desktop. 

<P>Running Topographica interactively is described in more detail in
the <A HREF="../User_Manual/scripts.html">User Manual</A>. If you want
to get straight into working with a full network, a good way to begin
is by working through the <A
HREF="../Tutorials/som_retinotopy.html">SOM</A> or <A
HREF="../Tutorials/lissom_oo_or.html">LISSOM</A> tutorials.

<P> Have fun with Topographica, and be sure to subscribe to the <A
HREF="https://lists.sourceforge.net/lists/listinfo/topographica-announce">topographica-announce</A>
mailing list to hear about future updates!



