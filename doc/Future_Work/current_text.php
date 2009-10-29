<P> This is the developers' to-do list. There are several sections,
with earlier ones being higher priority than later ones.  Tasks
within each section are also ordered approximately by priority.

<DL COMPACT>
<P>Most of our current tasks have been moved to
sourceforge's <a href="http://sourceforge.net/tracker/?group_id=53602">trackers</a>;
those are our primary record of outstanding tasks, so please
check there first. In particular, <em>new tasks should be submitted to
a tracker rather than added to this list</em>.

<P><DT>Tasks to be addressed for the upcoming 1.0 release</DT><DD>
What the developers are working on most actively right now.

<!--
<P><DT>Tasks to be addressed after the upcoming n+1 release</DT><DD>
Tasks that the developers hope to be able to start on after finishing
their work for the current release.
-->  
<P><DT>Things we hope to take care of eventually</DT><DD>
Tasks of lower priority; if you would like to see one of these tasks
completed any time soon, please volunteer (even if a developer is
already assigned)! 

<P><DT>Ongoing work</DT><DD>
Long-term tasks that are underway, and tasks that the developers might
currently be investigating: work with uncertain finishing times.
</DL>

<P> By each task, initials in parentheses typically indicate the main
person working on an item, but others may also be involved.  Items
with no initials are not (yet) assigned to a specific developer (so
please feel free to volunteer!!!!). Dates indicate when the item was
first added to the list, or a change was made.


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->


<H2>ALERTs in topo.base</H2>

<pre>
Priorities:
8: release 1.0
3: release someday
0: remove alert

* (8) boundingregion.py cleanup

* cf.py
(8) learning rate moves to learning function rather than cfprojection (CEB)
(8) where mask created (by cfprojection/cf)  (CEB)
(8) learning rate a parameter of CFPLearningFn (CEB)
(8) CFPOutputFn mask parameter could be dropped now a masked iterator 
    can be passed in (CEB)
(8) JCALERT! We might want to change the default value of the
### input value to self.src.activity; but it fails, raising a
### type error. It probably has to be clarified why this is
### happening (CEB)
(3) calculation of no. of units (internal)


* functionfamily.py
(8) TransferFn: rename norm_value (CEB)
(8) LearningFn should have learning_rate param 
    (see same alert in cf.py) (CEB)

* projection.py
(8) other SheetMask + subclasses cleanup 

* Slice
(8) M[slice]-style syntax (first figuring out performance implications
of attribute access) (CEB)
(8) general cleanup (CEB)


