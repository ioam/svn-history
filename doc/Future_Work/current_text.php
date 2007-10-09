<P> This is the developers' to-do list. There are several sections,
with earlier ones being higher priority than later ones.  Tasks
within each section are also ordered approximately by priority.

<DL COMPACT>
<P><DT>Tasks to be addressed for the upcoming n release</DT><DD>
What the developers are working on most actively right now.

<P><DT>Tasks to be addressed after the upcoming n+1 release</DT><DD>
Tasks that the developers hope to be able to start on after finishing
their work for the current release.
  
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

<P>We are slowly changing over to use sourceforge's <a
href="http://sourceforge.net/tracker/?group_id=53602">trackers</a>, so
please also check there. Ideally, <B>new tasks should be submitted to a
tracker rather than added to this list</B>.

<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->

<H2>Tasks to be addressed before the upcoming 0.9.4 release:</H2>

<H4>2007/10/09 (CB): gui bugs</H4>
Clicking "Normalize" on a pref window causes refresh (re-measurement).
"Strength only" is messed up on a pref window. Right click > Connection Fields
is not fixed.

<H4>2007/10/03 (CB): Urgent tkgui + plotgroup cleanup</H4>
<ul>
<li>Cleanup + doc of tkparameterizedobject.py and parametersframe.py</li>
<li>Cleanup + doc of *panel.py files</li>
<li>Cleanup + doc of plotgroup.py</li>
<li>Reorganize classes and filenames in tkgui</li>
<li>scrollbars: clean up behavior (can we stop bars coming on and going off
when resize pressed? can we stop empty space when there are no bars? can we stop
bars being there when not required [a bwidget bug])? why is 'press refresh to see
plots...' text not centered? clean up + doc code. </li>
<li>finish basic developer manual tkgui intro</li>
<li>on windows, progress  bar always flicks on for a small fraction of a second
(even for runs of 1).</li>
</ul>

<H4>2007/09/01: timing code </H4>
The timing object is nearly done, allowing progress bars, time
remaining estimates, etc., but Jim needs to look at it to finish it up
(and then close tracker 1432101).

<H4>2007/04/21: Note for Windows users</H4>
Where to put this note? Working from the cmd.exe on Windows, single
quotes must appear inside double quotes: it can't be the other way
round. Applies to anywhere in topographica that there are commandline
instructions that might include one string inside another.
i.e. "'Hello'", not '"Hello"'<BR>
We might also want to add notes about omitting './' and changing
'/' to '\' in general (currently on the downloads page).

<H4>2007/10/09: Note for Windows developers</H4>
Paths in the code *must* be unix-style paths. The functions
resolve_filename and normalize_path both handle conversion to
Windows format. (Note for all developers: use resolve_filename()
and normalize_path() for code that works on Windows and linux.) 

<H4>2007/03/28 (?): Update tutorial</H4>
Update the lissom_oo_or tutorial page to include how to start and stop
training and to add a section about plotting 'Orientation tuning
fullfield' tuning curves.
CB: would the tutorial benefit from being split up a little more?
Maybe it's getting daunting?

<H4>2007/08/12: Finish support for measuring receptive fields</H4>
Finishing cleaning up associated code (maybe mostly for Jim to do?).
Could eventually use STRFPAK or a similar approach.


<H4>2006/03/26 (CB): scheduled_actions in lissom examples</H4>
Insert missing actions in case someone tries higher densities.
JAB 2007/10/08: I checked lissom_oo_or.ty (but not any other
.ty scripts!), and I count just as many actions of each type
as there are in commands/or_defs in C++ lissom.  So I think that
this note is obsolete, unless there are other .ty scripts to check
or some other reason to think this task is not done.


<H4>2007/10/08 (CB): test topographica-win</H4>
Test that results from Windows version match those from the standard
one. The unit tests and the "make compare_oo_or" test are fine, but I
can't run the other, smaller tests of all the networks because the
checked in _DATA files don't seem to work on Windows. I get
"ImportError: no module named fixedpoint" during unpickling. Importing
fixedpoint works in Windows, and I can see it there in
site-packages. So there's some confusion somewhere, and it could be
difficult to solve. I have no idea whatever about this problem.


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->

<H2>Tasks to be addressed after the 0.9.4 release:</H2>

