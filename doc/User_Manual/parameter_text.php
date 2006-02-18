<H1>Topographica's Parameters</H1>

<!--CEBHACKALERT: still being written. Needs reorganizing
and updating (already!). -->

<P>Simulation parameters are handled specially in Topographica, to
allow specific behaviours.  This special handling is provided by
ParameterizedObject - the base class for most objects in Topographica
- in conjunction with the Parameter class.

<H2>Introduction to Parameters</H2>

<P>Consider the ParameterizedObject instance
<code>G=topo.patterns.basic.Gaussian()</code>.  This is a
two-dimensional Gaussian pattern generator. You can see in a Test
Pattern window that a Gaussian is specified by <code>scale</code>,
<code>offset</code>, <code>x</code>, <code>y</code>,
<code>size</code>, <code>aspect_ratio</code>, and
<code>orientation</code>. These are all Parameters of <code>G</code>.
You can see one feature of Parameters immediately by trying to enter
<code>-1</code> in the <code>aspect_ratio</code> box: a ValueError
occurs. The bounds of a Parameter can be specified so that an error is
raised if a user attempts to set a value outside these bounds; in this
case, the <code>aspect_ratio</code> cannot be negative.

<P>Looking at the source code for
<code>topo.patterns.basic.Gaussian</code>, you can see that
<code>aspect_ratio</code> is declared to be a <code>Number</code>
parameter. There are several different types of
<code>Parameter</code>; which to use depends on what behaviour you
want: a <code>DynamicNumber</code>, for example, allows you to
generate a new value each time it is accessed, whereas a
<code>Constant</code>'s value cannot be changed.

<P>You might also notice in the source file that not all the
parameters needed to specify a Gaussian pattern are isent. Most, such
as <code>x</code> and <code>y</code> are inhertied from the base
class, PatternGenerator: Parameters themselves are inherited up the
TopoObject class hierarchy. In addition to TopoObjects inheriting
Parameters, Parameters themselves can inherit attributes. Let's say I
want the default value of <code>x</code> to be different for the
Gaussian. I declare a new Number parameter in the Gaussian source code
<code>x</code> with a different <code>default</code> value: 

<pre> x=Number(default=0.5) </pre> 

Gaussian patterns will have <code>x</code> values that default to
<code>0.5</code> instead of <code>0.0</code>. In
<code>PatternGenerator</code>, you can see that as well as a
<code>default</code> value, there are <code>softbounds</code>,
<code>doc</code>, and <code>precedence</code>. What these do is
explained in <code>Parameter</code>'s specific documentation, but
taking the example of <code>doc</code> (which describes what the
parameter is), after re-defining <code>x</code> and setting a new
<code>default</code> in <code>Gaussian</code>, <code>Gaussian.x</code>
will contain the same string for <code>doc</doc> as
<code>PatternGenerator.x</code>.


<H2>Using Parameters</H2>
<P>
In Python, attributes declared at the class level are shared by all
instances of that class, unless an instance overwrites the attribute
with its own copy of the variable. For example: 

<pre> 
class
Example(object):

    a = 10

    def __init__(self,b):
        self.b = b

</pre>
<code>a</code> is a class attribute; creating two instances of Example demonstrates the important behaviour:
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
<code>PiecewiseLinear</code>, which has the attributes <code>upper_bound</code>
and <code>lower_bound</code>. A user might want to declare that all his
<code>CFSheet</code>s will have response functions that are 
<code>PiecewiseLinear</code>. Under usual Python circumstances,  
instances of the class <code>CFSheet</code>, with its attribute 
<code>output_fn</code>, would share a single <code>PiecewiseLinear</code>
object. A user with a number of <code>CFSheet</code>s might be
surprised to find that setting the <code>lower_bound</code> on one
particular <code>CFSheet</code> would change it on them all:
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
To avoid this confusion, the author of <code>CFSheet</code> can
declare that the output_fn Parameter always be 
instantiated:
<pre>
output_fn = Parameter(default=PiecewiseLinear(),instantiate=True)
</pre>
In this case, each instance of CFSheet will have its own
instance of PiecewiseLinear, independent of other
CFSheets' PiecewiseLinear() instances.

<br><br>

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
