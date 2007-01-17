<!-- -*-html-helper-*- mode -- (Hint for Emacs)-->

<H1>Parameters</H1>

<P>The behavior of most of the objects making up a Topographica
simulation can be controlled by variables called Parameters. A 
<?php classref('topo.base.parameterizedobject','Parameter')?> 
is a special type of Python attribute extended to have
features such as type and range checking, dynamically generated
values, documentation strings, default values, etc., each of which
is inherited from parent classes if not specified in a subclass.

<P>Objects that can contain Parameters are called
<?php classref('topo.base.parameterizedobject','ParameterizedObject')?>.
For instance, Sheets, Projections, and
PatternGenerators are all ParameterizedObjects.  The Parameters of a
Sheet include its <code>nominal_density</code> and <code>nominal_bounds</code>, and
the Parameters of a PatternGenerator include its <code>scale</code> and
<code>offset</code>.

<H2>Basic usage</H2>

<P>For the most part, Parameters can be used just like Python
attributes.  For instance, consider
<code>G=topo.patterns.basic.Gaussian()</code>.  This is a
two-dimensional Gaussian pattern generator, which has the Parameters
<code>scale</code>, <code>offset</code>, <code>x</code>,
<code>y</code>, <code>size</code>, <code>aspect_ratio</code>, and
<code>orientation</code>.  (To see this list, you can select Gaussian
in a Test Pattern window, or type 
<code>G.params().keys()</code> at a Topographica command
prompt.)  From a Topographica command prompt, you can type
<code>G.scale</code> to see its scale (e.g. 1.0), and e.g.
<code>G.scale=0.8</code> to set it.  Alternatively, you can set the
value via the <code>scale</code> widget in a Test Pattern window.

<P>The biggest difference from a standard Python attribute is visible
when one tries to set a Parameter to a value that is not allowed.  For
instance, you can try to enter <code>-1</code> in the
<code>aspect_ratio</code> box, or type <code>G.aspect_ratio=-0.5</code>
at the command prompt, but in either case you should get a ValueError.
Similarly, trying to set it to anything but a number
(e.g. <code>G.aspect_ratio="big"</code>) should produce an error.
These errors are detected because the <code>aspect_ratio</code> has
been declared as a <code>Number</code> Parameter with bounds
'(0,None)' (i.e. a minimum value of 0.0, and no maximum value). 

<P>To provide reasonable checking for parameters of different types, a large number of
<A HREF="../Reference_Manual/topo.base.parameterclasses.html">other
Parameter types</A> are provided besides
<?php classref('topo.base.parameterclasses','Number')?>,
such as
<?php classref('topo.base.parameterclasses','Integer')?>,
<?php classref('topo.base.parameterclasses','Filename')?>,
<?php classref('topo.base.parameterclasses','Enumeration')?>,
and
<?php classref('topo.base.parameterclasses','BooleanParameter')?>.
Each of these types can be declared to be constant, in which case the
value cannot be changed after the ParameterizedObject that owns the
Parameter has been created.  Some classes like
<?php classref('topo.base.parameterclasses','DynamicNumber')?> 
allow the parameter values to be generated from a sequence or random
distribution, such as for generating random input patterns.

<P>Some Parameter types or instances can also be declared to have
<code>softbounds</code>, which are used to suggest the sizes of GUI
sliders for the object, <code>precedence</code>, which determines the
sorting order for the Parameter in the GUI or in lists, and a
<code>doc</code> string, which is a brief explanation of what the
Parameter does.


<H2>Inheritance and class Parameters</H2>

<P>ParameterizedObjects are designed to inherit Parameter values from
their parent classes, so that ParameterizedObjects can use default
values for most Parameters.  This is designed to work just as Python
attribute inheritance normally works, but also inheriting any
documentation, bounds, etc. associated with the Parameter, even when
the default value is overridden.  For instance, the Gaussian
PatternGenerator parameters <code>x</code> and <code>y</code> are not
actually specified in the Gaussian class, but are inherited from the
base class, PatternGenerator.  If the value for x or y is set on the
Gaussian object <code>G</code> (as in <code>G.x=0.5</code>) or the
Gaussian class itself (by typing <code>Gaussian.x=0.5</code> or
<code>x=0.5</code> in the source code for the Gaussian class), the
values will overwrite the defaults, yet the same documentation and
bounds will still apply.

