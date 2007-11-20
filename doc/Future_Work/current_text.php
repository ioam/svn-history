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

<!-- <H2>Tasks to be addressed before the next release (0.9.5 or 1.0) :</H2> -->

<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->

<H2>Tasks to be addressed after the 0.9.4 release:</H2>


<H4>2007/10/03 (CB): Urgent tkgui + plotgroup cleanup</H4>
<ul>
<li>Cleanup + doc of tkparameterizedobject.py and parametersframe.py</li>
<li>Cleanup + doc of *panel.py files</li>
<li>Cleanup + doc of plotgroup.py</li>
</ul>

<H4>2007/09/20: copying plotgroup from plotgroups</H4>
See ALERT next to plotgroups in plotgroup.py.

<H4>2007/09/01: timing code </H4>
The timing object is nearly done, allowing progress bars, time
remaining estimates, etc., but Jim needs to look at it to finish it up
(and then close tracker 1432101).

<H4>2007/10/26: Update tutorial</H4>
Update the lissom_oo_or tutorial page to include fresh figures; some
are a bit out of date.  Add a section about plotting 'Orientation
tuning fullfield' tuning curves.  CB: would the tutorial benefit from
being split up a little more?  Maybe it's getting daunting?


<H4>2007/10/08 (CB): test topographica-win</H4>
Test that results from Windows version match those from the standard
one. The unit tests and the "make compare_oo_or" test are fine, but I
can't run the other, smaller tests of all the networks because the
checked in _DATA files don't seem to work on Windows. I get
"ImportError: no module named fixedpoint" during unpickling. Importing
fixedpoint works in Windows, and I can see it there in
site-packages. So there's some confusion somewhere, and it could be
difficult to solve. I have no idea whatever about this problem.


<H4>2007/10/03 (CB): Less-urgent tkgui cleanup</H4>
<ul>
<li>Control which options are available on right-click menu.
The menus need to be dynamic, adapting to whatever channels are
present, rather than always assuming that plots are SHC plots.</li>
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


<H4>2007/03/29 (CB): connectionfield/slice/sheetcoords</H4>
HACKALERTs relating to connection fields; test file for
connectionfield; cleaning up cf.py and projections/basic.py along with
the Slice class and SheetCoordinateSystem (there are several
simplifications that can be made).  Maybe we can use masked arrays,
now that Numpy has support for several varieties that might meet our
needs better than Numeric's did.

<H4>2007/07/07: more tests </H4>
We need a test with non-square input sheets, non-square LISSOM sheets, etc., 
with both types of non-squareness...and we also need to test whatever
map measurement that we can (e.g. or maps).

<H4>2007/02/26: Move to IPython</H4>
Would get command-prompt completion in the local namespace, debugging
in the namespace of the exception, with easier to follow tracebacks,
persistent command histories, easy interaction with the system shell
(using ! to get a shell and $ to feed it Python variables), and
session logging.  Combined with ipython.el, Emacs users will then
be able to see the line of the source code where the error or
breakpoint occurred.  Also consider an alternative debugger,
http://www.digitalpeers.com/pythondebugger/.


<H4>2007/11/20: output from pychecker in topo.base</H4>

topo/base/cf.py:30: (abs) shadows builtin
topo/base/parameterclasses.py:702: (max) shadows builtin
topo/base/parameterclasses.py:702: (min) shadows builtin
topo/base/arrayutils.py:136: (range) shadows builtin
topo/base/arrayutils.py:10: (sum) shadows builtin
topo/base/simulation.py:1053: (vars) shadows builtin
topo/base/simulation.py:1068: (vars) shadows builtin