<H4>2007/10/03 (CB): Plotting non-CFProjection Projections</H4>
Modify PlotGroup and ProjectionPGPanels so that we can plot
a wider variety of Projections.


<H4>2007/10/05 (CB): Dynamic info</H4>
Dynamic info is currently disabled on projection panel windows
because it hasn't been implemented for those classes. Need to 
generalize coordinate-calculation method in plotgrouppanel.py
and then add one or more specializations for the projection
panels. (Plus ProjectionView needs some modification, probably.)


<H4>2007/10/03 (CB): Less-urgent tkgui cleanup</H4>
<ul>
<li>ModelEditor(PlotGroupPanel), and cleanup of model editor</li>
<li>Control which options are available on right-click menu (e.g. no
'Connection Fields' for a Connection Fields plot).</li>
<li>Replace Pmw balloon and message bar with those from bwidget; remove
Pmw</li>
<li>Use parametersframe/tkparameterizedobject in more places (topoconsole, 
right click menus...) </li>
<li>Restriction on operations in parallel? (E.g. run and map measurement.)</li>
<li>Which widgets should expand (expand=YES ?), which should fill the
space (fill=X?) (e.g. in parameters frames sliders etc should
expand), and so on. Switch to grid layout where it's more
appropriate.</li>
<li>Document some Tkinter tips. More tasks/notes in
topo/tkgui/__init__.py</li>
</ul>


<H4>2006/05/24 (JB): Problems with examples/joublin_bc96.ty</H4>
Strange Projection plots.

<H4>2007/03/29 (CB): connectionfield/slice/sheetcoords</H4>
HACKALERTs relating to connection fields; test file for
connectionfield; cleaning up cf.py and projections/basic.py along with
the Slice class and SheetCoordinateSystem (there are several
simplifications that can be made).  Maybe we can use masked arrays,
now that Numpy has support for several varieties that might meet our
needs better than Numeric's did.


<H4>2006/07/07 (CP): Fix normalization to allow negative weights.</H4> 

<H4>2007/05/03: Cross normalization</H4>
Need a button you can press that will normalize maps against each
other (to view plots on the same scale).  Maybe we can automatically
joint normalize plots for any joint-normalized projections?  That's
presumably how we want it to behave with multiplicative normalization,
because the sum is constant for each independent normalization, and
thus the relative values are not very interesting unless the sums are
normalized together.

<H4>2007/03/27 (CB): abstract classes</H4>
given how private attributes work in Python, it seems like we can just
have a parameter __abstract_class=True for abstract classes, and then
__is_abstract can check to see if there is such an attribute (and that
it is True, just in case).


<H4>2007/09/26: Better spiking support </H4>
There is a spiking network implemented now (see leaky_lissom_or.ty),
but it needs to be generalized to support a large family of spiking
algorithms. 

<H4>2007/07/07: more tests </H4>
We need a test with non-square input sheets, non-square LISSOM sheets, etc., 
with both types of non-squareness...and we also need to test whatever
map measurement that we can (e.g. or maps).

<H4>2007/04/29: Weight seeds</H4>
[See SF feature tracker]

<H4>2007/04/10 (JB): Add an example that is a good starting point for</H4>
wrapping an external simulation as a Sheet in Topographica.  A
first pass wrapping a spiking retina simulation written in PyNN/PyNEST
was done at the FACETS CodeJam in March 2007, but a cleaner example
can be made.

<H4>2007/03/26 (CB): right-click menus</H4>
Tidy code, then make it possible to add things to the menu without
changing the tkgui files, like the templates work for activity plots.
The menus need to be dynamic, adapting to whatever channels
are present, rather than always assuming that plots are SHC plots.

<H4>2006/02/21: ReadOnlyParameter</H4>
To allow declaration of something but not let it be set anywhere else,
even in a ParameterizedObject constructor.

<H4>2006/06/19 (JB): Number, DynamicNumber</H4>
- Need to replace the current implementation with one where Number has a
'dynamic' slot that can be turned on or off, so that any Number could
be dynamic.  Includes making sure something sensible happens in model
editor, and (eventually) making it possible to set their values and
(hopefully) change any Number to be dynamic.
- Need to make sure DynamicNumbers are advanced only once per simulation time.

