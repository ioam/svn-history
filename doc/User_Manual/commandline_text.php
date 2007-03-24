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

<P>For very large arrays, numpy will suppress printing the array data
to avoid filling your terminal with numbers.  If you do want to see
the data, you can tell numpy to print even the largest arrays:

<pre>
Topographica&gt; numpy.set_printoptions(threshold=2**30)
</pre>

<P>To see what is available for inspection or manipulation for any
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

<H2>Plotting from the command line</H2>

<A NAME="pylab">If the GUI is running, you can also plot any vector or matrix in the
program:</A>

<pre>
$ ./topographica -g examples/cfsom_or.ty 
Topographica&gt; from topo.commands.pylabplots import *
Topographica&gt; V1 = topo.sim['V1']
Topographica&gt; matrixplot(V1.activity)
Topographica&gt; vectorplot(V1.activity[0])
Topographica&gt; vectorplot(V1.activity[1])
Topographica&gt; vectorplot(V1.activity[10])
Topographica&gt;
</pre>

Result:

<center>
<IMG src="images/matrixvectorplot.png" WIDTH="420" HEIGHT="473">
</center>

<P>The prompt can also be used for any mathematical calculation or
plotting one might wish to do, a la Matlab:

<!-- JABALERT! Should include screenshots of what the plotting looks like -->
<pre>
$ ./topographica -g
Topographica&gt; from Numeric import *
Topographica&gt; 2*pi*exp(1.6)
31.120820554943471
Topographica&gt; t = arange(0.0, 1.0+0.01, 0.01)
Topographica&gt; s = cos(2*2*pi*t)
Topographica&gt; from pylab import *
Topographica&gt; plot(s)
[&lt;matplotlib.lines.Line2D instance at 0xb6b1aeac&gt;]
Topographica&gt; show._needmain = False
Topographica&gt; show()
</pre>

Resulting plot:

<center>
<IMG src="images/sine_plot.png" WIDTH="658" HEIGHT="551">
</center>

<P>See the <A
href="http://numeric.scipy.org/numpydoc/numdoc.htm">Numeric</A>
documentation for more details on the mathematical expressions and
functions supported, and the <A
href="http://matplotlib.sourceforge.net/">MatPlotLib</A> documentation
for how to make new plots and change their axes, labels, titles, line
styles, etc.


<H2>Customizing the command prompt</H2>

<P>The contents of the command prompt itself are controlled by
the class variable <code>CommandPrompt.format</code>, which can be set
to any Python code that evaluates to a string.  As of 12/2006, the
default prompt is <code>Topographica_t0></code>, where 0 is the
current value of <code>topo.sim.time()</code> when the prompt is
printed.  This can be changed by doing something like:

<pre>
  from topo.misc.commandline import CommandPrompt
  CommandPrompt.format = '"Topographica_t%g> " % topo.sim.time()'
</pre>

Here any Python expression that returns a string when evaluated
in __main__ can be used, to include information other than the
current simulation time.  If your terminal supports ANSI colors, you
can use those in your prompt if you wish:

<pre>
  CommandPrompt.format = '"\x1b[32;40;1mTopographica\x1b[33;40;1m_t%g>\x1b[m " % topo.sim.time()'
</pre>

We've provided a shortcut for the above format to make it easier:

<pre>
  CommandPrompt.format = CommandPrompt.ansi_format
</pre>

<P>The result should be something like:

<P><IMG HEIGHT=66 WIDTH=283 SRC="../images/ansiprompt.png">

<!-- Could use TerminalController from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475116 for portable output... -->  
<P>Note that ANSI colors are not used by default, because terminals
that do not support them will display them as unrecognizable symbols.
				    
<H2>Site-specific customizations</H2>

<P>If you have any commands that you want to be executed whenever you
start Topographica, you can put them into the file
'$HOME/.topographicarc', if the HOME directory can be found and the
file exists.  For instance, to use the ANSI colors every time, just
create that file and add these lines to it:

<pre>
from topo.misc.commandline import CommandPrompt
CommandPrompt.format = CommandPrompt.ansi_format
</pre>
