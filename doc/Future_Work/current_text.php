<h3>Current tasks</h3>

<p><small>
By each task, initials in parentheses typically indicate the main
person working on an item, but others may also be involved.  Items
with no initials are not (yet) assigned to a specific developer (so
please feel free to volunteer!!!!). Dates indicate the item was first
added to the list, or a change was made.
</small>

<h3>Tasks to be addressed for the 0.9.3 release:</h3>

<ul>

<li>
2006/12/14 (JB): Replace Numeric with NumPy, and upgrade MatPlotLib.
</li>

<li>
2006/11/09 (CP): Add automatic assignment of topo.sim.name, by taking
the base name of the first .ty file in sys.argv (if any).  Also should
clean up how the window titles are initialized, so that it is done
after a .ty script is loaded (whether on the initial command line or
from the GUI).  (Right now the name is updated only when a window is
first opened, or when learning is done in the topoconsole.)
</li>

<li>
2006/07/07 (CP): Fix normalization to allow negative weights.  Also
consider adding other normalization options, including joint
normalization across all plots with the same name.
</li>

<li>
2006/10/10 (JL): Add FFT plot using Jim's Octave code; shouldn't be
difficult.  Might not be that hard to port it to Python, either.
</li>

<li>
2006/11/09 (JL): Add plotting of tuning curves and contrast response functions
</li>

<li>
2006/11/09 (JL): Support better saving of results during long batch
runs (e.g. orientation maps and other plots).
</li>

<li>
2006/11/09 (CP/JL): Add support for measuring receptive fields,
perhaps using STRFPAK or a similar approach.
</li>

<li>
2006/11/09 (CP): Add numerical indication of size and brightness scales
to plots, to allow different Projections, etc. to be compared properly.
</li>

<li>
2006/11/09 (CP?): Add support for plotting outstar connections, i.e. outgoing
ConnectionFields.
</li>

<li>
2006/11/09 (RZ): Add support for automatic generation of reports with
statistics about maps, e.g. for estimating perceived quantities.
</li>

<li>
2006/11/09 (RZ): Add simple timing functions to suggest what components
need optimizing.
</li>

<li>
2006/11/09 (RZ): Need to implement more of the optimizations from the C++ LISSOM code.
</li>

<li>
2006/05/15 (JB): Missing scheduled_actions in lissom examples
</li>

<li>
2006/05/24 (JB): Problems with examples/joublin_bc96.ty: strange Projection
plots.
</li>


<li>
2006/11/23 (JB,CP): Matching lissom_oo_or with C++ lissom (do a 'make compare'
to see the current matching status).
</li>


<li>
2006/05/23 (JB): binding help balloon to the widget (already bound to
the label) in parametersframe so that help can be seen for objects
that are e.g. being selected.
</li>


</ul>


<h3>Things we hope to take care of eventually</h3>

<ul>

<li>
2006/11/09 (JA?): Need to do a general overhaul of the GUI; it needs to be clean 
and well designed so that it can be flexible.
</li>

<li>
2006/11/09 (JL?): Add better support for exploring and optimizing parameter spaces.
</li>

<li>
2006/11/23: ParametersFrame doesn't properly set object properties when 
right click is used (there's a more detailed explanation in parametersframe.py: see
comments by uses of 'translator_dictionary').
</li>

<li>
2006/06/03: Allow min_matrix_radius to be set to zero, and then say
that if no unit ends up in the CF, then there will be no CF for that
unit.  But that's going to make the rest of the code hard to write,
because we'll either have to deal with CFs with empty matrices, or
deal with CFs missing altogether.
(As an example, the problem of zero-sized CFs arises in examples/joublin_bc96.ty.)
</li>

<li>
2006/05/23: tkgui cleanup - what widgets should expand (expand=YES ?), which should fill the space (fill=X ?) (e.g. the command output box should expand when topoconsole does, and in parameters frames sliders etc should expand).
</li>