<H4>2007/02/26: Move to IPython</H4>
Would get command-prompt completion in the local namespace, debugging
in the namespace of the exception, with easier to follow tracebacks,
persistent command histories, easy interaction with the system shell
(using ! to get a shell and $ to feed it Python variables), and
session logging.  Combined with ipython.el, Emacs users will then
be able to see the line of the source code where the error or
breakpoint occurred.  Also consider an alternative debugger,
http://www.digitalpeers.com/pythondebugger/.


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->

<H2>Things we hope to take care of eventually</H2>

<H4>2006/11/09: plot outstar connections</H4>
Add support for plotting outstar connections, i.e. outgoing
ConnectionFields.

<H4>2006/11/09 (RZ): map statistics</H4>
Add support for automatic generation of reports with statistics about
maps, e.g. for estimating perceived quantities.

<H4>2006/11/09 (JA): optimizations from c++</H4>
Need to implement more of the optimizations from the C++ LISSOM code.

<H4>2006/11/09 (CP): Add automatic assignment of topo.sim.name</H4>
Take the base name of the first .ty file in sys.argv (if any).  Also
should clean up how the window titles are initialized, so that it is
done after a .ty script is loaded (whether on the initial command line
or from the GUI).  (Right now the name is updated only when a window
is first opened, or when learning is done in the topoconsole.)


<H4>2007/05/06 (CB): plot histograms</H4>
Histograms for the plots, with easy control over the number or bars,
scale, etc.<BR>
Need to add some controls and reasonable defaults for various plots.


<H4>2007/03/29 (CB): Makefiles to python scripts</H4>
Control tests from a python file rather than the Makefile.  Can then include
more tests of examples, by specifying sheet to look at etc.  And importantly,
can easily run tests on Windows version.


<H4>2007/03/26 (CB): Support for optimization</H4>
Do we need our own simple timing functions to make it easier for users
to optimize their components (as opposed to the overall Topographica
framework, for which the current profile() commands are appropriate)?
A facility for reporting the approximate time spent in methods of each
EventProcessor?  In any case, provide more guide for the user for
doing optimization, focusing on the components we expect to be the
bottlenecks. Add general advice for optimization to the manual pages.


<H4>2007/03/26 (CB): developer page about efficient array computations.</H4>
Measurement of numpy.sum(X)/X.sum()/sum(X) performance. Difference
between simulation results on different platforms (for slow-tests in
Makefile).

<H4>2007/09/24 (JB) More icons for buttons</H4> 
We've now added icons for the buttons in PlotGroupPanel.  These need
to be used in the Model Editor as well for consistency, and it might
also be useful to develop icons for the parameters in PlotGroupPanel,
not just the buttons.  That will require more work, i.e. finding a
suitable starting icon in BlueSphere-SVG-snapshot-Nov-29-2002, editing
it using Inkscape, and adding it to the distribution, plus making
BooleanParameter support images.  But the result should be much
cleaner-looking windows, with more screen space devoted to the images
rather than the text.

