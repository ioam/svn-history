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
from Numeric import zeros,array,floor,ceil,Float,ArrayType,around

from boundingregion import BoundingBox, BoundingRegionParameter
import sheetview 

# CEBHACKALERT: seems likely that CoordinateTransformer should
# go into its own file, so things such as PatternGenerator do
# not depend on all the rest of Sheet.


# CEBHACKALERT: The user-specified input to a CT is 'bounds' and
# 'density'. For a Sheet, this means the parameters are 'bounds' and
# 'density'.  The true bounds are stored as 'true_bounds', and the
# true densities as 'xdensity', and 'ydensity'. That's probably not so
# good.  The main reason I haven't considered changing the parameters
# to 'user_bounds' and 'user_density' (so that the true bounds can be
# stored in 'bounds' is the search-and-replace effort that would be
# required.
# (This is a similar issue to the one in CFProjection - seems like
# weights_bounds should be user_weights_bounds, or something like
# that.)

class CoordinateTransformer(object):
    """
    Provides methods to allow conversion between sheet and matrix
    coordinates.    
    """
    ### xdensity and ydensity are properties so that xstep is kept in
    ### sync with xdensity, and similarly for ystep and ydensity. We
    ### use xstep and ystep so that the repeatedly performed
    ### calculations in matrix2sheet() use multiplications rather than
    ### divisions, for speed.
    def set_xdensity(self,density):
        self.__xdensity=density
        self.__xstep = 1.0/density
        
    def set_ydensity(self,density):
        self.__ydensity=density
        self.__ystep = 1.0/density

    def get_xdensity(self): return self.__xdensity
    def get_ydensity(self): return self.__ydensity
    
    xdensity = property(get_xdensity,
                        set_xdensity,
                        None,
                        """The spacing between elements in an underlying
                        matrix representation, in the x direction.""")

    ydensity = property(get_ydensity,
                        set_ydensity,
                        None,
                        """The spacing between elements in an underlying
                        matrix representation, in the y direction.""")

    ### CEBHACKALERT: temporary implementation
    def get_shape(self):
        r1,r2,c1,c2 = self.bounds2slice(self.true_bounds)
        return (r2-r1,c2-c1)

    ### shape is a property so that it's like Numeric.array.shape
    shape = property(get_shape)


    def __init__(self,bounds,xdensity,ydensity=None,equalize_densities=False):
        """
        Store the bounds (as l,b,r,t in an array), xdensity, and
        ydensity.
    
        If ydensity is not specified, it is assumed to be equal to
        xdensity.

        If equalize_densities is True, then only one density can be
        supplied, and this is not assumed to match the bounds (i.e. it
        is nominal): it may be adjusted.
        """
        if equalize_densities:
            if ydensity!=None: raise TypeError(
                "Can't specify xdensity and ydensity and request equal " \
               +"densities in each dimension.")
            bounds,xdensity = self.__equalize_densities(bounds,xdensity)

        self.true_bounds = bounds
        self.xdensity, self.ydensity = xdensity, ydensity or xdensity
        self.lbrt = array(bounds.lbrt())


    def __equalize_densities(self,nominal_bounds,nominal_density):
        """
        Calculate the true density along x, and adjust the top and
        bottom bounds so that the density along y will be equal.

        Returns (adjusted_bounds,true_density)
        """
        left,bottom,right,top = nominal_bounds.lbrt()
        width = right-left; height = top-bottom
        center_y = bottom + height/2.0
        # The true density is not equal to the nominal_density
        # when nominal_density*(right-left) is not an integer.
        true_density = int(nominal_density*(width))/float((width))

        n_cells = round(height*true_density,0)
        adjusted_half_height = n_cells/true_density/2.0
        # (The above might be clearer as (step*n_units)/2.0, where
        # step=1.0/density.)
        
        return (BoundingBox(points=((left,  center_y-adjusted_half_height),
                                    (right, center_y+adjusted_half_height))),
                true_density)
    

    def sheet2matrix(self,x,y):
        """
        Convert a point (x,y) in Sheet coordinates to continuous matrix
        coordinates.

        Returns (float_row,float_col), where float_row corresponds to y,
        and float_col to x.

        Valid for scalar or array x and y.

        Note about Bounds
        For a Sheet with BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))
        and density=3, x=-0.5 corresponds to float_col=0.0 and x=0.5
        corresponds to float_col=3.0.  float_col=3.0 is not inside the
        matrix representing this Sheet, which has the three columns
        (0,1,2). That is, x=-0.5 is inside the BoundingBox but x=0.5
        is outside. Similarly, y=0.5 is inside (at row 0) but y=-0.5
        is outside (at row 3) (it's the other way round for y because
        the matrix row index increases as y decreases).
        """
        # First translate to (left,top), which is [0,0] in the matrix,
        # then scale to the size of the matrix. The y coordinate needs
        # to be flipped, because the points are moving down in the
        # sheet as the y index increases in the matrix.
        float_col = (x-self.lbrt[0]) * self.__xdensity
        float_row = (self.lbrt[3]-y) * self.__ydensity
        return float_row, float_col


    def sheet2matrixidx(self,x,y):
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
        r,c = self.sheet2matrix(x,y)
        r = floor(r)
        c = floor(c)
        return int(r), int(c)


    def sheet2matrixidx_array(self,x,y):
        """
        sheet2matrixidx but for arrays of x and y.
        """
        r,c = self.sheet2matrix(x,y)
        r = floor(r)
        c = floor(c)
        return r.astype(int), c.astype(int)


    def matrix2sheet(self,float_row,float_col):
        """
        Convert a floating-point location (float_row,float_col) in matrix
        coordinates to its corresponding location (x,y) in sheet
        coordinates.

        Valid for scalar or array float_row and float_col.

        Inverse of sheet2matrix().
        """
        x = float_col*self.__xstep + self.lbrt[0]
        y = self.lbrt[3] - float_row*self.__ystep
        return x, y


    def matrixidx2sheet(self,row,col):
        """
        Return (x,y) where x and y are the floating point coordinates of
        the *center* of the given matrix cell (row,col). If the matrix cell
        represents a 0.2 by 0.2 region, then the center location returned
        would be 0.1,0.1.

        NOTE: This is NOT the strict mathematical inverse of
        sheet2matrixidx(), because sheet2matrixidx() discards all but the integer
        portion of the continuous matrix coordinate.

        Valid only for scalar row and col.
        """
        x,y = self.matrix2sheet((row+0.5), (col+0.5))

        # Rounding is useful for comparing the result with a floating point number
        # that we specify by typing the number out (e.g. fp = 0.5).
        # Round eliminates any precision errors that have been compounded
        # via floating point operations so that the rounded number will better
        # match the floating number that we type in.
        return round(x,10),round(y,10)


    def matrixidx2sheet_array(self,row,col):
        """
        matrixidx2sheet() but for arrays.
        """
        x,y = self.matrix2sheet((row+0.5), (col+0.5))
        return around(x,10),around(y,10)


    def sheetcoordinates_of_matrixidx(self):
        """
        Return x,y where x is a vector of sheet coordinates
        representing the x-center of each matrix cell, and y
        represents the corresponding y-center of the cell.
        """
        n_rows,n_cols = self.shape
        rows = array(range(n_rows)); cols = array(range(n_cols))
        return self.matrixidx2sheet_array(rows,cols)


    ### CEBHACKALERT: move these two methods to Slice.
    def bounds2slice(self,slice_bounds):
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

        t_m,l_m = self.sheet2matrix(l,t)
        b_m,r_m = self.sheet2matrix(r,b)

        l_idx = int(ceil(l_m-0.5))
        t_idx = int(ceil(t_m-0.5))
        r_idx = int(floor(r_m+0.5))
        b_idx = int(floor(b_m+0.5))

        return t_idx,b_idx,l_idx,r_idx


    def slice2bounds(self,slice_):
        """
        Construct the bounds that corresponds to the given slice.
        This way, this function is an exact transform of bounds2slice. 
        That enables to retrieve the slice information from the bounding box.
        """
        r1,r2,c1,c2 = slice_

        left,bottom = self.matrix2sheet(r2,c1)
        right, top  = self.matrix2sheet(r1,c2)

        return BoundingBox(points=((left,bottom),
                                   (right,top)))


    
