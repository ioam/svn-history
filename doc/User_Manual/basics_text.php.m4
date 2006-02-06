m4_dnl Must be preprocessed by m4 to handle the citations
m4_include(shared/bib2html.m4)m4_bib2html_init[[]]m4_dnl

<P>
<A HREF="basics.html">Topographica basics</A><BR>
<A HREF="background.html">Background</A><BR>
<A HREF="features.html">Topographica features</A><BR>
<A HREF="about.html">About Topographica</A><BR>

<P><IMG src="../images/Topo-arch-white.jpg" width="300" height="326" border="2" alt="Sample architecture"><BR>

<P><img border="2" width="649" height="529" src="images/toplevel.png"><BR> <!-- Also, _bare -->
<P><img border="2" width="388" height="381" src="images/sheet_coords.png"><BR>
<P><img border="2" width="372" height="369" src="images/matrix_coords.png"><BR>
<P><img border="2" width="372" height="397" src="images/connection_field.png"><BR>
<P><img border="2" width="509" height="505" src="images/retina_edge_buffer.png"><BR>

<HR>

<P>Where to set parameters -- classes?  objects?  How does inheritance work?


Should present brief background, then point to the book.
-- general motivation and background (why use Topographica?  Why not?)

Overview of basic design:

  Event-driven simulator, time scale
  Sheets
  sheet coordinates, densities, bounding boxes
  class parameters
  instance/constructor parameters
  How to define a new simulator
  Hierarchy diagram: the major classes that matter
  Lots of examples

What to trust?
What types of new things are easy to add?
What's the current status?  What do we want users to use Topographica for right now?

Point to python tutorial


 Starting point:
  1) existing model, want to make a change, or
  2) biological system, want to model it
      - Need to choose sheets, projections, properties from existing list, then
      - Need to analyze how it behaves (plotting, statistics, etc.), then
      - Depending on how well it fills the needs, need to be able to add
          new primitives or edit existing ones
      - Produce figures, tables, etc. for publication


Sheet
  ProjectionSheet
    CFSheet
      CFSOM
      LISSOM

Connection
  Projection
    CFProjection
      SharedWeightCFProjection
      CFProjection_CPointer

OutputFunction
  DivisiveSumNormalize
  DivisiveLengthNormalize
  PiecewiseLinearSigmoid
  Identity

ResponseFunction
  CFDotProduct
  CFDotProduct_Py

CFLearningFunction
  GenericCFLF
  DivisiveHebbian
  HebbianSOMLF

PatternGenerator
  Gaussian
  Constant
  UniformRandom