<H4>2007/05/29 (JP) Mac GUI cleanup</H4>
The Mac GUI needs a variety of things to make it more Mac-like.
<ul>
<li> Menus are only visible when Console is frontmost. Probably need a menubar
for every window.
<li> Pmw radio buttons are broken on mac.  Their selected state is invisible. E.g. in Test pattern window.
<li> Various window styles need to be tweaked: e.g.  EntryFields should be sunken, backgrounds, light grey (not white), etc.
<li> Tooltip timing is screwed up.
</ul>
(Note that some of these would be fixed by switching to Tile (see 'investigate using Tile' task). Do any Mac apps use a series of separate windows as topographica does? Anyway, we are already considering (or will consider sometime!) if it's possible to have a workspace for topographica (like matlab has) with tkinter.)


<H4>2007/03/29 (CB): tidy up c++ lissom matching</H4>
Set c++ lissom params so that topographica doesn't have to set ganglia
weight mask specially. Generalize oo_or_map_topo.params.


<H4>2006/06/19 (CB): things not to pickle</H4>
e.g. Filename's search_paths attribute shouldn't be pickled.
Presumably there will be other such items, so should objects have a
standard attribute/parameter that lists attributes not to pickle? Or
something like that.  Otherwise, save_snapshot and load_snapshot could
specifically avoid items. Parameter could have a 'pickle' attribute
that indicates whether or not to pickle its contents. Could we have some
global list of objects not to pickle? Need to think about what's best.


<H4>2007/03/26 (CB): PatternGeneratorParameter default value</H4>
Investigate why this:
"
from topo.base.patterngenerator import PatternGeneratorParameter
PatternGeneratorParameter.default=topo.patterns.basic.Line()
"
gives errors about being read only sometimes. (Try at 
the commandline, from a script, and saving/loading snapshots.)


<H4>2007/02/28 (CB): OneDPowerSpectrum & Audio PatternGenerators</H4>
Finish the two classes. Make a demo with Audio. Both currently don't work
with test pattern window because plotting expects 2d arrays.


<H4>2007/03/30 (CB): PatternGenerator, PatternGenerator2D</H4>
Have a second abstract class so that the base PatternGenerator is
simpler.


<H4>2007/05/09: topoconsole workspace</H4>
Can we have a matlab-like workspace?


<H4>2007/03/26: wrap MDP</H4>
Add a wrapper around the Modular Data Processing (MDP) toolkit
(http://mdp-toolkit.sourceforge.net) to provide easy access to the
PCA, ICA, SFA, ISFA, etc. algorithms.


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


<H4>2006/02/04 (JAB): tune non-inline-optimtized components</H4>
Should work through some of the most commonly used
non-inline-optimized components to see if the implementation can be
tuned slightly for better performance.  For instance, numpy.dot()
appears to be much faster than the current sum(x*y) implementation of
DotProduct:

<pre>
Topographica_t0> import time,numpy,Numeric
Topographica_t0> def runtime(code): start = time.time() ; 
... z = eval(code) ; end = time.time() ; print z, end-start
Topographica_t0> x=2*numpy.ones((1000,10000))
Topographica_t0> y=numpy.ones((1000,10000))
Topographica_t0> runtime("numpy.dot(x.ravel(),y.ravel())")
20000000.0 0.122502088547
Topographica_t0> runtime("numpy.sum(x.ravel()*y.ravel())")
20000000.0 0.312201976776
Topographica_t0> 
Topographica_t0> 
Topographica_t0> x=2*Numeric.ones((1000,10000))
Topographica_t0> y=Numeric.ones((1000,10000))
Topographica_t0> runtime("Numeric.dot(x.flat,y.flat)")
20000000 0.0919671058655
Topographica_t0> runtime("Numeric.sum(x.flat*y.flat)")
20000000 0.358192205429
</pre>

After this, it would be interesting to get some hard numbers about how
much faster the inline-optimized components are than those using numpy
primitives.


<H4>2006/11/09 (JA): parameter spaces</H4>
Add better support for exploring and optimizing parameter spaces.


<H4>2006/12/21: lock to real time?</H4>
Could add an option to lock Topographica to real time, so that once
processing is done at a particular virtual time, it waits until the
next real time before moving to the next event (which may be different
due to real-time input arriving by then).  On the other hand, maybe
this isn't necessary?  E.g. everything could be driven from a
PatternGenerator that produces a new pattern whenever some real-world
input arrives, and then the rest of the processing can be triggered
from that, as fast as it can compute.  Worth thinking about, e.g. to
handle simple webcam input.


<H4>2006/06/03: zero-sized CFs</H4>
Allow min_matrix_radius to be set to zero, and then say that if no
unit ends up in the CF, then there will be no CF for that unit.  But
that's going to make the rest of the code hard to write, because we'll
either have to deal with CFs with empty matrices, or deal with CFs
missing altogether.  (As an example, the problem of zero-sized CFs
arises in examples/joublin_bc96.ty.)  Maybe it would be simplest to
use a non-zero CF size, but with a mask making no unit visible; not
sure.


<H4>2006/05/19: pychecker</H4>
look at the output from:
bin/python lib/python2.4/site-packages/pychecker/checker.py topo/base/*.py
Decide which ones of the messages are real problems.  Running it
right now gives 86 warnings, which isn't too hard to imagine looking
at.  Some of them look like things that could be genuinely confusing,
and would be easy to fix (like having local variables named min or
max), and at least one detected an existing hackalert.  Some others
are clearly not problems, but then there is a huge category that I
don't quite understand (like "Function (__init__) uses named
arguments" or "__set__ is not a special method"); those would be worth
understanding.  Once that's done for base/, the rest should be much
easier.


<H4>2006/05/15: array type</H4>
All arrays should be numpy.float32


<H4>2006/04/20: unit tests</H4>
Need to be cleaned up so they run correctly. For example, many of the
tests in testsheet.py run twice - correct that.  See CEBALERT in
topo/tests/testsheet.py.


<H4>2006/04/20 (JB): Composite & Image test files.</H4>
Complete test file for Composite and Image.  investigate failing test
in testimage.py (that uses sheet functions).  Currently commented out;
may not be a problem.


<H4>2006/02/21 (JB): Parameters: remove 'hidden' attribute</H4>
Instead use (e.g. negative) precendence.


<H4>2006/02/21 (JB): PatternGenerator parameters</H4>
Have size and aspect_ratio Parameters in PatternGenerator so that
subclasses can inherit doc, precedence attributes (etc), but have them
not used unless a subclass does really use them.  It might be better
just to create an abstract PatternGenerator class for grouping
together all patterns using those parameters, which shouldn't be too
hard.


<H4>2006/03/07 (JL): change_bounds()</H4>
make change_bounds() able to enlarge as well as shrink 


<H4>2005/01/01: grouping sheets for plotting</H4>
Add a mechanism to group Sheets into a logical unit for plotting,
analysis, etc.  For instance, it should be possible to group three
R,G,B sheets into one eye, two ON and OFF sheets into one LGN area,
and several V1 layers into one stack.  Such grouping should support
e.g. presenting a color bitmap to an Eye instead of to R, G, and B
separately, plotting the resulting activation from the three areas in
true color, combining ON and OFF plots into one bitmap (by
subtraction), and measuring a vertically summed orientation map for a
model using several layers.

<H4>2005/01/01: porting other simulations from c++ lissom</H4>
Finish porting all categories of simulations from parts II and III of
the LISSOM book (i.e. orientation maps, ocular dominance maps,
direction maps, combined maps, face maps, and two-level maps) to
Topographica.

<H4>2007/06/07: plotgrouppanel's plots </H4>
Maybe should be one canvas with bitmaps drawn on. Then we'd get
canvas methods (eg postscript()). But right-click code will need
updating. Should be easy to lay out plots on a canvas, just like
the grid() code that we have at the moment.



<!-- 2007/04/18
Information about OS X & icons, from Kevin Walzer (www.codebykevin.com)

The application icon is part of the application bundle structure. See
the link below for some basic tips on how to create an icon and specify
it in your application. (Note this article does not deal specifically
with deploying Python applications, but the parts about the icon are
applicable.)

http://tk-components.sourceforge.net/tk-bundle-tutorial/index.html

The easiest way to specify the icon with a Python application is part of
the setup file you use with py2app (which wraps all Python packages into
an application package on the Mac).  Here's a basic example:

"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app
import os

imagedir = (os.getcwd() + "/images")
helpdir = (os.getcwd() + "/html")

setup(
    app = ['Phynchronicity.py'],
    data_files = [imagedir, helpdir],
    options=dict(py2app=
                    dict(iconfile='Phynchronicity.icns',
                    plist = 'Info.plist'),
             ),
    )

You can get more information about using py2app, and help with
questions, on the MacPython mailing list.

-->


<!-- Also suggested by Geisler, 7/1/2005:
  Package as a Matlab toolbox to get the right people to use it?
  Package it as an easy-to-use out-of-the-box optical imaging simulator
    -- need to tell it what stimulus, what eccentricity, what cortical patch
  Be able to look at the effects of attention
  Add specific models for intrinsic or voltage-sensitive-dye imaging 
-->


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
   for bg on handling arbitrary units.
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

<H4>2006/12/14 (JB): Documentation for the new Numeric </H4>
It's not free. But we could document differences from the current
Numeric documentation for our users, as we find these differences.
This doesn't seem very urgent any more, as the online Numpy
documentation has gotten much better.

<H4>2006/04/10 (CB): optional external packages on platforms other than linux</H4>
Optional packages (e.g. mlabwrap, pyaudio) on Windows and OS X.


<H4>2006/02/23 (all): Making more things be Parameters</H4>
And writing doc strings at the same time. E.g. the x and y widgets in
the Unit Weights window can be Numbers with bounds, etc.


<H4>2006/02/23 (all): ensuring classes are declared abstract if they are abstract</H4>
Plus making sure base and simple classes are imported into packages
(i.e. Sheet into topo/sheets/, Projection into topo/projections/,
Constant into topo/patterns/, and so on).


<H4>2006/02/21: read-only objects</H4>
Might someday be interesting to have read-only objects, aiming at
copy-on-write semantics, but this seems quite difficult to achieve in
Python.


<H4>2006/02/21 (all): documentation, unit tests</H4>
Improving both, plus eliminating ALERTs.

			     
<H4>2007/03/14 (CB): gnosis.xml.pickle </H4>
Needs to be updated for numpy. I'm working with module's author at the
moment.


<H4>2007/03/14 (CB): building scipy</H4>
how to build scipy without requiring any of the external linear
algebra libraries, etc? Then scipy would at least build easily, and
users could install the optimized versions if they wished.
Investigate garnumpy.


<H4>2007/09/06 (CB): Investigate using Tile</H4> 
Tile widgets looks good on linux, windows, and mac.  Tile uses themes
& styles, so we get a GUI that looks 'right' on Windows and Mac.

<P> To use Tile: <code>make -C external tile</code> and remove
<code>Pmw.initialize(root)</code> from __init__.py (means you lose the
GUI popup errors - you won't be sad about that), then uncomment marked
code in __init__.py.

<P> Status (tile-0.7.8,bwidget-1.7.0): On linux, console starts with all its
widgets themed by Tile (except MessageBar), but various parts of
Tkinter (e.g. tkFileDialog) are obviously not compatible with Tile
(try an 'Open' dialog). Tile is incompatible with options like
-background.  Plot group panels won't open as someone somewhere passes
some -background options. Is it possible some bwidgets are not
possible with Tile, too? In the Tk world, I think bwidget and Tile are
very popular, so there should be some information.

<P> Pmw is definitely not compatible with Tile. Pmw.Balloon and
Pmw.MessageBar are fine since they happen not to interact, but we
can't use Pmw.OptionMenu and Pmw.Group (among others).

<P> Tile is already in Tk8.5a6, so it'll come into Tkinter eventually
anyway.

<P>
Tile: http://wiki.tcl.tk/11075 <BR>
Migrate to Tile: http://wiki.tcl.tk/15443 <BR>
Apps using Tile: http://wiki.tcl.tk/13636 <BR>
Tile into tk core: http://www.nabble.com/Tile-merged-into-the-core-t2549979.html<BR>
bwidget: http://tkinter.unpy.net/bwidget/


<H4>2007/07/24 (JB): Matlab Toolbox for Dimensionality Reduction</H4>

Consider interfacing to this toolbox, which contains Matlab
implementations of twenty techniques for dimensionality reduction. A
number of these implementations were developed from scratch, whereas
other implementations are based on software that is already available
on the Web.  http://www.cs.unimaas.nl/l.vandermaaten/dr


<H4>2007/07/24 (JB): Digital Embryo Workshop</H4>

Consider interfacing to this toolbox, which is handy for generating
novel 3D objects, e.g. to use as training stimuli (perhaps for
somatosensory simulations?).
http://www.psych.ndsu.nodak.edu/brady/downloads.html


<!-- NOTES NEEDING TO BE TURNED INTO TASKS 


Any idea what this does?
alterdot()
numpy.alterdot(...)
alterdot() changes all dot functions to use blas.

_________________________________________________________


|            if output_fn is not IdentityOF: # Optimization (but may not actually help)
|  !             output_fn(result)           # CEBHACKALERT: particularly since everything but
|  !                                         # the IdentityOF *class* will pass this if-test!
|  !         return result                   # Should be: "if not instance(output_fn,IdentityOF):".
|  !                                         # I guess this needs fixing in several places.

I think the "optimization" should just be removed
everywhere.  It would be good to test the speed first, but if that's
too much trouble, just removing it is fine.


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


Has anyone looked at the (new to python 2.4) decimal module? 
http://docs.python.org/lib/module-decimal.html


_________________________________________________________


(CB) embed matplotlib windows / "histograms" conversation


_________________________________________________________


(CB) add note for developers: always specify GMT in cvs date commands
when doing any kind of search through cvs history. your timezone might
be different (e.g. BST or china time...) 

_________________________________________________________


Start to use doctest. Unit tests need to be sorted out: reset state
between tests (e.g. by saving/restoring class attributes)?

_________________________________________________________

Some useful links:
http://scipy.org/Tentative_NumPy_Tutorial
http://scipy.org/NumPy_for_Matlab_Users



_________________________________________________________



-->

