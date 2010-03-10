<H1>Performance optimization</H1>

<P>According to C.A.R. Hoare, "Premature optimization is the root of all
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
overridden in the subclass with the special purpose code.  That way
all optimization will be local (and thus maintainable).  If it's not
clear how to optimize something cleanly, first do it uncleanly to see
if it will have any effect, but don't check it in to SVN.  If it looks
like the optimization is worthwhile, brainstorm with other team
members to figure out a way to do it cleanly and check in the clean
version instead.

<P>This document considers runtime performance primarily; optimizing
total memory is considered separately under
<A href="memuse.html">Memory usage</a>.  On the other hand, the
<i>patterns</i> of access to memory are crucially important for
performance in large simulations.  For a good overview of how to
optimize memory usage patterns,
<A href="http://lwn.net/Articles/250967/">Ulrich Drepper's
article</A>.  If you are ambitious, even the most optimized components
in Topographica could be further improved using these techniques,
possibly substantially.


<H2>Optimizing Python code</H2>

<P>Although dramatic speedups usually require big changes as described
below, sometimes all you need is minor tweaks to Python code to get it
to have reasonable performance.  Usually this involves avoiding
unnecessary attribute lookup, as described
<A href="http://www.informit.com/articles/article.asp?p=453682&rl=1">here</A>.

<P>What is usually more important to ensure is that anything that can
use the array-based primitives provided by
<A href="http://numpy.scipy.org/">numpy</A> does so, because these
generally have underlying C implementations that are quite fast.
Using numpy operations should be the first approach when optimizing
any component, and indeed when writing the component for the first
time (because the numpy primitives are much easier to use and
maintain than e.g. explicitly writing <code>for</code> loops).


<H2>Providing optimized versions of Topographica objects</H2>

<!-- CB: update to numpy! & cleanup numpy/Numeric in following section!-->

However, there are certain cases where the performance of numpy is
not sufficient, or where numpy is unsuitable (for example, some
numpy operations do not act in-place on arrays).  Other components
may be able to be implemented much more quickly if certain assumptions
are made about the nature of their arguments, or the types of
computations that can be performed.

<P>In these cases, it is worthwhile to have a reference
version of the object that is simple to understand and does not make
any special assumptions. Then, an optimized version can be offered as
an alternative. The convention we use is to add the suffix
<code>_optN</code> to the optimized version, where <code>N</code> is a
number that allows to distinguish between different optimized
versions. This is helpful both for understanding and for ensuring
correctness.

<P>For example, consider <code>CFPRF_DotProduct</code>, from
<code>topo.responsefn.projfn</code>. If users wish to use a version
optimized by having been written in C, they can instead import
<code>CFPRF_DotProduct_opt</code> from
<code>topo.responsefn.optimized</code>. We use
<code>CFPRF_DotProduct_opt</code> as standard in our code because it's
much faster than --- but otherwise identical to --- the unoptimized
version. However, because <code>CFPRF_DotProduct_opt</code> relies on a
more complex setup (having the weave module installed, as well as a
correctly configured C++ compiler), we cannot assume all users will
have access to it. It is also extremely difficult to read and
understand. Therefore, we provide an automatic fall-back to the
unoptimized version (see <code>topo/responsefn/optimized.py</code>
for an example of how to do this).

<P>The non-optimized version also acts as a simple specification of
exactly what the optimized version is supposed to do, apart from any
optimizations.  The optimized versions are often nearly unreadable, so
having the simple version available is very helpful for understanding
and debugging.  The expectation is that the simple (slow) versions
will rarely change, but the optimized ones will get faster and faster
over time, while preserving the same user-visible behavior.


<H2>Finding bottlenecks</H2>

<P>As discussed above, we wish to spend our time optimizing parts of
the code that account for most of the run
time. <code>topo.misc.util</code> contains the
<code>profile()</code> function, providing a simple way to do
this.

<P>For instance, if we have a simple simulation consisting of a
SOM-based sheet connected to a <code>GeneratorSheet</code>
with a <code>CFProjection</code>, we might wish to find out if there
is an obvious bottleneck that could be eliminated, speeding up the
network's performance. For concreteness, let us say that in this
instance the <code>CFProjection</code> has a learning function of
<code>CFPLF_HebbianSOM()</code>, and a response function of
<code>CFPRF_Plugin()</code>, and that the script
<code>lissom_oo_or.ty</code> simply creates the network but does not run
the simulation.

