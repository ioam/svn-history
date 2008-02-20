<H2>Developing Topographica with Git</H2>

<P>The master repository for Topographica code is stored by
<a href="cvs.html">Subversion</a> (SVN) at SourceForge.net.  It is
often useful to work on separate copies of the code, either to develop
a new, complicated feature, to make far-reaching changes that need
extensive testing, or to keep track of changes useful only at your
local site (such as private research code).  In such cases it can be
useful to use the <a href="http://git.or.cz/">Git</a> version control
tool to establish a local branch of Topographica, so that you can have
the benefits of version control (keeping track of different revisions)
without necessarily affecting the global repository.  If it does turn
out that the local changes would be useful to other Topographica
users, they can then be "pushed" onto the global repository for
everyone to use once they are completed.

<P>SVN's own branching and merging facilities can be used in some
cases, but (a) they are only available to Topographica developers, (b)
they are far more difficult to use and error-prone than those from git
and other
<a href="http://www.inf.ed.ac.uk/teaching/courses/sapm/2007-2008/readings/uvc/version-control.html">
distributed version control systems</a>, (c) they require constant
access to a centralized server, and thus cannot provide version
control when no network connection is available, and (d) most
operations are slow, in part because of the dependence on the remote
server.  Branches maintained using git have none of these problems,
and because git can work seamlessly with the centralized SVN server
when necessary, git can be very useful for any of the uses mentioned
above.

<H3>Installing git on your machine</H3>

<P>Although git is not typically installed in most Linux
distributions, it is usually easy to add it.  E.g. for Debian or
Ubuntu Linux, just do 'apt-get install git git-svn git-doc'; for
others you can get installation packages from
<a href="http://git.or.cz/">git.or.cz</a>.  The git-svn package allows
git to connect to Topographica's SVN repository.

<P>** The remainder of this file is draft documentation ** <BR>
If you know Git well, you can probably already perform the operations
described here. In that case, please help to improve the documentation
below! Thanks.


<H3>Getting the Topographica code</H3>

<P>First, you need to select the revision from which you would like your
git history to begin. For most work, a recent revision is fine (but make
sure the path you want to get actually existed in that revision). Then,
you can execute the following:

<!--CB: will cut output out of examples eventually, and make commands
more generic-->

<pre>
ceball@doozy:~/g$ export TOPOROOT=https://topographica.svn.sourceforge.net/svnroot/topographica
ceball@doozy:~/g$ mkdir topographica
ceball@doozy:~/g$ cd topographica/
ceball@doozy:~/g/topographica$ git-svn init $TOPOROOT/trunk/topographica
Initialized empty Git repository in .git/
ceball@doozy:~/g/topographica$ git-svn fetch -r7986
        A       topo/coordmapperfns/__init__.py
        A       topo/coordmapperfns/basic.py
        ...
        A       examples/goodhill_network90.ty
        A       examples/laminar_or.ty
r7986 = 03b4d77b03a4ad27f1c9fb7e8c8bd23f25200ca8 (git-svn)
Checking 571 files out...
 100% (571/571) done
Checked out HEAD:
  https://topographica.svn.sourceforge.net/svnroot/topographica/trunk/topographica r7986
ceball@doozy:~/g/topographica$ git-svn rebase
        A       doc/Downloads/git_text.php
r7987 = 6c15be77a2b82610484a79a25eb84e6f867e6307 (git-svn)
        M       doc/Downloads/git_text.php
r7988 = f0d17b08e6c4c560dac048e84f27d9b372c63713 (git-svn)
First, rewinding head to replay your work on top of it...

HEAD is now at f0d17b0... Continued writing.
Fast-forwarded master to refs/remotes/git-svn.
ceball@doozy:~/g/topographica$ git-svn rebase
Current branch master is up to date.
</pre>

(substituting values appropriate for what you wish to do). If you're getting just a recent revision of the <code>topographica</code> code (and not <code>topographica-win</code> or <code>facespace</code>), the new directory will occupy about 124 megabytes (as of February 2008).

