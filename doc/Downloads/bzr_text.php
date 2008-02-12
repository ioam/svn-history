<H2>Installing Topographica using Bazaar</H2>

<P>**These instructions are not finished, and probably contain errors**

<P><A HREF="http://bazaar-vcs.org/">Bazaar</A> (bzr) is a 
distributed version control system. Something something something.

<P>The trunk of Topographica's SVN repository 
is continuously imported to a public bzr branch,
allowing anyone to make his or her own bzr branch, and keep that
branch up to date by merging from the trunk over time. This 
is an easy way for anyone (registered Topographica developer or not)
to develop a particular feature.

<P>Our trunk bzr branch is hosted by <A
HREF="https://launchpad.net/">Launchpad</A>. The essentials for using
bzr at Launchpad are described below; see XXXX for more details or if
you have any difficulties.  Note that you will need to run at least
bzr 0.92 on your machine; older bzr clients will complain that they do
not recognize the Topographica branch format.


<H3>Downloading via Bazaar</H3>

<pre>
bzr branch http://bazaar.launchpad.net/~vcs-imports/topographica/trunk
</pre>



Notes:
* launchpad branch can be 6-24 hours behind sf.net trunk
* talk about how launchpad user can publish his/her own branch of topographica
