<H1>Revision control</H1>

<P>Revision control is by SVN.  Please check in changes as soon as
they are stable, e.g. at least by the end of each significant workday.
Conversely, be sure to update your checked out code before doing any
new work.  The goal is to make sure that all developers are always
working with the latest code.

<P>Every SVN commit <em>must</em> include an informative log message,
summarizing the items changed in easily understandable terms, and
avoiding pejorative language (i.e. comments like "Lord only knows what
idiot coded it that way!"). If possible (e.g. when adding a feature or
fixing a bug), try to link the commit log message to one of the sf.net
tracker IDs (and mention the revision number that fixed the bug when
closing it on sf.net).  When describing the changes, it is crucial to
examine every line produced by <CODE>svn diff</CODE> to verify that
only intentional changes (and not stray characters or temporary
changes) are checked in, and that the log message covers all the
important changes.  You should also do <CODE>svn status</CODE> to make
sure that you don't have any important files not yet checked into SVN,
as <CODE>svn diff</CODE> will not report these.

<P>If so many items were changed that any single log message would
have to be very general (e.g. "Misc changes to many files"), then
please check in smaller groups of files, each with a meaningful log
message. Using smaller,
meaningful chunks also makes debugging much easier later, allowing the
source of a new bug to be tracked down to a small, understandable set
of related changes.  Conversely, if the same trivial changes were made to a
large group of files, please check in all of those at once, with the
same log message, so that it will be clear that they go together.

<P>Ideally, each commit should reflect a single purpose (e.g. addition
of a new feature or a bug fix); each commit increments Topographica's
version number, and the log message applies to that whole version.
Therefore, when committing files, please do it in the appropriate
order and grouping so that the code works at every time in the SVN
repository history.  That is, if you change several files, adding a
function to one file and then calling it in another, consider if you should
check in the file with the new function first, or if you should
check in the two files together. In this situation you should certainly
<EM>not</EM> check in the file that calls the function before checking
in the file containing the function. In this opposite order, the
repository would temporarily be in a state where it could not supply
working code.  Even if you know no one else is working at that time,
such gaps make it much more difficult to debug using the SVN revision
history, because they make it impractical to roll back history one
change at a time to try to find the source of a bug.

<P>When making and checking in particularly extensive changes, please
keep refactoring completely separate from new features whenever
possible.  That is, if you have to change or clean up a lot of old
code in order to add a new feature, follow something like this
procedure:

<PRE>
  svn commit .	  # Commit all outstanding edits
  make tests	  # Verify that things work when you start
  emacs		  # Refactor old code, not changing behavior at all
  make tests      # Verify that nothing has been broken
  svn diff        # Will have many widespread changes
  svn commit -m    "No visible changes" .
  emacs		  # Add new feature and new test for it
  make tests      # See if tests still work, fixing if necessary
  svn diff	  # Short list: only the new code
  svn commit -m    "Added feature Y" .
</PRE>
  
That way nearly all of the lines and files you changed can be tested
thoroughly using the existing test suite as-is, and any tests added
can be tested equally well on both the old and new code.  Then the few
lines implementing the new feature can be added and debugged on their
own, so that it will be very simple to see whether the new feature was
the source of a bug, or whether it was all those other changes that
<i>shouldn't</i> have changed anything.


<H2>Revision info</H2>

<P>Every readable file (i.e. text, source code, html, etc.) should
include an <CODE>&#36;Id:&#36;</CODE> tag so that the SVN revision
information will be visible immediately, even in files outside of the
SVN repository.

<P>For text files, the <CODE>Id:</CODE> tag should be placed near the
top, surrounded by dollar signs, on a line by itself.  Near the bottom
is also acceptable, but not preferred.  See the top of the README.txt
file for an example; SVN fills in all but the letters "Id:" and the
dollar signs.

<P>For Python files, the <CODE>Id:</CODE> tag should be placed at the
end of the Python doc string for that module, surrounded by dollar
signs, on a line by itself.  

<P>If you include the following in
your <code>~/.subversion/config</code> file, these things will be done
automatically for you:

<pre>
# ... (other content you have already)
[auto-props]
# ... (other content you have already)
Makefile = svn:eol-style=native;svn:keywords="Author Date Id Revision"
*.ty = svn:eol-style=native;svn:keywords="Author Date Id Revision"
*.py = svn:eol-style=native;svn:keywords="Author Date Id Revision"
*.txt = svn:eol-style=native;svn:keywords="Author Date Id Revision"
*.diff = svn:eol-style=native
*.png = svn:mime-type=image/png
*.jpg = svn:mime-type=image/jpeg
</pre>

<p>You will usually also need to set "enable-auto-props yes", as the 
config file usually has auto-props disabled by default.

<!-- .cvsignore -> svn property on directory; document -->

<!--
CB: going to remove Revision tags?
In addition, just after the doc string,
the version number of the file should be declared.  For example:

<PRE>
  """
  The module documentation...

  &#36;Id&#36;
  """
  __version__ = "&#36;Revision&#36;"
</PRE>
-->


<!--
Authentication realm: <https://topographica.svn.sf.net:443> SourceForge Subversion area
-->



<!--
[lodestar]v1cball: svn commit ...
Authentication realm: <https://topographica.svn.sourceforge.net:443> SourceForge Subversion area
Password for 'v1cball': 

Authentication realm: <https://topographica.svn.sourceforge.net:443> SourceForge Subversion area
Username: ceball
Password for 'ceball': X

-->
