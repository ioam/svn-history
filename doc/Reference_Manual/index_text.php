This reference manual contains detailed documentation of each
component making up Topographica, assuming that the user is already
familiar with basic Topographica usage.  See the <A
HREF="../User_Manual/index.html">User Manual</A> and <A
HREF="../Tutorials/index.html">Tutorials</A> for such a introduction.
Note that the documentation of these components is gradually being
improved, and not every component is properly documented yet.
Moreover, the documentation is often much more verbose than necessary,
because many little-used yet often duplicated methods are included for
each class.  Still, the reference for a given component does
provide a comprehensive listing of all attributes and methods,
inherited or otherwise, which is difficult to obtain from the
source code.


<H2>Main packages</H2>

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
<P><DT><A href="topo.misc.html"><strong>misc</strong></A></DT>
<DD>Miscellaneous independent utility functions and classes</DD>
<P><DT><A href="topo.tkgui.html"><strong>tkgui</strong></A></DT>
<DD>Tk-based graphical user interface (GUI)</DD>
</dl>

The <strong>base</strong> directory contains the most fundamental
Topographica classes, implementing basic functionality such as
Parameters (user-controllable attributes), Sheets (arrays of units),
Projections (large groups of connections between Sheets),
ConnectionFields (spatially localized groups of connections to one
unit), and the event-driven Simulation.  All of these files are
independent of the rest of the files in topo/, and act as the primary
programming interface on which Topographica is built.  The rest of the
directories add components used in specific models, and implement the
GUI.

<H2>Library</H2>

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
<DD>EventProcessor classes: other simulation objects</DD>
<P><DT><A href="topo.outputfns.html"><strong>outputfns</strong></A></DT>
<DD>Output functions: apply to matrices to do e.g. normalization or squashing</DD>
<P><DT><A href="topo.responsefns.html"><strong>responsefns</strong></A></DT>
<DD>Calculate the response of a unit or a Projection</DD>
<P><DT><A href="topo.learningfns.html"><strong>learningfns</strong></A></DT>
<DD>Adjust weights for a unit or a Projection</DD>
<P><DT><A href="topo.commands.html"><strong>commands</strong></A></DT>
<DD>High-level user commands</DD>
</DL>

<P>All of the library components are optional, in the sense that they
can be deleted or ignored or replaced with custom versions without
affecting the code in any of the main packages.  (Of course, any
specific model that depends on the component would not be able to
function without it.)

<P>Each of the library directories can be extended with new classes
of the appropriate type, just by adding a new .py file to that
directory.  E.g. a file of new PatternGenerator classes can be copied
into patterns/, and will then show up in the GUI menus as potential
input patterns.  The GUI will also show any class derived from those
in the library directories, even if it is defined in your own files,
as long as that file has been run or imported before the GUI window 
is opened.

<P>Many of the components come in multiple varieties, to be used at
different levels in a model.  For instance, there are learningfns that
operate on a single unit (type LearningFn), and ones that operate on
an entire CFProjection (type CFPLearningFn).  The lower level
components can be used by providing them to a "Plugin" version of the
higher level component, which will apply the lower level version to
each unit.  For instance, a LearningFn can be used with a
CFPLearningFn of type CFPLF_Plugin, and will be applied the same to
each unit individually.

<P>Many components also come with an optimized version, usually
written in C for speed.  The fastest, but least flexible, components
will be high-level components written in C, such as CFPLF_Hebbian_opt.


<!-- JABALERT! This should probably move to its own page. -->
<H2>External Packages</H2>

<P>Topographica makes extensive use of external packages included with the 
distribution.  For full use of the features of these packages, see their
documentation:

<!-- Should we make these point to the local copy instead? -->
<P><DL COMPACT>

<P><DT><A href="http://python.org/doc/">Python</A></DT>
<DD>Topographica command and scripting language (essential!).  For a
good basic introduction, check out the <A
HREF="http://docs.python.org/tut/tut.html">Python tutorial</A>.  There
are also books and many websites available with more information.
Topographica is built on an unmodified copy of Python, so anything that
Python can do is also valid for Topographica.
</DD>

<P><DT><A href="http://numeric.scipy.org/numpydoc/numdoc.htm">Numeric</A></DT>
<DD>Topographica makes heavy use of Numeric arrays and math functions; these
provide high-level operations for dealing with matrix data.  The
interface and options are similar to Matlab and other high-level array
languages.  These operations are generally much higher performance
than explicitly manipulating each matrix element, as well as being
simpler, and so they should be used whenever possible.
</DD>

<P><DT><A href="http://matplotlib.sourceforge.net/">MatPlotLib</A></DT>
<DD>Matplotlib is used for generating 1D (line)
and 2D (plane) plots, such as topographic grid plots.  It provides
a very general Matlab-like interface to creating plots of any quantities
one might wish to visualize, including any array or vector in the program.
</DD>

<P><DT><A href="http://www.pythonware.com/products/pil/">PIL</A></DT>
<DD>Topographica uses the Python Imaging Library for reading and
writing bitmap images of various types.  PIL also provides a variety
of image processing and graphics routines, which are available for use
in Topographica components and scripts.</DD>

<P><DT><A href="http://pmw.sourceforge.net/">Pmw</A></DT>
<DD>Topographica uses Pmw for its graphical user interface (GUI)
classes, and those who want to add their own GUI windows can use any
widgets from Pmw.</DD>

<P><DT><A href="http://www.scipy.org/documentation/weave/">Weave</A></DT>
<DD>Topographica uses weave to allow snippets of C or C++ code to be
included within Python functions, usually for a specific speed optimization.
This functionality is available for any user-defined library function, 
for cases when speed is crucial.</DD>

</DL>

