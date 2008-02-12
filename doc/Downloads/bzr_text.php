<H2>Topographica using Bazaar</H2>

<P>**These instructions are not finished, and probably contain errors**
me in URLs works if you're logged into launchpad.

<P><A HREF="http://bazaar-vcs.org/">Bazaar</A> (bzr) is a
distributed version control system. Something something something.

<P>The trunk of Topographica's SVN repository is continuously mirrored
to a public bzr branch, allowing anyone to make his or her own bzr
branch easily, and keep that branch up to date by merging from the
trunk over time. Starting from this branch is an easy way for anyone
(registered Topographica developer or not) to develop a particular
feature.

<!--
<P>Alternatively, you yourself can make your own branch of Topographica's SVN trunk
using bzr... probably "bzr branch $TOPOROOT/trunk" or similar.
-->

<P>Our trunk bzr branch is hosted by <A
HREF="https://launchpad.net/">Launchpad</A>. The essentials for using
bzr at Launchpad are described below; see XXXX for more details or if
you have any difficulties.  Note that you will need to run at least
bzr 0.92 on your machine; older bzr clients will complain that they do
not recognize the Topographica branch format.

<P>Change to the path where you want the <code>trunk/</code> directory
  to appear, then type:
<pre>
bzr branch http://bazaar.launchpad.net/~vcs-imports/topographica/trunk
</pre>

<P>
This command can take a while to execute, because the Topographica
repository contains some quite large external packages. bzr displays
the progress; once complete, the new directory will occupy around
1 Gb (as of 02/2008).

<P>After you have checked out the source code, you probably want to build
Topographica. To do this, simply follow the XXXX svn build instructions
for your platform.


<H3>Working with branch</H3>

<P>Now that you have your own branch, you are free to work with it
however you wish.  You can commit changes whether or not you are a
Topographica developer, and because Bazaar keeps track of the history
on your local copy, you can easily revert files. None of this activity
requires network access.

<P>Before committing for the first time, you should inform bzr who you
are, so that changes are attributed to the correct username:
<pre>
bzr whoami "Your Name <user@address.ext>"
</pre>

<P>To stay up to date with the SVN version of Topographica, you
can update your own branch with changes committed to Topographica's
trunk:
<pre>
$ bzr merge
Merging from remembered location http://bazaar.launchpad.net/~vcs-imports/topographica/trunk/
 M  topographica/examples/lissom_or_noshrinking.ty
All changes applied successfully.

$ bzr commit -m 'Merged changes from SVN trunk.' .
</pre>
Or, if your copy has not diverged from the SVN trunk, you can simply pull the changes:
<pre>
$ bzr pull
Using saved location: http://bazaar.launchpad.net/~vcs-imports/topographica/trunk/
+N  topographica/doc/Downloads/bzr_text.php
 M  topographica/external/Makefile
-D  topographica/external/ipython-0.7.3.tar.gz
 M  topographica/topo/tests/testDynamicParameter.txt
All changes applied successfully.
Now on revision 7812.
</pre>


<P>Once you have done some work, you probably want to make your
changes publicly visible (currently they exist only on your local
copy).  To do this, you have two options. The first is simply to
publish your own branch, and the second is to 'push' your changes to
the Topographica SVN repository (for which you need to be a
Topographica developer).


<H4>Publish your own branch</H4>

<P>Topographica developers might wish to make their changes publicly
visible while working on a new feature or fixing a bug. Non-developers
might like to make their changes available to anyone (for use or
consideration). Either way, publishing a branch is an easy way to do
this. As explained in the XXXX bzr docs, you can publish to any server
you wish. Here, we assume you are a Launchpad user, and that
you want to publish to your Launchpad space and have the branch 
associated with Topographica:

<pre>
bzr push bzr+ssh://user@bazaar.launchpad.net/~user/topographica/branch_name
</pre>

where <code>user</code> is your Launchpad username,
and <code>branch_name</code> is the name you wish to give your
branch. For this command to work, you must first have 
<A HREF="https://launchpad.net/people/+me/+editsshkeys">set up some
SSH keys in your Launchpad account</A>.


You (and anyone else) should then be able to see your branch at the
URL <code>https://code.launchpad.net/~user</code>.  Note that if you
do not want to associate your branch with Topographica,
replace <code>topographica</code> in the command above
with <code>+junk</code>.



<H4>Push changes to Topographica SVN</H4>

<P>If you are a Topographica developer implementing a new feature or
fixing a bug, you will want to commit your finished work to the central
Topographica repository...

XXXX
http://bazaar-vcs.org/BzrForeignBranches/Subversion
Get bzr-svn
copy downloaded,unpacked dir to ~/.bazaar/plugins
bzr push ...


<!--
add team branch section
-->

Notes:
* launchpad branch can be 6-24 hours behind sf.net trunk

+How we could replace subverion with a central, team bzr branch:
https://help.launchpad.net/FeatureHighlights/TeamBranches
no need for everyone to checkout whole history





