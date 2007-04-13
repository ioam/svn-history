<!--CB: going to go through this file and: 
- order tasks by priority
- check all my tasks from emails are here
-->

<p>
This is the developers' to-do list. It's divided into several
sections, with earlier sections being higher priority than later ones.
Tasks within each section are also ordered approximately by priority.

<li><em>Tasks to be addressed for the upcoming n release</em><br />
What the developers are working on most actively right now.
</li>

<li><em>Tasks to be addressed for the upcoming n+1 release or later</em><br />
Tasks that the developers hope to be able to start on after finishing
their work for the current upcoming release.
</li>

<li><em>Things we hope to take care of eventually</em><br />
Tasks of lower priority; if you would like to see one of these tasks
completed any time soon, please volunteer (even if a developer is
already assigned)! 
</li>

<li><em>Ongoing work </em><br />
Long-term tasks that are underway, and tasks that the developers might
currently be investigating: work with uncertain finishing times.
</li>
</p>

<p>
By each task, initials in parentheses typically indicate the main
person working on an item, but others may also be involved.  Items
with no initials are not (yet) assigned to a specific developer (so
please feel free to volunteer!!!!). Dates indicate the item was first
added to the list, or a change was made.
</p>

<H2>Tasks to be addressed for the upcoming 0.9.3 release:</H2>

<pre>
2007/02/20 (JB): Errata before release
- update Changelog.txt, summarize major changes in it for the release
notes
- make a pass through the documentation to fix anything that is not up
to date (especially things related to Numpy support and to describe
new features)
- build on the various platforms, etc.


2007/03/28 (?): Update tutorial
Update the lissom_oo_or tutorial page to match changes in the GUI and
elsewhere.  E.g. we can mention the right-click menus, how to use the
dynamic info to see the coordinate systems and numeric values, how to
start and stop training, and add sections about plotting 'Orientation
tuning fullfield' tuning curves and FFTs.


2007/03/28 (JB): Using new SOM support
Finish converting som_retinotopy.ty and obermayer_pnas90.ty to use the
new simpler and faster SOM support as in cfsom_or.ty, and delete all
of the old SOM support.  Requires checking that the som_retinotopy.ty
tutorial still works ok after the conversion.  Also check that
the examples handle exponential decay of parameter values, so that
they are good starting points.


2007/02/20 (JB): Upgrade epydoc 
Update to the current SVN version to incorporate recent changes and
bugfixes for the Reference Manual.


2007/04/10: update weave
Update scipy (weave) so that the numpy test deprecation warnings go away.


2007/03/02 (CB): update topographica-win
Test that results from Windows version match those from the standard
one. 


2007/04/05 (CB): examples/Makefile -> python
Migrate examples/Makefile to python script. Then, Windows users
can follow the tutorial instructions. 


2007/04/04 (CB): Dynamic text
Projection activity window gives some error around edges of plot.


2007/04/12 (CB): Rename autosizemask
And change comment about being temporary.


2007/04/12 (CB): Update mlabwrap
  

2007/03/28 (?): Figure out where to put this info in the docs:
<blockquote>
If you often need to change the parameters for map or curve measurement,
then you can do that easily without modifying your copy of
Topographica by putting the following lines into the .ty file to which
they apply:

<blockquote>
  from topo.plotting.templates import plotgroup_templates
  plotgroup_templates["Orientation Preference"].command="measure_or_pref(scale=0.75,offset=0.5,display=False,pattern_presenter=PatternPresenter(pattern_generator=SineGrating(),apply_output_fn=True,duration=0.225))"
</blockquote>

<P>Of course, the specific parameters here can be anything you want, and
you can do it for any plot.

<P>You can also put these lines into $HOME/.topographicarc, if you find
that you always want different defaults than Topographica's, for all
scripts that you look at...
</blockquote>
       
We also need to document .topographicarc somewhere.
</pre>


<H2>Tasks to be addressed for the 0.9.4 or later releases:</H2>

<pre>
2007/04/10 (JB): Add an example that is a good starting point for
wrapping an external simulation as a Sheet in Topographica.  A
first pass wrapping a spiking retina simulation written in PyNN/PyNEST
was done at the FACETS CodeJam in March 2007, but a cleaner example
can be made.


2007/04/05 (CB): scrollbars on plotgrouppanel windows
Add scrollbars when not auto-resizing (and ideally even when
auto-resizing but the window would otherwise be larger than the
screen).
Currently disabled, since they seem to have strange behavior.
Consider not using Pmw's scrolledframe component.


