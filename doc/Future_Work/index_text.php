<P>Topographica is still under very active development.  As described
below, a large number of changes and new features are scheduled over
the next few months, as well as over the next few years.  Our current
<a href="current.html">lower-level list of tasks</a> is kept separately.

<H2>Most urgent (Winter 2006/2007):</H2>
<DL COMPACT>
<DT>ALERTs</DT><DD>
There are a large number of relatively small problems noted in the
source code for the simulator; these are marked with comments
containing the string ALERT.  These comments help clarify how the code
should look when it is fully polished, and act as our to-do list.
They also help prevent poor programming style from being propagated to
other parts of the code before we have a chance to correct it.  We are
slowly working to correct these issues.

<P><DT>Stable APIs</DT><DD>
The Topographica API (determined by the classes in base/) is gradually
becoming more stable, and by the time of the 1.0 release it should be
possible to build add-in components and model scripts and expect them
to be usable in future versions (or to have a conversion program
available for them).

<P><DT>Command-line and batch interfaces</DT><DD>
Although Topographica is written to be independent of the type of
interface, and does not require a GUI or other interactive console,
some functions are currently implemented only in the GUI.  Others are
currently more difficult to use in batch mode, requiring longer and
more complex commands than necessary.  These items will be simplified
and made more appropriate for command-line and batch use, to make
using larger networks more practical.

<P><DT>Spiking support</DT><DD>
Topographica primarily supports firing-rate (scalar) units, but
spiking models are currently under development, and preliminary
versions are included already.  We will be developing interfaces
between spiking and non-spiking Sheets and analysis tools for spiking
neurons.  We primarily expect to support integrate-and-fire and
related computationally tractable spiking unit models; more detailed
compartmental models can be simulated in Neuron or Genesis instead.

<P><DT>Polishing the GUI model editor</DT><DD>
The Topographica model editor allows a model to be constructed,
modified, visualized, and edited.  However, there are a few operations
not currently supported, such as setting a parameter to a random
stream of numbers.  These limitations (combined with the ongoing
changes to the saved file formats) mean that most models are best
constructed using .ty script files rather than the editor.  These
remaining limitations are feasible to overcome, but in the meantime
the editor is still quite useful for exploring and modifying 
models created using .ty scripts.
</DL>


<H2>Near future:</H2>
<DL COMPACT>

<P><DT>Archival state saving</DT><DD>

Model state saving is currently implemented using Python "pickling"
(persistent storage).  As the Topographica classes change, these files
quickly become out of date, and cannot be loaded into more recent
versions.  By the 1.0 release we plan to provide an upgrade path, so
that old saved files can be used with new versions.  To make this
simpler, we are working on an alternative implementation of state
saving using XML, which is designed to be an archival, readable
format.  In the meantime, users should be aware that saved snapshot
files will not necessarily be readable by future versions of
Topographica, and should be considered temporary.
<!-- Also consider CDF, HDF, or something like it for binary files -->
  
<P><DT>Progress updating and cancellation</DT><DD> 
Progress reporting of the display has now been implemented during
learning, so that users will be able to tell how much progress has
been made.  However, during other processor-intensive computations
like computing preference maps, the display will not yet be updated,
and users are likely to assume that the software has hung.  Thus it is
crucial to provide a status display in such cases, as well as allowing
interruption or other activities during long computations.
<!--
  Using an RPC (or XML-RPC) subprocess would be nice, because it will
  allow a "clean reload" of the simulation like what you get with F5
  in IDLE, and will allow the GUI to be local while the simulator runs
  on a distant machine.
-->
In addition to the progress bars, it would be nice to have an estimate
for the memory requirements of a large network, so that the user can
verify that it is a reasonable simulation to run on his or her machine.

<!-- Should consider sparse layers with patch distribution of units -->

<P><DT>More example models</DT><DD>
Topographica currently includes a small sampling of example models,
primarily from the visual system.  Additional models are being implemented
in Topographica, including somatosensory models and additional visual
models from our labs and elsewhere (including motion direction, eye
preference, and color map simulations) as well as other sample visual
system models from the literature.  These will act as starting points
for developing models in Topographica.

<P><DT>Bitmap plotting enhancements</DT><DD>

The current basic support for two-dimensional bitmap plotting will
eventually need to be expanded to allow the user to control plot
brightness scaling, provide numerical indications of the plotting
scales, allow custom colormaps, and add an "overload" or "cropped"
indicator to show if some values are too large to be displayed in the
selected range.

<P><DT>Automatic line-based 2D plotting</DT><DD>
We have recently added 1D (line) and 2D (contour or vector field)
plots based on
<A HREF="http://matplotlib.sourceforge.net/">MatPlotLib</A> for any
program object selected by the user.  We will also eventually be
making the general-purpose template-based plotting use the 2D plots,
which will make it possible to do
<A HREF="http://matplotlib.sourceforge.net/screenshots/pcolor_demo_large.png">contour</A>
plots, as well as matrix plots showing axis ticks and labels.  We
also plan to use MatPlotLib 2D plots to allow any SheetView(s) to be
used as a or vector field overlay on top of a bitmap, e.g. for joint
preference maps (such as direction arrows on topo of an orientation
bitmap plot).
<!-- Plan: Templates accept a Contours parameter, which can be a list
of (sheetview, threshold) pairs, which will be drawn in order. -->

