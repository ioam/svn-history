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
2006/02/28 (CB): Fix problem (matching previous work) with som_retinotopy.
</li>

<li> 
2006/02/21 (JC): Cleaning up ports.
</li>

<li>
2006/02/21: (JC) Splitting output functions from learning functions to learn and
apply_output_fn, to allow joint normalization across CFs.
</li>

<li>
2006/02/28 (CB): A better way to implement Wrapper class (and a better name for it); independent random streams (finalize RandomWrapper); a way to implement scheduled actions so that they will pickle (e.g. execute strings in __main__.__dict__) [not committed, but working - just needs cleaning]; document pickle and update documentation now it's changed (e.g. tutorials, don't need to load script first of all); change all examples so they set input parameters on an object rather than the class (using Wrapper); why RetinotopicSOM can't be found on unpickling. 
</li>

<li>
2006/02/28 (CB): SimSingleton class, allowing access to the simulator via topo.sim; provide easier access to objects in the simulator (something like topo.sim['V1']) [working, but not committed].
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
2006/02/28 (CB): Filename paths (for Filename Parameter and plot templates etc). Check on Windows.
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
2006/02/24 (CB): Slice class; HACKALERTs relating to Sheet, xdensity, ydensity (etc).
</li>

<li>
2006/02/23 (CB): Cleaning Composite and Image pattern generators.
</li>

<li>
2006/02/21: Renaming of *_py classes so that *_py ones have the original name
(they are the reference versions), and c (or otherwise optimized
versions) are suffixed _opt1, _opt2, etc., rather than with nothing or
_cpointer.
<br />
e.g. CFDotProduct_Py goes to CFDotProduct, CFDotProduct goes to 
CFDotProduct_opt1, CFDotProduct_cpointer goes to CFDotProduct_opt2
</li>

<li>
2006/02/21: ReadOnlyParameter to allow declaration of something but not let it
be set anywhere else, even in a ParameterizedObject constructor.
</li>

<li>
2006/02/21 (CB): HACKALERTs relating to connection fields; matching
with C++ LISSOM when there are circular connection fields.
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
2006/02/28: Verbose command line option. Check new command line things on Windows.
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
</ul>
