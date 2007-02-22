"""
Provides SheetCoordinateSystem, allowing conversion between the two
coordinate systems used in Topographica.

'Sheet coordinates' allow simulation parameters to be specified in
units that are density-independent, whereas 'matrix coordinates'
provide a means of realizing the continuous sheets.

Hence we can have a pair of 'sheet coordinates' (x,y); floating-point
Cartesian coordinates indicating an arbitrary point on the sheet's plane.
We can also have a pair of 'matrix coordinates' (r,c), which are used
to address an underlying matrix. These matrix coordinates are also
floating-point numbers to allow precise conversion between the two
schemes. Where it is necessary to address a specific element of the
matrix (as is often the case in calculations), we also have the usual
matrix index coordinates (r_idx, c_idx). We refer to these as
matrixidx coordinates. SheetCoordinateSystem provies methods for converting
between sheet and matrix coordinates, as well as sheet and matrixidx
coordinates.

Everyone should use these facilities for conversions between the two
coordinate systems to guarantee consistency.




Example of how the matrix stores the representation of the Sheet
================================================================

For the purposes of this example, assume the goal is a Sheet with
density=3 that has a 1 at (-1/2,-1/2), a 5 at (0.0,0.0), and a 9 at
(1/2,1/2).  More precisely, for this Sheet,

the continuous area from -1/2,-1/2 to -1/6,-1/6 has value 1, 
the continuous area from -1/6,-1/6 to  1/6,1/6  has value 5, and 
the continuous area from  1/6,1/6  to  1/2,1/2  has value 9.

With the rest of the elements filled in, the Sheet would look like::

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
these Sheet coordinates is::

  [[7 8 9]
   [4 5 6]
   [1 2 3]]

If we have such a matrix, we can access it in one of two ways: Sheet
or matrix/matrixidx coordinates.  In matrixidx coordinates, the matrix is indexed
by rows and columns, and it is possible to ask for the element at
location [0,2] (which returns 9 as in any normal row-major matrix).
But the values can additionally be accessed in Sheet coordinates,
where the matrix is indexed by a point in the Cartesian plane.  In
Sheet coordinates, it is possible to ask for the element at location
(0.3,0.02), which returns floating-point matrix coordinates that can
be cropped to give the nearest matrix element, namely the one with
value 6.

Of course, it would be an error to try to pass matrix coordinates like
[0,2] to the sheet2matrix calls; the result would be a value far
outside of the actual matrix.

$Id$
"""

__version__ = '$Revision$'


from numpy.oldnumeric import zeros,array,floor,ceil,around

from boundingregion import BoundingBox



# Note about the 'bounds-master' approach we have adopted
# =======================================================
#
# Our current approach is a "bounds-master" approach, where we trust
# the user's specified x width, and choose the nearest density and y
# height to make that possible.  The advantage of this is that when we
# change the density (which is often), each such simulation is the
# best possible approximation to the given area.  Generally, the area
# is much more meaningful than the density, so this approach makes
# sense.  Plus, the y height is usually the same as the x width, so
# it's not usually a problem that the y height is not respected.  The
# disadvantage is that the user's area can only be trusted in one
# dimension, because of wanting to avoid the complication of separate
# xdensity and ydensity, which makes this approach very difficult to
# explain to the user.
#
# The other approach is density-master: trust the user's specified
# density as-is, and simply choose the nearest area that fits that
# density.  The advantages are that (a) it's very simple to describe
# and reason about, and (b) if a user asks for a different area, they
# get a true subsection of the same simulation they would have gotten
# at the larger area.  The disadvantage is that the simulation isn't
# the best approximation of the given area that it could be -- e.g. at
# low densities, the sheet area could be quite significantly different
# than the one the user requested.  Plus, if we took this approach
# seriously, then we'd let the density specify the matrix coordinate
# system entirely, including the origin, which would mean that the
# actual area would often be offset from the intended one, which is
# even worse.  Differences between the area and the offset could cause
# severe problems in the alignment of projections between sheets with
# different densities, which would make low-density versions of
# hierarchical models behave very strangely.




class SheetCoordinateSystem(object):
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
        r1,r2,c1,c2 = self.bounds2slice(self.bounds)
        return (r2-r1,c2-c1)

    ### shape is a property so that it's like Numeric.array.shape
    shape = property(get_shape)


    def __init__(self,bounds,xdensity,ydensity=None):
        """
        Store the bounds (as l,b,r,t in an array), xdensity, and
        ydensity.
    
        If ydensity is not specified, it is assumed that the specified
        xdensity is nominal and that the true xdensity should be
        calculated. The top and bottom bounds are adjusted so that
        the ydensity is equal to the xdensity. 
        
        If both xdensity and ydensity are specified, these and the bounds
        are taken to be exact and are not adjusted.
        """
        if not ydensity:
            bounds,xdensity = self.__equalize_densities(bounds,xdensity)

        self.bounds = bounds
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
        true_density = int(nominal_density*(width))/float(width)

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
