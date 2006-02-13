<H1>Topographica Command Line</H1>

The GUI interface of Topographica provides the most commonly used
plots and displays, but it is often useful to be able to manipulate
the underlying program objects interactively.  The Topographica
command prompt allows you to do this easily.  This section will
eventually include detailed information on how to do this, but
hopefully the current information will help you get started.
<!-- JABALERT: Needs much expansion -->

<P>The command prompt gives you direct access to
<A href="http://python.org/doc/">Python</A>, and so any expression
valid for Python can be entered.  For instance, if your script defines
a Sheet named V1, you can display and change V1's parameters using
Python commands:

<pre>
$ ./topographica -i examples/cfsom_or.ty 
Topographica&gt; V1.density
50
Topographica&gt; V1.output_fn
&lt;Identity00003&gt;
Topographica&gt; from topo.outputfns.basic import *
Topographica&gt; V1.output_fn=PiecewiseLinear(lower_bound=0.1,upper_bound=0.8)
Topographica&gt; V1.output_fn
&lt;PiecewiseLinear05032&gt;
Topographica&gt; V1.activity
array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
              0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
              0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
...
</pre>

If the GUI is running, you can also plot any vector or matrix in the
program:

<pre>
$ ./topographica -g examples/cfsom_or.ty 
Topographica&gt; from topo.commands.pylabplots import *
Topographica&gt; matrixplot(V1.activity)
Topographica&gt; vectorplot(V1.activity[0])
Topographica&gt;
</pre>

To see what is available for inspection or manipulation for any
object, you can use <code>dir()</code>:

<pre>
$ ./topographica -i examples/cfsom_or.ty 
Topographica&gt; dir(V1)
['_Sheet__saved_activity', ..., 'apply_output_fn', 'bounds', 'density', ...]
Topographica&gt; 
</pre>

Note the directory will typically include many items that are not
useful to inspect, including those starting with an underscore
(<code>_</code>), but it gives a good idea what an object contains.
You can also get help for most objects:

<pre>
$ ./topographica -i examples/cfsom_or.ty 
Topographica&gt; help(V1)
Help on CFSOM in module topo.sheets.cfsom object:

class CFSOM(topo.base.connectionfield.CFSheet)
 |  Kohonen Self-Organizing Map algorithm extended to support ConnectionFields.
 |  
 |  This is an implementation of the Kohonen SOM algorithm extended to
 |  support ConnectionFields, i.e., different spatially restricted
 |  input regions for different units.  With fully connected input
 |  regions, it should be usable as a regular SOM as well.
...
 |  Methods defined here:
 |  
 |  __init__(self, **params)
 |  
 |  alpha(self)
 |      Return the learning rate at a specified simulator time, using exponential falloff.
...
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |  
 |  alpha_0 = 0.5
...
Topographica&gt;
</pre>

<P>The prompt can also be used for any mathematical calculation or
plotting one might wish to do, a la Matlab:

<pre>
$ ./topographica -g examples/cfsom_or.ty 
Topographica&gt; from Numeric import *
Topographica&gt; 2*pi*exp(1.6)
31.120820554943471
Topographica&gt; from topo.commands.pylabplots import *
Topographica&gt; t = arange(0.0, 1.0+0.01, 0.01)
Topographica&gt; s = cos(2*2*pi*t)
Topographica&gt; from pylab import *
Topographica&gt; plot(s)
[&lt;matplotlib.lines.Line2D instance at 0xb6b1aeac&gt;]
Topographica&gt; 
</pre>

See the <A href="http://numeric.scipy.org/numpydoc/numdoc.htm">Numeric</A>
and <A href="http://matplotlib.sourceforge.net/">MatPlotLib</A>
documentation for more details.
