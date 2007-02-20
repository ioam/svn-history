<H1>Optimization</H1>

<P>According to Knuth, "Premature optimization is the root of all
evil".  Although the performance of Topographica is critically
important, the way to achieve high performance is by spending <i>all</i> of
our optimization efforts on the very small portion of the code that
accounts for nearly all of the run time, i.e., the bottlenecks.  The
overall architecture of Topographica is designed explicitly to
localize those bottlenecks into specific functions and objects that
can then be heavily optimized without affecting any of the rest of the
code.  Only in such small, local regions, behind well-defined modules
with clear semantics, is it possible to optimize effectively in a way
that can be maintained in the long run.  If it is precisely clear what
the module is supposed to do, then the implementation can be polished
to achieve that, while reasoning only about the behavior of that one
specific module.

<P>Conversely, finding that good performance requires adding special
hacks in the largest-scale, general-purpose parts of the overall
Topographica architecture means that the architecture is flawed and
needs to be re-thought.  For instance, please do not add any special
checks scattered through the code testing for specific
PatternGenerator or Sheet objects, substituting a quicker version of
some operation but falling back to the general case for others.  Such
code is impossible to understand and maintain, because changes to the
specific object implementations will not have any effect.  Instead, we
can optimize the individual PatternGenerator or Sheet object heavily.
If some special hack needs to be done at a high level, e.g. at the
base Sheet class level, we can add a method there that then gets
overridden in the base class with the special purpose code.  That way
all optimization will be local (and thus maintainable).  If it's not
clear how to optimize something cleanly, first do it uncleanly to see
if it will have any effect, but don't check it in to CVS.  If it looks
like the optimization is worthwhile, brainstorm with other team
members to figure out a way to do it cleanly and check in the clean
version instead.


<H2>Providing optimized versions of Topographica objects</H2>

<!-- CB: update to numpy! & cleanup numpy/Numeric in following section!-->

<P>Where possible, Python components can be implemented with high
performance using
<A href="http://numeric.scipy.org/numpydoc/numdoc.htm">Numeric</A>
matrix operations.  This should be the first approach when optimizing
any component, and indeed when writing the component for the first
time (because the Numeric primitives are much easier to use and
maintain than e.g. explicitly writing <code>for</code> loops).
However, there are certain cases where the performance of Numeric is
not sufficient, or where Numeric is unsuitable (for example, many
Numeric operations do not act in-place on arrays).  Other components
may be able to be implemented much more quickly if certain assumptions
are made about the nature of their arguments, or the types of
computations that can be performed.

<P>In the cases mentioned above, it is worthwhile to have a reference
version of the object that is simple to understand and does not make
any special assumptions. Then, an optimized version can be offered as
an alternative. The convention we use is to add the suffix
<code>_optN</code> to the optimized version, where <code>N</code> is a
number that allows to distinguish between different optimized
versions. This is helpful both for understanding and for ensuring
correctness.

<P>For example, consider <code>CFPRF_DotProduct</code>, from
<code>topo.responsefns.projfns</code>. If users wish to use a version
optimized by having been written in C, they can instead import
<code>CFPRF_DotProduct_opt</code> from
<code>topo.responsefns.optimized</code>. We use
<code>CFPRF_DotProduct_opt</code> as standard in our code because it's
much faster than --- but otherwise identical to --- the unoptimized
version. However, because <code>CFPRF_DotProduct_opt</code> relies on a
more complex setup (having the weave module installed, as well as a
correctly configured C++ compiler), we cannot assume all users will
have access to it. It is also extremely difficult to read and
understand. Therefore, we provide an automatic fall-back to the
unoptimized version (see <code>topo/responsefns/optimized.py</code>
for an example of how to do this).

<P>The non-optimized version also acts as a simple specification of
exactly what the optimized version is supposed to do, apart from any
optimizations.  The optimized versions are often nearly unreadable, so
having the simple version available is very helpful for understanding
and debugging.  The expectation is that the simple (slow) versions
will rarely change, but the optimized ones will get faster and faster
over time, while preserving the same user-visible behavior.


