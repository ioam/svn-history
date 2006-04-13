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
from parameterclasses import BooleanParameter, Number, Parameter
from Numeric import zeros,array,floor,ceil,Float

from boundingregion import BoundingBox, BoundingRegionParameter
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
    left,bottom,right,top = bounds.lbrt()

    # Compute the true density along x and y. The true density does
    # not equal to the 'density' argument when density*(right-left) or
    # density*(top-bottom) is not an integer.
    # (These true densities could be cached by a Sheet if that would
    # speed things up.)
    #xdensity = int(density*(right-left)) / float((right-left))
    #ydensity = int(density*(top-bottom)) / float((top-bottom))

    # First translate to (left,top), which is [0,0] in the matrix,
    # then scale to the size of the matrix. The y coordinate needs to
    # flipped, because the points are moving down in the sheet as the
    # y index increases in the matrix.
    float_col = (x-left) * density
    float_row = (top-y)  * density
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


def sheet2matrixidx_array(x,y,bounds,density):
    """
    sheet2matrixidx but for arrays of x and y.
    """
    r,c = sheet2matrix(x,y,bounds,density)
    r = floor(r)
    c = floor(c)
    return r.astype(int), c.astype(int)



def matrix2sheet(float_row,float_col,bounds,density):
    """
    Convert a floating-point location (float_row,float_col) in matrix
    coordinates to its corresponding location (x,y) in sheet
    coordinates, given a bounds and density.
    
    Inverse of sheet2matrix().
    """
    left,bottom,right,top = bounds.lbrt()

    # CEBHACKALERT: xdensity and/or ydensity could be zero (with a small
    # BoundingBox or low density). Either that should be dealt with here,
    # or it should be disallowed earlier.
    # This problem arises in several places (e.g. see PatternGenerator).

    step = 1.0 / density
    x = float_col*step + left
    y = top - float_row*step
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


def bounds2slice(slice_bounds, sheet_bounds, sheet_density):
    """
    Convert a bounding box into an array slice suitable for computing
    a submatrix.

    Includes all units whose centers are within the specified sheet
    coordinate bounding box slice_bounds.

    The returned slice does not respect the sheet_bounds: use
    crop_slice_to_sheet_bounds() to have the slice cropped to the
    sheet.
    
    Returns (a,b,c,d) such that a matrix M can be sliced using M[a:b,c:d].
    """
    l,b,r,t = slice_bounds.lbrt()
    
    t_m,l_m = sheet2matrix(l,t,sheet_bounds,sheet_density)
    b_m,r_m = sheet2matrix(r,b,sheet_bounds,sheet_density)

    l_idx = int(ceil(l_m-0.5))
    t_idx = int(ceil(t_m-0.5))
    r_idx = int(floor(r_m+0.5))
    b_idx = int(floor(b_m+0.5))

    return t_idx,b_idx,l_idx,r_idx


def crop_slice_to_sheet_bounds(slice_,sheet_bounds,density):
    """
    Crop the given slice to the specified sheet_bounds.
    """
    maxrow,maxcol = sheet2matrixidx(sheet_bounds.aarect().right(),
                                    sheet_bounds.aarect().bottom(),
                                    sheet_bounds,density)
    t_idx,b_idx,l_idx,r_idx = slice_
    
    rstart = max(0,t_idx)
    rbound = min(maxrow,b_idx)
    cstart = max(0,l_idx)
    cbound = min(maxcol,r_idx)

    return rstart,rbound,cstart,cbound


def bounds2slicearray(slice_bounds, input_bounds, input_density):
    """
    Same as bounds2slice(), but return a Numeric array instead of a tuple.
    """
    r1,r2,c1,c2 = bounds2slice(slice_bounds,input_bounds,input_density)
    return array([r1,r2,c1,c2])


# CEBHACKALERT: slice is a Python type.
def slice2bounds(slice,sheet_bounds,sheet_density):
    """
    Construct the bounds that corresponds to the given slice.
    This way, this function is an exact transform of bounds2slice. 
    That enables to retrieve the slice information from the bounding box.
    """
    r1,r2,c1,c2 = slice

    left,bottom = matrix2sheet(r2,c1,sheet_bounds,sheet_density)
    right, top   = matrix2sheet(r1,c2,sheet_bounds,sheet_density)

    bounds = BoundingBox(points=((left,bottom),
                                  (right,top)))

    # yfsit: why do we need to check for <= 0?
    #if (int(sheet_density*(right-left)) <= 0):
    #   xstep = float((right-left)) / int(sheet_density)
    #else:
    #   xstep = float((right-left)) / int(sheet_density*(right-left))
    #
    #if (int(sheet_density*(top-bottom)) <= 0):
    #   ystep = float((top-bottom)) / int(sheet_density)
    #else:
    #   ystep = float((top-bottom)) / int(sheet_density*(top-bottom))

    return bounds


