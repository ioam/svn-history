m4_dnl Must be preprocessed by m4 to handle the citations
m4_include(shared/bib2html.m4)m4_bib2html_init[[]]m4_dnl

<P>
<H1>Introduction</H1>

m4_dnl Should ask Science for permission to use vanessen figure
<P>The cerebral cortex of mammals primarily consists of a set of brain areas
organized as topographic maps
m4_bib2html_cite_named(kaas:ccortex97,[[Kaas et al. 1997]],vanessen:vres01,[[Vanessen et al. 2001]]). 
These maps contain systematic two-dimensional representations of
features relevant to sensory, motor, and/or associative processing, such
as retinal position, sound frequency, line orientation, or sensory or
motor motion direction
m4_bib2html_cite_named(blasdel:orientation,[[Blasdel 1992]],merzenich:jnp75,[[Merzenich et al. 1975]],weliky:nature96,[[Weliky et al. 1996]]).
Understanding the development and function of topographic maps is
crucial for understanding brain function, and will require integrating
large-scale experimental imaging results with single-unit studies of
individual neurons and their connections.

<P>Computational simulations have proven to be a powerful tool in this
endeavor.  In a simulation, it is possible to explore how topographic
maps can emerge from the behavior of single neurons, both during
development and during perceptual and motor processing in the adult.
(For a review of this class of models, see
m4_bib2html_npcite_named(swindale:network96,[[Swindale et al. 1996]]).)
However, the models to date have been limited in size and scope
because existing simulation tools do not provide specific support for
biologically realistic, densely interconnected topographic maps.
Existing biological neural simulators, such as NEURON
m4_bib2html_cite_named(hines:nc97,[[Hines et al. 1997]]) and 
GENESIS m4_bib2html_cite_named(bower:genesisbook98,[[Bower et al. 1998]]), 
primarily focus on detailed studies of individual neurons or very
small networks of them.  Tools for simulating large populations of
abstract units, such as PDP++
m4_bib2html_cite_named(oreilly:book00,[[O'Reilly et al, 2000]]) and
Matlab (www.mathworks.com),
focus on engineering or cognitive science applications, rather than
detailed models of neurons and connections in cortical and subcortical
areas.  As a result, current simulators also lack specific support for
measuring topographic map structure or generating input patterns at
the topographic map level.

<P>The Topographica map-level simulator is designed to make it
practical to simulate large-scale, detailed models of topographic
maps.  Topographica complements the existing low-level and abstract
simulators, focusing on biologically realistic networks of tens or
hundreds of thousands of neurons, forming topographic maps containing
tens or hundreds of millions of connections.  

<P>Topographica was developed as a collaboration between the
<a href="http://www.cs.utexas.edu/">University of Texas at Austin</a>
and the <a href="http://www.anc.ed.ac.uk/">University of
Edinburgh</a>, as part of the
<a href="http://www.nimh.nih.gov/neuroinformatics/">Human Brain
Project</a> of the <a href="http://www.nimh.nih.gov">National
Institutes of Mental Health</a>.  Now that the simulator has been
released, it is a fully open source project managed by
<a href="http://homepages.inf.ed.ac.uk/jbednar">James A. Bednar</a>,
who coordinates contributions from all users.  Binaries and source
code are all freely available through the internet at
<A HREF="http://topographica.org">topographica.org</A>, and volunteers
are encouraged to join as Topographica users and developers.

<P>In the sections below, we describe the models and modeling
approaches supported by Topographica, how the simulator is designed,
and how it can be used to advance the field of computational
neuroscience.


<H2>Scope and modeling approach</H2>

<P>Topographica is designed to simulate topographic maps in any
two-dimensional cortical or subcortical region, such as visual,
auditory, somatosensory, proprioceptive, and motor maps, plus the
relevant parts of the external environment.  Typically, models will
include multiple brain regions, such as a part of an auditory or
visual processing pathway, and simulate a large enough area to allow
the organization and function of each map to be studied.  

<P>To make it practical to model topographic maps at this large scale,
the fundamental neural unit in the simulator is a two-dimensional
<I>sheet</I> of neurons, rather than a neuron or a part of a neuron.
Conceptually, a sheet is a continuous, two-dimensional area (as in
m4_bib2html_npcite_named(amari:topographic,[[Amari]],roquedasilvafilho:phd92,[[Roque
da Silva Filho et al. 1992]]), which is typically approximated by a
finite array of neurons.  Topographica models consist of an
interconnected set of such sheets, where each brain region is
represented by one or more sheets.

<table border=0 width="320" height="346" ALIGN=RIGHT>
<tr><td><IMG BORDER="2" WIDTH="320" HEIGHT="346" SRC="images/generic-cortical-hierarchy-model.png"></td></tr>
<tr><td ALIGN="CENTER"><b><A NAME="generic-model">Sample Topographica model of the visual system</A></b></td></tr>
</table>

<P>The figure at right shows a sample Topographica model of the early
visual system m4_bib2html_cite_named(bednar:nc03,[[Bednar et
al. 2003]],bednar:neurocomputing04-or,[[Bednar et al. 2004]]).  In
this model, the eye is represented by three sheets: a sheet
representing an array of photoreceptors, plus two sheets representing
different types of retinal ganglion cells.  The lateral geniculate
nucleus of the thalamus is represented by two sheets, and three
cortical areas are represented by one sheet each.  Each of these
sheets can be coarse or detailed, plastic or fixed, and simple or
complex, as needed for a particular study.

<P>Sheets can be connected to other sheets in any combination,
including lateral connections from the same sheet to itself, and
recurrent feedback between sheets.  Sheet-to-sheet connections are
called projections; these typically consist of a large set of
individual connections between sheets.  For one cell in each sheet in
the figure, example connections are shown for each projection,
including lateral projections in V1 and higher areas.

<P>Similar models can be used for topographic maps in somatosensory,
auditory, and motor cortex.  Current biologically realistic models
include only a small number of sheets starting with a sensory area,
but Topographica is designed to make larger, more complex models
possible to simulate and to understand.  Explicitly formulating models
at the sheet level is crucial to the simulator design, because it
allows user parameters, model specifications, and interfaces to be
independent of the details of how each sheet is implemented.

<P>As a result, the user can easily trade off between simulation detail
and computational requirements, depending on the specific phenomena
under study in a given simulator run.  (See
m4_bib2html_npcite_named(bednar:neuroinformatics04,[[Bednar et
al. 2004]]) for more details on model scaling.)
If enough computational power and experimental measurements are
available, models can be simulated at full scale, with as many neurons
and connections as in the animal system being studied.  More
typically, a less-dense approximation will be used, requiring only
ordinary PC workstations.  Because the same model specifications and
parameters can be used in each case, switching between levels of
analysis does not require extensive parameter tuning or debugging, as
would be required in neuron-level or engineering-oriented simulators.

<P>For most simulations, the individual neuron models within sheets
can be implemented at a high level, consisting of single-compartment
firing-rate or integrate-and-fire units. More detailed neuron models
can also be used, when required for experimental validation or to
simulate specific phenomena.  We plan for these models to be
implemented using interfaces to existing low-level simulators such as
NEURON and GENESIS.


<H2>Software design and architecture</H2>

<P>Topographica is implemented as a set of Python-language
<A HREF="../Reference_Manual/index.html#core">packages providing
the core functionality</A>, including the graphical user interface (GUI),
plus an <A HREF="../Reference_Manual/index.html#library">extensible
library of models, analysis routines, and visualizations</A>. The
model primitives library consists of objects useful in constructing a
model, such as sheets, projections, neural response functions, and
learning rules.  Many predefined objects are included, and adding new
object types is designed to be straightforward.  These building blocks
are combined into a model using either the GUI or the Python scripting
language.

<P>
The analysis and visualization libraries include measurement and
plotting capabilities geared towards large, two-dimensional areas.
They also focus on data displays that can be compared with
experimental results, such as optical imaging recordings, for
validating models and for generating predictions.

<P>
<table border=0 width="320" height="346" ALIGN=RIGHT>
<tr><td><A HREF="../images/060220_topographica_screen_shot.png">
<IMG WIDTH="525" HEIGHT="364" SRC="images/060220_topographica_screen_shot_small.png"></a></td></tr>
<tr><td ALIGN="CENTER"><b>Screenshot of Topographica visualizations</b></td></tr>
</table>

The figure at right shows a Topographica 0.9.1 screenshot with
examples of the visualization types currently supported; the exact
contents of each window will vary in other Topographica versions.
Here the user is studying the behavior of an orientation map in the
primary visual cortex (V1), using a model similar to the one depicted
<A HREF="#generic-model">above</A>.  The window at the bottom labeled
``Orientation Preference'' shows the self-organized orientation map in
V1; each pixel represents the preferred orientation of cells at that
location in the V1 sheet, color-coded using the key at the left.  The
window labeled ``Activity'' shows a sample visual image on the left,
along with the responses of the OFF-center and ON-center retinal
ganglia and LGN (labeled ``LGNOff'' and ``LGNOn'', and V1 (labeled
``Primary'').  The input pattern was generated using the ``Preview''
dialog in the center, currently displaying a Gabor-shaped pattern yet
to be presented.  The window labeled ``Connection Fields'' shows the
strengths of the LGN connections to one neuron in V1.  The color-coded
lateral inhibitory weights for a regular sampling of the V1 neurons
are shown in the ``Projection'' window at the top; neurons tend to
connect to their immediate neighbors and to distant neurons of the
same orientation.  Distortions in the mapping from retina to V1 are
shown in the ``Topographic mapping'' window, which visualizes the
preferred location in retinal space of each V1 neuron.  This type of
large-scale analysis is difficult with existing simulators, but
Topographica is well suited for it.

<P>To allow large models to be executed quickly, the numerically
intensive portions of the simulator are implemented in C++.  Equally
important, however, is that prototyping be fast and flexible, and that
new architectures and other extensions be easy to explore and test.
Although C++ allows the fine control over machine resources that is
necessary for peak performance, it is difficult to write, debug and
maintain complex systems in C++ or other similarly high performance
languages.

<P>To provide flexibility, the bulk of the simulator is implemented in
the <A HREF="http://www.python.org">Python scripting language</A>.
Python is an interactive high-level language that allows rapid
software development and interactive debugging, and includes a wide
variety of widely supported software libraries for tasks such as data
analysis, statistical measurements, and visualization.  Unlike the
script languages typically included in simulators, Python is a
complete, well-defined, mature language with a strong user base.  As a
result, it enjoys strong support outside of the field of computational
neuroscience, which provides much greater flexibility for users, and
also makes the task of future maintenance easier.

<P>The following sections will introduce specific features of
Topographica, focusing on how they can be used to construct
large-scale models of topographic areas.  A good way to make this
material more concrete is to work through one or more of the
<A HREF="../Tutorials/">Topographica tutorials</A>, to gain experience
using Topographica for a particular task.  More details about the
specific objects discussed can be found in the 
<A HREF="../Reference_Manual/">reference manual</A>.

<HR>
m4_bib2html_bibliography(topographica)
