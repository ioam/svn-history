<H1>Generating patterns</H1>

<P>Topographica provides comprehensive support for creating
two-dimensional patterns of various sorts.  These patterns can be used
for generating training or testing inputs, generating initial or fixed
weight patterns, neighborhood kernels, or any similar application.

<H2>Simple patterns</H2>

<P>Topographica patterns are created using objects of type
<A HREF="../Reference_Manual/topo.base.patterngenerator.html">
PatternGenerator</A>, which is an object that will return a 2D pattern
when it is called as a function.  For instance, the Gaussian
PatternGenerator will return Gaussian-shaped patterns:

<pre>
$ ./topographica -g
Topographica&gt; from topo.patterns.basic import Gaussian
Topographica&gt; pg=Gaussian(xdensity=10,ydensity=10,size=0.3,aspect_ratio=1.0)
Topographica&gt; 
Topographica&gt; from topo.commands.pylabplots import *
Topographica&gt; matrixplot(pg())
Topographica&gt; matrixplot(pg(size=0.5))
</pre>

<center>
<img src="images/gaussian_0.3.png" width=279 height=279><img src="images/gaussian_0.5.png" width=279 height=279>
</center>

<P>As you can see, the parameters of a PatternGenerator can be set up
when you create the object, or they can be supplied when you generate
the pattern.

<P>The reason for the name PatternGenerator is that the objects can
each actually return an infinite number of patterns, if any of the
parameters are set to Dynamic values.  For instance, a Gaussian input
pattern can be specified to have a random orientation and (x,y)
location:

<pre>
$ ./topographica  -g
Topographica&gt; from topo.patterns.basic import Gaussian
Topographica&gt; from topo.base.parameterclasses import DynamicNumber
Topographica&gt; from topo.misc.numbergenerators import UniformRandom
Topographica&gt; input_pattern = Gaussian(size=0.08, aspect_ratio=4,
                 x=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=12)),
                 y=DynamicNumber(UniformRandom(lbound=-0.5,ubound=0.5,seed=34)),
                 orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=56)))
Topographica&gt; matrixplot(input_pattern())
Topographica&gt; matrixplot(input_pattern())
</pre>

<center>
<img src="images/or_gaussian_1.png" width=279 height=279><img src="images/or_gaussian_2.png" width=279 height=279>
</center>

<P>There are many other types of patterns available already defined in
the <A HREF="../Reference_Manual/topo.patterns.html">
topo/patterns</A> directory, and adding new patterns is
straightforward.  Just find one from that directory to use as a
starting point, then copy it to a new file, modify it, and put the new
file in the patterns directory.  The new pattern should then show up
in the Test Pattern window of the GUI automatically, and can be used
in scripts the same way.

<H2>Composite patterns</H2>

<P>Often, rather than writing a new PatternGenerator class, you can
combine existing PatternGenerators to make a new pattern.  For
instance, you can make connection weights be random but with a
Gaussian falloff in strength by setting:

<pre>
CFProjection.weights_generator=topo.patterns.basic.Composite(
    generators=[topo.patterns.random.UniformRandom(),
                topo.patterns.basic.Gaussian(aspect_ratio=1.0,size=0.2)],
    operator=Wrapper("Numeric.multiply"))
</pre>

<center>
<img src="images/gaussianrandomweights.png" width=640 height=432>
</center>

<P>Similarly, you can construct patterns with different objects in
fixed or variable positions relative to each other, adding or
subtracting from each other (see the
<A HREF="../Reference_Manual/topo.patterns.basic.html#Composite">
Composite parameter <code>operator</code></A>), etc.  In principle, any
pattern can be constructed using Composite, but some will still be
easier to do by coding a new PatternGenerator class.


<H2>Selector patterns</H2>

<P>It is also often useful to choose from a set of different patterns,
randomly or in order, such as from a set of natural images.  This can
be done with the Selector PatternGenerator.  As a contrived example,
weights can be choosen at random from a set of four different
patterns:

<pre>
CFProjection.weights_generator=topo.patterns.basic.Selector(generators=[
    topo.patterns.basic.Gaussian(orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=99))),
    topo.patterns.basic.Gaussian(aspect_ratio=1.0),
    topo.patterns.basic.Rectangle(size=0.2,orientation=DynamicNumber(UniformRandom(lbound=-pi,ubound=pi,seed=99))),
    topo.patterns.basic.Disk(size=0.25)])
</pre>

<center>
<img src="images/fourclassweights.png" width=640 height=436>
</center>
