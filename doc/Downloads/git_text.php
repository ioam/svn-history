<H2>Developing Topographica with Git</H2>


<P>As well as git itself, you need to have git-svn.




<H3>Getting the Topographica code</code>
TOPOROOT=https://topographica.svn.sourceforge.net/svnroot/topographica

<pre>
mkdir topographica_something
cd topographica_something
git-svn init $TOPOROOT/trunk/topographica
# set N below to the first revision you want to have in your history
git-svn fetch -rN  
git-svn rebase
</pre>

(I just used 7986 but git is supposed to be fast enough and space-efficient enough that it doesn't really. Plus you only need to do it once, bedcause the rest of the time you can make branches from your 'master'.)

<H3>Sending changes to Topographica's SVN repository</H3>

<P>The first time, make sure you have identified yourself to git:
<pre>
ceball@doozy:~/temp$ git config --global user.email ceball@users.sf.net
ceball@doozy:~/temp$ git config --global user.name "C. E. Ball"
</pre>

Then the following command will send each of your git commits to the SVN repository:
<pre>
git-svn dcommit
</pre>


References

Git-svn manual
http://www.kernel.org/pub/software/scm/git/docs/git-svn.html

Howto use git and svn together
http://www.flavio.castelli.name/howto_use_git_with_svn

Git for Subversion users:
http://git.or.cz/course/svn.html