<P>Other minor changes planned include adding outlining of
ConnectionField extents, plotting histograms for each bitmap,
and separate default colors for onscreen and publication plots.
<!-- plus user-defined arbitrary colormaps ("KRYW", "BbKrR", etc.). -->
  
<P><DT>Selecting units for plotting or analysis</DT><DD>
In many of the GUI displays, a large number of units are shown.  These
plots are designed to make the large-scale topographic structure of
the network clear.  However, it is often desirable to relate this
large-scale structure to the small-scale structure of individual units
or small areas of them.  Doing so is currently difficult, because the
individual units are not labeled or individually selectable.  We plan
to make all such plots "live", so that individual units or
ConnectionFields can be selected and analyzed.

<P><DT>Map statistics</DT><DD>  
We will implement general routines for measuring the statistical
properties of Sheets, such as for computing a perceived orientation.
</DL>


<H2>Eventually:</H2>
<DL COMPACT>

<P><DT>Improve documentation</DT><DD>
The reference manual is generated automatically from the source code,
and needs significant attention to ensure that it is readable and
consistent.  For instance, not all parameters are documented yet, but
all will need to be.

<P><DT>More testing code</DT><DD>
Topographica has a fairly complete test library, but there are still
classes and functions without corresponding tests.  Eventually, there
should be tests for everything.

<P><DT>Pycheck/pylint</DT><DD>
It would be helpful to go through the output from the pycheck and
pylint programs (included with Topographica), fixing any suspicious
things, and disabling the remaining warnings.  That way, new code
could be automatically checked with those programs and the warnings
would be likely to be meaningful.

<P><DT>Animating plot histories</DT><DD>
GUI plot windows save a history of each plot, and it should be
feasible to add animations of these plots over time, as a helpful
visualization.

<P><DT>Registry editor</DT><DD>
In a large network with components of different types, each having
various parameters and default values, it can be difficult to
determine the values that will be used for new objects of a certain
type.  We plan to add a hierarchical global variable display and
editor to allow these values to be inspected and changed more easily.

<P>We also plan to add the ability to track which parameters have
actually been used by a given object, so that it is clear how
to modify the behavior of that object.

<P><DT>User-defined scales</DT><DD>
The simulator is written in terms of abstract dimensions, such as
Sheet areas that default to 1.0.  This helps ensure that the simulator
is general enough to model a variety of systems.  However, it is often
desirable to calibrate the system for specific scales, such as degrees
of visual angle, millimeters in cortex, etc.  We plan to add
user-defined scales on top of the arbitrary scales, mapping from
values in the simulator to user-defined quantities for display.
<!-- See http://ipython.scipy.org/doc/manual/node11.html for bg on handling arbitrary units. -->

<P><DT>Parallelization</DT><DD>
Due to their weakly interconnected graph structure, Topographica
models lend themselves naturally to coarse-grained parallelization.
Each event processor (e.g. a Sheet) can run on a different physical
processor, exchanging information with other event processors using
either shared memory or message passing protocols such as MPI.
Implementing this type of parallelization is not likely to require
significant changes to the simulator.
<!-- 
  Should be able to do this without significant
  changes to the code, by adding a parallel Simulator class and proxies
  for the EPs and Connections. E.g. for shared memory threads, need
  two new classes ThreadedSimulator and EPThreadProxy:

  - Each time an EP is added to  the simulator it's wrapped in an
    EPThreadProxy that intercepts all calls between the Simulator
    and the EP (i.e. the EP's .sim attribute points to the proxy,
    instead of the simulator) (jprovost)

  Should also be able to do it using RPC or MPI.

  May also be able to distribute Projections, not just Sheets,
  automatically. 
-->

<P>Fine-grained parallelism is also possible, distributing computation
for different units or subregions of a single Sheet, or different
parts of a Projection across different
processors.  This has been implemented on a prototype version for a
shared-memory Cray MPP machine, and may be brought into the main
release if it can be made more general.  Such fine-grained parallelism
will be restricted to specific Sheet and/or Projection types, because
it requires access to the inner workings of the Sheet.

<P><DT>More non-visual modalities</DT><DD>
Most of the specific support in Topographica is designed with visual
areas in mind, but is written generally so that it applies to any
topographically organized region.  We plan to implement specific
models of non-visual areas, providing input generation, models of
subcortical processing, and appropriate visualizations.  We also plan
to add similar support for motor areas.  Contributions from
Topographica users with experience in these domains will be
particularly helpful.

<P><DT>Data import/export</DT><DD> It will be crucial to provide
easy-to-use interfaces for exchanging data and calling code in other
simulators, such as Matlab (see
<A HREF="http://pymat.sourceforge.net">pymat.sourceforge.net</A>).
These will be used both for analyzing Topographica data, and for
allowing connection patterns and/or map organization to be specified
from experimental data.  Meanwhile, the Python command-line interface
can be used to display or save any element of the model.

<P><DT>Lesion support</DT><DD>
Eventually, all components will be temporarily lesionable, i.e.,
disabled in a way that their function can be restored.  This
capability will be crucial for testing which components are required
for a certain behavior, and for replicating animal lesion experiments.

<P><DT>More library components</DT><DD>
Topographica currently includes examples of each type of library
component, such as Sheets, Projections, ResponseFunctions,
LearningFunctions, and PatternGenerators.  However, many other types
are used in the literature, and as these are implemented in
Topographica they will be added to the library.  Again, user
contributions are very welcome!