<!--
ceball@doozy:~/topographica2$ git-svn init https://topographica.svn.sourceforge.net/svnroot/topographica -T/trunk/topographica
Initialized empty Git repository in .git/
ceball@doozy:~/topographica2$ git-svn fetch -r 7988:HEAD
-->

<!--
You could get the entire history? You'd only need to do it once, because after that you'd be using git branches.
-->

<P>Note that if you get a message such as <code>unknown revision or path not in the working tree</code>, then you have probably specifed a path that does not exist at the specified revision. You can use <code>svn log</code> on an SVN copy of Topographica to get information about revisions, or you can <a href="http://topographica.svn.sourceforge.net/viewvc/topographica/">view the SVN repository on the web</a>.

<P>After you have the source code, you probably want to
<A HREF="index.html#building-topographica">build Topographica</A>.


<H3>Working with your Git repository</H3>

<P>Now that you have the Topographica source code in your own
Git repository, you are free to work on it as you wish. You can
commit files, add files, delete files, and so on. If you are new
to Git, you might find the <A HREF="http://www.kernel.org/pub/software/scm/git/docs/tutorial.html">Git tutorial</A> useful; there is also a 
<A HREF="http://git.or.cz/course/svn.html">crash course for SVN
users</A>. Operations such as <code>diff</code>
and <code>commit</code> that you perform with <code>git</code> are
local to your repository.


<!-- mention git commit -a -->

<P>Before committing to your repository, you should probably identify
yourself to git:
<pre>
ceball@doozy:~/g$ git config --global user.email ceball@users.sf.net
ceball@doozy:~/g$ git config --global user.name "C. E. Ball"
</pre>

Also, you probably want to instruct git to ignore the same files as SVN ignores:

<pre>
(echo; git-svn show-ignore) >> .git/info/exclude
</pre>


<P>Example...
<pre>
ceball@doozy:~/g/topographica$ emacs -nw topo/base/parameterizedobject.py 
ceball@doozy:~/g/topographica$ git diff
diff --git a/topo/base/parameterizedobject.py b/topo/base/parameterizedobject.py
index f0a4f2c..906766f 100644
--- a/topo/base/parameterizedobject.py
+++ b/topo/base/parameterizedobject.py
@@ -411,12 +411,7 @@ class Parameter(object):
         # ParameterizedObject class)
         if self.constant or self.readonly:
             if self.readonly:
-                # CB: interpreted 'read only' to include not being
-                # able to set on the class object. If that's wrong,
-                # switch this 'if readonly' block with the below 'elif
-                # not obj' block to allow setting on the
-                # class, and make readonly=>instantiate.
-                # Otherwise please remove this comment.
+                # CB: 'read only' includes not being able to set on class
                 raise TypeError("Read-only parameter '%s' cannot be modified"%self._attrib_name)
             elif not obj:
                 self.default = val
ceball@doozy:~/g/topographica$ git commit -m "Updated comment." topo/base/parameterizedobject.py
Created commit 5f209a3: Updated comment.
 1 files changed, 1 insertions(+), 6 deletions(-)
</pre>


<P>After working on your own copy of Topographica, there are a couple
of operations that you will probably want to perform at some stage:
tracking other peoples' changes to the Topographica SVN repository,
adding your changes to the Topographica SVN repository, and sharing
your Git repository.


<H4>Tracking Topographica's SVN repository</H4>

<P>To get updates from the Topographica SVN repository, your own copy
should have no local changes. (If you do have local changes,
the git-stash command allows you to store your own
changes for later retrieval.)

<pre>
# (git-stash if required)
ceball@doozy:~/g/topographica$ git-svn rebase
        M       doc/Downloads/git_text.php
r7992 = b31884caa7780766a2732cac7418ab5020085757 (git-svn)
First, rewinding head to replay your work on top of it...

HEAD is now at b31884c... Topographica with Git: added more info (still incoherent).

Applying Updated comment.

