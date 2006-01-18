<H1>Using consistent names</H1>

<P>Where there are already classes defined, please use the existing
names when writing new code, documentation, variable names, user
messages, window names, and comments.  (Or else change all of the old
ones to match your new version!)  For instance, Topographica is based
on Sheets, so everything should call a Sheet a Sheet, not a Region,
Area, or Layer.

<P>In particular, when writing user interface code, think about what
you are letting the user plot or manipulate, and ask whether that's
one of the concepts for which we have (laboriously!) worked out a
specific term. Examples of acceptable, well-defined terms:

<DL COMPACT>
<DT><CODE>Sheet</CODE>
<DT><CODE>Unit</CODE>
<DT><CODE>ConnectionField</CODE>
<DT><CODE>Projection</CODE>
<DT><CODE>ProjectionSheet</CODE>
<DT><CODE>CFSheet</CODE>
<DT><CODE>GeneratorSheet</CODE>
<DT><CODE>SheetView</CODE>
<DT><CODE>UnitView</CODE>
<DT><CODE>Event</CODE>
<DT><CODE>EventProcessor</CODE>
<DT><CODE>Activity</CODE>
</DL>

<P>Examples of confusing, ambiguous terms to be avoided:

<DL COMPACT>
<DT>region<DT><DD>          (Sheets only sometimes correspond to neural regions like V1)
<DT>area<DT><DD>            (Same problem as Region)
<DT>map<DT><DD>             (Used in too many different senses)
<DT>layer<DT><DD>           (Biology and neural-network people use it very differently)
<DT>activation<DT><DD>      (Implies a specific stimulus, which is not always true)
<DT>receptive field<DT><DD> (Only valid if plotted with reference to the external world)
</DL>

<P>As discussed for object-oriented design above, such undefined terms
can be used in examples that bring in concepts from the world outside
of Topographica, but they are not appropriate for variable or class
names, documentation, or comments making up the Topographica simulator
itself.
