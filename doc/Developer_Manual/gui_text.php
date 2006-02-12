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
