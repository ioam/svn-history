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
2006/04/26 (CB): matching with C++ LISSOM when there are circular connection fields [seems to match, just have to check bounds changes etc and then after 20000 iterations]; HACKALERTs relating to connection fields; test file for connectionfield
</li>

<li>
2006/04/27 (CB): New CompositePatternGenerator does not work correctly (e.g. when used for weights) (this must affect Image too, since they both use the same code). [** before release - can always revert to previous version, which did work]
</li>


<li> 
2006/04/21 (CB): Finish Slice and CoordinateTransformer classes; update PatternSampler; investigate failing test in testimage.py (that uses sheet functions); did the performance change (e.g. lissom_oo_or)? [** before release]
</li>

<li> 
2006/04/24 (CB): Update user manuals regarding Sheet density [** before release]
</li>

<li>
2006/04/24: (CB) Switch all examples to use schedule_command(); delete schedule_action() and SAEvent. [** before release]
</li>

<li>
2006/04/26 (CB): A better way to implement the Wrapper class(es); change all examples and tests so they set input parameters on an object rather than the class (using Wrapper or RandomWrapper); pickling of random streams  [** before release (but not the reimplementation part)] 
</li>

<li>
2006/04/24 (CB): Update tutorials now that scripts don't need to be run before loading a snapshot. [** before release]
</li>

<li>
2006/04/07: (CB) Allowing joint normalization of projections for a CFSheet. [This appears to work, but results from LISSOM simulations do not yet match those of C++ LISSOM.]
</li>

<li>
2006/04/12: (CB) Finish reorganizing response functions and CFProjection response functions; rename CFProjectionGenericOutputFn to GenericCFPOutputFn, etc.; rename connectionfield.py to cf.py; rename Identity to IdentityOutputFn; create Identity learning function; create topo/base/functionfamilies.py and move LearningFns etc into it; rename SharedCFProjection SharedWeightCFProjection; make sure GUI lists are populated (and try to make that simpler). [** before release]
</li>

<li>
2006/04/07: (CB) Implement joint normalization via ports - check ports work as expected.
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
2006/03/17 (CB): Change current code over to use topo.sim['V1']-type
access to simulator, and finalize connect2 etc; then remove old
code. [hierarchical.ty example shows how the new way works.]
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
2006/04/27 (CB): Number, DynamicNumber: allowing an attribute that has been declared as a Number to work with something that produces a number (i.e. do it properly - because it does work at the moment).
</li>


<li>
2006/04/27 (CB): Allowing there to be a slower, more in-depth set of tests (that don't run with make tests, etc). Slower tests that are required: pickling, that example networks' results haven't changed,
</li>

<li>
2006/03/07 (CB): Why RetinotopicSOM can't be found on unpickling.
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
2006/02/21: ReadOnlyParameter to allow declaration of something but not let it
be set anywhere else, even in a ParameterizedObject constructor.
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
2006/02/21 (all): Improving documentation and test files; eliminating ALERTs.
</li>

<li>
2006/03/07: (Windows) Build python on windows with free compiler. Maybe use pymingw?
</li>

</ul>
