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


<!-- ### These tasks before the next release (i.e. 2006/05/08) ### -->

<li>
2006/05/16 (CB): Problem with SharedWeightCFProjection vs CFProjection.
</li>

<li>
2006/05/15 (CB): Missing scheduled_actions in lissom examples [** before release]
</li>

<li> 
2006/05/02 (CB): Update documentation in general [** before release]
</li>

<li>
2006/04/24 (CB): Update tutorials now that scripts don't need to be run before loading a snapshot. [** before release]
</li>


<!-- ### end of 'before release' ### -->


<li>
2006/05/15 (CB): Matching lissom_oo_or with C++ lissom. 
</li>

<li>
2006/04/07: (CB) Allowing joint normalization of projections for a CFSheet. [This appears to work, but results from LISSOM simulations do not yet match those of C++ LISSOM.]
</li>

<li> 
2006/02/23 (all): Ensuring classes are declared abstract when they should be, and making sure base and simple classes are imported into packages (i.e. Sheet into topo/sheets/, Projection into topo/projections/, Constant into topo/patterns/, and so on).
</li>

<li>
2006/02/23 (all): Making more things be Parameters, and writing doc strings at the same time. E.g. the x and y widgets in the Unit Weights window can be Numbers with bounds, etc.
</li>

</ul>


<h3>Tasks to be carried out next</h3>

Tasks which the developers are about to start.

<ul>

<li>
2006/05/17 (CB): Number, DynamicNumber: allowing an attribute that has
been declared as a Number to work with something that produces a
number (i.e. do it properly - because it does work at the
moment). Includes making sure something sensible happens in model
editor, and that printing dynamic parameters doesn't cause them
to generate a new value.
</li>

<li>
2006/05/15: All arrays should be Numeric.Float32
</li>

<li>
2006/05/17: Windows-specific files to new module in CVS.
</li>

<li>
2006/05/17 (CB): Script to create Windows python/topographica installation, for generating python_topo directory.
</li>

<li>
2006/05/02 (CB): HACKALERTs relating to connection fields; test file for connectionfield.
</li>

<li>
2006/04/27 (CB): Allowing there to be a slower, more in-depth set of tests (that don't run with make tests, etc). Slower tests that are required: pickling, that example networks' results haven't changed, that performance doesn't get worse
</li>

<li>
2006/05/15: Objects in the simulation are indexed by name, so name needs to be a constant Parameter. There is probably an easy way to allow renaming, though. Hacks in ParametersFrame.
</li>

<li> 
2006/05/04: Tidy model editor's handling of sheet and projection class parameeters (why does the parametersframe have to be in a separate window for the widgets to work properly)?
</li>


<li>
2006/04/07: (CB) Implement joint normalization via ports - check ports work as expected.
</li>

<li> 
2006/05/02 (CB): Finish Slice and SheetCoordinateSystem classes.
</li>

<li> 
2006/03/17 (CB): Fix problem (matching previous work) with som_retinotopy.
</li>

<li> 
2006/04/20 (CB): many of the tests in testsheet.py run twice - correct that.
</li>

<li>
2006/04/20 (CB): write test file for Composite and complete Image's test file.
</li>

<li>
2006/02/24 (CB): SheetSelectorParameter etc (so that the GUI (model editor) can
display list of sheets etc from a Parameter. find_classes_in_package() will
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
2006/04/30: What's this? 
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
2006/02/21: Remove Parameter's hidden attribute, and instead use (e.g. negative) precendence.
</li>

<li>
2006/02/21: Have size, aspect_ratio (etc) Parameters in
PatternGenerator so that subclasses can inherit doc, precedence
attributes (etc), but have them not used unless a subclass does really
use them.
</li>

<li> 
2006/05/02 (CB): investigate failing test in testimage.py (that uses sheet functions).
</li>

<li>
2006/05/04 (CB): ParametersFrame needs to be tidied up!
</li>

<li> 
2006/03/03: delete objects from simulator; setup GUI to use this.
</li>

<li> 
2006/03/07 (CB): (Windows) Script to generate the python_topo directory.
</li>

<li>
2006/03/07: make change_bounds() able to enlarge as well as shrink [made a first draft, JL is working with it]
</li>

</ul>


<h3>Other work</h3>

Ongoing work with uncertain finishing times.

<ul>
<li>
2006/02/21 (CB): Read-only objects, aiming at copy-on-write semantics
</li>

<li>
2006/05/01: Pickle e.g. classes that were defined in scripts? At the moment
a warning is printed for such classes and functions (including lambda functions).
</li>

<li>
2006/02/21 (all): Improving documentation and test files; eliminating ALERTs.
</li>

<li>
2006/03/07: (Windows) Build python on windows with free compiler. Maybe use pymingw?
</li>

</ul>
