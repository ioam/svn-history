<P>Topographica is still under very active development.  As described
below, a large number of changes and new features are scheduled over
the next few months, as well as over the next few years.

<H2>Most urgent (2005):</H2>
<DL COMPACT>
<DT>ALERTs</DT><DD>
There are a large number of relatively small problems noted in the
source code for the simulator; these are marked with comments
containing the string ALERT.  These comments help clarify how the code
should look when it is fully polished, and act as our to-do list.
They also help prevent poor programming style from being propagated to
other parts of the code before we have a chance to correct it.  We are
working to correct all of these issues in the very near future.

<P><DT>Windows and Mac versions</DT><DD> 

Topographica is written in Python, which is available for many
platforms.  We are committed to supporting the Windows version, and
also plan to support the Mac OS X version.  Recent versions have so
far been tested only on Linux, and due to the rapid pace of
development, some changes are expected to be needed for non-Linux
platforms.  We will announce when these changes have been made,
although it is possible for individual users to get Topographica
working on those platforms before we have had a chance to look at

<P><DT></DT><DD>
The GUI and the simulation run should be asynchronous, either using
threads or subprocesses.  Right now, the GUI is on hold (not even
redrawing the screen) during processor-intensive computations such as
learning or computing preference maps.  Without any progress report or
status meter, users are likely to assume that the software has hung.
Thus it is crucial to provide this sort of status display, as well as
allowing interruption or other activities during long computations.
<!-- 
  Using an RPC (or XML-RPC) subprocess would be nice, because it will
  allow a "clean reload" of the simulation like what you get with F5
  in IDLE, and will allow the GUI to be local while the simulator runs
  on a distant machine.
-->

<P><DT>Plotting</DT><DD>
Two-dimensional bitmap plots are already supported, but will be
expanded significantly over the near term and longer term.  Immediate
tasks include allowing the user to control plot brightness scaling if
desired, and adding an "overload" or "cropped" indicator to show if
some values are too large to be displayed in the selected range.  We
will also be adding support for arbitrary user-defined colormaps.

<P><DT>Input patterns</DT><DD>
The support for drawing input patterns is fairly mature, but to handle
multiple patterns per presentation, it will be necessary to add a
Composite pattern type, which combines multiple PatternGenerator
outputs into a single pattern.  
<!-- Also need to respect bounding boxes for this to be practical. -->

<P><DT>Sheet scaling</DT><DD>
The size and density of Sheets can currently be specified and changed
arbitrarily, but some parameters (such as the learning rates) are still
defined in forms that are valid only for specific densities.  These
parameters will be redefined to be expressed in density-independent terms.

<P><DT>Circular CFs</DT><DD>
Currently, only square ConnectionFields are implemented, but support
for circular (or any arbitrary shape) ConnectionFields will be added soon. 
<!-- Also should consider sparse layers with patch distribution of units -->

<P><DT>Convolution Projections</DT><DD>
Typical LGN models use Difference of Gaussians (DoG) units, which are
effectively convolutions of a fixed weight vector with an input
region.  Implementing these in Topographica will be straightforward,
and should be done in the near future.

<P><DT>Command-line and batch interfaces</DT><DD>
Although Topographica is written to be independent of the type of
interface, and does not require a GUI or other interactive console,
some functions are currently implemented only in the GUI.  Others are
currently more difficult to use in batch mode, requiring longer and
more complex commands than necessary.  These items will be simplified
and made more appropriate for command-line and batch use, to make
using larger networks more practical.

</DL>


<H2>Near future (early 2006):</H2>
<DL COMPACT>

<P><DT>Example models</DT><DD>
Topographica currently includes a small sampling of example models
drawn from the work of the authors.  However, over the next few months
we will be adding a large number of other example models from our labs
(including motion direction, eye preference, and color map
simulations) as well as other sample visual system models from the
literature.  These will act as starting points for developing models
in Topographica.

<P><DT>Plotting</DT><DD>
We will be adding 1D (line) and 2D (contour or vector field) plots
based on <A HREF="http://matplotlib.sourceforge.net/">MatPlotLib</A>
in the near future.  MatPlotLib is already included in the
distribution, and can be used to visualize any data in the simulation,
but we do not yet provide examples or generate the plots
automatically.  We plan to use MatPlotLib 2D plots to allow any
SheetView(s) to be used as a <A
HREF="http://matplotlib.sourceforge.net/screenshots/pcolor_demo_large.png">contour</A>
or vector field overlay on top of a bitmap, e.g. for joint preference
maps (such as direction arrows on topo of an orientation bitmap plot).

