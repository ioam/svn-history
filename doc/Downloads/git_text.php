<H2>Developing Topographica with Git</H2>


<P>As well as git itself, you need to have git-svn.


<P>If you know Git well, you can probably already perform the operations
described here, and be able to avoid limitations described below.


<H3>Getting the Topographica code</code>


<P>First, you need to select the revision from which you would like your
git history to begin. For most work, a recent revision is fine (but make
sure the path you want to get actually existed in that revision). Then,
you can execute the following:

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
should have no local changes. If you do have local changes,
the <A HREF="">git-stash</A> command is allows you to store your own
changes for later retrieval.

<pre>
# (git-stash if required)




http://www.kernel.org/pub/software/scm/git/docs/user-manual.html#using-git-rebase









 Since you are very likely to have local changes, 

<pre>
 git-svn rebase
(make sure no local changes: use git-stash
   1. put aside your changes using the command: git-stash
   2. update your working copy using: git-svn rebase as usual
   3. take back your changes typing: git-stash apply
   4. clear the stash typing: git-stash clear



switch to branch master
git checkout master




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


<H3>Committing changes to Topographica's SVN trunk</H3>

<P>The first time, make sure you have identified yourself to git:
<pre>
ceball@doozy:~/temp$ git config --global user.email ceball@users.sf.net
ceball@doozy:~/temp$ git config --global user.name "C. E. Ball"
</pre>

Then the following command will send each of your git commits to the SVN repository:
<pre>
git-svn dcommit
</pre>


<H3>Committing your changes as a branch on Topographica's SVN</H3>


<H3>Sharing your changes</H3>

<P>You or anyone else can <A HREF="">XXXXclone</A> your repository to
share code.

<pre>
mkdir new_repo
cd new_repo
git clone /path/to/repo
</pre>

<P>If you are collaborating with someone, you might decide to share
a repository. In that case, the safest approach is to use a
repository that is not also a working copy.

<pre>
mkdir ~/git/some-feature-name
cd ~/git/some-feature-name
git clone --bare /path/to/repo
</pre>

<P>Now you can both push and pull to that repository:

<pre>
git clone ~/git/some-feature-name
</pre>


git clone ssh://ceball@doozy.inf.ed.ac.uk/home/ceball/git/tkgui-tk85








git push git@gitorious.org:topographica/tkgui-tk85.git


Access denied or bad repository path
fatal: The remote end hung up unexpectedly
error: failed to push to 'git@gitorious.org:topographica/tkgui-tk85.git'

git remote add origin git@gitorious.org:/topographica/tkgui-tk85.git




References

Git-svn manual
http://www.kernel.org/pub/software/scm/git/docs/git-svn.html

Howto use git and svn together
http://www.flavio.castelli.name/howto_use_git_with_svn

Git for Subversion users:


http://utsl.gen.nz/talks/git-svn/intro.html





publishing 

[remote "origin"]
        url = ceball@localhost:git/tkgui-tk85/
        fetch = +refs/heads/*:refs/remotes/origin/*
[branch "tkgui-tk85"]
        remote = origin
        merge = refs/heads/tkgui-tk85

git push origin tkgui-tk85



git clone /home/ceball/git/tkgui-tk85 tkgui-tk85
