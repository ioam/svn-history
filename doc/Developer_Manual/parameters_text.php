<H1>Parameters and bounds</H1>

<P>When writing user-visible classes, variables that are meant to be
user-modifiable should be of class Parameter, so that they will be
visible in the various user interfaces.

<P>Parameters should have the narrowest type and tightest bounds that
would be meaningful.  For instance, a parameter that can be either
true or false should be of type BooleanParameter, while one that can
only have a value from 0 to 0.5 should be of type Number with a hard
bound of 0 to 0.5.  Using the right types and bounds greatly
simplifies life for the programmer, who can reason about the code
knowing the full allowable range of the parameter, and for the user,
who can tell what values make sense to use.

<P>For Parameters that might show up in a GUI, soft bounds should also
be included wherever appropriate.  These bounds set the range of
sliders, etc., and are a suggested range for the Parameter.  If there
are hard bounds at both ends, soft bounds are not usually needed, but
can be useful if the reasonable range of the Parameter is much smaller
than the legal range.

<P>Parameters should each be documented with an appropriate docstring
passed to the constructor.  The documentation should be written from
the user perspective, not the programmer's, because it will appear in
various online and other forms of user documentation.


<H1>Numerical units in the user interface</H1>

<P>All quantities visible to the user, such as GUI labels, parameters,
etc. must be in appropriate units that are independent of simulation
or implementation details.  For instance, all coordinates and
subregions of sheets must be in Sheet coordinates, not e.g. exposing
the row and column in the underlying matrix.  Similarly, unit
specifiers should be in Sheet coordinates, selecting the nearest
appropriate unit, not row and column.

<P>Appropriate units for most parameters can be determined by
considering the continuous plane underlying the discrete units forming
the model sheet, and the continuous logical timeline behind the
discrete timesteps in the model. Some parameters should be expressed
in terms of lengths in that plane, some in terms of areas, and some in
terms of volumes, rather than numbers of units, etc.  Others are
expressed in terms of lengths of time, rather than number of time
steps.  More information is available in <A
HREF="http://nn.cs.utexas.edu/keyword?bednar:neuroinformatics04">
<cite>Bednar et al, Neuroinformatics, 2004</cite></A>.  There is
usually only one correct answer for how to specify a particular
parameter, so please discuss it with all, or at least with Jim, before
picking a unit arbitrarily.