<li>
2006/05/19: look at the output from:
<code>bin/python lib/python2.4/site-packages/pychecker/checker.py topo/base/*.py</code>.
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
</li>


<li>
2006/06/19 (JB): Number, DynamicNumber: Need to replace the current
implementation with one where Number has a 'dynamic' slot that
can be turned on or off, so that any Number could be dynamic.
Includes making sure something sensible happens in model editor,
and (eventually) making it possible to set their values and
(hopefully) change any Number to be dynamic.
<br />
Need to make sure DynamicNumbers are advanced only once per simulation time.
</li>

<li>
2006/05/15: All arrays should be Numeric.Float32
</li>

<li>
2006/05/22: HACKALERTs relating to connection fields; test file for connectionfield; cleaning up cf.py and projections/basic.py (e.g. DummyCF) along with the Slice class (there are several simplifications that can be made).
</li>

<li>
2006/04/27 (JB): Allowing there to be a slower, more in-depth set of tests
(that don't run with make tests, etc). Required slower tests: pickling [testsnapshots.py], that
example networks' results haven't changed [testlissom_oo_or.py], that performance doesn't get worse, ...
</li>

<li>
2006/05/15: Objects in the simulation are indexed by name, so name needs to be a constant Parameter (which <i>might</i> cause some other problems).  There are some related hacks in ParametersFrame that would also need to be cleaned up.
</li>

<li> 
2006/05/04: Tidy model editor's handling of sheet and projection class parameters (why does the parametersframe have to be in a separate window for the widgets to work properly)?
</li>

<li> 
2006/05/02: Finish Slice and SheetCoordinateSystem classes (see ALERTs).
</li>

<li> 
2006/03/17 (JB): Fix problem (matching previous work) with som_retinotopy, at least for small densities.
</li>

<li> 
2006/04/20: many of the tests in testsheet.py run twice - correct that.  See CEBHACKALERT in topo/tests/testsheet.py.
</li>

<li>
2006/04/20 (JB): Complete test file for Composite and Image.
</li>

<li>
2006/02/24: SheetSelectorParameter etc (so that the GUI (model editor) can
display list of sheet classes etc from a Parameter).
</li>

<li>
2006/02/24 (JB): find_classes_in_package() will become a method of ClassSelectorParameter. 
</li>

<li>
2006/02/21: ReadOnlyParameter to allow declaration of something but not let it
be set anywhere else, even in a ParameterizedObject constructor.
</li>

<li>
2006/05/02: Upgrade Numeric? Maybe some of the current problems will be solved? In particular, savespace has been removed from Numeric now. Perhaps trying to deepcopy a ufunc no longer leads to an error? Documentation for the new Numeric is not free, though. But we could document differences from the current Numeric documentation for our users, as we find these differences.
</li>

<li>
2006/04/30: What does this error mean? 
<pre>
Topographica> p=PatternGeneratorParameter(default=Line())
Topographica> PatternGeneratorParameter.default=Constant()
Topographica> q=PatternGeneratorParameter(default=Line())
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "/home/v1cball/topographica/topo/base/patterngenerator.py", 
    line 207, in __init__
    super(PatternGeneratorParameter,self).__init__
         (PatternGenerator,default=default, suffix_to_lose='Generator',
	  **params)
  File "/home/v1cball/topographica/topo/base/parameterclasses.py", 
    line 508, in __init__
    Parameter.__init__(self,default=default,instantiate=instantiate,
  File "/home/v1cball/topographica/topo/base/parameterizedobject.py", 
    line 241, in __init__
    self.default = default
AttributeError: 'PatternGeneratorParameter' object attribute 'default' 
is read-only
Topographica> 
</pre>
</li>

<li>
2006/02/21 (JB): Remove Parameter's hidden attribute, and instead use (e.g. negative) precendence.
</li>

<li>
2006/02/21 (JB): Have size and aspect_ratio Parameters in
PatternGenerator so that subclasses can inherit doc, precedence
attributes (etc), but have them not used unless a subclass does really
use them.  It might be better just to create an abstract PatternGenerator
class for grouping together all patterns using those parameters, which shouldn't be too hard. 
</li>

<li> 
2006/05/02: investigate failing test in testimage.py (that uses sheet functions).
Currently commented out; may not be a problem.
</li>

<li>
2006/03/07 (JL): make change_bounds() able to enlarge as well as shrink [made a first draft, JL is working with it]
</li>

<li>
2006/06/13: Make command prompt more informative. Could be done by making a 
variable in topo.misc.commandline that contains something that can be evaluated 
to provide a string, which will then be used for the prompt.  That way the user 
can change that to be anything he likes, just as in C++ LISSOM (in which there 
is a variable called command_prompt_format whose default value is
<code>lissom.t${iteration}.p${presentation}.c${command_num_called}${current_param_set_path}></code>.<br />
In Python, there aren't any such string macros, but we could still
have a variable topo.misc.commandline.prompt that is expected to be
set to something callable in __main__, and whose value is evaluated
before each time the prompt is executed.
</li>

<li>
2006/06/19: e.g. Filename's search_paths attribute shouldn't be pickled.
Presumably there will be other such items, so should objects have a standard 
attribute/parameter that lists attributes not to pickle? Or something like that.
Otherwise, save_snapshot and load_snapshot could specifically avoid items.
</li>

<li>
2005/01/01: Should add simple timing functions -- what was the total
time to run?  What components are taking a long time to run?  Guide
the user for optimization, focusing on the components we expect to be
the bottlenecks.
</li>

<!--
<li>
2005/01/01: Could add a web site with results of unit tests, updated nightly
</li>
-->

<li>
2005/01/01: Could consider using or taking components from: SciPy,
ScientificPython, Chaco, Pyro (the robotics package), g, logger
(instead of our custom messaging functions).
</li>

<li>
2005/01/01: Should add support for additive or multiplicative noise, with
many possible places it could be added.
<!-- Also suggested by Geisler, 7/1/2005:
  Package as a Matlab toolbox to get the right people to use it?
  Package it as an easy-to-use out-of-the-box optical imaging simulator
    -- need to tell it what stimulus, what eccentricity, what cortical patch
  Be able to look at the effects of attention
  Add specific models for intrinsic or voltage-sensitive-dye imaging 
-->
</li>

<li>
2005/01/01: Add a mechanism to group Sheets into a logical unit for
plotting, analysis, etc.  For instance, it should be possible to group
three R,G,B sheets into one eye, two ON and OFF sheets into one LGN
area, and several V1 layers into one stack.  Such grouping should
support e.g. presenting a color bitmap to an Eye instead of to R, G,
and B separately, plotting the resulting activation from the three
areas in true color, combining ON and OFF plots into one bitmap (by
subtraction), and measuring a vertically summed orientation map for a
model using several layers.
</li>

<li>
2005/01/01: Finish porting all categories of simulations from parts II
and III of the LISSOM book (i.e. orientation maps, ocular dominance
maps, direction maps, combined maps, face maps, and two-level maps) to
Topographica.
</li>

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
   user-configurable units. I think that's is the only way to do things
   like this, because the simulator is not limited to vision only, and so
   the underlying units have to be very general.)

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

</ul>


<h3>Other work</h3>

Ongoing work with uncertain finishing times.

<ul>
<li>
2006/02/23 (all): Making more things be Parameters, and writing doc strings at the same time. E.g. the x and y widgets in the Unit Weights window can be Numbers with bounds, etc.
</li>

<li> 
2006/02/23 (all): Ensuring classes are declared abstract when they should be, and making sure base and simple classes are imported into packages (i.e. Sheet into topo/sheets/, Projection into topo/projections/, Constant into topo/patterns/, and so on).
</li>

<li>
2006/05/24 (JB): Add a facility for reporting the approximate time spent
in methods of each EventProcessor, to allow simple debugging without having
to use the profiler.  Or at least add the hotshot commands from lissom_or.ty
to a function that can be called easily, which wouldn't be very difficult.
</li>

<li>
2006/02/21: Might someday be interesting to have read-only objects,
aiming at copy-on-write semantics, but this seems quite difficult to
achieve in Python.
</li>

<li>
2006/02/21 (all): Improving documentation and test files; eliminating ALERTs.
</li>

<li>
2006/03/07: Build python on windows with free compiler. Maybe use pymingw?
</li>

</ul>
