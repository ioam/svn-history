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
from Numeric import zeros,array
from boundingregion import BoundingBox
import sheetview 

def sheet2matrix(x,y,bounds,density):
    """
    Convert a point (x,y) in sheet coordinates to matrix coordinates given 
    the sheet's bounds and density.

    When computing this transformation for an existing sheet foo, one
    should use the Sheet method foo.sheet2matrix(x,y).
    """

    left,bottom,right,top = bounds.aarect().lbrt()

    # compute the true density along x and y. The true density does not equal
    # to density argument when density*(right-left) or density*(top-bottom) is
    # not an integer.
    xdensity = int(density*(right-left)) / float((right-left))
    ydensity = int(density*(top-bottom)) / float((top-bottom))

    # First translate to (left,top), which is [0,0] in the matrix, then scale to
    # the size of the matrix. y coodinate needs to flipped, because the points
    # are moving down in the sheet as the y-index increases in the matrix.
    col = (x-left) * xdensity
    row = (top-y)  * ydensity
    return row, col

def sheet2matrixidx(x,y,bounds,density):
    """
    Convert a point (x,y) in sheet coordinates to the row and column index
    of the matrix cell in which that point falls given bounds and density.
    Returns (row,column).  

    NOTE: This is NOT the strict mathematical inverse of matrixidx2sheet.
    NOTE2: If the coordinates along the left or bottom boundary are passed into
    this function, the returned matrix coordinate of the boundary will be right
    outside the matrix.
    """

    r,c = sheet2matrix(x,y,bounds,density)

    return int(r), int(c)


def matrix2sheet(mx,my,bounds,density):
    """
    Inverse of sheet2matrix.
    
    Convert a point (mx,my) in matrix coordinates to its
    corresponding point (x,y) in sheet coordinates given bounds and
    density.
    """

    left,bottom,right,top = bounds.aarect().lbrt()
    xstep = float((right-left)) / int(density*(right-left))
    ystep = float((top-bottom)) / int(density*(top-bottom))
    x = mx*xstep + left
    y = top - my*ystep
    return x, y


def matrixidx2sheet(row,col,bounds,density):
    """
    Returns (x,y) where x and y are the floating point coordinates of
    the CENTER of the given matrix cell (row,col). If the matrix cell
    represents a 0.2 by 0.2 region, then the center location returned
    would be 0.1,0.1

    NOTE: This is NOT the strict mathematical inverse of sheet2matrixidx.
    
    When computing this transformation for an existing sheet foo, one
    should use the Sheet method foo.matrixidx2sheet(r,c).
    """

    x,y = matrix2sheet((col+0.5), (row+0.5), bounds, density)

    # Rounding is useful for comparing the result with a floating point number
    # that we specify by typing the number out (e.g. fp = 0.5).
    # Round eliminates any precision errors that have been compounded
    # via floating point operations so that the rounded number will better
    # match the floating number that we type in.
    return round(x,10),round(y,10)


def activity_submatrix(slice_bounds,activity,activity_bounds,density):
    """
    Returns a submatrix of an activity matrix defined by bounding
    rectangle. Uses sheet.input_slice().  Does not copy the
    submatrix!
    """
    r1,r2,c1,c2 = input_slice(slice_bounds,activity_bounds,density)
    return activity[r1:r2,c1:c2]

def input_slice(slice_bounds, input_bounds, input_density):
    """
    Gets the parameters for slicing an activity matrix given the
    slice bounds, activity bounds, and density of the activity
    matrix.

    returns a,b,c,d -- such that an activity matrix M
    can be sliced like this: M[a:b,c:d]
    """

    left,bottom,right,top = slice_bounds.aarect().lbrt()
    rows,cols = bounds2shape(slice_bounds,input_density)
    toprow,leftcol = sheet2matrixidx(left,top,input_bounds,input_density)

    cr,cc = sheet2matrixidx((left+right)/2,(top+bottom)/2,input_bounds,input_density)
    toprow = cr - rows/2
    leftcol = cc - cols/2

    maxrow,maxcol = sheet2matrixidx(input_bounds.aarect().right(),input_bounds.aarect().bottom(),input_bounds,input_density)

    maxrow = maxrow - 1
    maxcol = maxcol - 1
    rstart = max(0,toprow)
    rbound = min(maxrow+1,cr+rows/2+1)
    cstart = max(0,leftcol)
    cbound = min(maxcol+1,cc+cols/2+1)

    return rstart,rbound,cstart,cbound