* PatternGenerator
(8) needs to support plasticity of output functions (after fixing
Pipeline's plasticity support)


* Simulation
(3) EPConnectionEvent always deepcopying data: does it need to?
(8) SomeTimer (also #1432101)
(8) the mess inside run(); how Forever etc is implemented 
(3) PeriodicEventSequence
    ## JPHACKALERT: This should really be refactored into a
    ## PeriodicEvent class that periodically executes a single event,
    ## then the user can construct a periodic sequence using a
    ## combination of PeriodicEvent and EventSequence.  This would
    ## change the behavior if the sequence length is longer than the
    ## period, but I'm not sure how important that is, and it might
    ## actually be useful the other way.
(8) gc alert in simulation.__new__ (CEB)

* Parameters
(8) FixedPoint doesn't work properly with Number (removing fixedpoint
anyway?) (CEB)
(3) logging: use python's instead of our own?
(3) script_repr: 
# JABALERT: Only partially achieved so far -- objects of the same
# type and parameter values are treated as different, so anything
# for which instantiate == True is reported as being non-default.
(8) ParamOverrides should check_params() (CEB)

</pre>


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->


<!--<H2>Tasks to be addressed in upcoming release:</H2>-->


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->



<H2>Tasks to be addressed by release 1.0</H2>

<H4>2008/09/30 (CB): clean up python code for slow-tests</H4>

<H4>2008/09/30 (CB): coordinates in GUI</H4>

<H4>2007/10/03 (CB): Urgent param/tk cleanup</H4>
Cleanup + doc of param/tk.py. Includes fixing 'from param import tk'.

<H4>2007/10/03 (CB): Urgent plotgroup cleanup</H4>
Cleanup + doc of plotgroup.py

<H4>CB: Idle branch</H4>
Merge or abandon idle branch. 

<H4>pylint: deal with or ignore all warnings</H4>
For make lint-base

<!--
<H4>2007/11/20: output from pychecker in topo.base</H4>
Look at output from "make check-base" and either fix the problems or
add them to the suppressions dictionary in .pycheckrc. Once finished,
can add make check-base to buildbot.

Running it right now gives about 130 warnings, which isn't too hard to imagine looking
at.  Some of them look like things that could be genuinely confusing,
and would be easy to fix (like having local variables named min or
max), and at least one detected an existing hackalert.  Some others
are clearly not problems, but then there is a huge category that I
don't quite understand (like "Function (__init__) uses named
arguments" or "__set__ is not a special method"); those would be worth
understanding.  Once that's done for base/, the rest should be much
easier.
-->


<H4>2007/10/26: Update tutorial</H4>
Add a section about plotting 'Orientation tuning fullfield' tuning
curves.  CB: would the tutorial benefit from being split up a little
more?  Maybe it's getting daunting?

<H4>CB: c++ comparisons</H4>
or/oo_or: Some BaseRN/BaseN combinations don't match. oo_dr: input
parameters don't match - need to adjust c++ lissom.

<H4>ConnectionField tests</H4>
no guarantee that code in/related to connectionfield is valid at all
densities (tied to c++ comparisons task).

<H4>2008/08/15 (JB): Cleanup of examples, especially for afferent radii</H4>

Once Kateryna's project completes, should systematically examine the
example files (see above task) and eliminate as many as possible;
several should now be able to be replicated using her master file.  At
the same time, should update most of the examples to use explicit
parameters for v1aff_radius and lgnaff_radius, so that the sizes of
the LGN and retina sheets can be calculated appropriately.  Currently
many of them have a size that includes a term 0.25 as a buffer, yet
the relevant radius to be buffered against is 0.27083.  There is no
difference in the resulting matrix sizes at the default densities, but
for high enough LGN densities we would expect that a few CFs around
the edge would be cut off slightly using the current values.

<H4>option to clean up external/</H4>
add an option to clean up external/ once topographica has been
built, to free up some space for users while still leaving it
updatable

<H4>Move test data files into subdirectories of topo/tests</H4>


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->


<H2>Things we hope to take care of eventually</H2>


<H4>Cleanup + doc of *panel.py files</H4>


<H4>2007/10/03 (CB): Less-urgent tkgui cleanup</H4>
<ul>
<li>Use parametersframe/tkparameterizedobject in more places
(topoconsole, right click menus...) </li>
<li>Restriction on operations in parallel? (E.g. run and map
measurement.)</li>
</ul>

<H4>(CB) cleanup test_pattern_present</H4> 
(or wherever I tried to add test for not-run simulation before
presenting patterns/saving generators)

<H4>gui: test fullfield x and y work</H4>

<H4>test that shows sim.time() can't be float</H4> 
test for recent run() problems - to catch problems with other future
number types

<H4>Mac</H4>
Have someone else get OS X 10.5 X11 (rather than aqua) working

<H4>parameters out</H4>
to different package

<H4>2008/07/14 (CB): replace internal name mangling for parameters</H4>
with a dict, so e.g. _x_param_value is instead _params['x']. (And decide
whether or not to do this elsewhere e.g. the attributes added to 
dynamic generators.)

<H4>2006/11/09 (JA): optimizations from c++</H4>
Need to implement more of the optimizations from the C++ LISSOM code.

<H4>2007/03/29: Makefiles to python scripts</H4>
Control tests from a python file rather than the Makefile.  Can then
include more tests of examples, by specifying sheet to look at etc.
And importantly, can easily run tests on Windows version.


<H4>2007/03/26: Support for optimization</H4>
Do we need our own simple timing functions to make it easier for users
to optimize their components (as opposed to the overall Topographica
framework, for which the current profile() commands are appropriate)?
A facility for reporting the approximate time spent in methods of each
EventProcessor?  In any case, provide more guide for the user for
doing optimization, focusing on the components we expect to be the
bottlenecks. Add general advice for optimization to the manual pages.


<H4>2007/03/26: developer page about efficient array computations.</H4>
Measurement of numpy.sum(X)/X.sum()/sum(X) performance. Difference
between simulation results on different platforms (for slow-tests in
Makefile).

<H4>alternatives to allow users to include optimized code</H4>
pyrex/cython, ...

<H4>some kind of global time_fn manager?</H4>
defaults to something like lambda:0; the gui could set
to topo.sim.time. Rather than having a default of topo.sim.time
in places that don't know about simulations. In parameterclasses?

<H4>2007/12/23: who's tracking the results of...</H4>
<ul>
<li>examples/joublin_bc96.ty</li>
<li>examples/lissom_whisker_barrels.ty</li>
<li>examples/ohzawa_science90.ty</li>
</ul>
And others...


<H4>2007/07/07: more tests </H4>
We need a test with non-square input sheets, non-square LISSOM sheets,
etc., with both types of non-squareness...and we also need to test
whatever map measurement that we can (e.g. or maps).  Could also add
coverage testing, e.g. using
<a href="http://darcs.idyll.org/~t/projects/figleaf/doc/">figleaf</a>
or <a href="http://nedbatchelder.com/code/modules/rees-coverage.html">coverage.py</a>.

<H4>2007/02/26: consider an alternative debugger</H4>
http://www.digitalpeers.com/pythondebugger/.

<H4>2007/02/28 (CB): OneDPowerSpectrum & Audio PatternGenerators</H4>
Finish the two classes. Make a demo with Audio. Both currently don't work
with test pattern window because plotting expects 2d arrays.

<H4>2005/01/01: components from external packages </H4>
Could consider using or taking components from: SciPy,
ScientificPython, Chaco, Pyro (the robotics package), g, logger
(instead of our custom messaging functions).

<H4>2007/02/23: which version of libraries is numpy using?</H4>
<pre>
- numpy.__config__.show()
- warn users if they're using a slow version?
- http://www.scipy.org/Numpy_Example_List?highlight=%28example
  %29#head-c7a573f030ff7cbaea62baf219599b3976136bac
>>>
>>> import numpy
>>> if id(dot) == id(numpy.core.multiarray.dot):
# A way to know if you use fast blas/lapack or not.
...   print "Not using blas/lapack!"
</pre>


<H4>2006/04/20 (JB): Composite & Image test files.</H4>
Complete test file for Composite and Image.  investigate failing test
in testimage.py (that uses sheet functions).  Currently commented out;
may not be a problem.

<H4>2005/01/01: porting other simulations from c++ lissom</H4>
Finish porting all categories of simulations from parts II and III of
the LISSOM book (i.e. orientation maps, ocular dominance maps,
direction maps, combined maps, face maps, and two-level maps) to
Topographica.


<H4>2007/05/29 (JP) Mac (aqua) GUI cleanup</H4>
The Mac GUI needs a variety of things to make it more Mac-like.
<ul>
<li>Various window styles need to be tweaked: e.g.  EntryFields
should be sunken, backgrounds, light grey (not white), etc.
<li> Tooltip timing is screwed up.
</ul>
(Note that some of these might be fixed automatically when we take
advantage of tk 8.5's themes. We have the bigger problem anyway of the
fact that no other Mac apps use a series of separate windows (as
topographica does).


<H4>2007/06/07: plotgrouppanel's plots </H4>
Maybe should be one canvas with bitmaps drawn on. Then we'd get
canvas methods (eg postscript()). But right-click code will need
updating. Should be easy to lay out plots on a canvas, just like
the grid() code that we have at the moment.

<H4>Run tkgui in its own thread?</H4>

<H4>2007/05/09: topoconsole workspace</H4>
Can we have a matlab-like workspace?

<H4>2006/02/21: read-only objects</H4>
Might someday be interesting to have read-only objects, aiming at
copy-on-write semantics, but this seems quite difficult to achieve in
Python.


<!-- From Tue Sep  6 15:32:25 BST 2005 meeting with Eyal

Major issues
____________

Overall, the documentation and software need to separate 'Learning and
self-organization' from 'Representing signals in topographic maps' and
'Understanding topographic maps'.

Should allow the user to specify the parameters and network setup
themselves, instead of having a learned map.  (E.g. select tuning
width, connection types, etc.)

It should also be possible to import a map measured in the lab into
Topographica, then allow the user to try it out by synthesizing a
network based on that data.

More ambitiously, could start out with the above rough sketch of a
network, then auto-optimize parameters to match a set of behavioral
observations. Longer-term project; will need ways to explore the
space of possible models matching those observations.

In general, it would be useful to start with a set of observations,
and select parameters that match that. 

Should be able to specify (parametrically?) the tuning properties, and
of course measure and display those.

Need to have some representation of receptive fields, mapped onto
actual size units in the world.

Need to be able to map things to millimeters of cortex, and degrees of
visual angle.  E.g. need to be able to map measured locations in the
visual cortex into the model, or even map the measured retinotopic
grid directly into the model.

Color lookup tables for plotting: user needs to pick them, and need
to have keys shown as a color bar.  Also needs to control the
baseline, clipping range, etc. and to have a clipping warning light.

For Eyal's work, adding realistic dynamics is key, including being
able to control the time course, e.g. with various delays.  E.g. it
would be great to have a movie showing the time course of an
activation.  Usually they look at an array of activation patterns, 10
images per row, and then average groups of e.g. 10 frames or subsample
them.  They would usually want to simulate to match the measurement
interval, e.g. 100 Hz, then average for display...

Should study how to add noise to the system.  Both neural noise and
measurement noise are important, including e.g. spatial correlations
(due to lateral connections or feedback?) in spontaneous or evoked
activity, and e.g. how they vary with different assumptions about the
connectivity.

In general, it's an open issue how to have a network with a good
dynamic range but still stable, given background levels of activity,
spontaneous activity in darkness, etc.; will be worth studying.


Less crucial points
___________________

For the display, will be useful to have the units displayed on screen,
etc.

For plotting styles, check Shmuel and Grinvald and Fitzpatrick lab
(e.g. does anyone else have OR-colored activity patterns?).

Array of curves plots:
If they start with an image of 1000x1000 pixels, they bin the data to
100x100 pixel blocks, then plot the average time course of the
response, as a single curve for each condition (x is time, y is change
in fluorescence).  Then each of 100 panels will show 5 or 6 different
curves for different experimental conditions.  (Similar to EEG data --
shows spatial location of small differences between conditions.)

Need good plots of receptive fields -- with the location and size
plotted on the retina.

Minor points for the tutorial:

   When we show the plots, we have white outlines around the lateral
   connections, but don't ever explain them. (easily fixed)
  
   Should show a color bar, and allow user to modify the clipping
   range, etc. (not likely to be fixed in LISSOM, but will be done in
   Topographica).
  
   Explain some of the parameters better (should be easily fixed)


Need to add color keys to the Preference Map panels, e.g. by having a
slot for it in the template.

_______________________________________________________________________________

More Eyal comments:

Need to specify what each 'neuron' in the simulation represents.
How many simulated 'neurons' per simulated 'column'?

Why are the lateral excitatory connections so limited and fixed?

It would be nice to include moving stimuli (drifting gratings, random dots etc.)

Display issues;
  
  1) Model editor - not clear how to interpret; how to modify;

  2) State that each little plot in the projection plot shows only the
     connection field of the neuron, not the entire set of afferents from the retina.

  3)      Suggestions for Test pattern window
  a. contrast (0-100%) instead of scale
  b. mean luminance (0-1) instead of offset
  c. Change units for orientation to deg

  (Part of our general project of allowing
   user-configurable units. I think that's the only way to do things
   like this, because the simulator is not limited to vision only, and so
   the underlying units have to be very general.
   See http://ipython.scipy.org/doc/manual/node11.html
   for bg on handling arbitrary units.  For example:
     ipython -p physics
       In [1]: x = 3 m/s^2
       In [2]: y = 15 s
       In [3]: x*y
       Out[3]: 45 m/s

   Or maybe use ScientificPython's PhysicalQuantity (alone and in object arrays)
   or "unum"s to represent quantities with units:
   http://books.google.com/books?id=3nR75KSvsq4C&pg=PA169&lpg=PA169&dq=numpy+physicalquantity&source=web&ots=_cmXEC0qpx&sig=JBEz9BlegnIQJor-1BwnAdRTKLE
 )

