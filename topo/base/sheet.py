"""
Neural sheet objects and associated functions.

The Sheet class is the base class for EPs that simulate
topographically mapped sheets of units (neurons or columns).  A Sheet
is an EventProcessor that maintains a rectangular array of activity
values, and sends the contents of this array as the data element in
events.

The dimensions of a Sheet's activity array are specified not with
numbers of rows and columns, but with a rectangular bounding box (see
boundingregion) and a density.  The default bounding box for
sheets is the unit square with its center at the origin.  i.e:


            (-0.5,0.5) +----+----+ (0.5,0.5)
                       |    |    |
                       |    |    |
                       +----+----+
                       |    |    |
                       |    |    |
           (-0.5,-0.5) +----+----+ (0.5,-0.5)

The default density is 10, giving the default sheet a 10x10
activity matrix.

This scheme gives a Sheet two coordinate systems.  A pair of 'sheet
coordinates' (x,y) are floating-point Cartesian coordinates indicating
an arbitrary point on the sheet's plane.  A pair of 'matrix
coordinates' (r,c), specify the row and column indices of a specific
unit in the sheet.  This module provides facilities for converting
between the two coordinate systems, and EVERYONE SHOULD USE THESE
FACILITIES to guarantee that coordinate transformations are done
consistently everywhere.

In general sheets should be thought of as having arbitrary density and
sheet coordinates should be used wherever possible, except when the
code needs direct access to a specific unit.  By adhering to this
convention, one should be able to write and debug a simulation at a
low density, and then scale it up to run at higher densities (or down
for lower densities) simply by changing e.g. Sheet.density.


Example of how the matrix stores the representation of the Sheet:

For the purposes of this example, assume the goal is a Sheet with
density=3 that has a 1 at (-1/2,-1/2), a 5 at (0.0,0.0), and a 9 at
(1/2,1/2).  More precisely, for this Sheet,

the continuous area from -1/2,-1/2 to -1/6,-1/6 has value 1, 
the continuous area from -1/6,-1/6 to  1/6,1/6  has value 5, and 
the continuous area from  1/6,1/6  to  1/2,1/2  has value 9.

With the rest of the elements filled in, the Sheet would look like:

    (-1/2,1/2) -+-----+-----+-----+- (1/2,1/2)
                |     |     |     |
                |  7  |  8  |  9  |
                |     |     |     |
    (-1/2,1/6) -+-----+-----+-----+- (1/2,1/6)
                |     |     |     |
                |  4  |  5  |  6  |
                |     |     |     |
   (-1/2,-1/6) -+-----+-----+-----+- (1/2,-1/6)
                |     |     |     |
                |  1  |  2  |  3  |
                |     |     |     |
   (-1/2,-1/2) -+-----+-----+-----+- (1/2,-1/2)

where element 5 is centered on 0.0,0.0.  A matrix that would match
these Sheet coordinates is:

  [[7 8 9]
   [4 5 6]
   [1 2 3]]

If we have such a matrix, we can access it in one of two ways: Sheet
or matrix coordinates.  In matrix coordinates, the matrix is indexed
by rows and columns, and it is possible to ask for the element at
location [0,2] (which returns 9 as in any normal row-major matrix).
But the values can additionally be accessed in Sheet coordinates,
where the matrix is indexed by a point in the Cartesian plane.  In
Sheet coordinates, it is possible to ask for the element at location
(0.3,0.02), which returns floating-point matrix coordinates that can
be cropped to give the nearest matrix element, namely the one with
value 6.

Of course, it would be an error to try to pass Matrix coordinates like
[0,2] to the sheet2matrix calls; the result would be a value far
outside of the actual matrix.

$Id$
"""

__version__ = '$Revision$'

from simulator import EventProcessor
from parameter import Parameter, BooleanParameter
from Numeric import zeros,array,floor
from boundingregion import BoundingBox
import sheetview 

