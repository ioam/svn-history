<!-- -*-html-helper-*- mode -- (Hint for Emacs)-->

<H1>Reporting specific problems with Topographica</H1>

<P>Topographica is used actively in research, and is thus continuously
changing, which inevitably adds new problems as old ones are fixed and
new features are added.  When you have found what appears to be a
problem with Topographica itself (whether a bug or a missing feature),
please try the following:

<ol>

<P><li> If you are using a version that is more than a few weeks old,
consider trying the most up to date ("bleeding-edge") version via
<a href="../Downloads/cvs.html">SVN</a>.  The code is updated nearly
every day, so by the end of a few weeks many changes will have
accumulated.  Often, bugs will have been fixed and new features will
have been added already in the SVN repository, even though they are
not yet released officially. <!--You can see what has changed since
a certain date by looking at ... -->

<p><li>If the problem is still present in the current version, you can
search the list of
<a href="https://sourceforge.net/tracker/?words=tracker_browse&sort=priority&sortdir=desc&offset=0&group_id=53602&atid=470929&assignee=&status=1&category=&artgroup=&keyword=&submitter=&artifact_id=">bug
reports</a> on our project pages at SourceForge to see if we already
know about the problem. If you find the problem, please feel free to
add additional comments to the report.</li>

<p><li>We also have a <a
href="http://topographica.org/Future_Work/current.html">task list</a>,
used by the developers to keep track of tasks. Try searching this list
for information about your problem. If you find a related task, please
send an e-mail to the developer listed as being in charge of that item
(if any).  If no one is yet listed as being responsible, feel free to
volunteer!</li>

<p><li>If you can locate where in the code there might be a problem
(e.g. by going to the line numbers mentioned in a Python exception),
you will often find a comment with the keyword "ALERT" beside the
code.  These notes are used to mark problems of which we are aware but
have not yet been able to address.  If so, please let us know that
fixing the problem is urgent, and/or suggest fixes for the offending
code. </li>

<p><li>Otherwise, please
<a href="http://sourceforge.net/tracker/?func=add&group_id=53602&atid=470929">
file a bug report</a>. If possible, please include:

<p>
<ul>
<li>the full error message, if any</li>

<li>if you are not using SVN (i.e. you downloaded a released version),
please include the Topographica release number (you can obtain this by
starting Topographica and typing <code>topo.release</code>)</li>

<li>if you are using SVN, please include the output of <code>svn
diff</code>, <code>svn status</code>, and <code>svn info</code>; you
can create a single file (<code>report</code>) containing this
information with the following command:
<pre>svn info > report; svn status >> report; svn diff >> report</pre></li>
<!--need to say it will overwrite any existing file called 'report'?-->

<li>which operating system you are using (Linux, Mac, or Windows)</li>
<li>any additional file needed to replicate the problem (e.g. a script you're using)</li>
<li>a specific recipe (list of steps) that can reproduce the problem</li>
</ul>

<P>To maximize the speed of resolution, please make sure that your
problem can be replicated using an unmodified copy of Topographica
(either released or from SVN), and try to have a small, clear,
quick-to-run example of the problem.  Any bug report is better than
none, so in any case please do send it in even if you can't satisfy
the above requests.  Even so, the clearer and simpler it is, the
quicker we will be able to address the problem.  </li>

<p><li>If you get no reply after a few days, you can try emailing
<A HREF="mailto:&#106&#98&#101&#100&#110&#97&#114&#64&#105&#110&#102&#46&#101&#100&#46&#97&#99&#46&#117&#107?subject=Bug%20report">Jim</a>
directly, in case there was some problem with the email notification
from the bug report system.  But it's much more effective to use the
bug report system, which automatically delivers the appropriate
messages to the appropriate developers.</li>

</ol>

</P>




