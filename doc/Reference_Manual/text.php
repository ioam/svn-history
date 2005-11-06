<P>Topographica is designed as a collection of packages from which
elements can be selected to model specific neural systems.  For more
information, see the individual subpackages:

<P><DL COMPACT>
<DT><A href="topo.base.html"><strong>base</strong></A></DT>
<DD>Core Topographica functions and classes</DD>
<P><DT><A href="topo.plotting.html"><strong>plotting</strong></A></DT>
<DD>Visualization functions and classes</DD>
<P><DT><A href="topo.analysis.html"><strong>analysis</strong></A></DT>
<DD>Analysis functions and classes (besides plotting)</DD>
<P><DT><A href="topo.tk.html"><strong>tk</strong></A></DT>
<DD>Tk-based graphical user interface (GUI)</DD>
<P><DT><A href="topo.commands.html"><strong>commands</strong></A></DT>
<DD>High-level user commands</DD>
</dl>

<P>The Topographica primitives library consists of an extensible
family of classes that can be used with the above functions and
classes:

<P><DL COMPACT>
<P><DT><A href="topo.patterns.html"><strong>patterns</strong></A></DT>
<DD>PatternGenerator classes: 2D input or weight patterns</DD>
<P><DT><A href="topo.sheets.html"><strong>sheets</strong></A></DT>
<DD>Sheet classes: 2D arrays of processing units</DD>
<P><DT><A href="topo.projections.html"><strong>projections</strong></A></DT>
<DD>Projection classes: connections between Sheets</DD>
<P><DT><A href="topo.eps.html"><strong>eps</strong></A></DT>
<DD>EventProcessor classes: other simulator objects</DD>
<P><DT><A href="topo.outputfns.html"><strong>outputfns</strong></A></DT>
<DD>Output functions: apply to matrices to do e.g. normalization or squashing</DD>
<P><DT><A href="topo.responsefns.html"><strong>responsefns</strong></A></DT>
<DD>Calculate the response of a Projection</DD>
<P><DT><A href="topo.learningfns.html"><strong>learningfns</strong></A></DT>
<DD>Adjust weights for a Projection</DD>
</dl>

<P>
Each of the library directories can be extended with new classes of
the appropriate type, just by adding a new .py file to that directory.
E.g. new PatternGenerator classes can be added to patterns/, and will
then show up in the GUI menus as potential input patterns.