def sheet2matrix(x,y,bounds,density):
    """
    Convert a point (x,y) in Sheet coordinates to continuous matrix
    coordinates.

    Returns (float_row,float_col), where float_row corresponds to y,
    and float_col to x.

    When computing this transformation for an existing sheet foo,
    use the Sheet method foo.sheet2matrix(x,y).    

    Bounds
    For a Sheet with BoundingBox(points=((-0.5,-0.5),(0.5,0.5))) and
    density=3, x=-0.5 corresponds to float_col=0.0 and x=0.5
    corresponds to float_col=3.0.  float_col=3.0 is not inside the
    matrix representing this Sheet, which has the three columns
    (0,1,2). That is, x=-0.5 is inside the BoundingBox but x=0.5 is
    outside. Similarly, y=0.5 is inside (at row 0) but y=-0.5 is
    outside (at row 3) (it's the other way round for y because the
    matrix row index increases as y decreases).

    Density
    When density*(left-right) or density*(top-bottom) is not an integer,
    the supplied density argument is not used as the exact density for
    the matrix. The matrix needs to tile the plane exactly,
    and for that to work the density may need to be adjusted.
    """

    left,bottom,right,top = bounds.aarect().lbrt()

    # Compute the true density along x and y. The true density does
    # not equal to the 'density' argument when density*(right-left) or
    # density*(top-bottom) is not an integer.
    # (These true densities could be cached by a Sheet if that would
    # speed things up.)
    xdensity = int(density*(right-left)) / float((right-left))
    ydensity = int(density*(top-bottom)) / float((top-bottom))

    # First translate to (left,top), which is [0,0] in the matrix,
    # then scale to the size of the matrix. The y coordinate needs to
    # flipped, because the points are moving down in the sheet as the
    # y-index increases in the matrix.
    float_col = (x-left) * xdensity
    float_row = (top-y)  * ydensity
    return float_row, float_col
  

def sheet2matrixidx(x,y,bounds,density):
    """
    Convert a point (x,y) in sheet coordinates to the integer row and
    column index of the matrix cell in which that point falls, given a
    bounds and density.  Returns (row,column).

    Note that if coordinates along the right or bottom boundary are
    passed into this function, the returned matrix coordinate of the
    boundary will be just outside the matrix, because the right and
    bottom boundaries are exclusive.

    Valid only for scalar x and y.
    """
    r,c = sheet2matrix(x,y,bounds,density)
    r = floor(r)
    c = floor(c)
    return int(r), int(c)


def matrix2sheet(float_row,float_col,bounds,density):
    """
    Convert a floating-point location (float_row,float_col) in matrix
    coordinates to its corresponding location (x,y) in sheet
    coordinates, given a bounds and density.
    
    Inverse of sheet2matrix().
    """

    left,bottom,right,top = bounds.aarect().lbrt()
    xstep = float((right-left)) / int(density*(right-left))
    ystep = float((top-bottom)) / int(density*(top-bottom))
    x = float_col*xstep + left
    y = top - float_row*ystep
    return x, y


def matrixidx2sheet(row,col,bounds,density):
    """
    Return (x,y) where x and y are the floating point coordinates of
    the *center* of the given matrix cell (row,col). If the matrix cell
    represents a 0.2 by 0.2 region, then the center location returned
    would be 0.1,0.1.

    NOTE: This is NOT the strict mathematical inverse of
    sheet2matrixidx(), because sheet2matrixidx() discards all but the integer
    portion of the continuous matrix coordinate.
    
    When computing this transformation for an existing sheet foo, one
    should use the Sheet method foo.matrixidx2sheet(r,c).

    Valid only for scalar x and y.
    """

    x,y = matrix2sheet((row+0.5), (col+0.5), bounds, density)

    # Rounding is useful for comparing the result with a floating point number
    # that we specify by typing the number out (e.g. fp = 0.5).
    # Round eliminates any precision errors that have been compounded
    # via floating point operations so that the rounded number will better
    # match the floating number that we type in.
    # (CEB: if someone wishes to use array x and y, changing this to around()
    # would work.)
    return round(x,10),round(y,10)


def submatrix(bounds,sheet_matrix,sheet_bounds,sheet_density):
    """
    Return the submatrix of a sheet_matrix specified by a bounds.

    Effectively computes the intersection between the sheet_bounds and
    the new bounds, returning the corresponding submatrix of the given
    sheet_matrix.  The submatrix is just a view into the sheet_matrix;
    it is not an independent copy.
    """
    r1,r2,c1,c2 = bounds2slice(bounds,sheet_bounds,sheet_density)
    return sheet_matrix[r1:r2,c1:c2]

