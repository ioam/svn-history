<h3>Current tasks</h3>

Tasks on which the developers are currently working. 
<br />

<small>
(Initials in parentheses typically indicate the main person working on
an item, but others may also be involved.  Items with no initials are
not (yet) assigned to a specific developer. Dates indicate the item
was first added to the list, or a change was made.)
</small>

<ul>

<!-- CB: I put my tasks in the approximate order that I'm doing them -->


<li>
2006/05/15: Missing scheduled_actions in lissom examples
</li>

<li>
2006/05/24 (JB): Problems with examples/joublin_bc96.ty: strange Projection
plots, errors for small radii (problem with the min_radius code)?
</li>


<li>
2006/05/15 (CB): Matching lissom_oo_or with C++ lissom. 
</li>

<li>
2006/05/23 (JB): tkgui making shell command prompt skip a line. If it doesn't prompt won't come back if information is printed.
</li>


<li>
2006/05/23 (JB): binding help balloon to the widget (already bound to the label) in parametersframe so that help can be seen for objects that are e.g. being selected.
</li>


<li>
2006/04/07: (CB) Allowing joint normalization of projections for a CFSheet. [This appears to work, but results from LISSOM simulations do not yet match those of C++ LISSOM.]
</li>

<li>
2006/05/19: CFPLF_Hebbian_opt or CFPOF_DivisiveNormalizeL1_opt (or both) cause
memory use to go up each call.  Also, CFPLF_Hebbian_opt does not seem to work
properly when used with CFPOF_DivisiveNormalizeL1.

</li>

</ul>


<h3>Tasks to be carried out next</h3>

Tasks which the developers are about to start.

<ul>

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
2006/05/17 (JB): Number, DynamicNumber: Need to replace the current
implementation with one where Number has a 'dynamic' slot that
can be turned on or off, so that any Number could be dynamic.
Includes making sure something sensible happens in model editor,
and (eventually) making it possible to set their values and
(hopefully) change any Number to be dynamic.
</li>

<li>
2006/05/15: All arrays should be Numeric.Float32
</li>

<li>
2006/05/17 (JB): Windows-specific files to new module in CVS.
</li>

<li>
2006/05/17 (CB): Script to create Windows python/topographica installation, for generating python_topo directory.
</li>

<li>
2006/05/22 (CB): Test file for connectionfield.
</li>

<li>
2006/05/22: HACKALERTs relating to connection fields; test file for connectionfield; cleaning up cf.py and projections/basic.py along with the Slice class (there are several simplifications that can be made).
</li>

<li>
2006/04/27 (JB): Allowing there to be a slower, more in-depth set of tests (that don't run with make tests, etc). Slower tests that are required: pickling, that example networks' results haven't changed, that performance doesn't get worse
</li>

<li>
2006/05/15: Objects in the simulation are indexed by name, so name needs to be a constant Parameter (which <i>might</i> cause some other problems).  There are some related hacks in ParametersFrame that would also need to be cleaned up.
</li>

<li> 
2006/05/04: Tidy model editor's handling of sheet and projection class parameeters (why does the parametersframe have to be in a separate window for the widgets to work properly)?
</li>

<li>
2006/04/07: (JB) Implement joint normalization via ports - check ports work as expected.
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
2006/04/20 (JB): write test file for Composite and complete Image's test file.
</li>

<li>
2006/02/24: SheetSelectorParameter etc (so that the GUI (model editor) can
display list of sheet classes etc from a Parameter).
</li>

<li>
2006/02/24 (JB): find_classes_in_package() will
become a method of ClassSelectorParameter. Then module as well as package list 
for ClassSelectorParameter. E.g. Want BoundingBoxParameter to be a 
ClassSelectorParameter, but don't want to add all of topo.base, just 
topo.base.boundingregion.
</li>

<li>
2006/04/28 (CB): Create subdirectory of tests called 'reference' and move into it the reference simulations plus all their data and other support files.
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
  File "/disk/data1/workspace/v1cball/t/topographica/topo/base/patterngenerator.py", line 207, in __init__
    super(PatternGeneratorParameter,self).__init__(PatternGenerator,default=default,suffix_to_lose='Generator',**params)
  File "/disk/data1/workspace/v1cball/t/topographica/topo/base/parameterclasses.py", line 508, in __init__
    Parameter.__init__(self,default=default,instantiate=instantiate,
  File "/disk/data1/workspace/v1cball/t/topographica/topo/base/parameterizedobject.py", line 241, in __init__
    self.default = default
AttributeError: 'PatternGeneratorParameter' object attribute 'default' is read-only
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
2006/05/04 (CB): ParametersFrame needs to be tidied up!
</li>

<li>
2006/03/07 (JL): make change_bounds() able to enlarge as well as shrink [made a first draft, JL is working with it]
</li>

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
