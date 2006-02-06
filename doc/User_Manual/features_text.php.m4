m4_dnl Must be preprocessed by m4 to handle the citations
m4_include(shared/bib2html.m4)m4_bib2html_init[[]]m4_dnl
m4_bib2html_cite_named(deangelis:jnp93,[[DeAngelis et al 1993]],deangelis:tins95,[[1995]]).

The Topographica project aims to make computational modeling of
cortical maps a viable research focus in behavioral neuroscience.
In the project, a set of software tools for large-scale
computational modeling of the structure, development, and function
of cortical maps are being developed. 

These tools are designed to support:
    
(1) Rapid prototyping of multiple, large cortical maps, with
specific afferent and lateral connectivity patterns, adaptation
and competitive self-organization, and firing rate and
spiking neuron models;

(2) Automatic generation of inputs for self-organization and
testing, allowing user control of the statistical environment,
based on natural or computer-generated inputs;

(3) Graphical user interface for designing networks and
experiments, and integrated visualization and analysis tools for
understanding the results, as well as for validating models
through comparison with experimental results.
  
The goal is to create a simulator that is user programmable,
generalizes to different network arrangements and phenomena of
different sizes, is interoperable with general-purpose analysis
and visualization tools and low-level neuron simulators, and runs
on PCs as well as parallel supercomputers. With Topographica,
models can be built that focus on structural, functional, or
integrative phenomena, either in the visual cortex or in other
sensory cortices.  The first full release of Topographica is
scheduled for late 2004, and it will be freely available over the
internet at <A HREF="http://topographica.org">topographica.org</A>.



User interface -- Topographica supports different interfaces for different tasks:
Graphical user interface (GUI) for interactive use
Command-line interface for remote use, with separate image viewer
Script interface (in the Python programming language) for batch use
User extensible using custom scripts

Platform Support:
Tested on Windows, Mac OS X, and Linux.
Should work on other varieties of UNIX.
Parallel-processor support planned


Building and Testing Models
Topographica Models

<IMG WIDTH="400" HEIGHT="433" SRC="images/generic-cortical-hierarchy-model.png">

Models are composed of interconnected maps
Each brain region can be represented by multiple overlaid maps (e.g. ON and OFF LGN cells)
Each map can be coarse or detailed, plastic or fixed, as needed
Maps can be monolithic or built up from primitives
Maps can be connected internally with lateral connections


Simulating Environment and Test Patterns:

Map-scale models require spatially coherent input patterns to
drive learning and test responses.  Topographica provides
facilities for generating and presenting visual inputs,
spontaneous activity, test patterns, etc.:
  User-definable streams of random (and other) distributions for controlling inputs
  Arbitrary input generation (rendered, sampled, scaled, composite)
  Library of standard two-dimensional patterns (Gaussian, Gabor, random noise, etc.)
  Flexibly coordinated/correlated patterns between input areas (e.g. eyes or layers)
  Test pattern generation (e.g.\ for psychophysical experiments)
  Natural image and natural video support 
  Real-time interfaces to cameras, video (possibly)
  Time-varying inputs, such as moving patterns
  Inputs from multiple modalities (auditory, somatosensory)

Topographica Primitives

Models can be constructed using primitives from the following
partial list:

Unit Models:
  Firing-rate neurons m4_bib2html_cite_named(wilson:biophysj72,[[Wilson et al. 1972]])
  Spiking (leaky integrate-and-fire) neurons m4_bib2html_cite_named(lapicque:jppg1907,[[Lapique 1907]])
  BCM m4_bib2html_cite_named(bienenstock:theory,[[Bienenstock et al.]])
  Pipeline model m4_bib2html_cite_named(geisler:nato99,[[Geisler et al. 1999]])
  External neuron plugins (GENESIS, NEURON)
  Arbitrary user-specified unit model in Python
  Activation function options for most of these types:  sigmoid, linear, bounded linear, arbitrary Python function


  Connection Types
      Mechanism: additive or multiplicative
      Effect: modulate activity (typical), or plasticity (learning gate) m4_bib2html_cite_named(kirkwood:jneuro94,[[Kirkwood et al. 1994]])
      Time delays: none, fixed, learned
      Fixed or initial weight configuration: specified via arbitrary 2D function
      Relative strength: sign determines excitatory or inhibitory; value and sign can be fixed, or a Python function of the current activation level
      %% (fn is e.g.\ for m4_bib2html_cite_named(stemmler:lateral,[[Stemmler et al.]]).)
      %% What about an offset as well as this scale?  (For e.g.\ centering around zero.)
      %% What would it mean for the scale and/or offset to be learnable?
      Storage location: instar m4_bib2html_cite_named(grossberg:kybernetik72,[[Grossberg et al. 1972]]),
      outstar m4_bib2html_cite_named(grossberg:pnas68,[[Grossberg et al. 1968]])
      Areal target or source: any region of any map, including self

 Plasticity rules
      Hebbian,
      Anti-Hebbian,
      Covariance m4_bib2html_cite_named(dayan:book01,[[Dayan et al. 2001]])
      BCM m4_bib2html_cite_named(bienenstock:theory,[[Bienenstock et al.]]),
      m4_bib2html_cite_named(oja:analyzer,[[Oja]]) rule
      Spike-Timing--Dependent Plasticity m4_bib2html_cite_named(markram:science97,[[Markram et al. 1997]])
      %%    Trace learning m4_bib2html_cite_named(wallis:pnb97,[[Wallis et al. 1997]]),
      m4_bib2html_cite_named(foldiak:nc91,[[Foldiak et al. 1991]])
      %%    Supervised rules (perceptron learning, delta/Widrow-Hoff)
      Synaptic depression/facilitation m4_bib2html_cite_named(finlayson:ebr95,[[Finlayson et al. 1995]])
      SOM learning rule m4_bib2html_cite_named(kohonen:original,[[Kohonen]])
      %%    Rules with weight decay term
      %%    Elastic net
      %%    Dynamic link matching
      Arbitrary user-specified plasticity rules
      Normalization: none, divisive, subtractive, saturation,
      %%    \ \ sum-of-weight-squares subtractive, sum-of-weight-squares divisive,
      arbitrary Python function from weights to weights\\[1.5ex]

Column models
      Simple: one unit per column
      Laminar: Combine arbitrary layers with units of different types
%     Arbitrary model: Python or GENESIS/NEURON plugin\\[1.5ex]

Layer/network models
      Multiple input channels (e.g.\ ON and OFF pathways)
      Arbitrary number and organization of cortical/subcortical areas
      Inter-area feedback connections
      Sparse layers with patchy distribution of units

Analyzing and Validating Models
  Computation of orientation maps, ocular dominance maps, etc.
  Arbitrary stimulus map computation 
  Statistical analysis of activity levels
  Flexible user-configurable plotting \\ (receptive fields, activity levels, maps, histograms)
  Arbitrary lesion support %prototyped
  %Generates color plots for typical use, monochrome equivalents for use with certain publications
  External data analysis and visualization %prototyped
  External image data import/export
  Externally-specified connection patterns and network data import
  
  
Interfacing spiking and firing-rate neurons:
  Firing-rate $\rightarrow$ spiking: Generate spike trains
  Spiking $\rightarrow$ firing-rate: Running average, other ways to extract scalar from temporal codes
  Will use set of glue/bridge classes

<HR>
m4_bib2html_bibliography(topographica)