In order to see how basic optimisation could be applied lets first roll this
script back to the unoptimised version. You can do this by editing 
<code>examples/lissom_oo_or.ty</code>. Replace code at line 76 with the following:
<code>projection.CFProjection.response_fn=responsefn.optimized.CFPRF_DotProduct()</code> 

<P>We can run topographica as follows, using the
<code>profile()</code> function to give us information about the 
performance:

<pre>
$ ./topographica examples/lissom_oo_or.ty -c "from topo.misc.util import profile; \
profile('topo.sim.run(99)',n=20)"  

         28115548 function calls (28112974 primitive calls) in 74.199 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 257 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   74.201   74.201 <string>:1(<module>)
        1    0.042    0.042   74.201   74.201 simulation.py:1120(run)
     2178    0.007    0.000   72.330    0.033 simulation.py:436(__call__)
     2178    0.022    0.000   72.305    0.033 projection.py:391(input_event)
     2178    0.003    0.000   72.255    0.033 projection.py:519(present_input)
     2178    0.050    0.000   72.251    0.033 cf.py:725(activate)
     1980    0.012    0.000   72.199    0.036 lissom.py:95(input_event)
     1980   13.755    0.007   72.048    0.036 cf.py:339(__call__)
  4561920    8.581    0.000   35.867    0.000 functionfamily.py:125(__call__)
  9124434   14.049    0.000   14.049    0.000 {method 'ravel' of 'numpy.ndarray' objects}
  4561920   13.642    0.000   13.642    0.000 sheetcoords.py:387(submatrix)
  4561920   13.237    0.000   13.237    0.000 {numpy.core.multiarray.dot}
  4563900    8.758    0.000    8.780    0.000 cf.py:809(__call__)
     1188    0.012    0.000    1.150    0.001 lissom.py:113(process_current_time)
     1094    0.006    0.000    0.871    0.001 inlinec.py:72(inline_weave)
     1094    0.018    0.000    0.859    0.001 inline_tools.py:130(inline)
     1094    0.647    0.001    0.826    0.001 {apply}
       99    0.001    0.000    0.685    0.007 basic.py:290(learn)
      100    0.003    0.000    0.560    0.006 basic.py:266(_normalize_weights)
       99    0.000    0.000    0.466    0.005 simulation.py:510(__call__)
</pre>

The <code>n=20</code> argument restricts the list to the top 20
functions, ordered by cumulative time.  For more information about the
types of ordering available, <code>help(profile)</code> provides a
link to Python's documentation.

<P>From <code>profile()</code>'s output above, we see (as expected) that 
all the time is spent in
<code>Simulation</code>'s <code>run()</code> method. We must proceed
down the list until we find a less granular function --- one that does
not call many others, but instead performs some atomic task. The first such
function is <code>cf.py:352(__call__)</code> (<code>cf.py</code>, line 352),
<code>CFPRF_Plugin</code>'s <code>__call__()</code> method:

<pre>
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
    single_cf_fn = param.ClassSelector(ResponseFn,default=DotProduct(),
        doc="Accepts a ResponseFn that will be applied to each CF individually.")
    
    def __call__(self, iterator, input_activity, activity, strength):
        single_cf_fn = self.single_cf_fn
        for cf,r,c in iterator():
            X = cf.input_sheet_slice.submatrix(input_activity)
            activity[r,c] = single_cf_fn(X,cf.weights)
        activity *= strength
</pre>

About 97% of the total run time is spent in this method, so if we were
able to optimize it, this would lead to good optimization of the
simulation in total. Looking further down the list, we can see
functions associated with learning, and that these account for about
half as much of the run time. So, optimizing the response function
will be approximately twice as beneficial as optimizing the learning
function in this case; only if it were much easier to optimize the learning
function would it be worthwhile to begin with that.

<P>How do we begin to optimize the response function?  We have more
fine-grained information about the occupation of the CPU while
executing the response function; the subsequent line in the output
shows that about 50% of the time spent running the response function
is spent in <code>functionfamily.py:151(__call__)</code>,
<code>CFPRF_Plugin</code>'s default <code>single_cf_fn</code>:

<pre>
class DotProduct(ResponseFn):
    """
    Return the sum of the element-by-element product of two 2D
    arrays.  
    """
    def __call__(self,m1,m2):
        return numpy.dot(m1.ravel(),m2.ravel())
</pre>

Here the Numpy's <code>dot</code> function is called in order to calculate 
the dot-product for two matrices. Numpy offers a very good level of optimisation 
as far as Python goes. However, we can get even better results by using C++. 