2006/03/26 (CB): scheduled_actions in lissom examples
Insert missing actions in case someone tries higher densities.


2007/01/25 (CB): ParametersFrame ok/apply/reset/cancel
Set order and names of ParametersFrame's Ok, Apply, Cancel, Reset, and
Defaults buttons, and make them behave as expected for classes and
instances.  Figure out and clean up translator_dictionary & its uses.


2007/03/26 (CB): minor tkgui cleanup
- Simplify tkgui, eliminating extra frames and any unnecessary
refresh() etc methods. At the moment, the complexity makes it 
difficult to add new features to the GUI and to correct problems.
- Collect my notes together (from __init__ and topoconsole).  Decide
what to do about them, and then start doing them.
- Which widgets should expand (expand=YES ?), which should fill the
space (fill=X ?) (e.g. in parameters frames sliders etc should
expand).


2007/04/13 (CB): make compare tests
Checkin some data for the make compare_or test.


2007/03/29 (CB): Makefiles to python scripts
Control tests from a python file rather than the Makefile.  Can then include
more tests of examples, by specifying sheet to look at etc.  And importantly,
can easily run tests on Windows version.


2007/03/26 (CB): Support for optimization  
Do we need our own simple timing functions to make it easier for users
to optimize their components (as opposed to the overall Topographica
framework, for which the current profile() commands are appropriate)?
A facility for reporting the approximate time spent in methods of each
EventProcessor?  In any case, provide more guide for the user for
doing optimization, focusing on the components we expect to be the
bottlenecks. Add general advice for optimization to the manual pages.


2007/03/26 (CB): developer page about efficient array computations.
Measurement of numpy.sum(X)/X.sum()/sum(X) performance. Difference
between simulation results on different platforms (for slow-tests in
Makefile).


2007/03/27 (CB): abstract classes
given how private attributes work in Python, it seems like we can just
have a parameter __abstract_class=True for abstract classes, and then
__is_abstract can check to see if there is such an attribute (and that
it is True, just in case).


2007/03/29 (CB): connectionfield/slice/sheetcoords
HACKALERTs relating to connection fields; test file for
connectionfield; cleaning up cf.py and projections/basic.py along with
the Slice class and SheetCoordinateSystem (there are several
simplifications that can be made).  Maybe we can use masked arrays,
now that Numpy has support for several varieties that might meet our
needs better than Numeric's did.


2006/12/14 (JB): Documentation for the new Numeric 
It's not free. But we could document differences from the current
Numeric documentation for our users, as we find these differences.


2006/11/09 (CP): Add automatic assignment of topo.sim.name
Take the base name of the first .ty file in sys.argv (if any).  Also
should clean up how the window titles are initialized, so that it is
done after a .ty script is loaded (whether on the initial command line
or from the GUI).  (Right now the name is updated only when a window
is first opened, or when learning is done in the topoconsole.)


2006/07/07 (CP): Fix normalization to allow negative weights.  
Also consider adding other normalization options, including joint
normalization across all plots with the same name.


2006/11/09 (JL): better saving during batch runs
Support better saving of results during long batch runs
(e.g. orientation maps and other plots).


2006/11/09 (CP/JL): Add support for measuring receptive fields
Perhaps use STRFPAK or a similar approach.


2006/11/09 (CP?): plot outstar connections
Add support for plotting outstar connections, i.e. outgoing
ConnectionFields.


2006/11/09 (RZ): map statistics
Add support for automatic generation of reports with statistics about
maps, e.g. for estimating perceived quantities.


2006/11/09 (JA): optimizations from c++
Need to implement more of the optimizations from the C++ LISSOM code.


2006/05/24 (JB): Problems with examples/joublin_bc96.ty
Strange Projection plots.
</pre>


<H2>Things we hope to take care of eventually</H2>

<pre>
2007/03/29 (CB): tidy up c++ lissom matching
Set c++ lissom params so that topographica doesn't have to set ganglia
weight mask specially. Generalize oo_or_map_topo.params.


2007/03/26 (CB): right-click menus
Tidy code, then make it possible to add things to the menu without
changing the tkgui files, like the templates work for activity plots.


2007/03/26 (CB): PatternGeneratorParameter default value
Investigate why this:
"
from topo.base.patterngenerator import PatternGeneratorParameter
PatternGeneratorParameter.default=topo.patterns.basic.Line()
"
gives errors about being read only sometimes. (Try at 
the commandline, from a script, and saving/loading snapshots.)


