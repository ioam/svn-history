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
git to connect to Topographica's SVN repository. Note that you should
try to get Git version 1.5.3 (used while writing this document) or
later. If you are building from source, you can skip git-doc, which
can be difficult to compile (XXXX link) since, and the documentation
is all available online (XXXX link).

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
# location of SVN repository
$ export TOPOROOT=https://topographica.svn.sourceforge.net/svnroot/topographica

# create directory to hold new files
$ mkdir topographica; cd topographica

# create a new Git repository
$ git-svn init $TOPOROOT/trunk/topographica

# retrieve the SVN files and history
# (you can choose a value for r)
$ git-svn fetch -r7986; git-svn rebase
</pre>

(substituting values appropriate for what you wish to do; e.g. you can
get more history by changing <code>-r</code>). If you're getting 
a recent revision of the <code>topographica</code> code (and
not <code>topographica-win</code> or <code>facespace</code>), the new
directory will occupy about 124 megabytes (as of February 2008).

<P>If you wished, you <i>could</i> get the complete history of the
Topographica project, using:
<pre>
 git svn clone $TOPOROOT/trunk/topographica topographica
</pre>
instead of all of the above commands after <code>export</code>, to
make a new directory <code>topographica/</code> with a copy of the
entire repository (620MB as of 2/2008) plus a working copy.  This will
usually take 2-3 hours to run, although you would only need to do it
once (because after that you could use branches to create different
versions).  Note that this only gets the trunk; if you want all tags
and branches as well (which seems unlikely), you can use the -T and -B
options described in the git manual.  In any case, this method is not
usually necessary, unless you want to do some comparison across a wide
range of historical versions of Topographica.

<P>Note that if you get a message such as <code>unknown revision or
path not in the working tree</code>, then you have probably specifed a
path that does not exist at the specified revision. You can
use <code>svn log</code> on an SVN copy of Topographica to get
information about revisions, or you
can <a href="http://topographica.svn.sourceforge.net/viewvc/topographica/">view
the SVN repository on the web</a>.

<P>After you have the source code, you probably want to
<A HREF="index.html#building-topographica">build Topographica</A>. You
probably also want to instruct git to ignore the same files as SVN
ignores:
<pre>
(echo; git-svn show-ignore) >> .git/info/exclude
</pre>
If <code>svn:ignore</code> properties are subsequently changed in the
SVN repository, you will have to update your <code>exclude</code>
information.


<H3>Working with your Git repository</H3>

<P>Now that you have the Topographica source code in your own Git
repository, you are free to work on it as you wish. You can commit
files, add files, delete files, and so on. All operations that you
perform with <code>git</code> (such as <code>diff</code>
and <code>commit</code>) are local; only operations
with <code>git-svn</code> have the potential to modify the SVN
repository.

<P>If you are new to Git, you might find
the <A HREF="http://www.kernel.org/pub/software/scm/git/docs/tutorial.html">Git
tutorial</A> useful. We recommend that you read through the 
<A HREF="http://git.or.cz/course/svn.html">crash course for SVN
users</A>, which will help you to avoid being surprised by differences
between similarly named git and svn commands. If you are still puzzled
by a particular operation in Git,
the <A HREF="http://git.or.cz/gitwiki/GitFaq">Git FAQ</A> is often
helpful.

<!--
<P>Note that for subversion users, <code>git revert</code> the behavior of <code>git
commit</code> in particular might be surprising when adding new files,
so be sure to take a look at
the <A HREF="http://www.kernel.org/pub/software/scm/git/docs/git-commit.html">git-commit
man page</A> or see the FAQ
entry <A HREF="http://git.or.cz/gitwiki/GitFaq#head-3aa45c7d75d40068e07231a5bf8a1a0db9a8b717">Why
is "git commit -a" not the default?</A>.
-->

<P>Before committing to your repository for the first time, you should
identify yourself to git:
<pre>
ceball@doozy:~/g$ git config --global user.email user@address.ext
ceball@doozy:~/g$ git config --global user.name "User Name"
</pre>

You should also check that your machine has the correct time and date,
otherwise your history can become confusing. Other configuration
options are available by reading <code>man git-config</code>.


<P>While you are still working locally, before you have
shared any changes, you can ammend commits (and even rewrite parts of
your history). XXXX link <!--When your changes are finally sent to
SVN, this can make your changes clearer to see for other users.-->

<P>After working on your own repository, there are a couple of
operations that you will probably want to perform at some stage:
tracking other peoples' changes to the Topographica SVN repository,
adding your changes to the Topographica SVN repository, and sharing
your Git repository. These are discussed in the following sections.


<H4>Tracking Topographica's SVN repository</H4>

<P>To get updates from the Topographica SVN repository, your own copy
should have no local changes. (If you do have local changes,
the <A HREF="http://www.kernel.org/pub/software/scm/git/docs/git-stash.html">git-stash</A>
command allows you to store your own changes for later retrieval.)

<pre>
# (git-stash if required)
$ git-svn rebase
# (git-stash apply; git-stash clear if required)
</pre>

<code>rebase</code> moves a whole branch to a newer "base" commit;
see <A HREF="http://www.kernel.org/pub/software/scm/git/docs/user-manual.html#using-git-rebase">Keeping
a patch series up to date using git-rebase</A> from the Git user
manual for further explanation.


<H4>Sending your changes to Topographica's SVN trunk</H4>

<P>Changes that you have committed in your local git repository are not
automatically exported to the main SVN repository for Topographica,
letting you use version control even for things that are not meant to
be part of the main Topographica distribution.  If you do want your
changes to be made public, then run:

<pre>
git-svn dcommit
</pre>

