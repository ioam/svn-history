<H2>Installing Topographica using CVS</H2>

<P><A HREF="http://www.nongnu.org/cvs/">CVS</A> (the Concurrent
Versions System) is the version control system used for managing
Topographica development.  It keeps track of every change made to any
file, and can reconstruct the state of the software from any date and
time in the history of Topographica development.  The Topographica CVS
repository is hosted by <A
HREF="http://sourceforge.net/projects/topographica">
SourceForge.net</A>.  The essentials for using CVS at SourceForge are
described below; see the <A
HREF="http://sourceforge.net/docman/display_doc.php?docid=29894&group_id=1">
SourceForge documentation</A> for more details or if you have any
difficulties.

<H3><A NAME="system-setup">Specifying a CVS repository</A></H3>

Many of the commands below require you to tell CVS where the
Topographica files are located and how to access them.  In these
commands, you should replace the string <code>$TOPOROOT</code> with
one of two different ways to access the files, depending on whether or
not you are an official Topographica developer.  Non-developers should
use the read-only version of the repository, with a
<code>$TOPOROOT</code> of:

<pre>
:pserver:anonymous@topographica.cvs.sf.net:/cvsroot/topographica
</pre>

Developers need read/write access, so that they can make changes that
become a permanent part of the project repository, and would use a
<code>$TOPOROOT</code> of:

<pre>
:ext:<i>uname</i>@topographica.cvs.sf.net:/cvsroot/topographica
</pre>

Here <i>uname</i> should be replaced with your SourceForge.net
username.

<P>Note that anyone interested in Topographica is welcome to join as a
Topographica developer to get read/write access, so that your changes
can become part of the main distribution.  Just sign up for a free
account at <A HREF="http://sourceforge.net/"> SourceForge.net</A>,
then email <A
HREF="mailto:&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107?subject=Request%20to%20be%20a%20Topographica%20developer">Jim</a>
your username and what you want to do,
and he'll tell you how to proceed from there.

<P>With either read-only or read-write access, you will need to choose
whether you want the very most recent version, with changes made
daily, or only the most recent stable version for which installation
packages have been created.  The very most recent version will be
called "bleeding-edge" below, while the stable version will be called
LATEST_STABLE.  Developers will want the very most recent version, as
will those working closely with developers.  Others will probably want
to stick to the LATEST_STABLE version except to fix specific problems.


<H3>Downloading via CVS</H3>

The CVS installation instructions differ on the various platforms, as
outlined below.  Regardless of platform, please note that the
Topographica repository contains some very large files, and the CVS
download process may appear to hang or freeze at various times while
these files are downloaded.  Unfortunately, CVS does not provide any
sort of feedback that this is occurring, so please just be patient
when downloading via CVS.  Such pauses should be rare after the first
CVS download, unless one of the large files has been updated.


<H4><A NAME="linux">Linux/UNIX:</A></H4>

Most Linux and other UNIX platforms already have all of the necessary
programs and libraries required for Topographica.  But if your
distribution does not include <code>cvs</code>, <code>ssh</code>, or
<code>php</code> by default, first obtain versions of those programs
for your system and install them.

<P>Then for read-only access, log in to the CVS server using the
command:

<pre>
  cvs -d $TOPOROOT login
</pre>

When a password is requested, just press return.

<P>For read/write access, no login step is needed, but you may need to
tell CVS to use <code>ssh</code> to transfer files.  Just type
<code>export CVS_RSH=ssh</code> for <code>sh/bash</code> or
<code>setenv CVS_RSH ssh</code> for csh/tcsh shells; you may wish to
put this in your shell startup script permanently.  The checkout and
update commands below should then ask for your SourceForge.net
password; if instead you get a message about rsh timing out, you have
probably forgotten to do the CVS_RSH command.

<P>For either read-only or read/write access, the actual files can be
checked out by changing to wherever you want the files to be stored,
and using the command:

<pre>
  cvs -d $TOPOROOT checkout -r LATEST_STABLE topographica
</pre>

The <code>-r LATEST_STABLE</code> option should be omitted if you want
the bleeding-edge version, which may not always be usable due to work
in progress.  The checkout process will likely take several minutes
(probably appearing to hang at certain points), as there are some
extremely large files involved.


<H4><A NAME="osx">Mac OS X</A></H4>

Topographica can be built on Mac OS X (or later) using the
<A HREF="#linux">Linux</A> instructions above, but you will likely
first need to install several packages needed by Topographica. These instructions also assume that you will be using Mac OS
X 10.4 (Tiger); other OS X versions may require small changes to this
procedure, to make sure that compatible libraries are available.  On
that version of the system, you would do:

<ol>
<li> If an X11 Xwindows server is not already installed, obtain one
  (free from Apple) and install it.  (It is also possible to build
  Topographica using a native (Aqua) version of Python, which looks a
  bit nicer, but we have not yet documented how to do that.)
