<H2>Updating your scripts for a new version of Topographica</H2>

<P>Topographica is used in current research, and as such it can change
quickly. Sometimes changes are made that render existing code obsolete
in some way. This usually manifests itself in two ways: the first is
that old snapshots can contain out-of-date code, and the second in
that old scripts can contain out-of-date code.

<P>Old snapshots should be supported automatically; if you find you
have an old snapshot that will not load in a newer version of
Topographica, please let us know by <A
HREF="../Forums/problems.html">filing a bug report</A>.

<P>Old scripts can be supported by starting Topographica with legacy
support (i.e. by passing <code>-l</code> to Topographica at startup).
Usually, however, it is better simply to update the script, then
Topographica does not need to be used with legacy support. As of 0.9.4,
we provide a utility to update scripts to run with newer versions.


<H3>Upgrading from 0.9.4 to 0.9.5</H3>

<P>To update a script (e.g. <code>/home/user/my_script.ty</code>)
written for 0.9.4, first change to your topographica/ directory, e.g.:

<pre>
$ cd /home/user/topographica
</pre>

Then run the update utility:

<pre>
$ etc/update_094_to_095 /home/user/my_script.ty
</pre>

This will produce a new script,
<code>/home/user/my_script.ty_0.9.5</code>, which should run on the
new version of Topographica. 

<P>If you find the script still will not run, please <A
HREF="../Forums/problems.html">file a bug report</A> so that we can
fix the problem. (To work with your originally script immediately, you
can instead try running Topographica with legacy support enabled, as
described earlier.)

<H3>Upgrading from a version prior to 0.9.4</H3>

<P>Currently, we do not explicitly support code written for versions
of Topographica prior to 0.9.4. Depending on the age of the code,
though, such support is possible in theory. Please let us know if you
an old script (or snapshot) that you need to use in a modern version
of Topographica.