def slicearray2bounds(slicearray,sheet_bounds,sheet_density):
    """
    Same as slice2bounds, but the slice is an array instead of a tuple.
    """
    return slice2bounds((slicearray[0],slicearray[1],slicearray[2],slicearray[3]), sheet_bounds, sheet_xdensity,sheet_ydensity)



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
    _abstract_class_name = "Sheet"


    bounds  = BoundingRegionParameter(BoundingBox(radius=0.5),constant=True,
                                      doc="BoundingBox of the Sheet coordinate area covered by this Sheet")
    ### JABHACKALERT: Should be type Number, but that causes problems
    ### when instantiating Sheets in the Model Editor.
    density = Parameter(default=10,constant=True,
                        doc="Number of processing units per 1.0 distance horizontally or vertically in Sheet coordinates")
    # JABALERT: Should be set per-projection, not per-Sheet, right?
    learning = BooleanParameter(True)
    precedence = Number(default = 0.1, softbounds=(0.0,1.0),
			doc='Allows defining a sorting order on Sheet objects.')


    def __init__(self,**params):

        super(Sheet,self).__init__(**params)

        self.debug("density = ",self.density)


        # Calculate the true density along x (from the left and right bounds and
        # the nominal density), then adjust the top and bottom bounds so that
        # the density along y is the same.
        # The top and bottom bounds are adjusted such that the center
        # y point remains the same, and each bound is as close as possible
        # to its specified value.
        # (move to docstring, etc)
        
        left,bottom,right,top = self.bounds.lbrt()
        width = right-left; height = top-bottom

        center_y = bottom + height/2.0

        # CEBHACKALERT: temporary - avoid the constant issue while we
        # calculate the bounds and the density
        self.initialized = False


        self.density = int(self.density*(width))/float((width))

        n_units = round(height*self.density,0)
        
        adjusted_half_height = n_units/self.density/2.0
        
        adjusted_bottom = center_y - adjusted_half_height
        adjusted_top = center_y + adjusted_half_height

        self.bounds=BoundingBox(points=((left,adjusted_bottom),(right,adjusted_top)))
        self.initialized=True

        # CEBHACKALERT: these will be removed
        self.xdensity = self.density
        self.ydensity = self.density

        # setup the activity matrix
        r1,r2,c1,c2 = bounds2slice(self.bounds,self.bounds,self.density)
        self.activity = zeros((r2-r1,c2-c1),Float)

        self.__saved_activity = []          # For non-learning inputs
        self.debug('activity.shape =',self.activity.shape)
        ### JABALERT: Should perhaps rename this to view_dict
        self.sheet_view_dict = {}


    ### JABALERT: This should be deleted now that sheet_view_dict is public
    ### JC: shouldn't we keep that, or at list write a function in utils that delete
    ### a value in a dictinnary without returning an error if the key is not in the dict?
    ### I leave for the moment, and have to ask Jim advise.
    def release_sheet_view(self,view_name):
        """
        Delete the dictionary entry with key entry 'view_name' to save
        memory.
        """
	if self.sheet_view_dict.has_key(view_name):   
	    del self.sheet_view_dict[view_name]

    def sheet2matrix(self,x,y):
        return sheet2matrix(x,y,self.bounds,self.density)

    def matrix2sheet(self,r,c):
        return matrix2sheet(r,c,self.bounds,self.density)

                
    def sheet2matrixidx(self,x,y):
        """
        Coordinate transformation: takes a point (x,y) in sheet
        coordinates and returns the (row,col) of the matrix cell it
        cooresponds to.
        """
        return sheet2matrixidx(x,y,self.bounds,self.density)


    def sheet2matrixidx_array(self,x,y):
        """
        sheet2matrixidx but for arrays of x and y.
        """
        return sheet2matrixidx_array(x,y,self.bounds,self.density)


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
        


# CEBHACKALERT: unfinished, unused, untested.
class Slice(object):
    """
    """
    def __init__(self,slice_bounds,sheet):
        """
        Create the matrix slice that corresponds to the sheet
        coordinate slice_bounds.
        """
        self.sheet = sheet
        self.slice_array = self.__bounds2slice(slice_bounds)


    def sheet_coordinate_bounds(self):
        """
        Return the sheet coordinate bounding box of this Slice.
        """
        r1,r2,c1,c2 = self.slice_array

        left,bottom = self.sheet.matrix2sheet(r2,c1)
        right, top  = self.sheet.matrix2sheet(r1,c2)

        return BoundingBox(points=((left,bottom),
                                   (right,top)))


    def lbrt(self):
        """
        Return the matrix idx coordinate slice as a tuple.
        """
        r1,r2,c1,c2 = self.slice_array
        return (c1,r2,c2,r1)


    def submatrix(self,M):
        """
        Return the submatrix of M defined by this Slice.
        """
        r1,r2,c1,c2 = self.slice_array
        return M[r1:r2,c1:c2]


    def __bounds2slice(self,slice_bounds):
        """
        Convert a bounding box into an array slice suitable for computing
        a submatrix.

        Includes all units whose centers are within the specified sheet
        coordinate bounding box slice_bounds.

        The returned slice does not respect the sheet's bounds: use
        crop_slice_to_sheet_bounds() to have the slice cropped to the
        sheet.

        Returns (a,b,c,d) such that a matrix M can be sliced using M[a:b,c:d].
        """
        l,b,r,t = slice_bounds.lbrt()

        t_m,l_m = self.sheet.sheet2matrix(l,t)
        b_m,r_m = self.sheet.sheet2matrix(r,b)

        l_idx = int(ceil(l_m-0.5))
        t_idx = int(ceil(t_m-0.5))
        r_idx = int(floor(r_m+0.5))
        b_idx = int(floor(b_m+0.5))

        return array((t_idx,b_idx,l_idx,r_idx))


    def cropped_to_sheet(self):
        """
        Return the slice cropped to the sheet's bounds.
        """
        sheet_right = self.sheet.bounds.aarect().right()
        sheet_bottom = self.sheet.bounds.aarect().bottom()
        maxrow,maxcol = self.sheet.sheet2matrixidx(sheet_right,sheet_bottom)

        t_idx,b_idx,l_idx,r_idx = self.slice_array

        rstart = max(0,t_idx)
        rbound = min(maxrow,b_idx)
        cstart = max(0,l_idx)
        cbound = min(maxcol,r_idx)

        return array((rstart,rbound,cstart,cbound))