topo/base/parameterizedobject.py:306: __delete__ is not a special method
topo/base/parameterclasses.py:110: __get__ is not a special method
topo/base/parameterclasses.py:394: __get__ is not a special method
topo/base/parameterclasses.py:449: __get__ is not a special method
topo/base/parameterclasses.py:522: __get__ is not a special method
topo/base/parameterizedobject.py:259: __get__ is not a special method
topo/base/boundingregion.py:182: __set__ is not a special method
topo/base/boundingregion.py:415: __set__ is not a special method
topo/base/parameterclasses.py:138: __set__ is not a special method
topo/base/parameterclasses.py:246: __set__ is not a special method
topo/base/parameterclasses.py:272: __set__ is not a special method
topo/base/parameterclasses.py:290: __set__ is not a special method
topo/base/parameterclasses.py:326: __set__ is not a special method
topo/base/parameterclasses.py:354: __set__ is not a special method
topo/base/parameterclasses.py:45: __set__ is not a special method
topo/base/parameterclasses.py:531: __set__ is not a special method
topo/base/parameterclasses.py:634: __set__ is not a special method
topo/base/parameterclasses.py:684: __set__ is not a special method
topo/base/parameterizedobject.py:277: __set__ is not a special method
topo/base/simulation.py:371: __set__ is not a special method


topo/base/boundingregion.py:179: __slots__ are empty in Cartesian2DPoint
topo/base/boundingregion.py:409: __slots__ are empty in BoundingRegionParameter
topo/base/cf.py:386: __slots__ are empty in CFPResponseFnParameter
topo/base/cf.py:440: __slots__ are empty in CFPLearningFnParameter
topo/base/cf.py:529: __slots__ are empty in CFPOutputFnParameter

topo/base/boundingregion.py:388: Function (__init__) doesn't support **kwArgs

topo/base/arrayutils.py:14: Function (set_printoptions) uses named arguments
topo/base/boundingregion.py:217: Function (__init__) uses named arguments
topo/base/cf.py:369: Function (__init__) uses named arguments
topo/base/cf.py:428: Function (__init__) uses named arguments
topo/base/cf.py:450: Function (__init__) uses named arguments
topo/base/cf.py:488: Function (__init__) uses named arguments
topo/base/cf.py:516: Function (__init__) uses named arguments
topo/base/cf.py:556: Function (__init__) uses named arguments
topo/base/cf.py:559: Function (__init__) uses named arguments
topo/base/cf.py:565: Function (__init__) uses named arguments
topo/base/cf.py:567: Function (__init__) uses named arguments
topo/base/cf.py:574: Function (__init__) uses named arguments
topo/base/cf.py:579: Function (__init__) uses named arguments
topo/base/cf.py:584: Function (__init__) uses named arguments
topo/base/cf.py:593: Function (__init__) uses named arguments
topo/base/cf.py:596: Function (__init__) uses named arguments
topo/base/cf.py:602: Function (__init__) uses named arguments
topo/base/cf.py:606: Function (__init__) uses named arguments
topo/base/cf.py:608: Function (__init__) uses named arguments
topo/base/cf.py:611: Function (__init__) uses named arguments
topo/base/cf.py:618: Function (__init__) uses named arguments
topo/base/cf.py:70: Function (__init__) uses named arguments
topo/base/cf.py:75: Function (__init__) uses named arguments
topo/base/parameterclasses.py:258: Function (__init__) uses named arguments
topo/base/parameterclasses.py:535: Function (attrib_name) uses named arguments
topo/base/parameterclasses.py:571: Function (__init__) uses named arguments
topo/base/parameterclasses.py:581: Function (attrib_name) uses named arguments
topo/base/parameterclasses.py:620: Function (__init__) uses named arguments
topo/base/parameterclasses.py:628: Function (attrib_name) uses named arguments
topo/base/parameterclasses.py:678: Function (__init__) uses named arguments
topo/base/parameterizedobject.py:1064: Function (get_PO_class_attributes) uses named arguments
topo/base/parameterizedobject.py:740: Function (get_param_values) uses named arguments
topo/base/projection.py:231: Function (send_output) uses named arguments
topo/base/simulation.py:1197: Function (__init__) uses named arguments