def input_slice(slice_bounds, input_bounds, input_density, x, y):
    """
    Gets the parameters for slicing an activity matrix given the
    slice bounds, activity bounds, and density of the activity
    matrix.

    returns a,b,c,d -- such that an activity matrix M
    can be sliced like this: M[a:b,c:d]    
    """
    rows,cols = bounds2shape(slice_bounds,input_density)

    cr,cc = sheet2matrixidx(x, y, input_bounds, input_density)

    toprow = cr - rows/2
    leftcol = cc - cols/2

    maxrow,maxcol = sheet2matrixidx(input_bounds.aarect().right(),
                                 input_bounds.aarect().bottom(),
                                 input_bounds,input_density)

    maxrow = maxrow - 1
    maxcol = maxcol - 1
    rstart = max(0,toprow)
    rbound = min(maxrow+1,cr+rows/2+1)
    cstart = max(0,leftcol)
    cbound = min(maxcol+1,cc+cols/2+1)

    return rstart,rbound,cstart,cbound


def bounds2shape(bounds,density):
    """
    Gives the matrix shape in rows and columns specified by the given
    bounds and density.  Returns (rows,columns).
    """
    left,bottom,right,top = bounds.aarect().lbrt()
    width = right-left
    height = top-bottom
    rows = int(height*density)
    cols = int(width*density)

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


    def sheet_view(self,request='Activity'):
        ### JABHACKALERT!
        ### 
        ### Shouldn't the name for an Activity View be a tuple, not
        ### a string concatenating the sheet and view names?
        """
        Create a SheetView object of the current activity of the
        Sheet.  Current implementation gives the raw activity
        matrix.  Uses self.sheet_view_dict if the request is not
        the default.

        The name for an Activity View should be the Sheet name plus
        '_Activity', e.g. 'Sheet0002_Activity'.

        Returns None if the View does not exist in this sheet.
        """
        ### JABHACKALERT!
        ### 
        ### Instead of this special coding for Activity, should make a
        ### function that populates the SheetView dictionaries with
        ### Activity plots, which will then be called before plotting.
        ### This should all work the same as for preference maps: with
        ### each plot template there will be associated code that will
        ### be called just before plotting, which should install any
        ### required SheetViews into the dictionary.
        if request == 'Activity':
            activity_copy = array(self.activity)
            new_view = sheetview.SheetView((activity_copy,self.bounds),
                                 src_name=self.name,view_type='Activity')
        elif self.sheet_view_dict.has_key(request):
            new_view = self.sheet_view_dict[request]
        else:
            new_view = None
        return new_view


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

    ### JABHACKALERT!
    ### 
    ### Instead of this special coding for Activity, should make a
    ### function that populates the SheetView dictionaries with
    ### Activity plots, which will then be called before plotting.
    def release_sheet_view(self,view_name):
        """
        Delete the dictionary entry with key entry 'view_name' to save
        memory.
        """
        if view_name == 'Activity':
            pass
        elif self.sheet_view_dict.has_key(view_name):        
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
        Returns the offset of the sheet origin from the lower-left
        corner of the sheet, in sheet coordinates.
        """
        return -self.bounds.aarect().left(),-self.bounds.aarect().bottom()

    def input_slice(self,slice_bounds,x,y):
        """
        Gets the parameters for slicing the sheet's activity matrix.

        returns a,b,c,d -- such that an activaiton matrix M
        originating from this sheet can be sliced like this M[a:b,c:d]
        """
        return input_slice(slice_bounds,self.bounds,self.density,x,y)

    def activity_submatrix(self,slice_bounds,activity=None):
        """
        Returns a submatrix of an activity matrix that originated
        from this sheet.  If no activity matrix is given, the
        sheet's current activity is used.  Does not copy the
        submatrix!  It is a true slice of the given matrix.
        """
        if not activity:
            activity = self.activity

        return activity_submatrix(slice_bounds,activity,self.bounds,self.density)

    def sheet_rows(self):
        """
        Returns a list of Y-coordinates corresponding to the rows of
        the activity matrix of the sheet.
        """
        rows,cols = self.activity.shape
        coords = [self.matrixidx2sheet(r,0) for r in range(rows-1,-1,-1)]
        return [y for (x,y) in coords]

    def sheet_cols(self):
        """
        Returns a list of X-coordinates corresponding to the columns
        of the activity matrix of the sheet.
        """
        rows,cols = self.activity.shape
        coords = [self.matrixidx2sheet(0,c) for c in range(cols)]
        return [x for (x,y) in coords]


    def activity_push(self):
        """
        Save the current sheet activity to an internal stack.
        """
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
        """Return length of elements in the __saved_activity stack."""
        return len(self.__saved_activity)
        