<H2>Finding bottlenecks</H2>

<P>As discussed above, we wish to spend our time optimizing parts of the
code which account for most of the run time. To do this, we must find
those bottlenecks; <code>topo.misc.utils</code> contains the <code>profile()</code>
function, which provides a simple way to do this.

<P>For instance, if we have a simple simulation consisting of a <code>CFSOM</code>
sheet connected to a <code>GeneratorSheet</code> with a <code>CFProjection</code>,
we might wish to find out if there is an obvious bottleneck that could be 
eliminated, suspecting that such a bottleneck could be in either the learning function or the response function. 
For concreteness, let us say that in this instance the <code>CFProjection</code> has a learning 
function of <code>CFPLF_HebbianSOM()</code>, and a response function of <code>CFPRF_Plugin()</code>, and
that the script <code>speed_test.ty</code> simply creates the network but does not run the simulation.

<P>We can run topographica as follows, using the <code>profile()</code> function to profile the run,
getting the following output:

<pre>
$ ./topographica speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(50)',n=20)" 
         371719 function calls (369619 primitive calls) in 13.129 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 111 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   13.129   13.129 <string>:1(?)
        1    0.011    0.011   13.129   13.129 simulation.py:626(run)
      100    0.001    0.000    8.696    0.087 simulation.py:452(__call__)
       50    0.003    0.000    7.605    0.152 projection.py:122(input_event)
       50    0.000    0.000    7.598    0.152 projection.py:182(present_input)
       50    0.002    0.000    7.598    0.152 cf.py:785(activate)
       50    2.066    0.041    7.594    0.152 cf.py:352(__call__)
    80000    3.043    0.000    5.526    0.000 functionfamilies.py:151(__call__)
      100    0.001    0.000    3.433    0.034 projection.py:151(process_current_time)
       50    0.002    0.000    3.390    0.068 cfsom.py:58(learn)
       50    0.002    0.000    3.376    0.068 cf.py:792(learn)
       50    1.518    0.030    3.371    0.067 som.py:66(__call__)
    80000    0.660    0.000    2.483    0.000 functions.py:21(sum)
    80000    1.823    0.000    1.823    0.000 fromnumeric.py:383(sum)
    13652    1.559    0.000    1.559    0.000 arrayutils.py:18(L2norm)
      100    0.012    0.000    1.143    0.011 patterngenerator.py:92(__call__)
       50    0.005    0.000    1.088    0.022 generatorsheet.py:106(input_event)
    14650    0.231    0.000    1.034    0.000 parameterizedobject.py:307(get_name)
5150/4850    0.036    0.000    1.030    0.000 parameterclasses.py:179(__get__)
      100    0.003    0.000    0.974    0.010 simulation.py:455(__repr__)

</pre>

The <code>n=20</code> argument restricts the list to the top 20 functions, ordered by cumulative time.
For more information about the types of ordering available, <code>help(profile)</code> provides a
link to Python's documentation.

<P>From the output, we can see that all the time is spent in <code>Simulation</code>'s <code>run()</code>
method. We must proceed down the list until we find a less granular function: one that does not call
many others, but performs some atomic task. The first such function is <code>cf.py:352(__call__)</code>,
<code>CFPRF_Plugin</code>'s <code>call()</code> method:

<pre>
from topo.base.functionfamilies import DotProduct

