<H1>Topographica' Parameters</H1>

<P>Simulation parameters are handled 
specially in Topographica, to allow specific behaviours.
This special handling is provided by TopoObject - the base class
for most objects in Topographica - in conjunction
with the Parameter class. 

<P>For example, take the TopoObject instance
G=topo.patterns.basic.Gaussian().  This is a two-dimensional Gaussian
pattern generator. You can see in a Test Pattern window that a
Gaussian is specified by scale, offset, x, y, size, aspect_ratio, and
orientation. These are all Parameters of G.  You can see one feature
of Parameters immediately by trying to enter <i>-1</i> in the
<i>aspect_ratio</i> box: a ValueError occurs. The bounds of a
Parameter can be specified so that an error is raised if a user
attempts to set a value outside these bounds; in this case, the
<i>aspect_ratio</i> cannot be negative. 

<P>Looking at the source code
for topo.patterns.basic.Gaussian, you can see that <i>aspect_ratio</i> is declared to be a Number parameter. There are several different types of Parameter; which to use depends on what behaviour you want: a DynamicNumber, for example, allows you to generate a new value each time it is accessed, whereas a Constant's value cannot be changed.

<P>You might also notice in the source file that not all the parameters needed to specify a Gaussian pattern are isent. Most, such as <i>x</i> and <i>y</i> are inhertied from the base class, PatternGenerator: Parameters themselves are inherited up the TopoObject class hierarchy. In addition to TopoObjects inheriting Parameters, Parameters themselves can inherit attributes. Let's say I want the default value of <i>x</i> to be different for the Gaussian. I declare a new Number parameter <i>x</i> with a different default value:
<br>
<i>x = Number(default=0.5)</i>
<br>
Gaussian patterns will have <i>x</i> values that default to 0.5 instead of 0.0. In PatternGenerator, you can see that as well as a default, softbounds are also specified for <i>x</i>. the purpose of these is to provide an indication for something such as a the graphical interface to Topographica what kind of scale ... CEBHACKALERT: (1) softbounds is a bad example (2) inheritance of bounds doesn't work: see HACKALERT in TopoObject.
<P>
<pre>
 - TopoObject: what does it provide?
 - Where should parameters for TopoObjects be set?
    - at the class level?
    - in the constructor for a TopoObject?
    - on a constructed instance?
   What is the meaning of setting in each of those places, and when is
   one better than the other?
 - How does Parameter inheritance work?
</pre>
