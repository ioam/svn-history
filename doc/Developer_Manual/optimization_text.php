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
marfa:~/dev_ext/topographica chris$ ./topographica speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(200)',n=20)" 
         1477056 function calls (1468656 primitive calls) in 60.782 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 111 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   60.782   60.782 <string>:1(?)
        1    0.122    0.122   60.782   60.782 simulation.py:626(run)
      400    0.005    0.000   40.816    0.102 simulation.py:452(__call__)
      200    0.011    0.000   35.588    0.178 projection.py:122(input_event)
      200    0.002    0.000   35.551    0.178 projection.py:182(present_input)
      200    0.010    0.000   35.549    0.178 cf.py:785(activate)
      200   10.216    0.051   35.531    0.178 cf.py:352(__call__)
   320000   14.853    0.000   25.312    0.000 functionfamilies.py:151(__call__)
      400    0.008    0.000   15.769    0.039 projection.py:151(process_current_time)
      200    0.014    0.000   15.578    0.078 cfsom.py:58(learn)
      200    0.011    0.000   15.516    0.078 cf.py:792(learn)
      200    6.844    0.034   15.498    0.077 som.py:66(__call__)
   320000    1.528    0.000   10.459    0.000 functions.py:21(sum)
   320000    8.932    0.000    8.932    0.000 fromnumeric.py:383(sum)
    52303    7.241    0.000    7.241    0.000 arrayutils.py:18(L2norm)
      400    0.049    0.000    5.451    0.014 patterngenerator.py:92(__call__)
      200    0.020    0.000    5.219    0.026 generatorsheet.py:106(input_event)
20600/19400    0.192    0.000    4.811    0.000 parameterclasses.py:179(__get__)
    58600    1.010    0.000    4.745    0.000 parameterizedobject.py:307(get_name)
      600    0.010    0.000    4.438    0.007 parameterclasses.py:386(__get__)
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
response function: the subsequent line in the output shows that about 70% of the time spent running
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

<P>In this case, it seems strange that <code>numpy</code>'s own <code>vdot</code> function is not being used;
why perform the dot product in stages ourselves when <code>numpy</code> provides a function to take care of
it? Straightaway, it is worthwhile to see if using an equivalent <code>numpy</code> function can speed up the 
performance. To find out, we can replace the implementation of <code>DotProduct</code> with the following:

<pre>
from numpy import vdot

class DotProduct(ResponseFn):
    def __call__(self,m1,m2):
        return vdot(m1,m2)
</pre>



<P>With this new DotProduct, we can profile the code again:

<pre>
$ ./topographica examples/speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(200)',n=20)"
         837056 function calls (828656 primitive calls) in 49.375 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 109 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   49.375   49.375 <string>:1(?)
        1    0.043    0.043   49.375   49.375 simulation.py:626(run)
      400    0.007    0.000   27.542    0.069 simulation.py:452(__call__)
      200    0.010    0.000   21.070    0.105 projection.py:122(input_event)
      200    0.002    0.000   21.035    0.105 projection.py:182(present_input)
      200    0.010    0.000   21.034    0.105 cf.py:785(activate)
      200    9.312    0.047   21.013    0.105 cf.py:352(__call__)
      400    0.004    0.000   17.303    0.043 projection.py:151(process_current_time)
      200    0.008    0.000   17.090    0.085 cfsom.py:58(learn)
      200    0.009    0.000   17.035    0.085 cf.py:792(learn)
      200    7.394    0.037   17.021    0.085 som.py:66(__call__)
   320000   11.699    0.000   11.699    0.000 functionfamilies.py:173(__call__)
    52303    8.110    0.000    8.110    0.000 arrayutils.py:18(L2norm)
      400    0.074    0.000    6.864    0.017 patterngenerator.py:92(__call__)
      200    0.024    0.000    6.462    0.032 generatorsheet.py:106(input_event)
20600/19400    0.174    0.000    5.937    0.000 parameterclasses.py:179(__get__)
    58600    1.071    0.000    5.798    0.000 parameterizedobject.py:307(get_name)
      600    0.012    0.000    5.567    0.009 parameterclasses.py:386(__get__)
    79328    2.169    0.000    4.709    0.000 parameterizedobject.py:513(get_param_descriptor)
      400    0.017    0.000    4.419    0.011 simulation.py:455(__repr__)
</pre>

<P>
More than halved functionfamilies, and cf.py call only 60% what it was. Overall, we
have cut time to 80% of original with just a few minutes' work.


<!--
ravel and dot instead of vdot - it's slightly faster:
<pre>
$ ./topographica speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(200)',n=20)"
         837056 function calls (828656 primitive calls) in 45.044 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 109 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   45.044   45.044 <string>:1(?)
        1    0.048    0.048   45.044   45.044 simulation.py:626(run)
      400    0.008    0.000   25.774    0.064 simulation.py:452(__call__)
      200    0.010    0.000   20.298    0.101 projection.py:122(input_event)
      200    0.001    0.000   20.269    0.101 projection.py:182(present_input)
      200    0.011    0.000   20.267    0.101 cf.py:785(activate)
      200    8.695    0.043   20.248    0.101 cf.py:352(__call__)
      400    0.007    0.000   15.153    0.038 projection.py:151(process_current_time)
      200    0.012    0.000   14.983    0.075 cfsom.py:58(learn)
      200    0.009    0.000   14.927    0.075 cf.py:792(learn)
      200    6.518    0.033   14.909    0.075 som.py:66(__call__)
   320000   11.551    0.000   11.551    0.000 functionfamilies.py:172(__call__)
    52303    6.987    0.000    6.987    0.000 arrayutils.py:18(L2norm)
      400    0.065    0.000    5.753    0.014 patterngenerator.py:92(__call__)
      200    0.022    0.000    5.463    0.027 generatorsheet.py:106(input_event)