def bounds2slice(slice_bounds, input_bounds, input_density):
    """
    Convert a bounding box into an array slice suitable for computing a submatrix.
    
    Given a slice bounding box, activity bounding box, and the density
    of a sheet matrix, returns a specification for slicing the matrix
    to return the portion within the bounds.  Returns (a,b,c,d), such
    that an activity matrix M can be sliced using M[a:b,c:d].
    """

   #  left,bottom,right,top = slice_bounds.aarect().lbrt()
#     rows,cols = bounds2shape(slice_bounds,input_density)

#     cr,cc = sheet2matrixidx((left+right)/2,(top+bottom)/2,input_bounds,input_density)
#     toprow = cr - rows/2
#     leftcol = cc - cols/2

#     maxrow,maxcol = sheet2matrixidx(input_bounds.aarect().right(),input_bounds.aarect().bottom(),
#                                     input_bounds,input_density)

#     maxrow = maxrow - 1
#     maxcol = maxcol - 1
#     rstart = max(0,toprow)
#     rbound = min(maxrow+1,cr+rows/2+1)
#     cstart = max(0,leftcol)
#     cbound = min(maxcol+1,cc+cols/2+1)

#     return rstart,rbound,cstart,cbound

 ### JCALERT! For the moment, bounds to slice is only used by submatrix, that is only used in 
 ### plot to get the submatrix corresponding  weights bounds
 ### the code below, associated with the correstion notified in sheet2matrix, makes it work to 
 ### re-transform the bounds to the original slice of the weight
 ### the original version (above) does not. I think that for eliminating the problem of different
 ### weight size, it is good to use cc-rows/2,.... but here what we want is a reliable transformation
 ### function from slice to bounds and bounds to slice (by the way write slice_to_bounds here and call
 ### it from connectionfield.)

    left,bottom,right,top = slice_bounds.aarect().lbrt()
    toprow,leftcol = sheet2matrixidx(left,top,input_bounds,input_density)
    botrow, rightcol =sheet2matrixidx(right,bottom,input_bounds,input_density)
   
    maxrow,maxcol = sheet2matrixidx(input_bounds.aarect().right(),input_bounds.aarect().bottom(),input_bounds,input_density)

    maxrow = maxrow - 1
    maxcol = maxcol - 1
    rstart = max(0,toprow+1)
    rbound = min(maxrow+1,botrow)
    cstart = max(0,leftcol+1)
    cbound = min(maxcol+1,rightcol)

    return rstart,rbound,cstart,cbound

####
 

def bounds2shape(bounds,density):
    """
    Return the matrix shape specified by the given bounds and density.

    Always returns a matrix shape with at least one element, even if the
    bounding box is smaller than one matrix element for this density.
    Returns (rows,columns).
    """

    ### JCALERT! New version of bounds2shape. It has to be checked that we
    ### really want to use sheet2matrixidx().
    ### The other solution would be to use sheet2matrixidx(), and directly make the difference
    ### Nevertheless, I think both methods are equivalent for implementing bounds2shape
    ### Furthermore, using one or the other does not lead to inconsistencies in the way we switch
    ### from slice to bound and bound to slice.

    left,bottom,right,top = bounds.aarect().lbrt()
    toprow,leftcol = sheet2matrix(left,top,bounds,density)
    botrow, rightcol = sheet2matrix(right,bottom,bounds,density)

    rows = int(botrow - toprow)
    cols = int(rightcol - leftcol)

    # Enforce minimum size
    if rows == 0: rows = 1
    if cols == 0: cols = 1
    
    return rows,cols


