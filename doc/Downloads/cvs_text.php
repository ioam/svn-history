<H2>Installing Topographica using Subversion</H2>

<P><A HREF="http://subversion.tigris.org/">Subversion</A> (SVN) is the
version control system used for managing Topographica development.  SVN
keeps track of every change made to any file, and can reconstruct the
state of the software from any date and time in the history of
Topographica development since 2004.  The Topographica SVN repository
is hosted by <A HREF="http://sourceforge.net/projects/topographica">
SourceForge.net</A>.  The essentials for using SVN at SourceForge are
described below; see the <A
HREF="http://sourceforge.net/docman/display_doc.php?docid=31070&group_id=1">
SourceForge SVN documentation</A> for more details or if you have any
difficulties.  You will need to run at least SVN 1.4 on your machine;
SVN clients 1.3 and below will complain that they are too old to
communicate with our repository.  If you don't need the very latest
updates, you can simply <a href="index.html">download a released
version</a> instead of using SVN.


<P>In the instructions below, you will need to choose whether you want
the very most recent version, with changes made daily, or only the
most recent stable version. <!--for which installation packages have
been created.--> The very most recent version will be called
"bleeding-edge" (or "trunk") below, while the stable version will be called
LATEST_STABLE.  Developers will want the very most recent version, as
will those working closely with developers.  Others will probably want
to stick to the LATEST_STABLE version except to fix specific problems.


<H3>Downloading via Subversion</H3>

The SVN installation instructions differ on the various platforms, as
outlined below.  Regardless of platform, please note that the
Topographica repository contains some very large files, and the SVN
download process may appear to hang or freeze at various times while
these files are downloaded.  Unfortunately, SVN does not provide any
sort of feedback that this is occurring, so please just be patient
when downloading.  Such pauses should be rare after the first SVN
download, unless one of the large files has been updated.

<P>The location (URL) of the Topographica repository is:
<pre>
https://topographica.svn.sourceforge.net/svnroot/topographica
</pre>

In commands given on this page, <code>$TOPOROOT</code> is used to
represent that URL, so please replace it in commands you enter. (For
instance, linux users might first type
<code>export TOPOROOT=https://topographica.svn.sourceforge.net/svnroot/topographica</code>,
and then <code>$TOPOROOT</code> will be substituted for them in the
commands below.)



<H4><A NAME="linux">Linux/UNIX:</A></H4>

Most Linux and other UNIX platforms already have all of the necessary
programs and libraries required for Topographica.  But if your
distribution does not include <code>svn</code>
<!--CB: with ssl?-->
or <code>php</code> by default, first obtain versions of those programs
for your system and install them.

<P>The Topographica files can be checked out by using the command:

<pre>
svn co $TOPOROOT/tags/LATEST_STABLE/topographica topographica
</pre>

<P>This will create a <code>topographica</code> directory in your present
working directory; omitting the final <code>topographica</code> will 
put the files directly into your present directory.

<P>To get the bleeding-edge (trunk) version, replace <code>tags/LATEST_STABLE</code> with 
<code>trunk</code>. Note that the bleeding-edge version
is not always usable due to work in progress (but you can check to see if the
code currently builds on a specific platform
(<a href="http://buildbot.topographica.org/one_box_per_builder?builder=linux_build">linux</a>,
<a href="http://buildbot.topographica.org/one_box_per_builder?builder=mac_build">Mac</a>) and whether our   
<a href="http://buildbot.topographica.org/one_box_per_builder?builder=linux_tests&builder=linux_slow-tests">code tests pass</a>).

<P>The checkout process will likely take several minutes (probably
appearing to hang at certain points), as there are some extremely
large files involved.


<H4><A NAME="osx">Mac OS X:</A></H4>

Topographica can be built on Mac OS X (or later) using the <A
HREF="#linux">Linux</A> instructions above, but you will likely first
need to install several packages required by Topographica. These
instructions also assume that you will be using Mac OS X 10.4 (Tiger);
other OS X versions may require small changes to this procedure, to
make sure that compatible libraries are available.  On that version of
the system, you would do:

<ol>

<!--CEBALERT: these instructions are out of date, right? 
E.g. there's no binary fink for 10.5 -->

