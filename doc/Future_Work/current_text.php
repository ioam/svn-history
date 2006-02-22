<h3>Current tasks</h3>

Tasks on which the developers are currently working. 
<br />
<small>(Although an item can have the initials of a developer, that doesn't mean others cannot be working on it too. Similarly, items with no initials are not being ignored. Dates indicate the item was first added to the list, or a change was made.)</small>

<ul>

<li> 
2006/02/21 (JC): Cleaning up ports
</li>

<li>
2006/02/21: Split output functions from learning functions to learn and
apply_output_fn, to allow joint normalization.
</li>

<li>
2006/02/21 (CB): Composite pattern generator
</li>

<li>
2006/02/21 (CB): Indication of whether or not a class is abstract, to prevent
instantiation and to hide from various lists.
</li>

</ul>

<h3>Tasks to be carried out next</h3>

Tasks which the developers are about to start.

<ul>
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
be set, including in a ParameterizedObject constructor.
</li>

<li>
2006/02/21: Clean up ClassSelectorParameter and subclasses.
</li>

<li> 
2006/02/21 (CB): HACKALERTs relating to Sheet, xdensity, ydensity (etc).
</li>

<li>
2006/02/21 (CB): HACKALERTs relating to connection fields; matching with c++ LISSOM when there are circular connection fields.
</li>

<li>
2006/02/21: Remove Parameter's hidden attribute, and instead use (e.g. negative) precendence.
</li>

<li>
2006/02/21: Have size, aspect_ratio (etc) Parameters in PatternGenerator so that subclasses can inherit doc, precedence attributes (etc), but have them not used unless a subclass does really use them.
</li>
</ul>


<h3>Other work</h3>

Ongoing work with uncertain finishing times.

<ul>
<li>
2006/02/21 (CB): Read-only objects, aiming at copy-on-write semantics
</li>

<li>
2006/02/21 (CB): pickling
</li>
</ul>