class Sheet(EventProcessor):
    """
    The generic base class for neural sheets.

    This class handles the sheet's activity matrix, and its
    coordinate frame.  It manages two sets of coordinates:

    _Sheet_coordinates_ are specified as (x,y) as on a normal
    Cartesian graph; the positive y direction is upward, and the scale
    and origin are arbitrary, and specified by parameters.

    _Matrix_coordinates_ are the (row,col) specification for an
    element in the activity matrix.  The usual matrix coordinate
    specs apply.

    Parameters:

    bounds:   A BoundingBox object indicating the bounds of the sheet.
              [default  (-0.5,-0.5) to (0.5,0.5)]
              
    density:  The linear density of the sheet [default 10]

    learning: Setting this to False tells the Sheet not to change its
              permanent state (e.g. any connection weights) based on
              incoming events.

    sheet_view_dict is a dictionary that stores SheetViews,
    i.e. representations of the sheet for use by analysis or plotting
    code.
    """

    bounds  = Parameter(BoundingBox(points=((-0.5,-0.5),(0.5,0.5))))
    density = Parameter(10)
    learning = BooleanParameter(True)

    def __init__(self,**params):

        super(Sheet,self).__init__(**params)

        self.debug("density = ",self.density)
        left,bottom,right,top = self.bounds.aarect().lbrt()
        width,height = right-left,top-bottom
        rows = int(height*self.density)
        cols = int(width*self.density)
        self.activity = zeros((rows,cols)) + 0.0
        self.__saved_activity = []          # For non-learning inputs
        self.debug('activity.shape =',self.activity.shape)
        self.sheet_view_dict = {}


    def add_sheet_view(self,view_name,sheet_view):
        """
        Add a SheetView to the view database in this Sheet object.
        Each view is stored by a dictionary key (string or tuple)
        passed into the function through view_name.  It is valid for
        sheet_view to be a list of SheetViews.

        Because each SheetView has its own internal name, or an entry
        may actually be a list, there is no guarantee that the
        SheetView '.name' will be the same as the view_name.  For
        example, the SheetView name might be 'UnitView7754' whereas
        the key may be, ('Projection',V1,R1toV1,0.2,0.3).  Or the
        sheet_view may be a list of UnitViews for a Projection plot.
        """
        self.sheet_view_dict[view_name] = sheet_view

  
    def release_sheet_view(self,view_name):
        """
        Delete the dictionary entry with key entry 'view_name' to save
        memory.
        """
	if self.sheet_view_dict.has_key(view_name):   
	    del self.sheet_view_dict[view_name]
            
                
    def sheet2matrixidx(self,x,y):
        """
        Coordinate transformation: takes a point (x,y) in sheet
        coordinates and returns the (row,col) of the matrix cell it
        cooresponds to.
        """
        return sheet2matrixidx(x,y,self.bounds,self.density)


    def matrixidx2sheet(self,row,col):
        """
        Coordinate transformation: Takes the (row,col) of an element
        in the activity matrix and gives its (x,y) in sheet
        coordinates.
        """
        return matrixidx2sheet(row,col,self.bounds,self.density)

    def sheet_offset(self):
        """
        Return the offset of the sheet origin from the lower-left
        corner of the sheet, in sheet coordinates.
        """
        return -self.bounds.aarect().left(),-self.bounds.aarect().bottom()


    def sheet_rows(self):
        """
        Return a list of Y-coordinates corresponding to the rows of
        the activity matrix of the sheet.
        """
        rows,cols = self.activity.shape
        coords = [self.matrixidx2sheet(r,0) for r in range(rows-1,-1,-1)]
        return [y for (x,y) in coords]

    def sheet_cols(self):
        """
        Return a list of X-coordinates corresponding to the columns
        of the activity matrix of the sheet.
        """
        rows,cols = self.activity.shape
        coords = [self.matrixidx2sheet(0,c) for c in range(cols)]
        return [x for (x,y) in coords]


    def activity_push(self):
        """Save the current sheet activity to an internal stack."""
        self.__saved_activity.append(array(self.activity))

    def activity_pop(self,restore_activity=True):
        """
        Pop an activity off the stack and return the values.  If
        restore_activity is True, then put the popped information
        back into the Sheet activity variable.
        """
        old_act = self.__saved_activity.pop()
        if restore_activity:
            self.activity = old_act
        return old_act

    def activity_len(self):
        """Return the number of items in pushed into the activity stack."""
        return len(self.__saved_activity)
        