Wrote tree eeb4607b62d41100a5e66aade9ba268e0e44ae34
Committed: 779f4bf3e1a526f53b7ba1e3d6351b717b4aaa65
# (git-stash apply; git-stash clear if required)
</pre>

<P>rebase moves a whole branch to a newer "base" commit; see <A HREF="http://www.kernel.org/pub/software/scm/git/docs/user-manual.html#using-git-rebase">Keeping a patch series up to date using git-rebase</A> from the Git user manual.


<!--
switch to branch master
git checkout master
-->

<!--
# Initialize a repo (like git init):
        git-svn init http://svn.foo.org/project/trunk
# Fetch remote revisions:
        git-svn fetch
# Create your own branch to hack on:
        git checkout -b tkgui-tk85 remotes/git-svn
# Do some work, and then commit your new changes to SVN, as well as
# automatically updating your working HEAD:
        git-svn dcommit
# Something is committed to SVN, rebase the latest into your branch:
        git-svn fetch && git rebase remotes/git-svn
# Append svn:ignore settings to the default git exclude file:
        git-svn show-ignore >> .git/info/exclude
-->


<H4>Sending your changes to Topographica's SVN trunk</H4>

Changes that you have committed in your local git repository are not
automatically exported to the main SVN repository for Topographica,
which lets you use version control even for things that are not meant
to be part of the main Topographica distribution.  If you do want your
changes to be made public, then run:

<pre>
git-svn dcommit
</pre>

This will will send each of your git commits, in order, to the SVN
repository, preserving their log messages, so that to an SVN user it
appears you made each of those changes one after the other in a
batch.  

<H4>Branching your own Git repository</H4>

<P>If you are working on a complicated new feature, you will probably
find it helpful to branch your git repository, and work on the branch.

<pre>
ceball@doozy:~/g/topographica$ git checkout -b some-feature-name remotes/git-svn
Switched to a new branch "some-feature-name"
</pre>

To see your branches:
<pre>
ceball@doozy:~/g/topographica$ git branch
  master
* some-feature-name
</pre>

<P>Now you can work on <code>some-feature-name</code>; changes there
will not appear in <code>master</code> (which you can check by making
a change, then inspecting the code after switching back with <code>git
checkout master</code>).

<P>You can push and pull changes between your own branches ... XXXX
<pre>
e.g. new-feature-name -> master
svn checkout master
?git pull . new-feature-name
git-svn dcommit   XXXX options about log message, --squash for one commit only
then delete new-feature-name branch.
</pre>


<H4>Sharing your repository</H4>

<P>You or anyone else can
<A HREF="http://www.kernel.org/pub/software/scm/git/docs/git-clone.html">clone</A>
your Git repository to share code (see the tutorial or other
documentation mentioned earlier for details of this).

<P>If you are collaborating with someone, or you work on multiple
machines, you might decide to share a repository. In that case, the
safest approach is to use a repository that is not also a working
copy.

<pre>
ceball@doozy:~/g/topographica$ mkdir ~/git/some-feature-name
ceball@doozy:~/g/topographica$ cd ~/git/some-feature-name
ceball@doozy:~/git/some-feature-name$ git clone --bare ~/g/topographica
Initialized empty Git repository in /home/ceball/git/some-feature-name/topographica/
remote: Generating pack...
remote: Done counting 635 objects.
remote: Deltifying 635 objects...
remote:  100% (635/635) done
Indexing 635 objects...
 100% (635/635) done
Resolving 63 deltas...
 100% (63/63) done
remote: Total 635 (delta 63), reused 0 (delta 0)
</pre>

(<code>--bare</code> instructs git not to clone all the files i.e. not to make a working copy.)

<P>If you both have read/write access to
<code>~/git/some-feature-name</code>, you can both <code>git
push</code>/<code>git pull</code> to/from that repository after first
cloning it:

