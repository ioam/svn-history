<P>Topographica is still under very active development, with a large
number of changes and new features scheduled over the next few months. 

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

</DL>

<H2>Near future (early 2006):</H2>
<DL COMPACT>

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
</DL>


<!-- Could consider adding external packages or taking some code from them:
     SciPy
     Pyro (Robotics)
     logger
     g
-->