images/000516_or_map_16MB.020000.or.pdf  48x48
images/000516_or_map_32MB.020000.or.pdf  64x64
images/000516_or_map_128MB.020000.or.pdf 96x96
images/000516_or_map_512MB.020000.or.pdf 144x144
Orientation map scaling:
    Four LISSOM orientation maps from networks of different sizes
    are shown; the parameters for each network were calculated using
    the scaling equations from m4_bib2html_cite_named(bednar:neuroinformatics04,[[(Bednar et al. 2004]]).  The size
    of the network in the number of connections ranged from $2\times
    10^7$ to $1\times 10^9$ (7 megabytes to 480 megabytes of
    simulation memory), and the simulation time ranged from ten
    minutes to four hours on the same machine, a single-processor 
    600MHz Pentium III with 1024 megabytes of RAM.  %3:54
    (Much larger simulations on the massively parallel Cray T3E
    supercomputer perform similarly.)  Despite this wide range of
    simulation scales, the final map organizations are both
    qualitatively and quantitatively similar, as long as the sheet size
    is above a certain minimum for the map type.


After exploring the behavior of the small network, the larger one can
then be simulated on a supercomputer, using the same software, and
without requiring a parameter search.  All Topographica parameters
are specified in units that are independent of the density of the
modeled regions, and thus the density can be changed at any time.

This rapid scaleup capability means that Topographica can be
used to obtain meaningful results in just a few minutes using a
personal computer, yet those results can be translated easily to a
large, densely sampled network on a larger machine.  In addition,
unlike neuron-level simulators, which will require much technological
progress before simulating a large brain area will be practical,
Topographica can already simulate all of human V1 (one of the largest
visual areas) at the single-column level on practical workstations
m4_bib2html_cite_named(bednar:neuroinformatics04,[[(Bednar et al. 2004]]). 
With increases in computing power, even multiple
cortical areas should become practical at the single-column level in
the near future.  The underlying scaling equations
also provide an easy trade-off between resolution and total size or
complexity, which makes it easy to focus on particular levels of
analysis, such as long-term organization or short-time-scale behavior.
They will also help calibrate the simulation parameters
of small networks with experimental measurements in larger
preparations. 





<H1>Introduction</H1>



Much of the cortex of mammals can be partitioned into topographic maps
m4_bib2html_cite_named(kaas:ccortex97,[[Kaas et al. 1997]],vanessen:vres01,[[Vanessen et al. 2001]]).  These maps contain systematic
two-dimensional representations of features relevant to sensory and
motor processing, such as retinal position, sound frequency, line
orientation, and motion direction
m4_bib2html_cite_named(blasdel:orientation,[[Blasdel 1992]],merzenich:jnp75,[[Merzenich et al. 1975]],weliky:nature96,[[Weliky et al. 1996]]).
Understanding the development and function of topographic maps is
crucial for understanding brain function, and will require integrating
large-scale experimental imaging results with single-unit studies of
individual neurons and their connections.

Computational simulations have proven to be a powerful tool in this
endeavor.  In a simulation, it is possible to explore how topographic
maps can emerge from the behavior of single neurons, both during
development and during perceptual and motor processing in the adult.
(For a review of this class of models, see m4_bib2html_cite_named(swindale:network96,[[Swindale et al. 1996]].)
However, the models to date have been limited in size and scope
because existing simulation tools do not provide specific support for
biologically realistic, densely interconnected topographic maps.
Existing biological neural simulators, such as NEURON
m4_bib2html_cite_named(hines:nc97,[[Hines et al. 1997]]) and GENESIS m4_bib2html_cite_named(bower:genesisbook98,[[Bower et al. 1998]]), primarily
focus on detailed studies of individual neurons or very small networks
of them.  Tools for simulating large populations of abstract units,
such as PDP++ m4_bib2html_cite_named(oreilly:book00,[[O'Reilly et al, 2000]]) and Matlab (www.mathworks.com),
focus on cognitive science and engineering applications, rather than
detailed models of cortical areas.  As a result, current simulators also
lack specific support for measuring topographic map structure or
generating input patterns at the topographic map level.

This paper introduces the Topographica map-level simulator, which is
designed to make it practical to simulate large-scale, detailed models
of topographic maps.  Topographica is designed to complement the existing
low-level and abstract simulators, focusing on biologically realistic
networks of tens of thousands of neurons, forming topographic maps
containing millions or tens of millions of connections.  Topographica is
being developed at the University of Texas at Austin as part of the
Human Brain Project of the National Institutes of Mental Health.
Topographica is an open source project, and binaries and source code will
be freely available through the internet at <A HREF="http://topographica.org">topographica.org</A>.
In the sections below, we describe the models and modeling approaches
supported by Topographica, how the simulator is designed, and how it can
be used to advance the field of computational neuroscience.

<H1>Scope and modeling approach</H1>


<IMG WIDTH="400" HEIGHT="433" SRC="images/generic-cortical-hierarchy-model.png">
  Topographica models
    This figure shows a sample Topographica model of the early visual
    system m4_bib2html_cite_named(bednar:nc03,[[Bednar et al. 2003]],bednar:neurocomputing03,[[Bednar et al. 2003]]).
    In Topographica, models are composed of interconnected sheets of neurons.  
    Each visual area in this model is represented by one or more sheets.  For
    instance, the eye is represented by three sheets: a sheet representing
    an array of photoreceptors, plus two sheets representing
    retinal ganglion cells.  Each of the sheets can be coarse or
    detailed, plastic or fixed, as needed for a particular study.  Sheets
    are connected to other sheets, and units within each sheet can be
    connected using lateral connections.  For one cell in each sheet in
    the figure, sample connections are shown, including lateral
    connections in V1 and higher areas.
    Similar models can be used for topographic maps in somatosensory,
    auditory, and motor cortex.
%%
Figure~1GENERIC illustrates the types
of models supported by Topographica.  The models focus on topographic maps
in any two-dimensional cortical or subcortical region, such as visual,
auditory, somatosensory, proprioceptive, and motor maps.  Typically,
models will include multiple regions, such as an auditory or visual
processing pathway, and simulate a large enough area to allow the
organization and function of each map to be studied.  The external
environment must also be simulated, including playback of visual
images, audio recordings, and test patterns.  Current models typically
include only a primary sensory area with a simplified version of an
input pathway, but larger scale models will be crucial for
understanding phenomena such as object perception, scene segmentation,
speech processing, and motor control.  Topographica is intended to support
the development of such models.

To make it practical to model topographic maps at this large scale,
the fundamental unit in the simulator is a two-dimensional
<I>sheet</I> of neurons, rather than a neuron or a part of a neuron.
Conceptually, a sheet is a continuous, two-dimensional area (as in
m4_bib2html_cite_named(amari:topographic,[[Amari]],roquedasilvafilho:phd92,[[Roque da Silva Filho et al. 1992]]), which is typically
approximated by a finite array of neurons.  This approach is crucial
to the simulator design, because it allows user parameters, model
specifications, and interfaces to be independent of the details of how
each sheet is implemented.

As a result, the user can easily trade off between simulation detail
and computational requirements, depending on the specific phenomena
under study in a given simulator run.  (See
m4_bib2html_cite_named(bednar:neuroinformatics04,[[Bednar et al. 2004]]) for more details on model scaling.)
If enough computational power and experimental measurements are
available, models can be simulated at full scale, with as many neurons
and connections as in the animal system being studied.  More
typically, a less-dense approximation will be used, requiring only
ordinary PC workstations.  Because the same model specifications and
parameters can be used in each case, switching between levels of
analysis does not require extensive parameter tuning or debugging as
would be required in neuron-level or engineering-oriented simulators.

For most simulations, the individual neuron models within sheets can
be implemented at a high level, consisting of single-compartment
firing-rate or integrate-and-fire units. More detailed neuron models
can also be used, when required for experimental validation or to
simulate specific phenomena.  These models will be implemented using
interfaces to existing low-level simulators such as NEURON and
GENESIS.  

<H1>Software design and architecture</H1>

Topographica consists of a graphical user interface (GUI), scripting
language, and libraries of models, analysis routines, and
visualizations. The model library consists of predefined types of
sheets, connections, neuron models, and learning rules, and can be
extended with user-defined components.  These building blocks are
combined into a model using the GUI and (when necessary) the script
language.

The analysis and visualization libraries include statistical tests and
plotting capabilities geared towards large, two-dimensional areas.
They also focus on data displays that can be compared with
experimental results, such as optical imaging recordings, for
validating models and for generating predictions.
Figure~SCREENSHOT shows examples of the visualization
types currently supported.  This figure is a screenshot from a
prototype version of Topographica, available for download at
<A HREF="http://topographica.org">topographica.org</A>.
%
<IMG WIDTH="400" HEIGHT="433" SRC="images/lissom.4.0_linuxscreenshot2_white.png">
  Software screenshot
    This image shows a sample session of a prototype version of
    Topographica that is available freely at 
    <A HREF="http://topographica.org">topographica.org</A>.  Here the
    user is studying the behavior of an orientation map in the primary
    visual cortex (V1), using a model similar to the one depicted in
    figure~GENERIC.  The window at
    the bottom labeled ``Orientation'' shows the self-organized
    orientation map and the orientation selectivity in V1.  The
    windows labeled ``Activity'' show a sample visual image on the
    left, along with the responses of the retinal ganglia and V1
    (labeled ``Primary'').  The input patterns were generated using
    the ``Test pattern parameters'' dialog at the left.  The window labeled
    ``Weights'' shows the strengths of the connections to one neuron
    in V1.  This neuron has afferent receptive fields in the ganglia
    and lateral receptive fields within V1.  The afferent weights for
    an 8x8 and 4x4 sampling of the V1 neurons are
    shown in the ``Weights Array'' windows on the right; most neurons
    are selective for Gabor-like patches of oriented lines.  The
    lateral connections for an 8x8 sampling of neurons are
    shown in the ``Weights Array'' window at the lower left; neurons
    tend to connect to their immediate neighbors and to distant
    neurons of the same orientation.  This type of large-scale
    analysis is difficult with existing simulators, but
    Topographica is well suited for it.  See 
    <A HREF="http://topographica.org">topographica.org</A> for
    a color version of this figure.

To allow large models to be executed quickly, the numerically
intensive portions of the simulator are implemented in C++.  Equally
important, however, is that prototyping be fast and flexible, and that
new architectures and other extensions be easy to explore and test.
Although C++ allows the fine control over machine resources that is
necessary for peak performance, it is difficult to write, debug and
maintain complex systems in C++.

To provide flexibility, the bulk of the simulator is implemented in the
Python scripting language.  Python is an interactive high-level
language that allows rapid software development and interactive
debugging, and includes a wide variety of software libraries for tasks
such as data analysis, statistical measurements, and visualization.
Unlike the script languages typically included in simulators, Python
is a complete, well-defined, mature language with a strong user
base.  As a result, it enjoys strong support outside of the field of
computational neuroscience, which provides much greater flexibility
for users, and also makes the task of future maintenance easier.



Progress towards
understanding brain function using computational models can be broken down into three
stages: (1) proposing and implementing a model based on existing data,
(2) understanding how the model works through simulation and
analysis, and (3) validating the predictions and insights from the model
in further neuroscience experiments.  This section will
explain the tools that Topographica will offer for model development, while
section~ANALYSIS-AND-VALIDATION will describe the analysis and
validation of completed models.

In order to simulate large models efficiently yet support flexible
prototyping and development of new models, Topographica provides
multiple levels of tools and extension capabilities.  First, efficient
pre-defined primitives are provided for the common mathematical and
computational models used by neuroscientists and modelers.  Where
necessary for good performance, these primitives have been implemented
in C and linked into the Python language, appearing just like those
written in Python.  Second, Python is used to combine the primitives
into a full system model (and a GUI interface is currently under
development to make this possible without programming directly in
Python).  Finally, new primitives may be defined
in the scripting language, through interfaces to external simulators,
or in C where necessary for performance.
We first review the primitives and then show how they can be combined
using the scripting language to support a wide variety of models.
The details of the software implementation are described later in 
section SCRIPTING.



The first full release of Topographica is scheduled for late 2004, and will include
support for Linux, Microsoft Windows, and Macintosh OS X platforms.  This
release focuses on support for models of vision, but most of the
primitives are also usable for auditory and somatosensory models.
Included are flexible routines for generating visual inputs (based on 
geometric patterns, mathematical functions, and photographic images),
and general-purpose mechanisms for measuring maps of visual stimulus
preference, such as orientation, ocular dominance, motion direction,
and spatial frequency maps.

<H1>Future research</H1>

Using the tools provided by Topographica, we expect that neuroscientists
and computational researchers will be able to answer many of the
outstanding research questions about topographic maps, including what
roles environmental and intrinsic cues play in map development, and
what computations they perform in the adult.  Other current research
topics include understanding how object segmentation, grouping, and
recognition are implemented in maps, and how feedback from higher
areas and visual attention affect lower level responses.  The
simulator is designed throughout to be general and extensible, and so
it will also be able to address new research questions that arise from
future experimental work.

Several releases of Topographica are planned over the next few years,
including user-contributed extensions and models.  An online
repository will also be set up for user contributions, so that
researchers can share code and models.  The overall goal is to 
work towards a common understanding of how topographic maps
develop and function.

<H1>Conclusion</H1>

The Topographica simulator fills an important gap between existing software
for detailed models of individual neurons, and software for abstract
models of cognitive processes.  The simulator focuses on models
formulated at the topographic map level, which is crucial for
understanding brain function.  We believe this shared, extensible tool
will be highly useful for the community of researchers working to
understand the large-scale structure and function of the cortex.



<HR>
m4_bib2html_bibliography(topographica)