<H3>Considering optimizations with C++ (weave)</H3>
Topographica makes it reasonably easy to re-write functions in C++ and
offer them as optimized alternatives. We might wonder if it would help
in this case, or does <code>numpy</code> already do a good job? We
could replace <code>DotProduct</code> with a version written in 
C++, or we could replace the entire <code>CFPRF_Plugin</code> class
with one written in C++. As at 02/2007, we find that simply re-writing
the <code>single_cf_fn</code> in C++ provides little performance improvement,
but that re-writing the entire CFP function provides a big performance
improvement.
<!-- CB: presumably because of the increased speed of looping through
all the CFs and having the slice_arrays available, all in C++, etc-
should add this explanation somewhere -->
<!-- CB: certainly for the response function, anyway.-->

<P>Let us edit the <code>examples/lissom_oo_or.ty</code> file once again and replace
the code at line 76 with 
<code>projection.CFProjection.response_fn=responsefn.optimized.CFPRF_DotProduct_opt()</code> </P>

<P>Now, instead of computing <code>DotProduct()</code> in <code>functionfamily.py</code> topographica
will call a different method located in <code>responsefn.optimised.py</code>:</P>

<pre>
class CFPRF_DotProduct_opt(CFPResponseFn):
    """
    Dot-product response function.

    Written in C for a manyfold speedup; see CFPRF_DotProduct for an
    easier-to-read version in Python.  The unoptimized Python version
    is equivalent to this one, but it also works for 1D arrays.
    """

    single_cf_fn = param.ClassSelector(ResponseFn,DotProduct(),readonly=True)    

    def __call__(self, iterator, input_activity, activity, strength, **params):
       
        temp_act = activity
        rows,cols = activity.shape
        irows,icols = input_activity.shape
        X = input_activity.ravel()
        cfs = iterator.proj._cfs
        mask = iterator.proj.dest.mask.data

        cf_type = iterator.proj.cf_type
    
        code = c_header + """
            DECLARE_SLOT_OFFSET(weights,cf_type);
            DECLARE_SLOT_OFFSET(input_sheet_slice,cf_type);

            npfloat *tact = temp_act;

            for (int r=0; r<rows; ++r) {
                PyObject *cfsr = PyList_GetItem(cfs,r);
                for (int l=0; l<cols; ++l) {
                    if((*mask++) == 0.0)
                        *tact = 0;
                    else {
                        PyObject *cf = PyList_GetItem(cfsr,l);

                        CONTIGUOUS_ARRAY_FROM_SLOT_OFFSET(float,weights,cf)
                        LOOKUP_FROM_SLOT_OFFSET(int,input_sheet_slice,cf);
                        
                        UNPACK_FOUR_TUPLE(int,rr1,rr2,cc1,cc2,input_sheet_slice);
                        
                        double tot = 0.0;
                        npfloat *xj = X+icols*rr1+cc1;
    
                        // computes the dot product
                        for (int i=rr1; i<rr2; ++i) {
                            npfloat *xi = xj;
                            float *wi = weights;                       
                            for (int j=cc1; j<cc2; ++j) {
                                tot += *wi * *xi;
                                ++wi;
                                ++xi;
                            }
                            xj += icols;
                            weights += cc2-cc1;
                        }  
                        *tact = tot*strength;

                        DECREF_CONTIGUOUS_ARRAY(weights);
                    }
                    ++tact;    
                }
            }
        """
        inline(code, ['mask','X', 'strength', 'icols', 'temp_act','cfs','cols','rows','cf_type'], local_dict=locals(), headers=['<structmember.h>'])
	
</pre>

<P>Replacing the CFP function with one written entirely in C++, we
get the following profile:
<pre>
./topographica examples/lissom_oo_or.ty -c "from topo.misc.util import profile; profile('topo.sim.run(99)',n=20)"  
         
         751948 function calls (749374 primitive calls) in 4.649 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 252 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    4.651    4.651 <string>:1(<module>)
        1    0.042    0.042    4.651    4.651 simulation.py:1120(run)
     3074    0.019    0.000    3.306    0.001 inlinec.py:72(inline_weave)
     3074    0.049    0.000    3.272    0.001 inline_tools.py:130(inline)
     3074    3.024    0.001    3.212    0.001 {apply}
     2178    0.006    0.000    2.755    0.001 simulation.py:436(__call__)
     2178    0.021    0.000    2.731    0.001 projection.py:391(input_event)
     2178    0.003    0.000    2.681    0.001 projection.py:519(present_input)
     2178    0.055    0.000    2.678    0.001 cf.py:725(activate)
     1980    0.011    0.000    2.624    0.001 lissom.py:95(input_event)
     2178    0.027    0.000    2.581    0.001 optimized.py:33(__call__)
     1188    0.012    0.000    1.166    0.001 lissom.py:113(process_current_time)
       99    0.001    0.000    0.691    0.007 basic.py:290(learn)
      100    0.002    0.000    0.573    0.006 basic.py:266(_normalize_weights)
       99    0.000    0.000    0.469    0.005 simulation.py:510(__call__)
       99    0.002    0.000    0.469    0.005 basic.py:140(generate)
     1089    0.117    0.000    0.465    0.000 projection.py:454(activate)
   297/99    0.016    0.000    0.451    0.005 patterngenerator.py:116(__call__)
       99    0.012    0.000    0.404    0.004 basic.py:582(function)
      400    0.002    0.000    0.340    0.001 cf.py:744(apply_learn_output_fns)