<li> If an X11 Xwindows server is not already installed, install
Apple's <a
href="http://www.apple.com/support/downloads/x11formacosx.html">X11
for Mac</a> (also available on the OS X installation DVD).  (It is
also possible to build Topographica using a native (Aqua) version of
Python, which looks a bit nicer, but we have not yet documented how to
do that.)

<li> If the X11 Software Development Kit (X11 SDK) is not already
installed, add that too.  (You'll know if it is missing if you get
messages like 'error: X11/Xlib.h: No such file or directory'.)

<li> From the Apple developer web site, download <A
HREF="http://developer.apple.com/tools/download/">Xcode 2.4.1</A>
(which, among other development utilities, provides the required GCC
C/C++ compiler).  Other versions should also work, but have not
necessarily been tested.

<li> Download and install the <A
HREF="http://www.finkproject.org/download/">Fink 0.8.1 Binary Installer</A>
package. Again, other versions should work, but have not necessarily
been tested. 
<!--CB: evaluate macports?-->

<li> Start an X11 terminal and enter the following command: <code>fink
install cvs libpng3 freetype219</code>. (These packages provide,
respectively, the CVS program required to access the Topographica code
repository, the PNG format handling, and the font handling for the
matplotlib library used by Topographica.)

<li> If you want to compile a local copy of the documentation
(e.g. for online help), use Fink to get imagemagick, transfig, php,
and m4 (if these are not already installed): <code>fink install
php4 m4 tetex imagemagick transfig</code>.
<!-- with fink for os x 10.5 (i.e. not binary fink), this command 
takes at least 6 hours to run on sake...and then it finishes with:
Failed: Fink::SysState: Could not resolve inconsistent dependencies-->
</ol>

<P>If you have trouble running <code>fink</code>, make sure the Fink
installation is actually in your path (the default Fink path is
<code>/sw/bin/</code>; the installer should have set this up for
you). Also, if you prefer not to use the commandline, you can install
<a href="http://finkcommander.sourceforge.net/">FinkCommander</a>, a
GUI for Fink that allows you to search for the packages above and
click to install them.

<P>Once these programs are installed, simply follow the <A
HREF="#linux">Linux</A> instructions above.

<!--If you have trouble, you might try specifying gcc 3.3 using
<code>sudo gcc_select 3.3</code>. CB: Installing xcode and fink-0.8.1
binary on 2007/09/05, then following the mac instructions, no
additional steps are required on ppc or intel macs (apart from
removing LDFLAGS as described in index_text.php).-->


<H4><A NAME="windows">Windows:</A></H4>
<!--  CEB: One day we might have instructions for building -->
<!--  Topographica on Windows, compiling everything from source...
<!--  see the list of current tasks.-->

<P><em>Please note that we have only recently moved from an older
revision control system (CVS) to SVN, and the SVN setup on Windows is
not yet complete.  To get the SVN version to build on Windows as of
1/2008, you will probably need to update some of the included external
packages.</em>

<P>Under Windows, we recommend installing
<A HREF="http://www.tortoisesvn.net/">TortoiseSVN</A> (tested 01/2008
using TortoiseSVN 1.4.7), which comes as an easy-to-install
executable. In general, TortoiseSVN users can easily translate
commandline SVN instructions (e.g. those we give for linux users) by
right clicking in an SVN-controlled directory and choosing the
appropriate command from the TortoiseSVN submenu.

<!--TortoiseCVS includes everything required
for read/write access, but if you are using another CVS client
you might also need an SSH client such as
<A HREF="http://www.chiark.greenend.org.uk/~sgtatham/putty/">PuTTY</A>.
-->

<P>After installing TortoiseSVN if you do not already have it, open
the Windows directory where you want the Topographica files to be
located on your machine (you might first wish to create a
'topographica' folder), then right click, select <code>SVN
Checkout</code>, and fill in the <code>URL of repository</code> with
<pre>
https://topographica.svn.sourceforge.net/svnroot/topographica/tags/LATEST_STABLE/topographica
</pre>

Ensure that the <code>Checkout directory</code> shows the location
into which you want the files to be placed (e.g. <code>c:\Documents
and Settings\username\My Documents\topographica</code>), then
click <code>OK</code>. As the files download, you will be informed of
the transfer speed and amount transferred; the total as of 01/2008 is
about 85 MBytes.