topo/base/cf.py:501: Local variable (norm_value) not used
topo/base/cf.py:676: Local variable (e) not used
topo/base/simulation.py:812: Local variable (remain) not used
topo/base/simulation.py:817: Local variable (starttime) not used


topo/base/boundingregion.py:412: Methods (rotate, scale) in BoundingBox need to be overridden in a subclass
topo/base/cf.py:567: Methods (rotate, scale) in BoundingBox need to be overridden in a subclass
topo/base/cf.py:572: Methods (function) in patterngenerator.Constant need to be overridden in a subclass
topo/base/cf.py:577: Methods (function) in patterngenerator.Constant need to be overridden in a subclass
topo/base/sheetcoords.py:206: Methods (rotate, scale) in BoundingBox need to be overridden in a subclass
topo/base/sheetcoords.py:373: Methods (rotate, scale) in BoundingBox need to be overridden in a subclass


topo/base/boundingregion.py:70: Modifying parameter (imports) with a default value may have unexpected consequences
topo/base/parameterizedobject.py:763: Modifying parameter (imports) with a default value may have unexpected consequences
topo/base/simulation.py:486: Modifying parameter (imports) with a default value may have unexpected consequences
topo/base/simulation.py:501: Modifying parameter (imports) with a default value may have unexpected consequences


topo/base/cf.py:41: Module member (from parameterclasses import BooleanParameter) re-imported


topo/base/parameterizedobject.py:887: Module (parameterclasses) imports itself


topo/base/parameterizedobject.py:460: No class attribute (_abstract_class_name) found


topo/base/cf.py:371: Overridden method (__call__) doesn't match signature in class (<class 'cf.CFPResponseFn'>)
topo/base/functionfamilies.py:59: Overridden method (__call__) doesn't match signature in class (<class 'functionfamilies.OutputFn'>)
topo/base/simulation.py:125: Overridden method (init) doesn't match signature in class (<class 'simulation.Singleton'>)


topo/base/boundingregion.py:66: Parameter (prefix) not used
topo/base/cf.py:451: Parameter (params) not used
topo/base/cf.py:490: Parameter (params) not used
topo/base/parameterclasses.py:394: Parameter (objtype) not used
topo/base/parameterclasses.py:449: Parameter (objtype) not used
topo/base/parameterizedobject.py:259: Parameter (objtype) not used
topo/base/parameterizedobject.py:681: Parameter (abstract_class) not used
topo/base/simulation.py:1308: Parameter (prefix) not used
topo/base/simulation.py:558: Parameter (sim) not used
topo/base/simulation.py:582: Parameter (imports) not used
topo/base/simulation.py:582: Parameter (prefix) not used
topo/base/simulation.py:590: Parameter (sim) not used
topo/base/simulation.py:657: Parameter (sim) not used


topo/base/parameterizedobject.py:540: Passing a constant string to setattr, consider direct reference


topo/base/cf.py:34: Using import and from ... import for (patterngenerator)


<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->
<!-- ------------------------------------------------------------------------ -->

<H2>Things we hope to take care of eventually</H2>

<H4>2006/11/09 (RZ): map statistics</H4>
Add support for automatic generation of reports with statistics about
maps, e.g. for estimating perceived quantities.

<H4>2006/11/09 (JA): optimizations from c++</H4>
Need to implement more of the optimizations from the C++ LISSOM code.

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


<H4>2007/03/30: PatternGenerator, PatternGenerator2D</H4>
Have a second abstract class so that the base PatternGenerator is
simpler.


<H4>2007/05/09: topoconsole workspace</H4>
Can we have a matlab-like workspace?


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

<H4>2006/04/10: optional external packages on platforms other than linux</H4>
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


<H4>2007/03/14: building scipy</H4>
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

> Second, is there any way to prevent obscure errors like this by
> checking to make sure that a Parameter is owned by a
> ParameterizedObject? I can't quite imagine how to do this, because
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

-->




