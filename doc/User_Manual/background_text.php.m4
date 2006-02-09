m4_dnl Must be preprocessed by m4 to handle the citations
m4_include(shared/bib2html.m4)m4_bib2html_init[[]]m4_dnl
m4_bib2html_cite_named(deangelis:jnp93,[[DeAngelis et al 1993]],deangelis:tins95,[[1995]]).

<p>Abstract: The biological function of cortical neurons can often be
understood only in the context of large, highly interconnected
networks.  These networks typically form two-dimensional topographic
maps, such as the retinotopic maps in the visual system.  This poster
briefly surveys phenomena that emerge at the topographic map level,
such as orientation and ocular dominance maps and object segmentation
and grouping.  It also reviews approaches to modeling and simulating
these phenomena, and provides examples using the LISSOM topographic
map model.  These types of simulations will be supported by our
upcoming Topographica map-level simulator.  Topographica is designed
to make large-scale models practical, allowing neuroscientists and
computational scientists to understand how topographic maps and their
connections organize and operate.  This understanding will be crucial
for integrating experimental observations into a theory of cortical
function.

Cortical surface is nearly two dimensional<BR>
Divided up into many roughly topographic maps<BR>
Understanding these maps is crucial for neuroscience<BR>

<P><CENTER><IMG BORDER="2" WIDTH="427" HEIGHT="189" SRC="images/measuring-map.v3.png"></CENTER>
In each area, optical imaging can be used to determine maps of
preference for different types of stimuli
E.g. m4_bib2html_npcite_named(blasdel:differential,[[Blasdel 1992]],chapman:jn96,[[(Chapman et al. 1996]],crair:science98,[[(Crair et al. 1998]],weliky:nature96,[[(Weliky et al. 1996]])

Orientation and Ocular Dominance
Canonical map examples
Overall organization is retinotopic
Orientation preference and eye preference are interleaved with position preference
Maps interact in non-trivial ways
Organization not visible if measuring only a few (or a few hundred) neurons
  
Other Maps::
Direction preference m4_bib2html_cite_named(weliky:nature96,[[(Weliky et al.,1996)]],shmuel:jneuro96,[[(Shmuel et al. 1996)]])
Spatial frequency m4_bib2html_cite_named(issa:jn01,[[(Issa et al. 2001)]])
Disparity?

Motor:
Movement location?

Auditory:
Frequency preference
IATD (inter-aural time difference)

Somatosensory:
Body location
Others?

Modeling Maps
Research Questions
    
How is the cortex divided into maps during development?
How does each topographic map develop, and why?
What are the roles of environmental and intrinsic cues in map development?
What computations do maps perform in the adult?
How are high-level operations such as object segmentation, grouping, and recognition implemented in maps?
How can we link phenomena at the map level to activity of single units?

Goal: understanding cortex at a scale relevant to behavior

Map-Scale Models
<P><CENTER><IMG BORDER="2" WIDTH="320" HEIGHT="346" SRC="images/generic-cortical-hierarchy-model.png"></CENTER>


Map models focus on patches of cortex several mm^2 in size (and above)
Emphasis is on 2D structure
Usually driven by optical imaging results

Goals of Map Models
    
Understand computation in adults
Understand map development
Link development and adult function
Explain sensory artifacts (illusions, aftereffects)
Predict response to injury, experimental manipulations

  
Modeling Approach
    
Pick cortical area to model (e.g. 4 mm$^2$ of cat V1)
Add detail as needed to study particular phenomena
Amount of detail limited by:
  Computation time
  Experimental data available to constrain behavior and parameters
  Conceptual complexity of model
Validate model on existing data
Make predictions for new experiments

Types of Map Models
    
Most represent a cortical area as an array of simple interconnected units on a grid
Individual unit models:
  Firing-rate point neurons (typical)
  Integrate-and-fire neurons
  Compartmental models (rare)

Synapses typically represented by a single number
Also: Continuous analytical approximations (rare)\\
 m4_bib2html_cite_named(amari:topographic,[[Amari]],roquedasilvafilho:phd92,[[(Roquedasilvafilho et al. 1992]])
    
See m4_bib2html_cite_named(swindale:network96,[[(Swindale et al. 1996]],erwin:models,[[Erwin et al.]]) for review

Conclusions

Models at the map level can be:

Detailed enough to be constrained biologically, yet
Practical to implement and evaluate
Suitable for testing both function and development
Extensible to greater detail

    
<HR>
m4_bib2html_bibliography(topographica)