<P>Note that there is an important difference between setting the
Parameter on the class and on the object.  If we do
<code>G.x=0.5</code>, only object G will be affected. If we do
<code>Gaussian.x=0.5</code>, all future objects of type Gaussian will
have a default x value of 0.5.  Moreover, all <i>existing</i> objects
of type Gaussian will also get the new x value of 0.5, unless the user
has previously set the value of x on that object explicitly.  That is,
setting a Parameter at the class level typically affects all existing
and future objects from that Class, unless the object has overriden
the value for that Parameter.  To affect only one object, set the
value on that object by itself.

<P>In certain cases, it can be confusing to have objects inherit from
a single shared class Parameter.  For instance, constant parameters
are expected to keep the same value even if the class Parameter is
later changed.  Also, mutable Parameter objects, i.e. values that have
internal state (such as lists, arrays, or class instances) can have
very confusing behavior if they are shared between
ParameterizedObjects, because changes to one ParameterizedObject's
value can affect all the others.  In both of these cases (constants
and Parameters whose values may be mutable objects) the Parameter
is typically set to <code>instantiate=True</code>, which forces every
ParameterizedObject owning that Parameter to instantiate its own
private, independent copy when the ParameterizedObject is created.
This avoids much confusion, but does prevent existing objects from
being controlled as a group by changing the class Parameters.


<H2>Inheritance examples</H2>

The following examples should clarify how Parameter values are
inherited and instantiated.  In Python, attributes (including but not
limited to Parameters) declared at the class level are shared by all
instances of that class, unless an instance overwrites the attribute
with its own copy of the variable. For example:

<pre>
class Example(object):
    a = 10

    def __init__(self,b):
        self.b = b
</pre>

Here <code>a</code> is a class attribute, because it is declared at
the class level (outside of any method like <code>__init__</code>).
Creating two instances of Example demonstrates that the value
<code>a</code> is shared between the instances:

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

Because instances share the object held in the class attribute, any
changes to attributes of the object will show up in all the instances.
The same general rules apply to Parameters declared at the class
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

<pre>
Topographica> example1 = ExampleP(b=12)
Topographica> example1.a
10
Topographica> ExampleP.a = 40
Topographica> example1.a
40
</pre>

However, if a specific Parameter value is passed in when creating
the object, there will be a separate and independent copy containing
that value:

<pre>
Topographica> e1 = ExampleP(5,a=8)
Topographica> e1.a
8
Topographica> ExampleP.a = 12
Topographica> e1.a
8
</pre>

The author of a class can also force this behavior even when no value
is supplied by declaring <code>a</code> with <code>a =
Parameter(default=10,instantiate=True)</code>.  As mentioned above,
this is useful when the Parameter will hold a mutable object, when
sharing between instances would lead to confusion.

<P>For instance, consider a Parameter whose value is the response
function <code>PiecewiseLinear</code>, which itself has the Parameters
<code>upper_bound</code> and <code>lower_bound</code>. A user might
want to declare that all his <code>CFSheet</code>s will have response
functions that are <code>PiecewiseLinear</code>.  Without
<code>instantiate=True</code>, instances of the class
<code>CFSheet</code>, with its attribute <code>output_fn</code>, would
share a single <code>PiecewiseLinear</code> object. A user with a
number of <code>CFSheet</code>s might be surprised to find that
setting the <code>lower_bound</code> on one particular
<code>CFSheet</code> would change it on them all:

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
declare that the output_fn Parameter always be instantiated:

<pre>
output_fn = Parameter(default=PiecewiseLinear(),instantiate=True)
</pre>

In this case, each instance of CFSheet will have its own instance of
PiecewiseLinear, independent of other <code>CFSheet</code>s'
<code>PiecewiseLinear()</code> instances.  In fact, output_fn
parameters (like others taking mutable objects) are typically declared
not as Parameter but as OutputFunctionParameter, which sets
<code>instantiate=True</code> automatically.  Thus in most cases
users can use Parameters without worrying about the details of
inheritance and instantiation, but the details have been included here
because the behavior in unusual cases may be surprising.
