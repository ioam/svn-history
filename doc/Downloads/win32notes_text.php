<!--CB: should be able to remove this when windows version includes a shell-->

<H3><A NAME="unix-commands-on-win">Translating UNIX commands to Windows</A></H3>


<P>To convert UNIX shell commands to Windows cmd.exe commands:
<ul>
<li>Omit any initial '<code>./</code>'</li>
<li>Replace any forward slash '<code>/</code>' in a path with a backslash '<code>\</code>'</li>
<li>Single quotes (<code>'</code>) must appear inside double quotes (<code>"</code>); double quotes cannot appear inside single quotes
</ul>

<P>Examples:

<TABLE>
<TR>
<TH>UNIX</TH>
<TH>Windows</TH>

<TR>
<TD><code>./topographica -g examples/lissom_oo_or.ty</code></TD>
<TD><code>topographica -g examples\lissom_oo_or.ty</code></TD>

<TR>
<TD><code>./topographica -c 'targets=["lissom_oo_or_10000.typ"]' examples/run.py</code></TD>
<TD><code>topographica -c "targets=['lissom_oo_or_10000.typ']" examples/run.py</code></TD>

</TABLE>