2007/02/28 (CB): OneDPowerSpectrum & Audio PatternGenerators
Finish the two classes. Make a demo with Audio Currently don't work
with test pattern window because plotting expects 2d arrays.


2007/03/30 (CB): PatternGenerator, PatternGenerator2D
Have a second abstract class so that the base PatternGenerator is
simpler.


2007/03/26: wrap MDP
Add a wrapper around the Modular Data Processing (MDP) toolkit
(http://mdp-toolkit.sourceforge.net) to provide easy access to the
PCA, ICA, SFA, ISFA, etc. algorithms.


2007/02/23: which version of libraries is numpy using?
- numpy.__config__.show()
- warn users if they're using a slow version?
- http://www.scipy.org/Numpy_Example_List?highlight=%28example%29#head-c7a573f030ff7cbaea62baf219599b3976136bac
>>>
>>> import numpy
>>> if id(dot) == id(numpy.core.multiarray.dot):           # A way to know if you use fast blas/lapack or not.
...   print "Not using blas/lapack!"


2006/02/04 (JAB): tune non-inline-optimtized components
Should work through some of the most commonly used
non-inline-optimized components to see if the implementation can be
tuned slightly for better performance.  For instance, numpy.dot()
appears to be much faster than the current sum(x*y) implementation of
DotProduct:

Topographica_t0> import time,numpy,Numeric
Topographica_t0> def runtime(code): start = time.time() ; z = eval(code) ; end = time.time() ; print z, end-start
... 
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

After this, it would be interesting to get some hard numbers about how
much faster the inline-optimized components are than those using numpy
primitives.


2006/11/09 (JA?): overhaul tkgui
Need to do a general overhaul of the GUI; it needs to be clean and
well designed so that it can be flexible. Before any such overall,
review the available graphics toolkits (e.g. wxpython vs tkinter).


2006/11/09 (JL?): parameter spaces
Add better support for exploring and optimizing parameter spaces.


2006/12/21: lock to real time?
Could add an option to lock Topographica to real time, so that once
processing is done at a particular virtual time, it waits until the
next real time before moving to the next event (which may be different
due to real-time input arriving by then).  On the other hand, maybe
this isn't necessary?  E.g. everything could be driven from a
PatternGenerator that produces a new pattern whenever some real-world
input arrives, and then the rest of the processing can be triggered
from that, as fast as it can compute.  Worth thinking about, e.g. to
handle simple webcam input.


2006/06/03: zero-sized CFs
Allow min_matrix_radius to be set to zero, and then say that if no
unit ends up in the CF, then there will be no CF for that unit.  But
that's going to make the rest of the code hard to write, because we'll
either have to deal with CFs with empty matrices, or deal with CFs
missing altogether.  (As an example, the problem of zero-sized CFs
arises in examples/joublin_bc96.ty.)  Maybe it would be simplest to
use a non-zero CF size, but with a mask making no unit visible; not
sure.


2006/05/19: pychecker
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


2006/06/19 (JB): Number, DynamicNumber
- Need to replace the current implementation with one where Number has a
'dynamic' slot that can be turned on or off, so that any Number could
be dynamic.  Includes making sure something sensible happens in model
editor, and (eventually) making it possible to set their values and
(hopefully) change any Number to be dynamic.
- Need to make sure DynamicNumbers are advanced only once per simulation time.


2006/05/15: array type
All arrays should be numpy.float32


2006/05/15: name should be constant
Objects in the simulation are indexed by name, so name needs to be a
constant Parameter (which <i>might</i> cause some other problems).
There are some related hacks in ParametersFrame that would also need
to be cleaned up.


2006/04/20: unit tests
Need to be cleaned up so they run correctly. For example, many of the
tests in testsheet.py run twice - correct that.  See CEBALERT in
topo/tests/testsheet.py.


2006/04/20 (JB): Composite & Image test files.
Complete test file for Composite and Image.  investigate failing test
in testimage.py (that uses sheet functions).  Currently commented out;
may not be a problem.


2006/02/24: SheetSelectorParameter etc 
So that the GUI (model editor) can display list of sheet classes etc
from a Parameter.


2006/02/24 (JB): ClassSelectorParameter
find_classes_in_package() will become a method of ClassSelectorParameter. 


2006/02/21: ReadOnlyParameter
To allow declaration of something but not let it be set anywhere else,
even in a ParameterizedObject constructor.


2006/02/21 (JB): Parameters: remove 'hidden' attribute
Instead use (e.g. negative) precendence.


2006/02/21 (JB): PatternGenerator parameters
Have size and aspect_ratio Parameters in PatternGenerator so that
subclasses can inherit doc, precedence attributes (etc), but have them
not used unless a subclass does really use them.  It might be better
just to create an abstract PatternGenerator class for grouping
together all patterns using those parameters, which shouldn't be too
hard.


2006/03/07 (JL): change_bounds()
make change_bounds() able to enlarge as well as shrink 


2006/06/19: things not to pickle
e.g. Filename's search_paths attribute shouldn't be pickled.
Presumably there will be other such items, so should objects have a
standard attribute/parameter that lists attributes not to pickle? Or
something like that.  Otherwise, save_snapshot and load_snapshot could
specifically avoid items.


2005/01/01: unit test results on the web
Could add a web site with results of unit tests, updated nightly


2005/01/01: components from external packages 
Could consider using or taking components from: SciPy,
ScientificPython, Chaco, Pyro (the robotics package), g, logger
(instead of our custom messaging functions).


2005/01/01: noise
Should add support for additive or multiplicative noise, with many
possible places it could be added.


2005/01/01: grouping sheets for plotting
Add a mechanism to group Sheets into a logical unit for plotting,
analysis, etc.  For instance, it should be possible to group three
R,G,B sheets into one eye, two ON and OFF sheets into one LGN area,
and several V1 layers into one stack.  Such grouping should support
e.g. presenting a color bitmap to an Eye instead of to R, G, and B
separately, plotting the resulting activation from the three areas in
true color, combining ON and OFF plots into one bitmap (by
subtraction), and measuring a vertically summed orientation map for a
model using several layers.


2005/01/01: porting other simulations from c++ lissom
Finish porting all categories of simulations from parts II and III of
the LISSOM book (i.e. orientation maps, ocular dominance maps,
direction maps, combined maps, face maps, and two-level maps) to
Topographica.
</pre>




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





<H2>Ongoing work</H2>

<pre>
2006/04/10 (CB): optional external packages on platforms other than linux
Optional packages (e.g. mlabwrap, pyaudio) on Windows and OS X.


2006/02/23 (all): Making more things be Parameters
And writing doc strings at the same time. E.g. the x and y widgets in
the Unit Weights window can be Numbers with bounds, etc.


2006/02/23 (all): ensuring classes are declared abstract if they are abstract
Plus making sure base and simple classes are imported into packages
(i.e. Sheet into topo/sheets/, Projection into topo/projections/,
Constant into topo/patterns/, and so on).


2006/02/21: read-only objects
Might someday be interesting to have read-only objects, aiming at
copy-on-write semantics, but this seems quite difficult to achieve in
Python.


2006/02/21 (all): documentation, unit tests
Improving both, plus eliminating ALERTs.


2007/03/26 (CB): Build topographica on windows 
With free compiler (python for windows is built with a Microsoft
compiler). Maybe use pymingw? Or cygwin? Currently trying cygwin, with
some success.

			     
2007/03/14 (CB): gnosis.xml.pickle 
Needs to be updated for numpy. I'm working with module's author at the
moment.


2007/03/14 (CB): building scipy
how to build scipy without requiring any of the external linear
algebra libraries, etc? Then scipy would at least build easily, and
users could install the optimized versions if they wished.
Investigate garnumpy.


2007/02/26: Consider moving to IPython
Would get command-prompt completion in the local namespace, debugging
in the namespace of the exception, with easier to follow tracebacks,
persistent command histories, easy interaction with the system shell
(using ! to get a shell and $ to feed it Python variables), and
session logging.


2007/02/21 (CB): Investigate using Tile 
Tile has become part of Tkinter now anyway.  Tile looks good on linux
and windows (haven't tried mac but screenshots look good). But, Tile
does not have all the widgets we need yet. Tile uses themes so we can
set it to classic and use Tile + Tkinter widgets and still have a
uniform look. This gives us nothing to begin with, but Tile should
eventually have all the widgets of Tkinter, at which point we can
simply set the theme to get a Topographica which looks 'right' on
windows and mac. Well, that is almost true. Pmw (which is not
compatible with Tile because of Tile's theme-based approach) provides
some things we really need. The first of these is balloon help. In
fact, that is ok to mix with other widgets; it doesn't need to match
the 'theme' since it's undecorated by the window manager.  The second
is the menubar, which could be replicated in Tkinter easily - except
that it doesn't seem to be possible to bind popup help to individual
menu items...a really useful feature.  [Add note about the others:
messagebar, combobox, radiobutton, etc.]
</pre>