</pre>

<P>The simulation now takes about 20 times less time than the Numpy
version took. 

<P>The C++ code adds extra work: for maintenance, for deployment on
different platforms, and for user understanding --- so it has to be 
justified, meaning it should provide large speedups. In this
case, the performance improvement justifies the additional costs
(which have been substantial in terms of maintenance and platform
support --- although platform support cost is diluted by all such C++
functions, and any added in the future).

<P>While making this kind of investigation, you should check that
simulations run with different versions of a function are producing 
the same results. In particular, when working with optimized C++ functions, 
it is possible for one version to appear much faster than another when in fact 
the computations being performed are not
equivalent. You could make a simple check by adding a print statement after
profiling to show the sum of V1 activity, or some similar indicator.

<P>A final consideration is to ensure that the profile run times are
long enough to obtain reliable results. For shorter runs, it would be
necessary to repeat them to find a reasonable estimate of the minimum
time.


<!--CB:
These timings come from 2007/02/21 13:27:26 on the numpy_test_branch, 
using the numpy libraries ?.


Note that numpy has vdot(a,b)=dot(a.ravel(),b.ravel()), but it
is slower than the dot & ravel version. However, the timing 
functions appear to be a little inconsistent, so once we upgrade
to Python 2.5 and use cProfile, that should be checked. If vdot
is actually as fast as dot & ravel, then vdot would be a complete
replacement for DotProduct:

<pre>
from numpy import vdot
class CFPRF_Plugin(CFPResponseFn):
    """
    Generic large-scale response function based on a simple single-CF function.

    Applies the single_cf_fn to each CF in turn.  For the default
    single_cf_fn of vdot, does a basic dot product of each CF with the
    corresponding slice of the input array.  This function is likely
    to be slow to run, but it is easy to extend with any arbitrary
    single-CF response function.

    The single_cf_fn must be a function f(X,W) that takes two
    identically shaped matrices X (the input) and W (the
    ConnectionField weights) and computes a scalar activation value
    based on those weights.
    """
    single_cf_fn = ResponseFnParameter(vdot,
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

However, vdot wouldn't show up in GUI menus etc because it's not
actually a ResponseFn.

The last couple of times I ran this vdot version, I was getting
<pre>
         516656 function calls (508256 primitive calls) in 34.597 CPU seconds

   Ordered by: cumulative time, internal time
   List reduced from 108 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000   34.597   34.597 <string>:1(?)
        1    0.053    0.053   34.597   34.597 simulation.py:626(run)
      400    0.006    0.000   17.882    0.045 simulation.py:452(__call__)
      200    0.017    0.000   13.440    0.067 projection.py:122(input_event)
      200    0.001    0.000   13.403    0.067 projection.py:182(present_input)
      200    0.011    0.000   13.401    0.067 cf.py:786(activate)
      200   13.381    0.067   13.381    0.067 cf.py:352(__call__)
      400    0.005    0.000   13.180    0.033 projection.py:151(process_current_time)
      200    0.009    0.000   13.023    0.065 cfsom.py:58(learn)
      200    0.008    0.000   12.943    0.065 cf.py:793(learn)
      200    5.704    0.029   12.930    0.065 som.py:66(__call__)
    52303    6.103    0.000    6.103    0.000 arrayutil.py:18(L2norm)
      400    0.048    0.000    4.611    0.012 patterngenerator.py:92(__call__)
      200    0.021    0.000    4.432    0.022 generatorsheet.py:106(input_event)
20600/19400    0.141    0.000    4.030    0.000 parameterclasses.py:179(__get__)
    58400    0.856    0.000    3.983    0.000 parameterizedobject.py:307(get_name)
      600    0.010    0.000    3.802    0.006 parameterclasses.py:386(__get__)
      400    0.009    0.000    3.417    0.009 simulation.py:455(__repr__)
 7600/400    0.563    0.000    3.386    0.008 parameterizedobject.py:642(__repr__)
    79328    1.508    0.000    3.111    0.000 parameterizedobject.py:513(get_param_descriptor)
</pre>
-->


<H3><A name="line-by-line">Line-by-line profiling</A></H3>

<P> The profile function described above (which uses Python's inbuilt
profiling) only reports time spent inside functions, but gives no
information about how that time is spent. There is also an optional
line-by-line profiling package available that gives
information about how the time is spent inside one or two specific
functions. So, for instance, if you have a function that does various
operations on arrays, you can now see how long all those operations
take relative to each other. That might allow you to identify a
bottleneck in the function easily. (Note that before doing a
line-by-line profile of a function, you should previously have
identified that function as a bottleneck using the profiling function
described earlier. Otherwise, optimizing the function will result in
little performance gain overall.)

<P>
The line-by-line profiling package is not yet built by default. If you
want to build it, execute the following from your Topographica
directory:
<pre>$ make -C external line_profiler</pre>

<P>
Then, the easiest way to use the new package is to:
<ol>
<li>put the following two lines into <code>~/ipy_user_conf.py</code> (in the <code>main()</code>
function):
<pre>
import line_profiler
ip.expose_magic('lprun',line_profiler.magic_lprun)
</pre></li>
<li>use <code>%lprun</code> from the Topographica prompt</li>
</pre>
</ol>

<H4>Examples</H4>

<P>
To profile topo.base.cf.ConnectionField's
_create_input_sheet_slice() method while starting the lissom.ty
script:
<pre>
$ ./topographica
topo_t000000.00_c1>>> from topo.base.cf import ConnectionField
topo_t000000.00_c2>>> %lprun -f ConnectionField._create_input_sheet_slice execfile("examples/lissom.ty")
</pre>

<P>
To profile calling of
topo.transferfn.HomeoStaticMaxEnt while Topographica is running:
<pre>
$ ./topographica -i contrib/lesi.ty
topo_t000000.00_c1>>> from topo.transferfn import HomeostaticMaxEnt
topo_t000000.00_c2>>> %lprun -f HomeostaticMaxEnt.__call__ topo.sim.run(30)
</pre>

The output you get is something like this:

<pre>
Timer unit: 1e-06 s

File: /disk/data1/workspace/v1cball/topographica/topo/transferfn/basic.py
Function: __call__ at line 749
Total time: 0.955004 s

Line Hits   Time  PerHit %Time Line Contents
================================================
749                           def __call__(self,x):      
750   450  13003   28.9   1.4    if self.first_call:
751     1      9    9.0   0.0         self.first_call = False
752     1     20   20.0   0.0         if self.a_init==None:
753     1    817  817.0   0.1             self.a = self.random_generator.uniform(low=10, high=20,size=x.shape)
754                                   else:
755                                       self.a = ones(x.shape, x.dtype.char) * self.a_init
756     1     27   27.0   0.0         if self.b_init==None:
757     1    411  411.0   0.0             self.b = self.random_generator.uniform(low=-8.0, high=-4.0,size=x.shape)
758                                   else:
759                                       self.b = ones(x.shape, x.dtype.char) * self.b_init
760     1    128  128.0   0.0        self.y_avg = zeros(x.shape, x.dtype.char) 
761                            
762                              # Apply sigmoid function to x, resulting in what Triesch calls y
763   450  88485  196.6   9.3     x_orig = copy.copy(x)
764                              
765   450  24277   53.9   2.5     x *= 0.0
766   450 662809 1472.9  69.4     x += 1.0 / (1.0 + exp(-(self.a*x_orig + self.b)))
767                                      
768                            
769   450   5979   13.3   0.6    self.n_step += 1
770   450  34237   76.1   3.6    if self.n_step == self.step:
771    30    253    8.4   0.0        self.n_step = 0
772    30    654   21.8   0.1        if self.plastic:                
773    30  19448  648.3   2.0            self.y_avg = (1.0-self.smoothing)*x + self.smoothing*self.y_avg 
774                                      
775                                      # Update a and b
776    30  65652 2188.4   6.9            self.a += self.eta * (1.0/self.a + x_orig - (2.0 + 1.0/self.mu)*...
777    30  38795 1293.2   4.1            self.b += self.eta * (1.0 - (2.0 + 1.0/self.mu)*x + x*x/self.mu)
</pre>

<P>From this output, you can see that 69.4% of the time is spent in line
766, which is thus the best place to start optimizing (e.g. by using a
lookup table for the sigmoid function, in this case).