class CFPRF_Plugin(CFPResponseFn):
    """
    Generic large-scale response function based on a simple single-CF function.

    Applies the single_cf_fn to each CF in turn.  For the default
    single_cf_fn of DotProduct(), does a basic dot product of each CF with the
    corresponding slice of the input array.  This function is likely
    to be slow to run, but it is easy to extend with any arbitrary
    single-CF response function.

    The single_cf_fn must be a function f(X,W) that takes two
    identically shaped matrices X (the input) and W (the
    ConnectionField weights) and computes a scalar activation value
    based on those weights.
    """
    single_cf_fn = ResponseFnParameter(default=DotProduct(),
        doc="Accepts a ResponseFn that will be applied to each CF individually.")
    
    def __call__(self, cfs, input_activity, activity, strength):
        rows,cols = activity.shape

        single_cf_fn = self.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_array
                X = input_activity[r1:r2,c1:c2]
                #if (X.shape != cf.weights.shape):
                #  self.warning("Shapes %s and %s are not compatible" % (X.shape,cf.weights.shape))
                activity[r,c] = single_cf_fn(X,cf.weights)
        activity *= strength
</pre>

About 60% of the total run time is spent in this method, so if we were able to optimize it, then this
would lead to good optimization of the simulation in total. Looking further down the list, we can see
functions associated with learning, and that these account for about half as much of the run time. So,
optimizing the response function will be approximately twice as beneficial as optimizing the learning
function; only if it were much easier to optimize the learning function would it be worthwhile to begin
with that.

<P>
How do we begin to optimize the response function?
In fact, we have more fine-grained information about the occupation of the CPU while executing the
response function: the subsequent line in the output shows that almost 75% of the time spent running
the response function is spent in <code>functionfamilies.py:151(__call__)</code>, <code>CFPRF_Plugin</code>'s
default <code>single_cf_fn</code>:

<pre>
import numpy.oldnumeric as Numeric

class DotProduct(ResponseFn):
    """
    Return the sum of the element-by-element product of two 2D
    arrays.  
    """
    def __call__(self,m1,m2):
        # Should work even for non-contiguous arrays, e.g. with matrix
        # slices or submatrices.
        a = m1*m2
        return Numeric.sum(a.ravel())
</pre>

<P>In this case, it seems strange that <code>numpy</code>'s own <code>dot</code> function is not being used;
why perform the dot product in stages ourselves when <code>numpy</code> provides a function to take care of
it? Straightaway, it is worthwhile to see if using an equivalent <code>numpy</code> function can speed up the 
performance. To find out, we can replace the implementation of <code>DotProduct</code> with the following:

<pre>
from numpy import dot

class DotProduct(ResponseFn):
    def __call__(self,m1,m2):
        return dot(m1.ravel(),m2.ravel())
</pre>

(Note that this is not necessarily the optimum arrangement, but we are considering only the replacement
of our own multiplication-then-sum with <code>numpy</code>'s <code>dot</code> function. In fact, we might
wish to eliminate our own DotProduct class entirely, and it might not be necessary to call <code>ravel()</code>
on both arrays.)

<P>With this new DotProduct, we can profile the code again:

<pre>

marfa:~/topographica chris$ ./topographica examples/speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(50)',n=20)" 
         211719 function calls (209619 primitive calls) in 10.706 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 109 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   10.706   10.706 <string>:1(?)
        1    0.010    0.010   10.706   10.706 simulation.py:626(run)
      100    0.001    0.000    6.115    0.061 simulation.py:452(__call__)
       50    0.002    0.000    4.635    0.093 projection.py:122(input_event)
       50    0.000    0.000    4.628    0.093 projection.py:182(present_input)
       50    0.002    0.000    4.628    0.093 cf.py:785(activate)
       50    2.069    0.041    4.624    0.092 cf.py:352(__call__)
      100    0.001    0.000    3.671    0.037 projection.py:151(process_current_time)
       50    0.002    0.000    3.627    0.073 cfsom.py:58(learn)
       50    0.002    0.000    3.613    0.072 cf.py:792(learn)
       50    1.627    0.033    3.603    0.072 som.py:66(__call__)
    80000    2.554    0.000    2.554    0.000 functionfamilies.py:151(__call__)
    13652    1.682    0.000    1.682    0.000 arrayutils.py:18(L2norm)
      100    0.015    0.000    1.528    0.015 patterngenerator.py:92(__call__)
       50    0.005    0.000    1.477    0.030 generatorsheet.py:106(input_event)