<li> If the X11 Software Development Kit is not already installed,
install x11SDK from the Apple OS X distribution.  (You'll know if
it is missing if you get messages like
'error: X11/Xlib.h: No such file or directory'.)
<li> From the Apple developer web site, download 
<A HREF="http://developer.apple.com/tools/xcode/index.html">XCode_Tool2.2</a>
(among other development utilities, it provides the required GCC C/C++ compiler).
Other versions should also work, but have not been tested.
<li> Download and install the <A HREF="http://fink.sourceforge.net/download/">Fink</a> package.
Also install the FinkCommander GUI, which makes finding and installing Unix software
more convenient.
<li> With Fink, find and install the following packages: <code>libpng</code> and 
<code>freetype219</code> (they provide, respectively, the PNG format
handling and the font handling for the matplotlib library used 
by Topographica).
<li> If you want to compile the local copy of the documentation
(e.g. for online help), use Fink to get imagemagick, transfig, php,
and m4, if these are not already installed.
<li> If CVS is not already installed, find and install
<code>cvsup</code> (and the associated library and client) with Fink.
</ol>

<P>Once these programs are installed, Mac users can simply follow the
<A HREF="#linux">Linux</A> instructions above.  If you have trouble,
you might try specifying gcc 3.3 using <code>sudo gcc_select
3.3</code>.  (The default GCC 4.0 compiler works fine with recent
versions of Topographica under Linux, but has not yet been tested
under OS X.)

<H4><A NAME="windows">Windows:</A></H4>
<!--  CEBALERT: One day we might have instructions for building -->
<!--  Topographica on Windows, compiling everything from source...
<!--  see the list of current tasks.-->

<P>Under Windows, we recommend installing
<A HREF="http://www.tortoisecvs.org/">TortoiseCVS</A> (tested 11/2006
using TortoiseCVS 1.8.29). TortoiseCVS includes everything required
for read/write access, but if you are using another CVS client
you might also need an SSH client such as
<A HREF="http://www.chiark.greenend.org.uk/~sgtatham/putty/">PuTTY</A>.

<P>Then open the Windows directory where you want the files to be
located on your machine, right click, select "CVS Checkout", fill in
CVSROOT with the appropriate <code>$TOPOROOT</code>, and type in
<code>topographica</code> for the module name.  Before clicking OK,
select the <code>Revision</code> tab and select <code>Choose branch or
tag</code>, filling in <code>LATEST_STABLE</code> as the tag name
(unless you want the bleeding-edge version).  When you click OK, the
files should be downloaded for you (though it might take a little time). 

<P>Following this step, it is necessary to obtain the Windows versions
of Topographica's support tools. Change into the <code>topographica</code>
directory that you just checked out, and again right click and select
"CVS Checkout". Re-use the settings from before, but change the module name 
from <code>topographica</code> to <code>topographica-win</code>.
<!--CB: should we say to set the revision tag again this time, or does it 
remain the same? I forgot to check.-->
The wait to download will be longer this time, since the Windows support
tools are distributed as binaries.


<H4><A NAME="windows">Cygwin:</A></H4>

<P><A HREF="http://www.cygwin.com/">Cygwin</a> is a set of Unix
commands and libraries that make it possible to compile most Unix
programs under Windows.  In principle, it should be possible to
use Topographica under Cygwin, because all of the core Topographica
files are platform independent.  However, some of the external
packages included with Topographica (e.g. python's Tkinter)
automatically detect that they are running under Windows, and install
non-Cygwin versions of themselves.  Users interested in modifying
these makefiles so that Topographica can be installed under
Cygwin should <A
HREF="mailto:&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107">contact
Jim</a> for more details.


<H3>Problems with CVS?</H3>

Sometimes the SourceForge.net cvs service experiences problems. If you
receive messages such as "connection closed by remote host", or the
cvs connection times out, you may wish to check the SourceForge.net 
<a href="https://sourceforge.net/docman/display_doc.php?docid=2352&group_id=1">status
page</a>. Be aware that this page is not always updated as fast as
problems appear.


<H3>Updating using CVS</H3>

Linux/UNIX/Mac users who have Topographica checked out via CVS can
update to the latest stable version at any time by doing:

<pre>
  cd topographica
  cvs update -d -P -r LATEST_STABLE
  make all
</pre>

<P>This will retrieve the latest version for which installation
packages have been released.  If you want the very most recent
version, stable or not, replace <code>-r LATEST_STABLE</code> with
<code>-A</code> to force a complete update. Before updating to the
most recent version, you can check its status (i.e. whether or not it
builds successfully, and whether or not all the tests pass) by
visiting <a
href="http://buildbot.topographica.org/">buildbot.topographica.org</a>.



<P>Windows TortoiseCVS users can right click in the topographica
directory and select <code>CVS Update</code> to get the new files.

<P>Note that updating the external/ subdirectory sometimes takes a
long time, if some of the external packages have been upgraded, and in
that case "make all" can also take some time to build.

<H3>SSH Agent</H3>

If you do a lot of CVS updates, especially if you are a Topographica
developer, you may wish to set up CVS so that SourceForge.net does not
have to keep asking for your password for every transaction.  This can
be done using SSH, by <A
HREF="https://sourceforge.net/docs/F02/">setting up SSH and uploading
your public keys to sf.net</A>, then starting ssh-agent on your local
machine.  Once the agent is running, you should be able to use CVS
with no password.