<pre>
someone@doozy:~/work/some-feature-name$ git clone /home/ceball/git/some-feature-name/topographica/
Initialized empty Git repository in /home/someone/work/some-feature-name/topographica/.git/
remote: Generating pack...
remote: Done counting 635 objects.
Deltifying 635 objects...
  Indexing 635 objects...one
 100% (635/635) donemote: ne
remote: Total 635 (delta 63), reused 635 (delta 63)
 100% (635/635) done
Resolving 63 deltas...
 100% (63/63) done
Checking 572 files out...
 100% (572/572) done
</pre>

Now someone will have a working copy in
<code>/home/someone/work/some-feature-name/topographica</code>. To get
a working copy, you would do a similar thing. After getting the copy,
XXXX you need to switch to the appropriate branch:

<pre>
?
git branch -r
git branch tkgui-tk85 origin/tkgui-tk85
git checkout tkgui-tk85
</pre>


<!-- or should it be fetch? -->

<P>You can both now share code via push/pull to/from that
repository. Once you finish the new feature, you can send it to
Topographica's SVN by pulling it into your XXXX git-svn repo and
dcommitting

<P>Note that Git supports the <code>ssh</code> protocol, so you and
your collaborators can work across machines. For instance, someone not
on doozy in the example above could clone the repository using the
following:

<pre> git clone
ssh://ceball@doozy.inf.ed.ac.uk/home/ceball/git/some-feature-name
</pre>

(share ssh keys to avoid passwords)

<!-- public hosting
[remote "origin"]
        url = ceball@localhost:git/tkgui-tk85/
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "tkgui-tk85"]
        remote = origin
        merge = refs/heads/tkgui-tk85

git push git@gitorious.org:topographica/tkgui-tk85.git

Access denied or bad repository path
fatal: The remote end hung up unexpectedly
error: failed to push to 'git@gitorious.org:topographica/tkgui-tk85.git'

git remote add origin git@gitorious.org:/topographica/tkgui-tk85.git
-->

<!-- CB: there seem to be various gui tools for git, too -->


<H2>References</H2>

<P>something something

<pre>

http://lwn.net/Articles/210045/


Git-svn manual
http://www.kernel.org/pub/software/scm/git/docs/git-svn.html

Howto use git and svn together
http://www.flavio.castelli.name/howto_use_git_with_svn


http://utsl.gen.nz/talks/git-svn/intro.html


http://tsunanet.blogspot.com/2007/07/learning-git-svn-in-5min.html


http://en.wikibooks.org/wiki/Source_Control_Management_With_Git/Interoperation/Subversion

http://hassox.blogspot.com/2007/12/using-git-with-svn.html

http://www.kernel.org/pub/software/scm/git/docs/everyday.html

Multiple branches using git-svn
http://www.dmo.ca/blog/20070608113513

tips about branches
http://wiki.laptop.org/go/Kuku/Git_Usage

http://wiki.sourcemage.org/Git_Guide


http://www.adeal.eu/

Merging branches

To get the difference between your master branch and the currently checked out branch: git diff master..HEAD

Merging a local branch is as easy as this: git checkout master; git pull . <branch>

Once you merged your branch you can delete it: git branch -d <branchname>


http://www.kernel.org/pub/software/scm/git/docs/git-merge.html


http://michael-prokop.at/blog/2007/12/03/git-svn-in-30-minutes/

http://blog.nanorails.com/tags/git
http://blog.nanorails.com/articles/2008/1/31/getting-started-with-git
</pre>



<pre>
My notes...

ceball@san:~/dev/topographica-git$ git checkout -b tkgui-tk85 remotes/git-svn

ceball@doozy:~$ mkdir git
ceball@doozy:~$ cd git/
ceball@doozy:~/git$ mkdir topographica
ceball@doozy:~/git$ cd topographica
ceball@doozy:~/git/topographica$ git --bare init
Initialized empty Git repository in /home/ceball/git/topographica/


ceball@san:~/dev/topographica-git$ git push ssh://ceball@doozy.inf.ed.ac.uk/home/ceball/git/topographica tkgui-tk85


merge:
bail is git reset 
fix conflict is git add 
</pre>
