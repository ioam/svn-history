m4_dnl Must be preprocessed by m4 to handle the citations
m4_include(shared/bib2html.m4)m4_bib2html_init[[]]m4_dnl

<P>
<A HREF="basics.html">Topographica basics (this file)</A><BR>
<A HREF="background.html">Background</A><BR>
<A HREF="features.html">Topographica features</A><BR>

<P>The external environment must also be simulated, including playback
of visual images, audio recordings, and test patterns.


<P><IMG src="../images/Topo-arch-white.jpg" width="300" height="326" border="2" alt="Sample architecture"><BR>

<P><img border="2" width="649" height="529" src="images/toplevel.png"><BR> <!-- Also, _bare -->

<HR>

<P>Where to set parameters -- classes?  objects?  How does inheritance work?


<P>Should present brief background, then point to the book.
<P>general motivation and background (why use Topographica?  Why not?)

<P>Overview of basic design:

  Sheets
  class parameters
  instance/constructor parameters
  Hierarchy diagram: the major classes that matter
  Lots of examples

<P>What to trust?
<P>What types of new things are easy to add?
<P>What's the current status?  What do we want users to use Topographica for right now?
<P>Point to python tutorial


<P> Starting point:
<P>  1) existing model, want to make a change, or
<P>  2) biological system, want to model it
<br>      - Need to choose sheets, projections, properties from existing list, then
<br>      - Need to analyze how it behaves (plotting, statistics, etc.), then
<br>      - Depending on how well it fills the needs, need to be able to add
<br>          new primitives or edit existing ones
<br>      - Produce figures, tables, etc. for publication


<pre>
images/000516_or_map_16MB.020000.or.pdf  48x48
images/000516_or_map_32MB.020000.or.pdf  64x64
images/000516_or_map_128MB.020000.or.pdf 96x96
images/000516_or_map_512MB.020000.or.pdf 144x144
</pre>
<P>Orientation map scaling:
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


<P>After exploring the behavior of the small network, the larger one can
then be simulated on a supercomputer, using the same software, and
without requiring a parameter search.  All Topographica parameters
are specified in units that are independent of the density of the
modeled regions, and thus the density can be changed at any time.

<P>This rapid scaleup capability means that Topographica can be
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






<P>Progress towards
understanding brain function using computational models can be broken down into three
stages: (1) proposing and implementing a model based on existing data,
(2) understanding how the model works through simulation and
analysis, and (3) validating the predictions and insights from the model
in further neuroscience experiments.  This section will
explain the tools that Topographica will offer for model development, while
section~ANALYSIS-AND-VALIDATION will describe the analysis and
validation of completed models.

<P>In order to simulate large models efficiently yet support flexible
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


<P>The first full release of Topographica is scheduled for late 2004, and will include
support for Linux, Microsoft Windows, and Macintosh OS X platforms.  This
release focuses on support for models of vision, but most of the
primitives are also usable for auditory and somatosensory models.
Included are flexible routines for generating visual inputs (based on 
geometric patterns, mathematical functions, and photographic images),
and general-purpose mechanisms for measuring maps of stimulus
preference, such as orientation, ocular dominance, motion direction,
and spatial frequency maps.

<H2>Future research</H2>

<P>Using the tools provided by Topographica, we expect that neuroscientists
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

<P>Several releases of Topographica are planned over the next few years,
including user-contributed extensions and models.  An online
repository will also be set up for user contributions, so that
researchers can share code and models.  The overall goal is to 
work towards a common understanding of how topographic maps
develop and function.

<H2>Conclusion</H2>

<P>The Topographica simulator fills an important gap between existing software
for detailed models of individual neurons, and software for abstract
models of cognitive processes.  The simulator focuses on models
formulated at the topographic map level, which is crucial for
understanding brain function.  We believe this shared, extensible tool
will be highly useful for the community of researchers working to
understand the large-scale structure and function of the cortex.





<HR>
m4_bib2html_bibliography(topographica)
