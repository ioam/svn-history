<H1>Topographica's Parameters</H1>

<!--CEBHACKALERT: still being written. Needs reorganizing
and updating (already!). -->

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

<P>You might also notice in the source file that not all the parameters needed to specify a Gaussian pattern are isent. Most, such as <i>x</i> and <i>y</i> are inhertied from the base class, PatternGenerator: Parameters themselves are inherited up the TopoObject class hierarchy. In addition to TopoObjects inheriting Parameters, Parameters themselves can inherit attributes. Let's say I want the default value of <i>x</i> to be different for the Gaussian. I declare a new Number parameter in the Gaussian source code <i>x</i> with a different default value:
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

<p>
In Python, attributes declared at the class level are shared by all instances of that class, unless an instance overwrites the attribute with its own copy of the variable. For example:
<pre>
class Example(object):

    a = 10

    def __init__(self,b):
        self.b = b

</pre>
<i>a</i> is a class attribute; creating two instances of Example demonstrates the important behaviour:
<pre>
Topographica> example1 = Example(b=12)
Topographica> example2 = Example(b=5)
Topographica> example1.a
10
Topographica> example1.b
12
Topographica> example2.a
10
Topographica> example2.b
5
Topographica> Example.a
10
Topographica> Example.a=7
Topographica> example1.a
7
Topographica> example2.a
7
</pre>
Note that setting the class attribute on the Example class changed the value
held in both instances. For an Example instance to have its own, independent
copy of the variable, it is necessary to set the variable directly on the 
instance:
<pre>
Topographica> example2.a=19
Topographica> Example.a
7
Topographica> example1.a
7
Topographica> Example.a=40
Topographica> example2.a
19
Topographica> example1.a
40
</pre>
Because instances share the object held in the class attribute, any changes to
attributes of the object will show up in all the instances.

<P>
The same general rules apply to Parameters, which are declared at the class
level:
<pre>
from topo.base.parameterizedobject import ParameterizedObject,Parameter

class ExampleP(ParameterizedObject):

    a = Parameter(default=10)

    def __init__(self,b,**params):
        # invoke ParameterizedObject's parameter handling
        super(ExampleP,self).__init__(**params)
        self.b = b
</pre>
In this case, the behaviour will as for the example above.
<pre>
Topographica> example1 = ExampleP(b=12)
Topographica> example1.a
10
Topographica> ExampleP.a = 40
Topographica> example1.a
40
</pre>
However, Parameters offer a number of advantages for controlling
behaviour. First, when creating an object, the value of a class
Parameter can be passed in and results in the object having its own
copy:
<pre>
Topographica> e1 = ExampleP(5,a=8)
Topographica> e1.a
8
Topographica> ExampleP.a = 12
Topographica> e1.a
8
</pre>
Second, the author of a class can make a particular Parameter 
be instantiated for each new object - overriding the default
behaviour. This is useful when the Parameter will hold a
mutable object that sharing between instances would lead to
confusion. An example of such an object is the response function
<i>PiecewiseLinear</i>, which has the attributes <i>upper_bound</i>
and <i>lower_bound</i>. A user might want to declare that all his
<i>CFSheet</i>s will have response functions that are 
<i>PiecewiseLinear</i>. Under usual Python circumstances,  
instances of the class <i>CFSheet</i>, with its attribute 
<i>output_fn</i>, would share a single <i>PiecewiseLinear</i>
object. A user with a number of <i>CFSheet</i>s might be
surprised to find that setting the <i>lower_bound</i> on one
particular <i>CFSheet</i> would change it on them all:
<pre>
Topographica> CFSheet.output_fn = PiecewiseLinear()
Topographica> LGNOn = CFSheet()
Topographica> LGNOff = CFSheet()
Topographica> LGNOff.output_fn.lower_bound
0.1
Topographica> LGNOn.output_fn.lower_bound = 0.05
Topographica> LGNOff.output_fn.lower_bound
0.05
</pre>
To avoid this confusion, the author of <i>CFSheet</i> can
declare that the output_fn Parameter always be 
instantiated:
<pre>
output_fn = Parameter(default=PiecewiseLinear(),instantiate=True)
</pre>
In this case, each instance of CFSheet will have its own
instance of PiecewiseLinear, independent of other
CFSheets' PiecewiseLinear() instances.

