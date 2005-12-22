<IMG src="../images/Topo-arch-white.jpg" 
     width="300" height="326" border="2" alt="Sample architecture" align="right"></A>

<P><!--img src="../images/T-bg.png" width="43" height="50" align="left" alt="T" border="2"-->Topographica 

is a software package for computational modeling of neural maps, developed by the 
<a target="_top" href="http://www.anc.ed.ac.uk">Institute for Adaptive and Neural Computation</a>
at the 
<a target="_top" href="http://www.ed.ac.uk">University of Edinburgh</a> and the 
<a target="_top" href="http://www.cs.utexas.edu/users/nn">Neural Networks Research
Group</a> at the 
<a target="_top" href="http://www.utexas.edu">University of Texas at Austin</a>.  
The project is funded by the 
<a target="_top" href="http://www.nimh.nih.gov/neuroinformatics/index.cfm">NIMH Human Brain Project</a> 
under grant 1R01-MH66991.  The goal is to help researchers understand
brain function at the level of the topographic maps that make up
sensory and motor systems.

<P>Topographica is intended to complement the many good low-level
neuron simulators that are available, such as
<A target="_top" HREF="http://www.genesis-sim.org/GENESIS/">Genesis</A> and
<A target="_top" HREF="http://kacy.neuro.duke.edu/">Neuron</A>.  
Those simulators focus on modeling the detailed internal behavior of
neurons and small networks of them.  Topographica instead focuses on
the large-scale structure and function that is visible only when many
thousands of such neurons are connected into topographic maps
containing millions of connections.  Many important phenomena cannot
be studied without such large networks, including the two-dimensional
organization of visual orientation and motion direction maps, and
object segmentation and grouping processes.

<P>To make such models practical, in Topographica the fundamental unit
is a sheet of neurons, rather than a neuron or a part of a neuron.  For most
simulations, the sheets can be implemented at a high level, consisting
of abstract firing-rate or integrate-and-fire neurons.  When required
for validation or for specific phenomena, Topographica will also
support interfaces to sheets developed using more detailed neuron models
in other simulators.  Less-detailed sheets can also be used temporarily,
e.g. when interacting with the model in real time.  Throughout,
Topographica makes it simple to use an appropriate level of detail and
complexity, as determined by the available computing power, phenomena
of interest, and amount of biological data available for validation.

<P>The figure at top right shows an example Topographica model of the
early stages in the visual system, modeling how retinal input is
transformed by the thalamus, primary visual cortex, and higher
cortical areas.  Because Topographica is a general-purpose map
simulator, it will also support any other sensory modality that is
organized into topographic maps, such as touch and hearing, as well as
motor areas.

<P>Topographica is freely available for downloading, and is an open
source project whose capabilities can be extended and modified by any
user.  The project is under active development, but as shown in the
Tutorial it is already suitable for running visual cortex simulations.

Also see our 
<A target="_top" HREF="http://nn.cs.utexas.edu/area-view.php?RECORD_KEY%28Areas%29=AreaID&AreaID(Areas)=11">
research pages</a> for results from simulations run with Topographica
and related tools, and our 
<A target="_top" HREF="http://computationalmaps.org">new book</A> for more details.

