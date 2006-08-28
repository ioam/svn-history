"""
Neural sheet objects and associated functions.

The Sheet class is the base class for EventProcessors that simulate
topographically mapped sheets of units (neurons or columns).  A Sheet
is an EventProcessor that maintains a rectangular array of activity
values, and sends the contents of this array as the data element in
events.

The Sheet itself is a SheetCoordinateSystem, so that units may be
accessed by sheet or matrix coordinates. In general, however, sheets
should be thought of as having arbitrary density and sheet coordinates
should be used wherever possible, except when the code needs direct
access to a specific unit.  By adhering to this convention, one should
be able to write and debug a simulation at a low density, and then
scale it up to run at higher densities (or down for lower densities)
simply by changing e.g. Sheet.nominal_density.

$Id$
"""

__version__ = '$Revision$'


from simulation import EventProcessor
from sheetcoords import SheetCoordinateSystem
from parameterclasses import BooleanParameter, Number, Parameter
from Numeric import zeros,array,Float,ArrayType

from boundingregion import BoundingBox, BoundingRegionParameter
import sheetview 

activity_type = Float

class Sheet(EventProcessor,SheetCoordinateSystem):
    """
    The generic base class for neural sheets.

    See SheetCoordinateSystem for how Sheet represents space, and
    EventProcessor for how Sheet handles time.
    """
    _abstract_class_name = "Sheet"

    nominal_bounds = BoundingRegionParameter(
        BoundingBox(radius=0.5),constant=True,
        doc="""
            User-specified BoundingBox of the Sheet coordinate area
            covered by this Sheet.  The left and right bounds--if
            specified--will always be observed, but the top and bottom
            bounds may be adjusted to ensure the density in the y
            direction is the same as the density in the x direction.
            In such a case, the top and bottom bounds are adjusted
            so that the center y point remains the same, and each
            bound is as close as possible to its specified value. The
            actual value of this Parameter is not adjusted, but the
            true bounds may be found from the 'bounds' attribute
            of this object.
            """)
    
    nominal_density = Number(
        default=10,constant=True,
        doc="""
            User-specified number of processing units per 1.0 distance
            horizontally or vertically in Sheet coordinates. The actual
            number may be different because of discretization; the matrix
            needs to tile the plane exactly, and for that to work the
            density might need to be adjusted.  For instance, an area of 3x2
            cannot have a density of 2 in each direction. The true density
            may be obtained from either the xdensity or ydensity attribute
            (since these are identical for a Sheet).
            """)
    
    # JABALERT: Should be set per-projection, not per-Sheet, right?
    learning = BooleanParameter(True,
        doc="""
            Setting this to False tells the Sheet not to change its
            permanent state (e.g. any connection weights) based on
            incoming events.
            """)

    precedence = Number(
        default = 0.1, softbounds=(0.0,1.0),
        doc='Allows a sorting order for Sheets, e.g. in the GUI.')


    def __init__(self,**params):
        """
        Initialize this object as an EventProcessor, then also as
        a SheetCoordinateSystem with equal xdensity and ydensity.

        sheet_view_dict is a dictionary that stores SheetViews,
        i.e. representations of the sheet for use by analysis or plotting
        code.    
        """
        EventProcessor.__init__(self,**params)

        # Initialize this object as a SheetCoordinateSystem, with
        # the same density along y as along x.
        SheetCoordinateSystem.__init__(self,self.nominal_bounds,self.nominal_density)

        n_units = round((self.lbrt[2]-self.lbrt[0])*self.xdensity,0)
        if n_units<1: raise ValueError(
           "Sheet bounds and density must be specified such that the "+ \
           "sheet has at least one unit in each direction; " \
           +self.name+ " does not.")

        # setup the activity matrix
        self.activity = zeros(self.shape,activity_type)

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
    Represents a slice of a SheetCoordinateSystem; i.e., an
    array specifying the row and column start and end points
    for a submatrix of the SheetCoordinateSystem.

    A Slice() is created from the specified slice_bounds by
    calculating the slice that corresponds to the bounds (see
    SheetCoordinateSystem.bounds2slice).

    The slice elements can be recovered by unpacking an instance
    (e.g. k = Slice(); r1,r2,c1,c2 = k).

    The exact bounds corresponding to the calculated slice are
    available as the 'bounds' attribute.

    Actions such as translate() do not respect the bounds of the
    SheetCoordinateSystem; to have the slice cropped to the
    SheetCoordinateSystem's bounds, use crop_to_sheet().
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
        (see SheetCoordinateSystem.bounds2slice()), and
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
        SheetCoordinateSystem's bounds and the slice_bounds, and
        returning the corresponding submatrix of the given matrix.

        The submatrix is just a view into the sheet_matrix; it is not
        an independent copy.
        """
        r1,r2,c1,c2 = self.__slice
        return matrix[r1:r2,c1:c2]

    ## CEBALERT: should be renamed to crop_to_bounds Because
    ## crop_to_sheet and translate are both called many, many times
    ## during CFProjection initialization, it might be worth making
    ## the bounds be accessed as a property so that it wouldn't be
    ## updated twice as it is now, and would instead be cached and
    ## reused.
    def crop_to_sheet(self):
        """
        Crop the slice to the SheetCoordinateSystem's bounds.
        """
        r1,r2,c1,c2 = self.__ct.bounds2slice(self.__ct.bounds)
        maxrow,maxcol = r2-r1,c2-c1
                        
        t_idx,b_idx,l_idx,r_idx = self.__slice

        rstart = max(0,t_idx)
        rbound = min(maxrow,b_idx)
        cstart = max(0,l_idx)
        cbound = min(maxcol,r_idx)
        
        self._set_slice((rstart,rbound,cstart,cbound))