Minor
  
3) Say in the tutorial that orientation maps look funny around the
edges, because of the effects of having lateral connections 
that are cut in half at that border.

To figure out:

4) There is no response in V1 to a small square despite a strong
   response in the retina. Does the response get canceled by the
   lateral inhibition?

5) At point 9 in the tutorial, when I press the Normalize toggle I get
   strange activity pattern in the retina and V1 and when I press the
   Normalize toggle again it does not revert to the old response.
-->


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->

<H2>Ongoing work</H2>

<H4>2006/04/10: optional external packages on platforms other than
linux</H4>
Optional packages (e.g. mlabwrap, pyaudio) on Windows and OS X.


<H4>2006/02/23 (all): Making more things be Parameters</H4>
And writing doc strings at the same time. 

<H4>2006/02/23 (all): ensuring classes are declared abstract if they
are abstract</H4>
Plus making sure base and simple classes are imported into packages
(i.e. Sheet into topo/sheets/, Projection into topo/projections/,
Constant into topo/patterns/, and so on).

<H4>2006/02/21 (all): documentation, unit tests</H4>
Improving both, plus eliminating ALERTs.  Could use Sphinx instead of
epydoc for Reference Manual; apparently searchable.

<H4>2007/03/14 (CB): gnosis.xml.pickle </H4>
Needs to be updated for numpy. I'm working with module's author at the
moment.

