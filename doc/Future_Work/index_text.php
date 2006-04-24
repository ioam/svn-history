<P>Topographica is still under very active development.  As described
below, a large number of changes and new features are scheduled over
the next few months, as well as over the next few years.

<H2>Most urgent (First quarter 2006):</H2>
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
platforms.  We are committed to supporting the Windows version, but also
currently support the Mac OS X version.  Recent versions have been
tested successfully on Linux, Mac, and Windows. However, because of the 
rapid pace of development and the developers' limited access to Mac and
Windows machines, it is possible that some new features will not work
on these platforms. However, it is not usually difficult for individual 
tech-savvy users to get Topographica working on those platforms before 
we have had a chance to look at them.

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

<P><DT>State saving</DT><DD>
Model state saving is currently implemented using Python "pickling"
(persistent storage).  Some important classes of objects cannot yet be
pickled, including class attributes (defaults for a class rather than
an object), functions scheduled using Simulator.schedule_action, and
any variable holding a lambda function.  As a result, there can be
cases when not all of the important properties of the network are
restored, and we will be working to eliminate such cases.  In
addition, pickling is not robust against changes to the class
definitions for LISSOM, such as changes in class names.  To reduce these
problems, we are working on an alternative implementation of state
saving using XML, which is designed to be an archival, readable
format.  In the meantime, users should be aware that saved snapshot
files will not necessarily be readable by future versions of
Topographica, and should be considered temporary.

<P><DT>Plotting</DT><DD>
Two-dimensional bitmap plots are already supported, but will be
expanded significantly over the near term and longer term.  Immediate
tasks include allowing the user to control plot brightness scaling if
desired, adding user-defined colormaps, and adding an "overload" or
"cropped" indicator to show if some values are too large to be
displayed in the selected range.  We will also be adding support for
arbitrary user-defined colormaps, and for numerical indications of the
plotting scales.

<P><DT>Input patterns</DT><DD>
The support for drawing input patterns is fairly mature, but support
for Composite patterns is not yet complete.  Composite patterns are
necessary for such things as weights initialized with Gaussians plus
random noise, multiple patterns per iteration, or selecting from a
database of natural images.  
<!-- Also need to respect bounding boxes for this to be practical. -->

<P><DT>Circular CFs</DT><DD>
Preliminary support is now implemented for circular (or any other
  shape) CFs, but this will be improved in upcoming releases.
<!-- Also should consider sparse layers with patch distribution of units -->

<P><DT>Convolution Projections</DT><DD>
LGN models use Difference of Gaussians (DoG) units, which are
effectively convolutions of a fixed weight vector with an input
region, are now supported, but these will be improved in upcoming
releases.

<P><DT>Command-line and batch interfaces</DT><DD>
Although Topographica is written to be independent of the type of
interface, and does not require a GUI or other interactive console,
some functions are currently implemented only in the GUI.  Others are
currently more difficult to use in batch mode, requiring longer and
more complex commands than necessary.  These items will be simplified
and made more appropriate for command-line and batch use, to make
using larger networks more practical.

<P><DT>GUI model editor</DT><DD>

The Topographica GUI supports plotting and analysis of existing
networks, and now includes a network construction GUI that allows
primitives to be selected from the library and connected into a model
network.  Parameters and options can then be set on these components,
thus defining a simulation without requiring coding (except to add new
primitives if desired).  This facility is still under development, and
is still missing some crucial functionality required for the graphical
approach to be useful, such as the ability to set object parameters
before they are constructed.  These limitations will be removed very
soon, allowing the editor to be used to construct useful models.
</DL>


<H2>Near future (first half 2006):</H2>
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
We have recently added 1D (line) and 2D (contour or vector field)
plots based on
<A HREF="http://matplotlib.sourceforge.net/">MatPlotLib</A> for any
program object selected by the user.  We will also be making the
general-purpose template-based plotting use the 2D plots, which will
make it possible to do
<A HREF="http://matplotlib.sourceforge.net/screenshots/pcolor_demo_large.png">contour</A>
plots, as well as matrix plots showing axis ticks and labels.  We
also plan to use MatPlotLib 2D plots to allow any SheetView(s) to be
used as a or vector field overlay on top of a bitmap, e.g. for joint
preference maps (such as direction arrows on topo of an orientation
bitmap plot).
<!-- Plan: Templates accept a Contours parameter, which can be a list
of (sheetview, threshold) pairs, which will be drawn in order. -->

<P>Other minor changes planned include adding outlining of
ConnectionField extents, and plotting histograms for each bitmap.

<P><DT>Selecting units for plotting or analysis</DT><DD>
In many of the GUI displays, a large number of units are shown.  These
plots are designed to make the large-scale topographic structure of
the network clear.  However, it is often desirable to relate this
large-scale structure to the small-scale structure of individual units
or small areas of them.  Doing so is currently difficult, because the
individual units are not labeled or individually selectable.  We plan
to make all such plots "live", so that individual units or
ConnectionFields can be selected and analyzed.