20600/19400    0.192    0.000    5.168    0.000 parameterclasses.py:179(__get__)
    58600    1.131    0.000    5.055    0.000 parameterizedobject.py:307(get_name)
      600    0.015    0.000    4.811    0.008 parameterclasses.py:386(__get__)
      400    0.009    0.000    3.999    0.010 simulation.py:455(__repr__)
 7600/400    0.657    0.000    3.967    0.010 parameterizedobject.py:642(__repr__)
</pre>
-->

<P>
 if we want, still further
room for optimization, noticing that lots of time still spent in call. Replace our <code>DotProduct</code>
 entirely with numpy's vdot, <code>CFPRF_Plugin.single_cf_fn=numpy.vdot</code> 

Then we get:

<pre>
$ ./topographica speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(200)',n=20)"
         514656 function calls (506456 primitive calls) in 40.731 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 108 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   40.731   40.731 <string>:1(?)
        1    0.041    0.041   40.730   40.730 simulation.py:626(run)
      400    0.005    0.000   21.262    0.053 simulation.py:452(__call__)
      200    0.010    0.000   16.158    0.081 projection.py:122(input_event)
      200    0.002    0.000   16.120    0.081 projection.py:182(present_input)
      200    0.012    0.000   16.119    0.081 cf.py:785(activate)
      200   16.095    0.080   16.097    0.080 cf.py:352(__call__)
      400    0.063    0.000   15.556    0.039 projection.py:151(process_current_time)
      200    0.008    0.000   15.282    0.076 cfsom.py:58(learn)
      200    0.008    0.000   15.215    0.076 cf.py:792(learn)
      200    6.886    0.034   15.200    0.076 som.py:66(__call__)
    52303    7.020    0.000    7.020    0.000 arrayutils.py:18(L2norm)
      400    0.073    0.000    5.323    0.013 patterngenerator.py:92(__call__)
      200    0.025    0.000    5.093    0.025 generatorsheet.py:106(input_event)
20600/19400    0.158    0.000    4.697    0.000 parameterclasses.py:179(__get__)
    58200    1.060    0.000    4.646    0.000 parameterizedobject.py:307(get_name)
      600    0.012    0.000    4.409    0.007 parameterclasses.py:386(__get__)
      400    0.010    0.000    3.794    0.009 simulation.py:455(__repr__)
 7400/400    0.659    0.000    3.752    0.009 parameterizedobject.py:642(__repr__)
    79328    1.776    0.000    3.566    0.000 parameterizedobject.py:513(get_param_descriptor)
</pre>


Now we have reduced the cf call to 45% of its original run time, and the total run time to 2/3 its original.


<P>[probably new subsection]Being possible to re-write functions in c, might wonder if it would help in this case, or does numpy already do a good job? We could replace the numpy dot with a dot written in c, but probably the overhead in calling is too much anyway so wouldn't be big enough optimization, but what about replacing whole function with a c version?
Replace <code>CFPRF_Plugin(single_cf_fn=dot)</code> with <code>CFPRF_DotProduct_opt</code>, an optimized version written in C.



<pre>
$ ./topographica speed_test.ty -c "from topo.misc.utils import profile; profile('topo.sim.run(200)',n=20)"
         517531 function calls (509129 primitive calls) in 28.509 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 155 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   28.509   28.509 <string>:1(?)
        1    0.057    0.057   28.509   28.509 simulation.py:626(run)
      400    0.004    0.000   16.689    0.042 projection.py:151(process_current_time)
      200    0.008    0.000   16.477    0.082 cfsom.py:58(learn)
      200    0.007    0.000   16.409    0.082 cf.py:792(learn)
      200    7.264    0.036   16.397    0.082 som.py:66(__call__)
    52303    7.726    0.000    7.726    0.000 arrayutils.py:18(L2norm)
      400    0.007    0.000    7.103    0.018 simulation.py:452(__call__)
      400    0.053    0.000    5.803    0.015 patterngenerator.py:92(__call__)
      200    0.020    0.000    5.607    0.028 generatorsheet.py:106(input_event)
20600/19400    0.182    0.000    5.242    0.000 parameterclasses.py:179(__get__)
    58400    1.154    0.000    5.168    0.000 parameterizedobject.py:307(get_name)
      600    0.011    0.000    4.848    0.008 parameterclasses.py:386(__get__)
      400    0.009    0.000    4.537    0.011 simulation.py:455(__repr__)
 7600/400    0.671    0.000    4.504    0.011 parameterizedobject.py:642(__repr__)
    79328    1.944    0.000    3.988    0.000 parameterizedobject.py:513(get_param_descriptor)
     7600    0.941    0.000    3.813    0.001 parameterizedobject.py:742(get_param_values)
    88545    2.384    0.000    2.384    0.000 parameterizedobject.py:29(classlist)
     8400    0.048    0.000    1.847    0.000 parameterizedobject.py:829(params)
     8400    1.491    0.000    1.799    0.000 parameterizedobject.py:533(classparams)
</pre>

<P>The simulation now takes less than half the time the original version took, and 70% the time numpy version takes. The c code adds 
a lot of complexity to the code: for maintenance, for deployment on different platforms, and
for user understanding - so it has to justify this with bigtime speedups.

<P>While making this kind of investigation, you should also check that the simulations are 
producing the same results. particularly when working with optimized c functions, it is
possible for one to appear much faster than another when the computations being performed are
not equivalent. 
(You could do this by adding a print statement after profiling to show the sum of v1 activity, or
something similar.) 

run times should be long enough for reliable results, or repeat and average.
