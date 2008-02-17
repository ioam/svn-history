<H2>Using Git to get Topographica's code</H2>


<P>As well as git itself, you need to have git-svn.




TOPOROOT=https://topographica.svn.sourceforge.net/svnroot/topographica

<pre>
mkdir topographica_something
cd topographica_something
git-svn init $TOPOROOT/trunk/topographica
# set N below to the first revision you want to have in your history
git-svn fetch -rN  
git-svn rebase
</pre>

ceball@doozy:~/temp$ git config --global user.name "C. Ball"
ceball@doozy:~/temp$ git config --global user.email ceball@users.sf.net
ceball@doozy:~/temp$ git config --global user.name "C. E. Ball"



References

Git-svn manual
http://www.kernel.org/pub/software/scm/git/docs/git-svn.html

Howto use git and svn together
http://www.flavio.castelli.name/howto_use_git_with_svn

Git for Subversion users:
http://git.or.cz/course/svn.html