<P><DT>Command console</DT><DD>
At the moment, the Topographica console GUI window provides a single 
command-line widget, allowing arbitrary Python commands to be executed.
However, the output from those commands goes into the shell window
from which Topographica was launched, which can be confusing, because
the commands themselves do not appear there.  It would be good to add
a visible command I/O history that shows both the commands executed
and their output, either as a single shell-editor component (like IDLE
or MatLab) or as a separate pane (not a drop-down).  
<!--
  The PMW HistoryText
  widget will probably work nicely for this, but you need to figure out
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
  for different uses, and to allow the streams to be played back reliably.

  <P><DT>Map statistics</DT><DD>  
  Will implement general routines for measuring the statistical
  properties of Sheets, such as for computing a perceived orientation.
-->
</DL>


<H2>Eventually:</H2>
<DL COMPACT>

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

<P><DT>Plot histories</DT><DD>
It would be nice if GUI plot windows could save a user-selectable
amount of history, so that one could scroll back and forth over time
to compare the time-stamped plots.  Once this is done, it should be
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

<P><DT>Improve documentation</DT><DD>

The reference manual is generated automatically from the source code,
and needs significant attention to ensure that it is readable and
consistent.  For instance, not all parameters are documented yet, but
all will need to be.

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

<P><DT>Non-visual modalities</DT><DD>
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



<!--

Should add links to CNV course and its exercises as something that can
be done with Topographica.

Should add filename of first script, or some other user-definable screen,
to all window titles, so that different simulators can be kept straight.



     Could consider adding external packages or taking some code from them:
     SciPy
     Pyro (Robotics)
     logger
     g

Should add simple timing functions -- what was the total time to run?
What components are taking a long time to run?  Guide the user for
optimization, focusing on the components we expect to be the
bottlenecks.

Should add ability to add arbitrary image to a PlotGroupTemplate (see
plot.py).

Consider adding a main Documentation page, which describes each of the
manuals and who should read which one.

Web site with results of unit tests, updated nightly?

From Geisler meeting 7/1/2005:
  Should support additive noise, with lots of places where it could be added
  Package as a Matlab toolbox to get the right people to use it?
  Package it as an easy-to-use out-of-the-box optical imaging simulator
    -- need to tell it what stimulus, what eccentricity, what cortical patch
  Be able to look at the effects of attention
  Add specific models for intrinsic or voltage-sensitive-dye imaging 
  Would be great if the software would support exploring the role of 
   different types of noise, before doing experiments
-->

<!-- Text from former MILESTONES file

  - Add bitmap colorizations (using palette.py)

  - Add black and white background options.

  - Add state (weight) saving. (done)

  - Verify/fix .ty file importing; it should work just like .py file
    importing.  May need to send some changes to the Python maintainers.

  - Verify that everything works on Windows and Mac.  

  - Support composite objects (for multiple training inputs, face
    patterns).

  - Add linking objects between eyes (for e.g. ocular dominance).

  - Add user-defined arbitrary colormaps ("KRYW", "BbKrR", etc.).

  - Add sheet edge buffers.

  - Implement binary file saving, using CDF, HDF, or something like it.

  - Add histogram plots.

  - Add remaining radial functions, if any, from both input generation
    and kernel factory routines.

  - Configure GUI to pop up a requestor for urgent-enough messages.
  
  - Consider supporting 1D and 3D line-based plotting, using
    e.g. Matplotlib or Pyx, though this can possibly be postponed to
    the next milestone.
  
  - Add bounding intersections and unions, which are needed when RFs
    extend past the edge of a sheet. (intersections done)
  
  - Make sure that most parameters use bounded ranges.
  
  - Consider adding a general mechanism for scaling values from one
    range to another, so that units can be specified as the user desires
    and then converted to what the code expects. 
  
  - Add a mechanism to group Sheets into a logical unit for plotting,
    analysis, etc.  For instance, it should be possible to group three
    R,G,B sheets into one eye, two ON and OFF sheets into one LGN area,
    and several V1 layers into one stack.  Such grouping should support
    e.g. presenting a color bitmap to an Eye instead of to R, G, and B
    separately, plotting the resulting activation from the three areas
    in true color, combining ON and OFF plots into one bitmap (by
    subtraction), and measuring a vertically summed orientation map for a
    model using several layers.  This functionality may only be required for
    later milestones, but is listed here in case it is required for ON/OFF
    plots.
  
  - Unify random number generation, so that users can manipulate seeds
    appropriately to play back a particular simulation.
  
  - Consider using the Python logger module as a back end for logging
    messages.
  
  - Might, or might not, want to support LISSOM's backprojection fuctions.

Milestone 4: Stable APIs. Finalize the user APIs, and port all
categories of simulations from parts II and III of the LISSOM book
(i.e. orientation maps, ocular dominance maps, direction maps,
combined maps, face maps, and two-level maps) to Topographica.

Reaching this milestone is primarily an issue of agreement between all
developers that the API has matured to the point that it will be
extensible in the directions we plan for Topographica to go, without
breaking existing user code.  Of course, we won't be able to do this
perfectly, and some changes to user code will be necessary, but after
this point we will have to provide some way to convert old user code
into something that will work with each new release.

