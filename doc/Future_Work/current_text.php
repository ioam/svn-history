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

<li>
2006/04/07: (CB) Allowing joint normalization of projections for a CFSheet. [This appears to work, but results from LISSOM simulations do not yet match those of C++ LISSOM.].
</li>

<li>
2006/04/07: (CB) Implement joint normalization via ports - check ports work as expected.
</li>

<li>
2006/04/12: (CB) Finish reorganizing response functions and CFProjection response functions; rename CFProjectionGenericOutputFn to GenericCFPOutputFn, etc.; rename connectionfield.py to cf.py; rename Identity to IdentityOutputFn; create Identity learning function; create topo/base/functionfamilies.py and move LearningFns etc into it; rename SharedCFProjection SharedWeightCFProjection  
</li>

<li> 
2006/03/17 (CB): Fix problem (matching previous work) with som_retinotopy.
</li>

<li> 
2006/04/12 (CB): Remove xdensity and ydensity now density in each dimension is equal for a sheet; slice class; investigate failing test in testimage.py (that uses sheet functions).
</li>

<li>
2006/04/07 (CB): HACKALERTs relating to connection fields; matching with C++ LISSOM when there are circular connection fields; test file for connectionfield.
</li>

<li>
2006/04/12 (CB): Uncomment new Composite class and remove the old one; write test file for Composite and complete Image's test file.
</li>

<li>
2006/04/08: (CB) Implement scheduled actions as strings exec'd in main [it worked a long time ago, it just needs to be implemented on a current copy!]
</li>

<li>
2006/04/08 (CB): A better way to implement the Wrapper class(es); change all examplesand tests so they set input parameters on an object rather than the class (using Wrapper) 
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
2006/04/08 (CB): Update tutorials now that scripts don't need to be run before loading a snapshot.
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
