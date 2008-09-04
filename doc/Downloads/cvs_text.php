<H2>Installing Topographica using Subversion</H2>

<P><A HREF="http://subversion.tigris.org/">Subversion</A> (SVN) is the
version control system used for managing Topographica development.  SVN
keeps track of every change made to any file, and can reconstruct the
state of the software from any date and time in the history of
Topographica development since January 2004 (see the ChangeLog.txt
file for info on each revision).  The Topographica SVN repository
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

<P>Most Linux and other UNIX platforms already have all of the necessary
programs and libraries required for Topographica.  But if your
distribution does not include <code>svn</code> or <code>php</code> by
default, first obtain versions of those programs for your system and
install them.

<P>The Topographica files can be checked out by using the command:

<pre>
svn co $TOPOROOT/tags/LATEST_STABLE/topographica topographica
</pre>

<P>This will create a <code>topographica</code> directory in your present
working directory; omitting the final <code>topographica</code> will 
put the files directly into your present directory.

<P>To get the bleeding-edge (trunk) version, replace <code>tags/LATEST_STABLE</code> with 
<code>trunk</code>. Note that the bleeding-edge version is not always
usable due to work in progress (but you can check to see if the code
currently builds on a specific platform, or if our code tests pass, by
visiting our <A HREF="http://buildbot.topographica.org/">automatic
tests page</A>).

<P>The checkout process will likely take several minutes (probably
appearing to hang at certain points), as there are some extremely
large files involved. Once it has completed, you can return to
instructions for <a href="index.html#building-topographica">building
Topographica</a> (although ensure your system has the prerequisites as
listed on that page for your platform)</a>.


<H4><A NAME="osx">Mac OS X:</A></H4>

<!-- note that out-of-date X11 instructions were removed in 
r8900. At that revision, we topographica wasn't working with X11.-->

<P>Topographica can be downloaded via SVN on Mac OS X using the Linux
instructions, once you have obtained the Subversion program. You can
download and install a binary from
the <A HREF="http://subversion.tigris.org/getting.html">Subversion
downloads page</A>, or you can use your package manager to install
it. We have used Fink (installed as described in the list
of <A HREF="index.html#mac-prerequisites">prerequisites</A> for Mac):
in a Terminal window, type <code>fink install svn</code>.

<P>Once you have SVN, simply follow the <A HREF="#linux">Linux</A>
instructions above.


<H4><A NAME="windows">Windows:</A></H4>

<!--CB: I assume 32 bit win xp. Don't know how much that matters...-->

<P>We support obtaining Topographica by SVN and building it on Windows
via <A HREF="http://www.mingw.org/">MSYS/MinGW</A>. If your system
does not already have MSYS/MinGW, please install
MSYS 1.0.11 and MingGW 5.1.4 (from the MinGW <A HREF="http://sourceforge.net/project/showfiles.php?group_id=2435">download page</A>). Other versions might work, but we
have not tested them. 
<!--CBENHANCEMENT: readymade MSYS/MinGW in topographica-win: move or doc-->

<P>Once you have installed MSYS/MinGW, you will need to install Subversion.
The easiest way to do this is to download the installer from the 
<A HREF="http://subversion.tigris.org/getting.html">Subversion downloads
page</A>.

<P>Currently, we do not provide a method to compile Python on Windows.
Therefore, it is also necessary to install Python 2.5.2 if your system does
not already have
it. An <A HREF="http://python.org/ftp/python/2.5.2/python-2.5.2.msi">installer
package</A> is available from Python.org.

<P>Having installed Python, it is finally necessary to install two further 
packages that we do not yet support building from source:
<ul>
<li>Install <A HREF="http://effbot.org/downloads/PIL-1.1.5.win32-py2.5.exe">PIL 1.1.5</A> if your system does not already have it</li>
<li>Install the GNU <A HREF="http://downloads.sourceforge.net/gnuwin32/jpeg-6b-4.exe">JPEG library</A> (again, if your system does not already have it).</li>
</ul>

<P>Once these requirements are all present, you can follow the <A
HREF="#linux">Linux SVN</A> instructions above by opening an MSYS
terminal (double click on the MSYS icon on your desktop). Note that
while using an MSYS terminal, you can enter commands as given for
Linux/UNIX rather than any alternative that might be given for
Windows.  If you have any problems, please feel free to ask for help
in our <A
HREF="http://sourceforge.net/forum/forum.php?forum_id=552131">Windows
forum</A>.  


<!--
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
-->


<H3>Updating using Subversion</H3>

Users who have Topographica checked out via SVN can update their copy
of Topographica by changing to the directory containing the
Topographica files and then doing:

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
version, you can check its status on our 
<a href="http://buildbot.topographica.org/">automatic tests page</a>.)
Alternatively, to switch to a separate branch named 'some-branch', replace
<code>tags/LATEST_STABLE</code> with <code>branches/some-branch</code>

<!--CB: just trying it out; embedding an image would be best-->

<P>You can discover if your copy is from the trunk or a particular
branch or tag by typing <code>svn info | grep URL</code>.
<!--CB: will need to clarify this when revisions are in branches/ -->

<!--
To see what other versions of the code are available, you can view the
<a href="http://topographica.svn.sourceforge.net/viewvc/topographica/tags/">tags</a>
directory of the SVN repository in your web browser, or type
<code>svn ls --verbose $TOPOROOT/tags/</code>. 
-->

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