Once milestone 4 is released, we can make a full 1.0 public release,
and we can stop using LISSOM for anything but retrieving historical
results.


Milestone 5: Advancing. Implement a large percentage of the features
promised in the Topographica grant proposal, enough to clearly
demonstrate that the software is a big advance over LISSOM
5.0.

Once milestone 5 has been reached, we can make another public
release and start heavily marketing the software to all potential
users, trying to convince them to switch from whatever they are
currently using to Topographica.  

Also see the Topographica grant proposal.  This milestone will include
things like GUI-based network building, algorithms other than LISSOM
and SOM, libraries of other learning rules and neuron types, etc.

_______________________________________________________________________________

From Tue Sep  6 15:32:25 BST 2005 meeting with Eyal

Major issues
____________

Overall, the documentation and software need to separate 'Learning and
self-organization' from 'Representing signals in topographic maps' and
'Understanding topographic maps'.

Should allow the user to specify the parameters and network setup
themselves, instead of having a learned map.  (E.g. select tuning
width, connection types, etc.)

It should also be possible to import a map measured in the lab into
Topographica, then allow the user to try it out by synthesizing a
network based on that data.

More ambitiously, could start out with the above rough sketch of a
network, then auto-optimize parameters to match a set of behavioral
observations. Longer-term project; will need ways to explore the
space of possible models matching those observations.

In general, it would be useful to start with a set of observations,
and select parameters that match that. 

Should be able to specify (parametrically?) the tuning properties, and
of course measure and display those.

Need to have some representation of receptive fields, mapped onto
actual size units in the world.

Need to be able to map things to millimeters of cortex, and degrees of
visual angle.  E.g. need to be able to map measured locations in the
visual cortex into the model, or even map the measured retinotopic
grid directly into the model.

Color lookup tables for plotting: user needs to pick them, and need
to have keys shown as a color bar.  Also needs to control the
baseline, clipping range, etc. and to have a clipping warning light.

For Eyal's work, adding realistic dynamics is key, including being
able to control the time course, e.g. with various delays.  E.g. it
would be great to have a movie showing the time course of an
activation.  Usually they look at an array of activation patterns, 10
images per row, and then average groups of e.g. 10 frames or subsample
them.  They would usually want to simulate to match the measurement
interval, e.g. 100 Hz, then average for display...

Should study how to add noise to the system.  Both neural noise and
measurement noise are important, including e.g. spatial correlations
(due to lateral connections or feedback?) in spontaneous or evoked
activity, and e.g. how they vary with different assumptions about the
connectivity.

In general, it's an open issue how to have a network with a good
dynamic range but still stable, given background levels of activity,
spontaneous activity in darkness, etc.; will be worth studying.


Less crucial points
___________________

For the display, will be useful to have the units displayed on screen,
etc.

For plotting styles, check Shmuel and Grinvald and Fitzpatrick lab
(e.g. does anyone else have OR-colored activity patterns?).

Array of curves plots:
If they start with an image of 1000x1000 pixels, they bin the data to
100x100 pixel blocks, then plot the average time course of the
response, as a single curve for each condition (x is time, y is change
in fluorescence).  Then each of 100 panels will show 5 or 6 different
curves for different experimental conditions.  (Similar to EEG data --
shows spatial location of small differences between conditions.)

Need good plots of receptive fields -- with the location and size
plotted on the retina.

Minor points for the tutorial:

   When we show the plots, we have white outlines around the lateral
   connections, but don't ever explain them. (easily fixed)
  
   Should show a color bar, and allow user to modify the clipping
   range, etc. (not likely to be fixed in LISSOM, but will be done in
   Topographica).
  
   Explain some of the parameters better (should be easily fixed)


Need to add color keys to the Preference Map panels, e.g. by having a
slot for it in the template.

_______________________________________________________________________________

More Eyal comments:

Need to specify what each 'neuron' in the simulation represents.
How many simulated 'neurons' per simulated 'column'?

Good point.

Why are the lateral excitatory connections so limited and fixed?

It would be nice to include moving stimuli (drifting gratings, random dots etc.)

Display issues;
  
  1) Model editor - not clear how to interpret; how to modify;

  2) State that each little plot in the projection plot shows only the
     connection field of the neuron, not the entire set of afferents from the retina.

  3)      Suggestions for Test pattern window
  a.       contrast (0-100%) instead of scale
  b.      mean luminance (0-1) instead of offset
  c.       Change units for orientation to deg

  (Part of our general project of allowing
   user-configurable units. I think that's is the only way to do things
   like this, because the simulator is not limited to vision only, and so
   the underlying units have to be very general.)

Minor
  
3) Say in the tutorial that orientation maps look funny around the
edges, because of the effects of having lateral connections 
that are cut in half at that border.

To figure out:

4) There is no response in V1 to a small square despite a strong
   response in the retina. Does the response get canceled by the
   lateral inhibition?

5) At point 9 in the tutorial, when I press the Normalize toggle I get
   strange activity pattern in the retina and V1 and when I press the
   Normalize toggle again it does not revert to the old response.
-->