<P>Following this step, it is necessary to obtain the Windows versions
of Topographica's support tools. In the folder that contains your
new <code>topographica</code> folder (i.e. the parent folder
of <code>topographica</code>), right click again and choose <code>SVN
Checkout</code> as before. Edit the last part of <code>URL of
repository</code>, changing
<code>topographica</code> to <code>topographica-win</code>. The URL
should then read: 
<pre>
https://topographica.svn.sourceforge.net/svnroot/topographica/tags/LATEST_STABLE/topographica-win
</pre>
After clicking <code>OK</code>, you will have to wait longer
than last time, since the Windows support tools are distributed as
binaries (the total as of 01/2008 is about 125 MBytes).

<P>Once the transfer has completed, move
the <code>topographica-win</code> folder into
the <code>topographica</code> folder (e.g. right click and hold down
on <code>topographica-win</code>, drag over <code>topographica</code>,
let go, then choose <code>Move</code>).

<P>Now that you have TortoiseSVN installed, and the SVN version of
Topographica, you can return to instructions
for <a href="index.html#building-topographica">building
Topographica</a>.

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


<!-- CB: error messages need to be updated. Maybe see if we get any
these days?
<H3>Problems with SVN?</H3>

Sometimes the SourceForge.net svn service experiences problems. If you
receive messages such as "connection closed by remote host", or the
cvs connection times out, you may wish to check the SourceForge.net 
<a href="https://sourceforge.net/docman/display_doc.php?docid=2352&group_id=1">status
page</a>. Be aware that this page is not always updated as fast as
problems appear.
-->


<H3>Updating using Subversion</H3>

Linux/UNIX/Mac users who have Topographica checked out via SVN can
update their copy of Topographica by changing to the
directory containing the Topographica files and then doing:

<pre>
  svn update 
  make
</pre>


<P>If you previously checked out the LATEST_STABLE version of
Topographica, this will update to the current LATEST_STABLE
code. If you previously checked out the 
bleeding-edge (trunk) version of Topographica, this will update
to the absolute most recent version of the code.

<P>If you wish, you can switch your copy of Topographica to 
a different version of the code. For instance, if you currently have the 
trunk version, you can switch to the LATEST_STABLE version
by typing:
<pre>
svn switch $TOPOROOT/tags/LATEST_STABLE/topographica
</pre>

To switch from the LATEST_STABLE version to the trunk version, replace
<code>tags/LATEST_STABLE</code> with <code>trunk</code>.  (Note that
before deciding whether to update to the bleeding-edge (trunk)
version, you can check its
<a href="http://buildbot.topographica.org/one_box_per_builder?builder=linux_tests&builder=linux_slow-tests">status</a>.)
Alternatively, to switch to a separate branch named 'some-branch', replace
<code>tags/LATEST_STABLE</code> with <code>branches/some-branch</code>

<!--CB: just trying it out; embedding an image would be best-->

<P>You can discover if your copy is from the trunk or a particular
branch or tag by typing <code>svn info | grep URL</code>.
<!--CB: will need to clarify this when revisions are in branches/ -->
To see what other versions of the code are available, you can view the
<a href="http://topographica.svn.sourceforge.net/viewvc/topographica/tags/">tags</a>
directory of the SVN repository in your web browser, or type
<code>svn ls --verbose $TOPOROOT/tags/</code>. 



<P>Windows TortoiseSVN users can right click in the topographica
directory and select <code>SVN Update</code> to get the new files.

<P>Note that updating the external/ subdirectory sometimes takes a
long time, if some of the external packages have been upgraded, and in
that case "make" can also take some time to build.





<!--CB svn caches username and password by default (caches with the
working copy forever, it seems?); decide what to do with the text
below 

<H3>SSH Agent</H3>

If you do a lot of CVS updates, especially if you are a Topographica
developer, you may wish to set up CVS so that SourceForge.net does not
have to keep asking for your password for every transaction.  This can
be done using SSH, by <A
HREF="https://sourceforge.net/docs/F02/">setting up SSH and uploading
your public keys to sourceforge.net</A>, then starting ssh-agent on your local
machine.  Once the agent is running, you should be able to use CVS
with no password.
-->