class Sheet(EventProcessor,CoordinateTransformer):
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
          
    sheet_view_dict is a dictionary that stores SheetViews,
    i.e. representations of the sheet for use by analysis or plotting
    code.    
    """
    _abstract_class_name = "Sheet"

    bounds = BoundingRegionParameter(
        BoundingBox(radius=0.5),constant=True,
        doc="""
            User-specified BoundingBox of the Sheet coordinate area
            covered by this Sheet.  The left and right bounds--if
            specified--will always be observed, but the top and bottom
            bounds may be adjusted to ensure the density in the y
            direction is the same as the density in the x direction.
            In such a case, the top and bottom bounds are adjusted
            such that the center y point remains the same, and each
            bound is as close as possible to its specified value. The
            actual value of this Parameter is not adjusted, but the
            true bounds may be found from the 'true_bounds' attribute
            of this object.
            """)
    
    ### JABHACKALERT: Should be type Number, but that causes problems
    ### when instantiating Sheets in the Model Editor.
    density = Parameter(
        default=10,constant=True,
        doc="""
            User-specified number of processing units per 1.0 distance
            horizontally or vertically in Sheet coordinates. The actual
            number may be different because of discretization; the matrix
            needs to tile the plane exactly, and for that to work the
            density may need to be adjusted.  For instance, an area of 3x2
            cannot have a density of 2 in each direction. The true density
            may be obtained from either the xdensity or ydensity attribute
            (for a Sheet, these are identical).
            """)
    
    # JABALERT: Should be set per-projection, not per-Sheet, right?
    learning = BooleanParameter(
        True,
        doc="""
            Setting this to False tells the Sheet not to change its
            permanent state (e.g. any connection weights) based on
            incoming events.
            """)

    precedence = Number(
        default = 0.1, softbounds=(0.0,1.0),
        doc='Allows a sorting order for Sheets, e.g. in the GUI.')


    def __init__(self,equalize_densities=True,**params):
        """
        Initialize this object as an EventProcessor, then also as
        a CoordinateTransformer with equal xdensity and ydensity.

        If equalize_densities is False, xdensity and ydensity are
        not guaranteed to be the same, which would likely violate
        assumptions made about sheets in other places.        """

        EventProcessor.__init__(self,**params)

        # Now initialize this object as a CoordinateTransformer, with
        # the same density along y as along x (unless equalize_densities
        # is False).
        CoordinateTransformer.__init__(self,self.bounds,self.density,
                                       equalize_densities=equalize_densities)

        n_units = round((self.lbrt[2]-self.lbrt[0])*self.xdensity,0)
        if n_units<1: raise ValueError(
           "Sheet bounds and density must be specified such that the "+ \
           "sheet has at least one unit in each direction; " \
           +self.name+ " does not.")

        # setup the activity matrix
        self.activity = zeros(self.shape,Float)

        # For non-learning inputs
        self.__saved_activity = []          

        ### JABALERT: Should perhaps rename this to view_dict
        self.sheet_view_dict = {}


    ### JABALERT: This should be deleted now that sheet_view_dict is public
    ### JC: shouldn't we keep that, or at least write a function in
    ### utils that deletes a value in a dictinnary without returning an
    ### error if the key is not in the dict?  I leave for the moment,
    ### and have to ask Jim to advise.
    def release_sheet_view(self,view_name):
        """
        Delete the dictionary entry with key entry 'view_name' to save
        memory.
        """
	if self.sheet_view_dict.has_key(view_name):   
	    del self.sheet_view_dict[view_name]


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
        # CEBHACKALERT: use matrixidx2sheet_array
        coords = [self.matrixidx2sheet(r,0) for r in range(rows-1,-1,-1)]
        return [y for (x,y) in coords]

    def sheet_cols(self):
        """
        Return a list of X-coordinates corresponding to the columns
        of the activity matrix of the sheet.
        """
        rows,cols = self.activity.shape
        # CEBHACKALERT: use matrixidx2sheet_array
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
        


class Slice(object):
    """
    Represents a slice of a CoordinateTransformer; i.e., an
    array specifying the row and column start and end points
    for a submatrix of the CoordinateTransformer.

    A Slice() is created from the specified slice_bounds by
    calculating the slice that corresponds to the bounds (see
    CoordinateTransformer.bounds2slice).

    The slice elements can be recovered by unpacking an instance
    (e.g. k = Slice(); r1,r2,c1,c2 = k).

    The exact bounds corresponding to the calculated slice are
    available as the 'bounds' attribute.

    Actions such as translate() do not respect the bounds of the
    CoordinateTransformer; to have the slice cropped to the
    CoordinateTransformer's bounds, use crop_to_sheet().
    """
    ### Allows shape to work like Numeric.array's
    # CEBHACKALERT: can this method be made private?
    def get_shape(self):
        """Return the shape of the slice."""
        r1,r2,c1,c2 = self.__slice
        return (r2-r1,c2-c1)
    shape = property(get_shape)

    def __init__(self,slice_bounds,coordinate_transformer):
        """
        Store the coordinate_transformer, calculate the
        slice corresponding to the specified slice_bounds
        (see CoordinateTransformer.bounds2slice()), and
        store the bounds that exactly correspond to that
        calculated slice.

        The slice_bounds do not have to be within the
        bounds of the coordinate_transformer. The method
        crop_to_bounds() can be called to ensure this
        is true.
        """
        self.__ct = coordinate_transformer
        self.__slice = self.__ct.bounds2slice(slice_bounds)
        self.bounds = self.__ct.slice2bounds(self.__slice)

    def tuple(self):
        r1,r2,c1,c2 = self.__slice
        return (r1,r2,c1,c2)


    def __iter__(self):
        """
        Make this object behave like a sequence.

        Specifically, allows unpacking:
        slice_ = Slice()
        r1,r2,c1,c2 = k
        """
        return iter(self.__slice)


    def translate(self, r, c):
        """
        Translate the slice by the specified number of rows
        and columns.
        """
        r1,r2,c1,c2 = self.__slice
        r1+=r; r2+=r
        c1+=c; c2+=c
        self._set_slice(array((r1,r2,c1,c2)))

    # CEBHACKALERT: temporarily available for outside use
    def _set_slice(self,slice_):
        """
        bypass creation of slice from bounds.
        """
        if not isinstance(slice_,ArrayType):
            self.__slice = array(slice_)
        else:
            self.__slice = slice_
        self.bounds = self.__ct.slice2bounds(self.__slice)


    def submatrix(self,matrix):
        """
        Return the submatrix of the specified matrix specified by this
        slice.

        Equivalent to computing the intersection between the
        CoordinateTransformer's bounds and the slice_bounds, and
        returning the corresponding submatrix of the given matrix.

        The submatrix is just a view into the sheet_matrix; it is not
        an independent copy.
        """
        r1,r2,c1,c2 = self.__slice
        return matrix[r1:r2,c1:c2]

    ## CEBHACKALERT: should be crop_to_bounds
    def crop_to_sheet(self):
        """
        Crop the slice to the CoordinateTransformer's bounds.
        """
        r1,r2,c1,c2 = self.__ct.bounds2slice(self.__ct.true_bounds)
        maxrow,maxcol = r2-r1,c2-c1
                        
        t_idx,b_idx,l_idx,r_idx = self.__slice

        rstart = max(0,t_idx)
        rbound = min(maxrow,b_idx)
        cstart = max(0,l_idx)
        cbound = min(maxcol,r_idx)
        
        self._set_slice((rstart,rbound,cstart,cbound))



