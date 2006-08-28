<!-- -*-html-helper-*- mode -- (Hint for Emacs)-->

<H1>Overview of Topographica design and features</H1>

This section will first give an overview of the parts that make up
Topographica, and will then give a guide on how to choose a subset of
them for use in any particular model.



<H2><a name="class-hierarchies">Major Topographica object types</a></H2>

<P>In this section, we outline the basic hierarchies of object types
used by Topographica.  All of these are available to the user when
designing a model, but as the <a href="#implementation-levels">
next section</a> indicates, not all of them need to be used for any
particular model.  These lists are only representative of the object
types available in each general class; see the
<A HREF="../Reference_Manual/">reference manual</A>, the menus in the
GUI <A HREF="modeleditor.html">model editor</A>, or the files in
topo/*/ to see the full list of the ones available.

<P>In each section, the relationships between the different classes
are shown as an inheritance diagram, in outline format.  As an
example, the indentation in this diagram:
<ul>
<li>Animal
    <ul>
    <li>Dog
        <ul>
        <li>Collie
        <li>Terrier
        </ul>
    </ul>
</ul>

indicates that a Dog is a type of Animal, and that Collies and
Terriers are both types of Dog (and thus also types of Animals).  All
Collies are Dogs, and all Collies are Animals, but not all Dogs are
Collies, and not all Animals are necessarily Dogs.  These
relationships show how the classes fit together; e.g., anything in
Topographica that requires an object of type Animal will accept a
Collie or a Terrier as well, plus any user-defined object of type Dog.


<H3>ParameterizedObjects and Parameters</H3>

<ul>
<li><?php classref('topo.base.parameterizedobject','ParameterizedObject')?>:
<li><?php classref('topo.base.parameterizedobject','Parameter')?>:
    <ul>
    <li><?php classref('topo.base.parameterclasses','Number')?>:
        <ul>
	<li><?php classref('topo.base.parameterclasses','Integer')?>:
        </ul>
    <li><?php classref('topo.base.parameterclasses','BooleanParameter')?>:
    <li><?php classref('topo.base.parameterclasses','CallableParameter')?>:
    <li><?php classref('topo.base.parameterclasses','ClassSelectorParameter')?>:
    <li><?php classref('topo.base.parameterclasses','CallableParameter')?>:
    </ul>
</ul>

<P>In Python, any object can have <i>attributes</i>, which consist of
a name and a value (of any type).  Topographica provides an extended
version of attributes called
<?php classref('topo.base.parameterizedobject','Parameter')?>s, which have
their own documentation, range and type error checking, and mechanisms for
inheritance of default values.  These features are provided for any
<?php classref('topo.base.parameterizedobject','ParameterizedObject')?>,
which is a Python object extended to support <?php
classref('topo.base.parameterizedobject','Parameter')?>s, such as
allowing any parameter to be set by keyword arguments when creating
the object.  Most Topographica objects are 
<?php classref('topo.base.parameterizedobject','ParameterizedObject')?>s.
<A HREF="parameters.html">Parameters</A> are discussed in more detail on 
<A HREF="parameters.html">a separate page</A>.


<H3>Simulation and Events</H3>

<ul>
<li><?php classref('topo.base.simulation','Simulation')?>:
<li><?php classref('topo.base.simulation','Event')?>:
<li><?php classref('topo.base.simulation','EventProcessor')?>:
    <ul>
    <li><?php classref('topo.base.sheet','Sheet')?>: (see below)
    </ul>
</ul>

<P>The set of objects to be simulated is kept by the 
<?php classref('topo.base.simulation','Simulation')?> class,
which keeps track of the current simulator time, 
<?php classref('topo.base.simulation','Event')?>s,
that are currently occurring or are scheduled to occur in the future.
The objects in the simulation are of type
<?php classref('topo.base.simulation','EventProcessor')?>,
which simply means that they can process events.  Events and
EventProcessors are both very general concepts, because
the Simulation must be able to include any possible process
that could be relevant for a model.


<H3>Sheets</H3>

<P>The actual EventProcessors in most Topographica simulations are
typically of type <?php classref('topo.base.sheet','Sheet')?>.  A
Sheet is a specific type of EventProcessor that occupies a finite 2D
region of the continuous plane, allows indexing of this region using
floating point coordinates, and maintains a rectangular array of
activity values covering this region.

<P>A hierarchy of different Sheet types is available, including (but
in no way limited to):

<P>
<ul>
<li><?php classref('topo.base.sheet','Sheet')?>: Abstract object type
  (of which specific subtypes such as those below can be instantiated).
    <ul>
    <li><?php classref('topo.base.projection','ProjectionSheet')?>:
      Sheet that can calculate activity based on a set of
      <?php classref('topo.base.projection','Projection')?>s.
        <ul>
        <li><?php classref('topo.base.cf','CFSheet')?>:
	  ProjectionSheet whose Projections are of type
	  <?php classref('topo.base.cf','CFProjection')?>,
	  which means that they are made up of
  	  <?php classref('topo.base.cf','ConnectionField')?>s
	  (below).  This Sheet type supports a large class of
	  topographic map models as-is, but others need specific
	  extensions.
        <li><?php classref('topo.sheets.cfsom','CFSOM')?>: 
	  CFSheet with extensions to support the Kohonen SOM algorithm.
        <li><?php classref('topo.sheets.lissom','LISSOM')?>: 
	  CFSheet with extensions to support the LISSOM algorithm.
        </ul>
    </ul>
</ul>


<H3>Connections and Projections</H3>

<P>EventProcessors can be connected together with unidirectional links
called <?php classref('topo.base.simulation','Connection')?>s.  These
connections provide a persistent mechanism for data generated by one
EventProcessor to be delivered to another one after some nonzero delay
in simulation time.

<P>Most connections between Sheets are of type <?php
classref('topo.base.projection','Projection')?>, which can be thought
of as a bulk set of connections that includes many individual
connections between neural units.  More specifically, a Projection is
a Connection that can produce an Activity matrix when given an input
Activity matrix, which will typically be used by the destination Sheet
when it computes its activation.  In the GUI, the Projection activity
can be visualized just as Sheet activity is, though the Sheet activity
is considered the actual response of each unit.  (The Projection
activity is just a handy way of computing and reasoning about the
contribution of each Projection to this overall Sheet activity.)

<P>The specific type of Projection currently implemented is 
<?php classref('topo.base.cf','CFProjection')?>, i.e. a Projection that
consists of a set of <?php
classref('topo.base.cf','ConnectionField')?> objects, each of which
contains the connections to one unit in the destination CFSheet.
A special type of CFProjection, 
<?php classref('topo.projections.basic','SharedWeightCFProjection')?>
is used to perform the mathematical operation of convolution, i.e.,
applying a set of weights to all points in a plane, and is equivalent
to having one ConnectionField shared by every destination neuron.

<ul>
<li><?php classref('topo.base.simulation','Connection')?>:
    <ul>
    <li><?php classref('topo.base.projection','Projection')?>:
        <ul>
        <li><?php classref('topo.base.cf','CFProjection')?>:
            <ul>
            <li><?php classref('topo.projections.basic','SharedWeightCFProjection')?>:
            </ul>
        </ul>
    </ul>
</ul>

<!-- ALERT: Does it work better to have the list first or second?  With -->
<!-- explanations or without? -->

<H3>PatternGenerators</H3>
<ul>
<li><?php classref('topo.base.patterngenerator','PatternGenerator')?>:
    <ul>
    <li><?php classref('topo.patterns.basic','Gaussian')?>:
    <li><?php classref('topo.patterns.basic','Constant')?>:
    <li><?php classref('topo.patterns.basic','UniformRandom')?>:
    </ul>
</ul>


<H3>Output functions</H3>

<ul>
<li><?php classref('topo.base.functionfamilies','OutputFn')?>:
    <ul>
    <li><?php classref('topo.outputfns.basic','DivisiveNormalizeL1')?>:
    <li><?php classref('topo.outputfns.basic','DivisiveNormalizeL2')?>:
    <li><?php classref('topo.outputfns.basic','PiecewiseLinear')?>:
    <li><?php classref('topo.outputfns.basic','Identity')?>:
    </ul>
</ul>

<ul>
<li><?php classref('topo.base.cf','CFPOutputFn')?>:
    <ul>
    <li><?php classref('topo.outputfns.basic','CFPOF_Plugin')?>:
    <li><?php classref('topo.outputfns.basic','CFPOF_DivisiveNormalizeL1')?>:
    </ul>
</ul>




<H3>Response functions</H3>

<ul>
<li><?php classref('topo.base.functionfamilies','ResponseFn')?>:
    <ul>
    <li><?php classref('topo.responsefns.basic','DotProduct')?>:
    </ul>
</ul>


<ul>
<li><?php classref('topo.base.cf','CFPResponseFn')?>:
    <ul>
    <li><?php classref('topo.responsefns.basic','CFPRF_Plugin')?>:
    <li><?php classref('topo.responsefns.basic','CFPRF_DotProduct')?>:
    <li><?php classref('topo.responsefns.optimized','CFPRF_DotProduct_opt')?>:
    </ul>
</ul>


<H3>Learning functions</H3>
<ul>

<li><?php classref('topo.base.functionfamilies','LearningFn')?>:
    <ul>
    <li><?php classref('topo.learningfns.basic','Hebbian')?>:
    </ul>
</ul>

<li><?php classref('topo.base.cf','CFPLearningFn')?>:
    <ul>
    <li><?php classref('topo.learningfns.basic','CFPLF_Plugin')?>:
    <li><?php classref('topo.learningfns.basic','')?>:
    <li><?php classref('topo.learningfns.optimized','CFPLF_DivisiveHebbian')?>:
    <li><?php classref('topo.learningfns.som','CFPLF_HebbianSOMLF')?>:
    </ul>
</ul>

<H2><a name="implementation-levels">How much of Topographica to use</a></H2>

<P>Topographica is designed as an extensible framework or toolkit,
rather than as a monolithic application with a fixed list of features.
Users can extend its functionality by writing objects in Python, a
fully general-purpose interpreted programming language.  As a result,
Topographica supports any possible model (and indeed, any possible
software program), but it provides much more specific support for
specific types of models of topographic maps.  This approach allows
some models to be built without any programming, while not limiting
the future directions of research.

<P>The following list explains the different levels of support
provided by Topographica for different types of models, depending on
which parts of Topographica you are able to use.  The list is ordered
so that the most general support, suitable for everyone but requiring
the most user effort, is at the top, and the most specific support is
at the bottom.  Note that everything in the levels below where your
model fits in can be ignored, because those files can be deleted with no ill 
effects unless some part of your model uses objects from those levels.

<P>Topographica levels:

<ol>
<p><li>Python with C interface (ignoring <i>everything</i> in topo/): 
<dl><dt>Supports:</dt><dd>Anything is possible, with no performance or 
	programming limitations (since anything can be written
	efficiently in C, and the rest can be written in Python)
    <dt>Limitations:</dt><dd>Need to do all programming yourself.  Can't
	mix and match code with other researchers very easily, because
	they are unlikely to choose similar interfaces or make similar 
	assumptions.
</dl>    
<p><li>Everything in 1., plus event-driven simulator with parameterizable objects, debugging 
        output, etc. (using just simulation.py, parameterclasses.py,
        and parameterizedobject.py from topo/base/):
<dl><dt>Supports:</dt><dd>Running simulations of any physical system, with 
	good semantics for object parameter specification with inheritance.
    <dt>Limitations:</dt><dd>Basic event structure is in Python, which is
	good for generality but means that performance will be good
        only if the computation in the individual events is big
        compared to the number of events.  This assumption is true for
        existing Topographica simulations, but may not always apply.
</dl>    
<p><li>Everything in 1.-2., plus Sheets (adding topo/base/sheet.py and its dependencies)
<dl><dt>Supports:</dt><dd>Uniform interface for a wide variety of brain 
        models of topographically organized 2D regions.  E.g. can measure
	preference maps for anything supporting the Sheet interface, and
	can do plotting for them uniformly.
    <dt>Limitations:</dt><dd>Not useful if the assumptions of what 
        constitutes a Sheet do not apply to your model -- e.g. ignores
        curvature, sulci, gyrii; has hard boundaries between regions,
        uses Cartesian, not hexagonal grid.  For instance, Sheets are
        not a good way to model how the entire brain is parcellated
        into brain areas during development, because that arguably
        happens in 3D and does not start out with very strict
        boundaries between regions.
</dl>    
<p><li>Everything in 1.-3., plus Projections and ConnectionFields (adding the rest 
	of topo/base/)
<dl><dt>Supports:</dt><dd>Anything with topographically organized 
	projections between Sheets, each of which contains an array of
	units, each unit having input from a spatially restricted
	region on another (or the same) sheet.  Any such sheet can be
	plotted and analyzed uniformly.
    <dt>Limitations:</dt><dd>Much more specific limitations on what 
	types of models can be used -- e.g. broad, sparse connectivity
	between regions is less well supported (so far), and
	non-topographic mappings are currently left out.
</dl>    
<p><li>Everything in 1.-4., plus the Topographica primitives library (the rest of topo/)
<dl><dt>Supports:</dt><dd>Can implement a large range of map models without
        coding any new objects -- instead setting parameters and calling
        methods on existing objects.  Easy to mix and match components
        between models, and to add just a few new components for a new
        but similar model.  Easy to compare different models from this
        class under identical conditions.
    <dt>Limitations:</dt><dd>Only a relatively small set of components
	has actually been implemented so far, and so in practice the
	primitives library will need to be expanded to cover most new
	models, even from the class of models described in 4.
</dl>    
</ol>

<P>As one moves down this list, the amount of programming required to
implement a basic model decreases (down to zero if you use only the
primitives we've already implemented), but the limitations governing
what can be done at that level increase.  To the extent that these
limitations are appropriate for what you want to model, Topographica
will be an appropriate tool.  If what you want to do conflicts with
these limitations, you will have to go up to higher levels in this
list, doing more of the implementation work yourself and gaining less
from what the Topographica developers have done.  If everything you
are doing ends up being implemented at level 1 above, then there is
probably no reason to use Topographica at all, except perhaps as an
example of how to use Python and C together with various external
libraries.

<P>Note that different parts of any particular model may be implemented
at different levels from this list.  For instance, even for a model that
is fully supported by the Topographica primitives in level 5, you may
want to add an interface to an external sensor such as a camera, which
would have to be implemented at level 1 because no such interface
currently exists.  Data from the camera would then presumably appear
in a form compatible with one of the lower layers 3-5, and could then
be used	with the other Topographica primitives.