5150/4850    0.041    0.000    1.402    0.000 parameterclasses.py:179(__get__)
    14650    0.234    0.000    1.398    0.000 parameterizedobject.py:307(get_name)
      150    0.003    0.000    1.310    0.009 parameterclasses.py:386(__get__)
    20378    0.403    0.000    1.160    0.000 parameterizedobject.py:513(get_param_descriptor)
      100    0.002    0.000    0.889    0.009 simulation.py:455(__repr__)


</pre>

<P>
More than halved functionfamilies, and cf.py call only 60% what it was. if we want, still further
room for optimization, noticing that lots of time still spent in call. Replace our dot
product entirely with numpy's dot, calling ravel first

<pre>
from numpy import dot

class CFPRF_Plugin(CFPResponseFn):
    """
    Generic large-scale response function based on a simple single-CF function.

    Applies the single_cf_fn to each CF in turn.  For the default
    single_cf_fn of DotProduct(), does a basic dot product of each CF with the
    corresponding slice of the input array.  This function is likely
    to be slow to run, but it is easy to extend with any arbitrary
    single-CF response function.

    The single_cf_fn must be a function f(X,W) that takes two
    identically shaped matrices X (the input) and W (the
    ConnectionField weights) and computes a scalar activation value
    based on those weights.
    """
    single_cf_fn = ResponseFnParameter(default=dot,
        doc="Accepts a ResponseFn that will be applied to each CF individually.")
    
    def __call__(self, cfs, input_activity, activity, strength):
        rows,cols = activity.shape

        single_cf_fn = self.single_cf_fn
        for r in xrange(rows):
            for c in xrange(cols):
                cf = cfs[r][c]
                r1,r2,c1,c2 = cf.slice_array
                X = input_activity[r1:r2,c1:c2]
                #if (X.shape != cf.weights.shape):
                #  self.warning("Shapes %s and %s are not compatible" % (X.shape,cf.weights.shape))
                activity[r,c] = single_cf_fn(X.ravel(),cf.weights.ravel())
        activity *= strength
</pre> 

Then we get:

<pre>
$ ./topographica examples/speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(50)',n=20)" 
         131119 function calls (129069 primitive calls) in 9.081 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 108 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    9.081    9.081 <string>:1(?)
        1    0.013    0.013    9.081    9.081 simulation.py:626(run)
      100    0.001    0.000    4.604    0.046 simulation.py:452(__call__)
      100    0.002    0.000    3.582    0.036 projection.py:151(process_current_time)
       50    0.002    0.000    3.536    0.071 cfsom.py:58(learn)
       50    0.002    0.000    3.523    0.070 cf.py:792(learn)
       50    1.573    0.031    3.520    0.070 som.py:66(__call__)
       50    0.003    0.000    3.498    0.070 projection.py:122(input_event)
       50    0.000    0.000    3.491    0.070 projection.py:182(present_input)
       50    0.003    0.000    3.491    0.070 cf.py:785(activate)
       50    3.486    0.070    3.486    0.070 cf.py:352(__call__)
    13652    1.651    0.000    1.651    0.000 arrayutils.py:18(L2norm)
      100    0.014    0.000    1.154    0.012 patterngenerator.py:92(__call__)
       50    0.008    0.000    1.103    0.022 generatorsheet.py:106(input_event)
5150/4850    0.038    0.000    1.047    0.000 parameterclasses.py:179(__get__)
    14550    0.231    0.000    1.042    0.000 parameterizedobject.py:307(get_name)
      150    0.003    0.000    0.948    0.006 parameterclasses.py:386(__get__)
      100    0.002    0.000    0.864    0.009 simulation.py:455(__repr__)
 1850/100    0.144    0.000    0.857    0.009 parameterizedobject.py:642(__repr__)
    20378    0.403    0.000    0.807    0.000 parameterizedobject.py:513(get_param_descriptor)
 
</pre>

and we have cut the total run time to 70% of its starting value with just a few minutes' work. learning function is now
taking the larger fraction of runtime
