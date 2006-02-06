<H1>Topographica coordinate systems</H1>

Topographica allows simulation parameters to be specified in units
that are independent of the level of detail used in any particular run
of the simulation.  To achieve this, Topographica provides multiple
coordinate systems, called <i>Sheet</i> and <i>matrix</i> coordinates.


<H2><A NAME="sheet-coords">Sheet coordinates</A></H2>

<P>Quantities in the user interface are expressed in Sheet
coordinates.  A Topographica <?php classref('topo.base.sheet','Sheet')
?> is a continuous abstraction of a finite, two-dimensional array of
neural units.  A Sheet corresponds to a rectangular portion of a
continuous two-dimensional plane.  The default Sheet has a square area
of 1.0 centered at (0.0,0.0):

<P><CENTER><IMG BORDER="2" WIDTH="388" HEIGHT="381" SRC="images/sheet_coords.png"></CENTER>

<P>Locations in a Sheet are specified using floating-point Sheet
coordinates (x,y) contained within the Sheet's <?php
classref('topo.base.boundingregion','BoundingBox') ?>.  The thick
black line in the figure above shows the BoundingBox of the default
Sheet, which extends from (-0.5,-0.5) to (0.5,0.5) in Sheet
coordinates.  Any coordinate within the BoundingBox is a valid Sheet
coordinate.


<H2><A NAME="matrix-coords">Matrix coordinates</A></H2>

<P>Although it is possible to do some computations using analytic
representations of the continuous Sheet, in practice, Sheets are
typically implemented using some finite matrix of units.  Each Sheet
has a parameter called its <i>density</i>, which specifies how many
units (matrix elements) in the matrix correspond to a unit length in
Sheet coordinates.  For instance, the default Sheet above with a
density of 5 corresponds to the following matrix:

<!-- JCALERT: Should add a copy of the Sheet coordinates, marking the -->
<!-- given point in both plots -->
<P><CENTER><IMG BORDER="2" WIDTH="372" HEIGHT="369" SRC="images/matrix_coords.png"></CENTER>

<P>Here, the 1.0x1.0 area of Sheet coordinates is represented with a
5x5 matrix, whose BoundingBox (represented by a thick black line)
corresponds exactly to the BoundingBox of the Sheet to which it
belongs.  Each floating-point location (x,y) in Sheet coordinates
corresponds uniquely to a floating-point location (r,c) in
floating-point matrix coordinates.  For the example Sheet
above, location (0.5,1.5) in matrix coordinates corresponds exactly to
location (-0.2,0.4) in Sheet coordinates.  Notice that matrix
coordinates start at (0.0,0.0) in the upper left and increase down and
to the right (as is the accepted convention for matrices), while
Sheet coordinates start at the center and increase up and to the right
(as is the accepted convention for Cartesian coordinates).

<P>Individual units or elements in this array are accessed using
integer <i>matrix index</i> coordinates, which can be calculated from
the matrix coordinate as
(<code>floor(int(r))</code>,<code>floor(int(c))</code>).  In this
example, the unit whose center is at matrix coordinate (0.5,1.5) has
the matrix index coordinate (0,1).

<P>The reason for having multiple sets of coordinates is that the same
Sheet can at another time be implemented using a different matrix
specified by a different density.  For instance, if this Sheet had a
density of 10 instead, the corresponding matrix would be:

<P><CENTER><IMG BORDER="2" WIDTH="377" HEIGHT="397" SRC="images/matrix_coords_hidensity.png"></CENTER>

<P>Using this higher density, Sheet coordinate (-0.2,0.4) now
corresponds to the matrix coordinate (1.0,3.0).  As long as the user
interface specifies all units in Sheet coordinates and converts these
to matrix coordinates appropriately, the user can use different
densities at different times without changing any other parameters.


<H2><A NAME="connection-fields">Connection fields</A></H2>

Units in a Topographica Sheet can receive input from units in other
Sheets.  Such inputs are generally contained within a <?php
classref('topo.base.connectionfield','ConnectionField') ?>, which is a
spatially localized region of an input Sheet.  A ConnectionField is
bounded by a BoundingBox that is a subregion of the Sheet's
BoundingBox.  The units contained within a ConnectionField are those
whose centers lie within that BoundingBox.

<P>For instance, if the user specifies a ConnectionField with Sheet bounds from
(-0.275,-0.0125) to (0.025,0.2885) for a sheet with a density of 10, the
corresponding matrix coordinate bounds are (5.125,2.250) to (2.125,5.25):

<!-- JCALERT: Should add a copy of the Sheet coordinates, marking the -->
<!-- given box in both plots -->
<P><CENTER><IMG BORDER="2" WIDTH="377" HEIGHT="397" SRC="images/connection_field.png"></CENTER>

<P>Here the medium black outline shows the BoundingBox in matrix
coordinates.  The units contained in this ConnectionField are (4,2) to
(2,4) (inclusive; shown by black dots with a yellow background).
Notice that the Sheet area of the ConnectionField will not
necessarily correspond exactly to the user-specified BoundingBox,
because the matrix is discrete.

<H2><A NAME="edge-buffers">Edge buffering</A></H2>

<P>If every Sheet has the default 1.0x1.0 area, units near the border
of higher-level Sheets will have ConnectionFields that extend past the
border of lower-level Sheets.  This ConnectionField cropping will
often result in artifacts in the behavior of units near the border.
To avoid such artifacts, lower-level Sheets should usually have areas
larger than 1.0x1.0.

<P>For instance, assume that Sheets have a 1.0x1.0 area.  If a a
higher level sheet U has a ConnectionField BoundingBox of size 0.4x0.4
on lower-level Sheet L, neurons near the border of U will have up to
0.2 in Sheet coordinate cut off of their ConnectionFields.  To prevent
this, the BoundingBox of L can be extended by 0.2 units Sheet
coordinates in each direction:

<P><CENTER><IMG BORDER="2" WIDTH="509" HEIGHT="505" SRC="images/retina_edge_buffer.png"></CENTER>

<P>Here, the thick black line shows the calculated size of L to avoid
edge cropping, and the dotted line shows the size of U for reference.
If L were the size of U, up to three quarters of the ConnectionField
of units in U near the border would be cut off.  With the size of L
extended as shown, all units in U will have full ConnectionFields.
Thus when calculating the behavior of U, the extended L will work as
if L were infinitely large in all directions.  This approach is
appropriate for avoiding edge effects when modeling a small patch of a
larger system.

<P>Of course, this technique cannot help you avoid such cropping for
lateral connections within U or feedback connections from areas above
U.  In some simulators, periodic boundary conditions can be enforced
such that such connections wrap around like a torus, but such wrapping
is not practical in Topographica because it focuses on drawing
realistic input patterns like photographs, which cannot be rendered
properly on a torus.