<H4>2007/03/14: building scipy</H4>
how to build scipy without requiring any of the external linear
algebra libraries, etc? Then scipy would at least build easily, and
users could install the optimized versions if they wished.
Investigate garnumpy.


<H4>2007/07/24 (JB): Matlab Toolbox for Dimensionality Reduction</H4>
Consider interfacing to this toolbox, which contains Matlab
implementations of twenty techniques for dimensionality reduction. A
number of these implementations were developed from scratch, whereas
other implementations are based on software that is already available
on the Web.  http://www.cs.unimaas.nl/l.vandermaaten/dr CB: or
consider a python/numpy alternative?
E.g. http://mdp-toolkit.sourceforge.net/


<H4>2007/07/24 (JB): Digital Embryo Workshop</H4>
Consider interfacing to this toolbox, which is handy for generating
novel 3D objects, e.g. to use as training stimuli (perhaps for
somatosensory simulations?).
http://www.psych.ndsu.nodak.edu/brady/downloads.html


<!-- NOTES NEEDING TO BE TURNED INTO TASKS 

Could consider interfacing to PsychoPy (http://www.psychopy.org) or
VisionEgg (http://www.visionegg.org/), free libraries for running
psychophysics experiments in Python.


The DAVIS visualization system might be useful to study, especially when moving
to 2-photon-imaging-like models: http://vip.cs.utsa.edu/research/Davis

Any idea what this does?
alterdot()
numpy.alterdot(...)
alterdot() changes all dot functions to use blas.
(but note that dot() is, for some reason, not a dot product.)


_________________________________________________________




|  > |  > - For (basic ?) indexing of an ndarray - is there any reason to prefer
|  > |  > A[i,j] over A[i][j]?
|  > |
|  > |  The latter involves two function calls and creation of an intermediate
|  > |  object (a view array).
|  >
|  > Whoa, I didn't realize that!  I guess we should always be doing
|  > A[i,j]?  I think in most of our code we do A[i][j]...

+(OPTIMIZATION PAGE)


_________________________________________________________


Start to use doctest. Unit tests need to be sorted out: reset state
between tests (e.g. by saving/restoring class attributes)?

_________________________________________________________

Some useful links:
http://scipy.org/Tentative_NumPy_Tutorial
http://scipy.org/NumPy_for_Matlab_Users



_________________________________________________________

> Second, is there any way to prevent obscure errors like this by
> checking to make sure that a Parameter is owned by a
> Parameterized? I can't quite imagine how to do this, because
> when the Parameter is constructed it's not owned by anything at all.

Unfortunately you can't patch __setattr__ on <type> or
<object>.  Seems like there should be some clever way, but I can't think
of anything off the top of my head.


_________________________________________________________

Effective logging

A very useful suggestion sent in by Robert Kern follows:

I recently happened on a nifty way to keep tidy per-project log files. I made a profile for my project (which is called "parkfield").

    include ipythonrc

    # cancel earlier logfile invocation:

    logfile ''

    execute import time

    execute __cmd = '/Users/kern/research/logfiles/parkfield-%s.log rotate'

    execute __IP.magic_logstart(__cmd % time.strftime('%Y-%m-%d')) 

I also added a shell alias for convenience:

    alias parkfield="ipython -pylab -profile parkfield" 

Now I have a nice little directory with everything I ever type in, organized by project and date.


_________________________________________________________
Enhanced Interactive Python with IPython
http://www.onlamp.com/pub/a/python/2005/01/27/ipython.html?page=1





_________________________________________________________
working with matlab: scipy's io.loadmat 



_________________________________________________________
lots of places I do isinstance(x,ParameterizedMetaclass) or 
something to determine class or obj. There are easier ways
(e.g. isinstance(X,type)), and maybe not all of them are required.





_________________________________________________________
CB: code I was experimenting with in Parameter's __init__ (everyone else please ignore)
(detects Parameter not declared inside Parameterized)

        f0 = sys._getframe(0)
        frames = [f0]

        for i in range(100):
            new_f = frames[i].f_back
            if new_f:
                frames.append(new_f)
            else:
                break

        found = False
        for f in frames:
            if 'Parameterized' in open(f.f_code.co_filename).readlines()[f.f_code.co_firstlineno-1]:
                found=True

        print found

        if not found:
            print self
        
                
##         import __main__; __main__.__dict__['z']=[f0,f1,f2,f3,f4]
##         print "zed for ",self
        
##         method_name = f.f_code.co_name
##         filename = f.f_code.co_filename
       
##         arg_class = None
##         args = inspect.getargvalues(f)
##         if (args[3].has_key('func')):
##             func = args[3]['func'] # extract wrapped function
##             try:
##                 arg_class = func.func_class
##                 method_name = func.func_name
##                 filename = func.func_code.co_filename
##             except:
##                 pass

##         print self,"*",arg_class

## #def called_class():
        
##         f = sys._getframe(0)       
## ##        method_name = f.f_code.co_name
## ##        filename = f.f_code.co_filename

##         arg = None
##         args = inspect.getargvalues(f)
##         if len(args[0]) > 0:
##             arg_name = args[0][0] # potentially the 'self' arg if its a method
##             a=args[3][arg_name]
##             print self," BY ",a,type(a)

       #return arg_class #(method_name, filename, arg_class)


 #       called_class()

_________________________________________________________



Something like
assert topo.guimain.tk.call("info","library").endswith("lib/tcl8.5")
could eventually form the basis of a buildbot test on os x that checks
we use Topographica's tcl/tk rather than the system one.



Consider nose unittest extension
http://somethingaboutorange.com/mrl/projects/nose/



have buildbot run make -C examples?



I'm not certain, but maybe we could make pickles smaller by taking advantage
of something new in protocol 2, documented at http://www.python.org/dev/peps/pep-0307/ (search for 'bloat' and '__newobj__') (implement __reduce__ and
__newobj__ for Parameterized)




_________________________________________________________

Parameters & Parameterized


Attributes of Parameterized that are Parameters behave
specially. Consider first the normal python attribute system:


class Someclass(object):
    x = 5

When you request the x attribute of Someclass (Someclass.x), Python
checks Someclass.__dict__ and finds Someclass.__dict__['x']; this is
simply the object float(5), and so it is returned
(i.e. Someclass.x==5)

Now consider Parameters. The Parameterized class looks something like
this:

class Parameterized(object):
    print_level = Parameter(default=0)


This is equivalent to:

p = Parameter(default=0)
class Parameterized(object):
    print_level = p

(allowing us to refer to the Parameter instance as p).


The attribute print_level of Parameterized
(Parameterized.__dict__['print_level']) is the instance p of the
Parameter class
(i.e. Parameterized.__dict__['print_level']==p). Because Parameter
defines the special __get__ method, it is called a descriptor; when
Python encounters an attribute that is set to a descriptor, it does
not simply return the object it finds (float(5) is returned for
Someclass.x, but p is *not* returned for Parameterized.print_level).
Instead, p.__get__() is called, and the value returned by that method
is returned for Parameterized.print_level.


Below is the __get__ method of Parameterized:

class Parameter(object):
    ...

    def __get__(self,owner_instance,owner_class): 
        """
        Return the value for this Parameter.

        If called for a Parameterized class, produce that
        class's value (i.e. this Parameter object's 'default'
        attribute).

        If called for a Parameterized instance, produce that
        instance's value, if one has been set - otherwise produce the
        class's value (default).
        """
        # NB: owner_instance can be None (when __get__ called for a
        # Parameterized class); owner_class is never None        
        if not owner_instance:
            result = self.default
        else:
            result = owner_instance.__dict__.get(self._internal_name,self.default)
        return result


When Python calls p.__get__(), it also passes the object in whose
dictionary p was found. In our current example, it is the
Parameterized class object that owns p (there is no owner_instance).
Therefore, the call is Parameter.__get__(p,None,Parameterized), and we
are now only concerned with the first part of the if-test above. The
value that is returned by __get__() is p.default; i.e.,
Parameterized.print_level is actually stored in p.default.  Repeating:
a Parameterized class's value of a parameter is not stored in the
Parameterized class, but in the Parameter instance instead.


Now consider an instance of Parameterized:

parameterized_instance = Parameterized()

What happens when we ask for parameterized_instance.print_level? First, if we
inspect parameterized_instance.__dict__, we find no mention of print_level:

    >>> parameterized_instance.__dict__.keys()
Out[27]:['initialized', 'nopickle', '_name_param_value']

But, if we ask for parameterized_instance.print_level, we do get a
value back.  This is because when you request an attribute of an
instance in Python, it first checks the class. So, Python finds the
Parameterized class object, and requests
Parameterized.__dict__['print_level']. This is of course our earlier
Parameter instance p. On finding that this is a descriptor, Python
calls its p.__get__(), just as before. This time, however, the call
contains a Parameterized instance:
Parameter.__get__(p,parameterized_instance,Parameterized). We must
now consider the 'else' part of the if-test above:

        else:
            result = owner_instance.__dict__.get(self._internal_name,self.default)
        return result

What is p._internal_name? It is the string
'_print_level_param_value'. So what is
parameterized_instance.__dict__['_print_level_param_value']? It does
not exist; there is no entry '_print_level_param_value' in the
dictionary. Therefore, we can see that p.default is again
returned. Saying this another way: requesting a parameter value that
has not been set on an instance gives the instance's class value,
which is stored on the parameter instance.

What about this '_print_level_param_value'? This is name we use to
store a value for print_level if it is set on parameterized_instance:
parameterized_instance.print_level=10 does not result in
parameterized_instance.__dict__['print_level']==10, as you would
expect for a normal attribute. Again, this is a consequence of
Parameter being a descriptor. In this case, because Parameter has a
__set__ method, something different happens for attribute setting from
in the normal case. I'm not going to talk about that here - the
important point is that setting a parameter on a parameterized
instance results in the value being stored in that instance, but under
a special entry ('_print_level_param_value') that is not accessed
directly. Rather, when parameterized_instance.print_level is
requested, Parameter.__get__() finds '_print_level_param_value' in
parameterized_instance.__dict__ and returns it. As we have already seen, 
if it doesn't find such an entry, it returns p.default.

Why go to all this trouble? Having Parameterized attributes that are
themselves instances of Parameter classes means that we can have
various special behaviors for attributes. Parameter has several 
fields, such as 'doc', 'default', and so on. Because of inheritance, 
the doc and default value for a Parameter 'size' of a Parameterized subclass can be
inherited by further Parameterized subclasses. Another example - we have the
Number(Parameter) subclass; its __set__ method can perform bounds
checking to ensure that such attributes can only be set to a
restricted range of values (i.e. numbers). A furhter example is the
Dynamic(Parameter) subclass. Attributes that are Dynamic parmeters can
generate new values when they are requested, because the method
Dynamic.__get__ that is called whenever such an attribute is requested
can do things like call a random number generator and return the
generated number.

In fact I want to discuss Dynamic parameters now. Before looking at
the parameter itself, though, let's list some example uses of Dynamic
parameters.

(1) The first example is having attributes that change once per simulation
time. If I have an input pattern that I want to vary each iteration, then
I need dynamic attributes:

input_pattern = Gaussian(x=UniformRandom())

Here I want a Gaussian pattern to be drawn with a different x
coordinate every iteration, and that the x coordinate should be drawn
from a UniformRandom distribution. For all the time that the simulation
time remains the same, I want the Gaussian's x to remain the same.


(2) The second example is having attributes that change every time
I request them. If I want to create a CFProjection with initial weights
that are a different shape for each CF, then I need attributes that
change every time they are requested:

CFProjection.weights_generator = Gaussian(x=UniformRandom())

Here I want a Gaussian pattern to be drawn with a different x
coordinate every time it is requested. The simulation time will
not change during construction of the CFProjction.


Actually, there is a third example, but I'll discuss that later.


We had (2) by default originally (before we changed Dynamic parameters
to be able to use a time_fn):

class param.Dynamic(Parameter):
    ...
    def __get__(self,owner_instance,owner_class):
        val = super(Dynamic,self).__get__(owner_instance,owner_class)
	if is_dynamic(val):
            return produce_value(val)
        else:
            return val

is_dynamic() simply checks that val is e.g. callable. 
produce_value() does whatever is necessary to val to generate a 
new value, e.g. calls val.

Any request for an attribute set to a Dynamic Parameter resulted
in the stored value being called if possible to generate a new value
(i.e. the dynamic parameters updated every time requested).
There was no way to have (1).


Now, we have (1) by default, and a more complex system:

class param.Dynamic(Parameter):
    time_fn = None                    
    def __init__(self,**params):
        super(Dynamic,self).__init__(**params)
        if is_dynamic(self.default):
            self._initialize_generator(self.default)

    def _initialize_generator(self,gen):
        gen._Dynamic_last = None
        gen._Dynamic_time = -1
                
    def __get__(self,owner_instance,owner_class):
        gen = super(Dynamic,self).__get__(owner_instance,owner_class)
	if is_dynamic(gen):
            return self._produce_val(gen)
        else:
            return gen
	
    def _produce_value(self,gen):
        """
        Return a value from gen.

        If there is no time_fn, then a new value will be returned
        (i.e. gen will be asked to produce a new value).

        If the value of time_fn() is greater than
        what it was was last time produce_value was called, a
        new value will be produced and returned. Otherwise,
        the last value gen produced will be returned.
        """
        if self.time_fn is None:
            value = produce_value(gen)
            gen._Dynamic_last = value
        else:
            time = self.time_fn()
            if time>gen._Dynamic_time:
                value = produce_value(gen)
                gen._Dynamic_last = value
                gen._Dynamic_time = time
            else:
                value = gen._Dynamic_last

        return value

    ...


Dynamic.time_fn = topo.sim.time


XXX got here



(3) The third example is also having an attribute that changes every
time I request it, but only a specified attribute (others changing
independently). If I want to create a CFProjection with initial
weights that are drawn using a variety of shapes, then I could use a 
Selector pattern generator to have each CF drawn with by a pattern
generator selected from a list of possibilites each time. Selector's 
index parameter should therefore be a dynamic parameter that updates
at every request.

XXX

* where to store time_fn for specific parameter instance

XXX

* How to override slot in subclass?
Unfortunately, I didn't realize how restrictive __slots__ can be. Consider this:

class Parameter(object):
    __slots__ = ['default','doc',...]
    def __init__(self,default=None,doc=None,...):
        super(Parameter,self).__init__(self)
        self.default=default
        ...

class param.Dynamic(Parameter):
    __slots__ = ['time_fn']
    def __init__(self,time_fn=None,**args):
        super(Number,self).__init__(**args)
        self.time_fn = time_fn
        ...

class param.Number(Dynamic):
    __slots__ = ['bounds',...]
    def __init__(self,bounds=None,...,**args):
        super(Number,self).__init__(**args)
        self.bounds = bounds
        ...

# no problem
d = param.Dynamic()

# gives error: Dynamic slot 'time_fn' is read only
n = param.Number()


_________________________________________________________

Pickling main (for 'saving session') 
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/572213
http://dev.pocoo.org/hg/sandbox/file/tip/pshell.py

CB: note that I'm not actually planning to pickle main/implement
session saving, but I do plan to read the above references anyway for
pickle tips.


_________________________________________________________

Parameterized.name returns __name__ rather than None?
(this is not Parameterized().name)

-->








<!-- Also suggested by Geisler, 7/1/2005:
  Package as a Matlab toolbox to get the right people to use it?
  Package it as an easy-to-use out-of-the-box optical imaging simulator
    -- need to tell it what stimulus, what eccentricity, what cortical patch
  Be able to look at the effects of attention
  Add specific models for intrinsic or voltage-sensitive-dye imaging 
-->



<!-- Useful or potentially useful developer references for attribute access etc.
http://www.cafepy.com/article/python_attributes_and_methods/python_attributes_and_methods.html

http://mail.python.org/pipermail/python-dev/2003-May/035732.html

http://www.cafepy.com/article/python_types_and_objects/

http://www.cafepy.com/article/python_types_and_objects/python_types_and_objects.html
-->



