"""
Neural sheet objects and associated functions.

The Sheet class is the base class for EPs that simulate
topographically mapped sheets of units (neurons or columns).  A Sheet
is an EventProcessor that maintains a rectangular array of activation
values, and sends the contents of this array as the data element in
events.

The dimensions of a Sheet's activation array are specified not with
numbers of rows and columns, but with a rectangular bounding box (see
topo.boundingregion) and a density.  The default bounding box for
sheets is the unit square with its center at the origin.  i.e:


            (-0.5,0.5) +----+----+ (0.5,0.5)
                       |    |    |
                       |    |    |
                       +----+----+
                       |    |    |
                       |    |    |
           (-0.5,-0.5) +----+----+ (0.5,-0.5)

The default density is 100, giving the default sheet a 10x10
activation matrix.

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
from params import Parameter, BooleanParameter
from Numeric import zeros,sqrt,array
from boundingregion import BoundingBox
from sheetview import SheetView

def sheet2matrix(x,y,bounds,density):
    """
    Convert a point (x,y) in sheet coordinates to the row and column
    of the matrix cell in which that point falls given bounds and density.
    Returns (row,column).  If the x,y is right on the edge of the sheet,
    so that it would normally bump up to a matrix unit that does not exist,
    it is knocked back one.  ie. If the right hand edge is 1.0, and the
    passed in x is 1.0, then the math would give a col of 'linear_density'
    but with matrices indexed from 0, this is an invalid location, so
    linear_density - 1 is used.

    NOTE: This is NOT the strict mathematical inverse of matrix2sheet!

    jbednar20050514: This implementation is not correct; it should
    return floats, not ints, with no if statements or other
    corrections.  It should just be a simple coordinate
    transformation, implementable using a matrix as in computer
    graphics routines.  An additional function sheet2matrixint
    might be useful which also crops to integer, but that function
    would be based on this one.

    When computing this transformation for an existing sheet foo, one
    should use the Sheet method foo.sheet2matrix(x,y).
    """
    left,bottom,right,top = bounds.aarect().lbrt()
    linear_density = sqrt(density)
    col = int((x-left) * linear_density)
    row = int((top-y)  * linear_density)

    # The border of the sheet should be inclusive.
    if col == int(linear_density * (right-left)): col = col - 1
    if row == int(linear_density * (top-bottom)): row = row - 1

    return row, col

    
def matrix2sheet(row,col,bounds,density):
    """
    Convert a point (row,col) in matrix coordinates to its
    corresponding point (x,y) in sheet coordinates given bounds and
    density.

    Returns (x,y) where x and y are the floating point coordinates of
    the CENTER of the given matrix cell.  If the matrix cell
    represents a 0.2 by 0.2 region, then the center location returned
    would be 0.1,0.1

    NOTE: This is NOT the strict mathematical inverse of sheet2matrix.

    jbednar20050514: This implementation is not correct; it should not
    assume that the arguments are integers, and should not contain any
    if statements or other corrections.  It should just be a simple
    coordinate transformation, implementable using a matrix as in
    computer graphics routines.
    
    When computing this transformation for an existing sheet foo, one
    should use the Sheet method foo.matrix2sheet(r,c).
    """
    left,bottom,right,top = bounds.aarect().lbrt()
    rows,cols = bounds2shape(bounds,density)
    width = right-left

    # Account for the coordinate transformation between Numeric arrays and
    # Topographica x/y.
    # 0 Indexed, and internal matrices are flipped.
    row = (rows-1) - row
    unit_size = float(width)  / cols

    x = left + (col + 0.5) * unit_size 
    y = bottom + (row + 0.5) * unit_size 
    if x > right: x = x - unit_size
    if y > top: y = y - unit_size

    # Round eliminates any precision errors that have been compounded
    # via math.  This way, any representation errors left, will be
    # minimum and will match coded floating points.
    return round(x,10),round(y,10)


def activation_submatrix(slice_bounds,activation,activation_bounds,density):
    """
    Returns a submatrix of an activation matrix defined by bounding
    rectangle. Uses topo.sheet.input_slice().  Does not copy the
    submatrix!
    """
    r1,r2,c1,c2 = input_slice(slice_bounds,activation_bounds,density)
    return activation[r1:r2,c1:c2]

def input_slice(slice_bounds, input_bounds, input_density):
    """
    Gets the parameters for slicing an activation matrix given the
    slice bounds, activation bounds, and density of the activation
    matrix.

    returns a,b,c,d -- such that an activation matrix M
    can be sliced like this: M[a:b,c:d]
    """

    left,bottom,right,top = slice_bounds.aarect().lbrt()
    rows,cols = bounds2shape(slice_bounds,input_density)
    toprow,leftcol = sheet2matrix(left,top,input_bounds,input_density)

    cr,cc = sheet2matrix((left+right)/2,(top+bottom)/2,input_bounds,input_density)
    toprow = cr - rows/2
    leftcol = cc - cols/2

    maxrow,maxcol = sheet2matrix(input_bounds.aarect().right(),input_bounds.aarect().bottom(),input_bounds,input_density)

    rstart = max(0,toprow)
    rbound = min(maxrow+1,cr+rows/2+1)
    cstart = max(0,leftcol)
    cbound = min(maxcol+1,cc+cols/2+1)

    return rstart,rbound,cstart,cbound



def input_slice(slice_bounds, input_bounds, input_density, x, y):
    """
    Gets the parameters for slicing an activation matrix given the
    slice bounds, activation bounds, and density of the activation
    matrix.

    returns a,b,c,d -- such that an activation matrix M
    can be sliced like this: M[a:b,c:d]    
    """
    rows,cols = bounds2shape(slice_bounds,input_density)

    cr,cc = sheet2matrix(x, y, input_bounds, input_density)

    toprow = cr - rows/2
    leftcol = cc - cols/2

    maxrow,maxcol = sheet2matrix(input_bounds.aarect().right(),
                                 input_bounds.aarect().bottom(),
                                 input_bounds,input_density)

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
    linear_density = sqrt(density)
    rows = int(height*linear_density)
    cols = int(width*linear_density)

    if rows == 0: rows = 1
    if cols == 0: cols = 1
    return rows,cols

class Sheet(EventProcessor):
    """
    The generic base class for neural sheets.

    This class handles the sheet's activity matrix, and it's
    coordinate frame.  It manages two sets of coordinates:

    _Sheet_coordinates_ are specified as (x,y) as on a normal
    cartesian graph; the positive y direction is upward, and the scale
    and origin are arbitrary, and specified by parameters.

    _Matrix_coordinates_ are the (row,col) specification for an
    element in the activation matrix.  The usual matrix coordinate
    specs apply.

    Parameters:

    bounds:   A BoundingBox object indicating the bounds of the sheet.
              [default  (-0.5,-0.5) to (0.5,0.5)]
    density:  The areal density of the sheet [default 100]

    jbednar20050514: All densities should be changed to be linear rather than areal. 
    
    _learning: Whether the Sheet should adjust weights based upon
              incoming events.  

    sheet_view_dict is a dictionary that stores SheetViews that are
    generated by the plotting environment and registered to Sheets
    to be used later by the bitmap display mechanism.
    """

    bounds  = Parameter(BoundingBox(points=((-0.5,-0.5),(0.5,0.5))))
    density = Parameter(100)
    _learning = BooleanParameter(True)

    def __init__(self,**params):

        super(Sheet,self).__init__(**params)

        linear_density = sqrt(self.density)

        self.debug("linear_density = ",linear_density)
        left,bottom,right,top = self.bounds.aarect().lbrt()
        width,height = right-left,top-bottom
        rows = int(height*linear_density)
        cols = int(width*linear_density)
        self.activation = zeros((rows,cols)) + 0.0
        self.__saved_activation = []          # For non-learning inputs
        self.debug('activation.shape =',self.activation.shape)
        self.sheet_view_dict = {}


    def sheet_view(self,request='Activation'):
        """
        Create a SheetView object of the current activation of the
        Sheet.  Current implementation gives the raw activation
        matrix.  Uses self.sheet_view_dict if the request is not
        the default.

        The name for an Activation View should be the Sheet name plus
        '_Activation', e.g. 'Sheet0002_Activation'.

        Returns None if the View does not exist in this sheet.
        """
        if request == 'Activation':
            activation_copy = array(self.activation)
            new_view = SheetView((activation_copy,self.bounds),
                                 src_name=self.name,view_type='Activation')
        elif self.sheet_view_dict.has_key(request):
            new_view = self.sheet_view_dict[request]
        else:
            new_view = None
        return new_view


    def add_sheet_view(self,view_name,sheet_view):
        """
        Add a SheetView to the view database in this Sheet object.
        Each view is stored by a dictionary keyword passed into the
        function through view_name.

        Because each SheetView has its own internal name, there is no
        guarantee that the SheetView 'name' will be stored under the key
        name passed into this function.
        """
        self.sheet_view_dict[view_name] = sheet_view

    def release_sheet_view(self,view_name):
        """
        Delete the dictionary entry with key entry 'view_name' to save
        memory.
        """
        if view_name == 'Activation':
            pass
        elif self.sheet_view_dict.has_key(view_name):        
            del self.sheet_view_dict[view_name]
            
                
    def sheet2matrix(self,x,y):
        """
        Coordinate transformation: takes a point (x,y) in sheet
        coordinates and returns the (row,col) of the matrix cell it
        cooresponds to.
        """
        return sheet2matrix(x,y,self.bounds,self.density)


    def matrix2sheet(self,row,col):
        """
        Coordinate transformation: Takes the (row,col) of an element
        in the activity matrix and gives its (x,y) in sheet
        coordinates.
        """
        return matrix2sheet(row,col,self.bounds,self.density)

    def sheet_offset(self):
        """
        Returns the offset of the sheet origin from the lower-left
        corner of the sheet, in sheet coordinates.
        """
        return -self.bounds.aarect().left(),-self.bounds.aarect().bottom()

    def input_slice(self,slice_bounds,x,y):
        """
        Gets the parameters for slicing the sheet's activation matrix.

        returns a,b,c,d -- such that an activaiton matrix M
        originating from this sheet can be sliced like this M[a:b,c:d]
        """
        return input_slice(slice_bounds,self.bounds,self.density,x,y)

    def activation_submatrix(self,slice_bounds,activation=None):
        """
        Returns a submatrix of an activation matrix that originated
        from this sheet.  If no activation matrix is given, the
        sheet's current activation is used.  Does not copy the
        submatrix!  It is a true slice of the given matrix.
        """
        if not activation:
            activation = self.activation

        return activation_submatrix(slice_bounds,activation,self.bounds,self.density)

    def sheet_rows(self):
        """
        Returns a list of Y-coordinates correspoinding to the rows of
        the activation matrix of the sheet.
        """
        rows,cols = self.activation.shape
        coords = [self.matrix2sheet(r,0) for r in range(rows-1,-1,-1)]
        return [y for (x,y) in coords]

    def sheet_cols(self):
        """
        Returns a list of X-coordinates corresponding to the columns
        of the activation matrix of the sheet.
        """
        rows,cols = self.activation.shape
        coords = [self.matrix2sheet(0,c) for c in range(cols)]
        return [x for (x,y) in coords]


    def activation_push(self):
        """
        Save the current sheet activation to an internal stack.
        """
        self.__saved_activation.append(array(self.activation))

    def activation_pop(self,restore_activation=True):
        """
        Pop an activation off the stack and return the values.  If
        restore_activation is True, then put the popped information
        back into the Sheet activation variable.
        """
        old_act = self.__saved_activation.pop()
        if restore_activation:
            self.activation = old_act
        return old_act

    def activation_len(self):
        """Return length of elements in the __saved_activation stack."""
        return len(self.__saved_activation)
        

    def disable_learning(self):
        """
        Turn off learning for the sheet.  Since learning is defined in
        this class as a pass, a pass here is also done.  This function
        should be defined in subclasses when learning needs to be
        disabled for user inputs.  Call enable_learning() when ready
        to resume.  Derived classes when redefining this function should
        call this code through 'super()'.

        Do NOT set self._learning directly, unless you're certain you
        know what you're doing.
        """
        self._learning = False


    def enable_learning(self):
        """
        Assert that learning has in fact been previously disabled,
        then restore the Sheet to the previous state before
        non-learning stimuli was presented.  This function will
        probably need to be extended by derived classes.  Derived
        class functions should call 'super()' to run this code.
        """
        self._learning = True