<P>Other minor changes planned include adding a "Situate" option to
weights plots (to show where the ConnectionField is located on the
input Sheet), outlining of ConnectionField extents, and adding
histograms for each bitmap.

<P><DT>Selecting units for plotting or analysis</DT><DD>
In many of the GUI displays, a large number of units are shown.  These
plots are designed to make the large-scale topographic structure of
the network clear.  However, it is often desirable to relate this
large-scale structure to the small-scale structure of individual units
or small areas of them.  Doing so is currently difficult, because the
individual units are not labeled or individually selectable.  We plan
to make all such plots "live", so that individual units or
ConnectionFields can be selected and analyzed.

<P><DT>Network design GUI</DT><DD>
The Topographica GUI supports plotting and analysis of existing
networks.  However, the networks themselves must be implemented using
the Python scripting language.  We are currently designing a network
construction GUI that will allow primitives to be selected from the
library and connected into a model network.  Parameters and options
can then be set on these components, thus defining a simulation
without requiring coding (except to add new primitives if desired).

<P><DT>Command console</DT><DD>
At the moment, the Topographica console GUI window provides a single 
command-line widget, allowing arbitrary Python commands to be executed.
However, the output from those commands goes into the shell window
from which Topographica was launched, which can be confusing, because
the commands themselves do not appear there.  It would be good to add
a visible command i/o history that shows both the commands executed
and their output, either as a single shell-editor component (like IDLE
or MatLab) or as a separate pane (not a drop-down).  
<!--
  The PMW HistoryText
  widget will probably work nicely for this, but you need to figureout
  how to get the output that normally goes to the shell window and put
  it in a gui pane.  Pyro Robotics does this, so you might be able to
  steal their code. (jprovost)
-->

<P><DT>Spiking support</DT><DD>
Topographica currently supports only firing-rate (scalar) units, but
we have prototyped integrate-and-fire spiking unit support separately.
We are currently working on adding spiking Sheets, interfaces between
spiking and non-spiking Sheets, and analysis tools for spiking
neurons.  We expect to support integrate-and-fire and related
computationally tractable spiking unit models; more detailed
compartmental models based on the cable equation can be simulated
in Neuron or Genesis instead.

<!--
  <P><DT>Random number streams</DT><DD>
  Need to provide finer control over the generation of separate
  streams of random numbers, allowing them to be selected independently
  for different uses, and to allow the sterams to be played back reliably.

  <P><DT>Map statistics</DT><DD>  
  Will implement general routines for measuring the statistical
  properties of Sheets, such as for computing a perceived orientation.
-->
</DL>


<H2>Eventually:</H2>
<DL COMPACT>

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

<P><DT>Improve documentation</DT><DD>

The reference manual is generated automatically from the source code,
and needs significant attention to ensure that it is readable and
consistent.


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
  for the EPs.  E.g. for shared memory threads, need two new classes
  ThreadedSimulator and EPThreadProxy:

  - Each time an EP is added to  the simulator it's wrapped in an
    EPThreadProxy that intercepts all calls between the Simulator
    and the EP (i.e. the EP's .sim attribute points to the proxy,
    instead of the simulator) (jprovost)

  Should also be able to do it using RPC or MPI.

  May also be able to distribute Projections, not just Sheets,
  automatically. 
-->

<P>Fine-grained parallelism is also possible, distributing computation
for different units or subregions of a single Sheet across different
processors.  This has been implemented on a prototype version for a
shared-memory Cray MPP machine, and may be brought into the main
release if it can be made more general.  Such fine-grained parallelism
will be restricted to specific Sheet and/or Projection types, because
it requires access to the inner workings of the Sheet.

<P><DT>Non-visual modalities</DT><DD>
Most of the specific support in Topographica is designed with visual
areas in mind, but is written generally so that it applies to any
topographically organized region.  We plan to implement specific
models of non-visual areas, providing input generation, models of
subcortical processing, and appropriate visualizations.  We also plan
to add similar support for motor areas.  Contributions from
Topographica users with experience in these domains will be
particularly helpful.


<P><DT>Data import/export</DT><DD>
It will be crucial to provide easy-to-use interfaces for exchanging
data and calling code in other simulators, such as Matlab.  These will
be used both for analyzing Topographica data, and for allowing
connection patterns and/or map organization to be specified from
experimental data.

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



<!-- Could consider adding external packages or taking some code from them:
     SciPy
     Pyro (Robotics)
     logger
     g
-->

</DL>