This will send each of your git commits, in order, to the SVN
repository, preserving their log messages, so that to an SVN user it
appears you made each of those changes one after the other in a
batch. 

<P>As with SVN, before committing you should first check that you have
updated and tested your code with changes from others (<code>git-svn
rebase; make tests</code>) to ensure that your changes are compatible
(and not just that they apply cleanly). Any actual conflict
encountered by git-svn (e.g.  you try to commit a file which has been
updated by someone else while you were working on it) will stop
the <code>dcommit</code> process, and the SVN error will be reported.

<!-- does git-svn dcommit also then run git-svn rebase after? -->



<H4>Branching your own Git repository</H4>

<P>If you are working on more than a few lines of code - a potentially
complicated new feature, for instance - you will probably find it more
helpful to branch your git repository, and work on the
branch. Afterwards, you can merge your branch into your master
repository and send the changes to Topographica's SVN repository.

<P>The <A HREF="http://www.kernel.org/pub/software/scm/git/docs/git-svn.html">git-svn</A>
man page gives an overview of a possible workflow:

<pre>
# Initialize a repo (like git init):
        git-svn init http://svn.foo.org/project/trunk
# Fetch remote revisions:
        git-svn fetch
# Create your own branch to hack on:
        git checkout -b new-branch-name remotes/git-svn
# Do some work, and then commit your new changes to SVN, as well as
# automatically updating your working HEAD:
        git-svn dcommit
# Something is committed to SVN, rebase the latest into your branch:
        git-svn fetch && git rebase remotes/git-svn
# Append svn:ignore settings to the default git exclude file:
        git-svn show-ignore >> .git/info/exclude
</pre>

To see your branches:
<pre>
ceball@doozy:~/g/topographica$ git branch
  master
* some-feature-name
</pre>

<P>You can of course now push, pull, and merge changes between your
own branches as you wish. You also can switch between branches to work
on different features using the same repository, although note that
the branch under which you issued the <code>make</code> command is the
one that determines which version of external packages were compiled
(this should not be a problem unless your branch is deliberately
dealing with different external pacakges).

<P>XXXX superdraft...Example of what I've been doing...working on a branch that will
replace tkgui. I wanted to keep the new feature branch updated with
changes from Topographica's SVN as I went along.

<pre>
ceball@doozy:~/g/topographica$ git checkout -b some-feature-name remotes/git-svn
Switched to a new branch "some-feature-name"
</pre>

<P>Now you can work on <code>some-feature-name</code>; changes there
will not appear in <code>master</code> (which you can check by making
a change, then inspecting the code after switching back with <code>git
checkout master</code>).

<P>To keep my branch up to date with SVN:

<pre>
git checkout master         # switch to master branch
git svn rebase              # retrieve the latest commits from subversion repo
git checkout some-feature-name
git rebase master   # makes sure that your branch is rebased against latest version of svn tree
</pre>

<P>On completion of the work, I will:

<pre>
# update master to match svn
git checkout master
git svn rebase

# bring my branch into master      
git rebase some-feature-name master  # fast-forwards master to include some-feature-name changes
git svn dcommit             
</pre>

Of course you are free instead to use <code>git merge</code>; the
approach here always moves your branch changes onto the end of the
updated SVN history. That makes most sense to me.

<P>
Conflicts...not documented yet

<pre>
XXXX
 git rebase master
 # ... reports merge conflicts
 # edit conflicting files file1 file2
 # git add file1 file2
 git rebase --continue
</pre>

<P>Delete branch when done. XXXX


<H4>Sharing your repository</H4>

<P>XXXX If you follow this section, you will probably get really
confused. Needs to be written when I know what I'm doing.

<P>You or anyone else
can <A HREF="http://www.kernel.org/pub/software/scm/git/docs/git-clone.html">clone</A>
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

(<code>--bare</code> instructs git not to clone all the files i.e. not
to make a working copy.)

<P>If you both have read/write access
to <code>~/git/some-feature-name</code>, you can both <code>git
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

Now someone will have a working copy
in <code>/home/someone/work/some-feature-name/topographica</code>. To
get a working copy, you would do a similar thing. After getting the
copy, XXXX you need to switch to the appropriate branch:

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
<pre>
git clone ssh://ceball@doozy.inf.ed.ac.uk/home/ceball/git/some-feature-name
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


<H2>References + Notes</H2>

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

To get the difference between your master branch and the currently checked out branch: 
git diff master..HEAD

Merging a local branch is as easy as this: git checkout master; git pull . <branch>

Once you merged your branch you can delete it: git branch -d <branchname>


http://www.kernel.org/pub/software/scm/git/docs/git-merge.html


http://michael-prokop.at/blog/2007/12/03/git-svn-in-30-minutes/

http://blog.nanorails.com/tags/git
http://blog.nanorails.com/articles/2008/1/31/getting-started-with-git



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

Q. How do I revert a commit?

A. The git-reset command allows you to reset the HEAD of the branch to
any given point in history. To go back one commit, run "git-reset
HEAD^". This will keep your local changes and you can make any
additional changes before re-commiting the new work. Also see the
"git-commit --amend" command and the "git-reset" man page for other
examples.

http://sipx-wiki.calivia.com/index.php/Mirroring_sipXecs_subversion_repository_with_git

man git-rev-parse


http://utsl.gen.nz/talks/git-svn/intro.html#wtf-why



list all recent actions
git reflog



pack to min disk usage

git pack-refs --prune
git reflog expire --all
git repack -a -d -f -l
git prune
git rerere gc



interactive rebasing

git rebase -interactive




gitk readable fonts

[ -r ~/.gitk ] || cat > ~/.gitk << EOF
set mainfont {Arial 10}
set textfont { Courier 10}
set uifont {Arial 10 bold}
EOF


</pre>
