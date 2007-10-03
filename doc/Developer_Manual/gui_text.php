<H1>Implementing the GUI</H1>

<P>When coding, the GUI should be considered an optional component.
No part of Topographica should import GUI files, rely on the presence
of a particular GUI or any GUI at all, or assume that the data it
generates will be used only by a GUI unless it is absolutely
necessary, e.g. for the actual GUI implementation.  This is a special
case of the <A HREF="ood.html">general principles of object-oriented design</A>
discussed elsewhere.

<P>Many components that would at first glance seem to be GUI-related
are, in, fact much more general.  Such code should be written for the general
case, not in terms of the GUI (and not even with names or comments
that suggest they are in any way limited to being part of a GUI).

<P>For instance, many of the analysis and plotting routines will
commonly be used in the context of a GUI.  However, the vast majority
of this code is not specific to a GUI, i.e. it does not require a user
to actually move a mouse or manipulate widgets.  E.g. a SheetView is a
bitmap representation of a Sheet; the resulting bitmap can of course
be displayed in a GUI window, but it could also be saved to a file,
and in batch mode or unit tests often <i>will</i> be saved directly to a
file, with no GUI window ever created.  Most of the important code for
plotting is independent of the output device, and any such code should
be written using general terminology like Plotting, not GUI.
Similarly for other analysis routines --- they should be implemented
and named in terms of some general module name like Analysis, not GUI.

<P>Obviously, it's very helpful for plots, etc. to have interactive
widgets to set the scales, select subplots, etc.  But these can
generally be implemented in a way that can also be specified
textually, i.e. without a mouse, so that they can be used without a
GUI, or at least without any particular GUI.  Even for things that are
inherently mouse-based, like data exploration tools that change
viewpoints dynamically based on the mouse position, as much code as
possible should be extracted out, made general, and kept out of the
GUI code.

<P>If you want more information on this approach, search the web for
Model-View-Controller.  Writing the code in this way helps ensure that
the core of the simulator is not dependent on any particular output
device, which is crucial because different output devices are
appropriate in different contexts, e.g. over the web, in
non-interactive runs, in batch testing, supporting different
look-and-feel standards, etc.  The approach also greatly eases
maintenance, because GUI libraries often vary significantly over time
and across platforms.  To be able to maintain our code over the long
term, we need to minimize the amount of our code that depends on such
varying details.  Finally, this approach ensures that scientific users
can ignore all of the GUI details, which are irrelevant to what
Topographica actually computes.  Allowing users to focus on the core
code is absolutely crucial for them to be able to understand and trust
what they are actually simulating.


<!--CB: work in progress-->

<H2>Programming with tkgui</H2>

<P>tkgui uses <a href="">Tkinter</a> to draw the GUI components, but
simplifies GUI implementation by handling linkage of
<code>ParameterizedObject</code>s with representations in the GUI.

<!--(Tkinter is very flexible, but often quite a large amount of code
is required to keep track of variables and display components
('widgets') ).-->

<P>The classes <a href="">TkParameterizedObject</a> and <a
href="">ParametersFrame</a> are the ones most often of used for
creating a new GUI representation of some Topographica
component. Which to use depends on how much you wish to customize the
display: a ParametersFrame displays all of a ParameterizedObject's
Parameters as a list in one frame, whereas a TkParameterizedObject can
display any number of the Parameters in any number of Frames (which
you specify). Hence the PlotGroupPanels, which display Parameters from
multiple ParameterizedObjects in a custom layout, are based on
TkParameterizedObject, whereas editing properties of an object in the
model editor simply brings up a ParametersFrame for that object.

<H3>ParametersFrame</H3>

<P>If you wish to display and/or edit the Parameters of a
ParameterizedObject in the GUI, you can simply insert a
ParametersFrame for that object into an existing container (a window
such as a <a href="">tkgui.TkguiWindow</a>, or a frame such as a <a
href="">Tkinter.Frame</a>):

<pre>
from topo.base.parameterizedobject import ParameterizedObject
from topo.tkgui.parametersframe import ParametersFrame
from topo.tkgui.tkguiwindow import TkguiWindow

p = ParameterizedObject(name="PO")
w = TkguiWindow()
f = ParametersFrame(w,parameterized_object=p)
</pre>

<P>All the non-hidden Parameters of <code>p</code> will be displayed
in a new Frame in <code>w</code>.

<!--CB: mention buttons, two types of PF-->



<H3>TkParameterizedObject</H3>

<!--CB: don't duplicate tkparameterizedobject.py's docstring.-->
