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
from parameterclasses import BooleanParameter, Number, Parameter, NumericTuple
from numpy.oldnumeric import zeros,array,Float,ArrayType

from boundingregion import BoundingBox, BoundingRegionParameter
import sheetview 

activity_type = Float

class Sheet(EventProcessor,SheetCoordinateSystem):
    """
    The generic base class for neural sheets.

    See SheetCoordinateSystem for how Sheet represents space, and
    EventProcessor for how Sheet handles time.
    """
    __abstract = True

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

    precedence = Number(default = 0.1, softbounds=(0.0,1.0),
        doc='Allows a sorting order for Sheets, e.g. in the GUI.')

    layout_location = NumericTuple(default = (-1,-1),hidden=True,doc="""
        Location for this Sheet in an arbitrary pixel-based space
        in which Sheets can be laid out for visualization.""")


    def __init__(self,**params):
        """
        Initialize this object as an EventProcessor, then also as
        a SheetCoordinateSystem with equal xdensity and ydensity.

        sheet_views is a dictionary that stores SheetViews,
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
        self._updating_state = []  

        ### JABALERT: Should perhaps rename this to view_dict
        self.sheet_views = {}


    ### JABALERT: This should be deleted now that sheet_views is public
    ### JC: shouldn't we keep that, or at least write a function in
    ### utils that deletes a value in a dictinnary without returning an
    ### error if the key is not in the dict?  I leave for the moment,
    ### and have to ask Jim to advise.
    def release_sheet_view(self,view_name):
        """
        Delete the dictionary entry with key entry 'view_name' to save
        memory.
        """
	if self.sheet_views.has_key(view_name):   
	    del self.sheet_views[view_name]


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
        # CEBALERT: Should use matrixidx2sheet_array
        coords = [self.matrixidx2sheet(r,0) for r in range(rows-1,-1,-1)]
        return [y for (x,y) in coords]

    def sheet_cols(self):
        """
        Return a list of X-coordinates corresponding to the columns
        of the activity matrix of the sheet.
        """
        rows,cols = self.activity.shape
        # CEBALERT: Should use matrixidx2sheet_array
        coords = [self.matrixidx2sheet(0,c) for c in range(cols)]
        return [x for (x,y) in coords]


    def state_push(self):
        """
        Save the current state of this sheet to an internal stack.

        This method is used by operations that need to test the
        response of the sheet without permanently altering its state,
        e.g. for measuring maps or probing the current behavior
        non-invasively.  By default, only the activity pattern of this
        sheet is saved, but subclasses should add saving for any
        additional state that they maintain, or strange bugs are
        likely to occur.  The state can be restored using state_pop().

        Note that Sheets that do learning need not save the
        values of all connection weights, if any, because
        learning can be turned off explicitly.  Thus this method
        is intended only for shorter-term state.
        """
        self.__saved_activity.append(array(self.activity))

    def state_pop(self):
        """
        Pop the most recently saved state off the stack.

        See state_push() for more details.
        """
        self.activity = self.__saved_activity.pop()

    def activity_len(self):
        """Return the number of items that have been saved by state_push()."""
        return len(self.__saved_activity)

    def stop_updating(self):
        """
        Save the current state of the learning parameter to an internal stack. 
        Turns off the updating parameter for the sheet.
        """
        self._updating_state.append(self.learning)
        self.learning=False

    def restore_updating(self):
        """Pop the most recently saved learning parameter off the stack."""
        self.learning = self._updating_state.pop()




# Needs cleanup/rename:
#
# since it's different from slice.  It's our special slice that's an
# array specifying row_start,row_stop,col_start,col_stop.
# 
# In python, a[slice(0,2)] (where a is a list/array/similar) is
# equivalent to a[0:2].
#
# So, not sure what to call this class. (Will need to rename some
# methods, too.)

from numpy import int32,ndarray

class Slice(ndarray):
    """
    Represents a slice of a SheetCoordinateSystem; i.e., an array
    specifying the row and column start and end points for a submatrix
    of the SheetCoordinateSystem.

    The slice is created from the supplied slice_bounds by calculating
    the slice that corresponds most closely to the specified bounds.
    Therefore, the slice does not necessarily correspond exactly to
    the specified bounds. Slice stores the bounds that do exactly
    correspond to the slice in the 'bounds' attribute.

    Note that the slice does not respect the bounds of the
    SheetCoordinateSystem, and that actions such as translate() also
    do not respect the bounds. To ensure that the slice is within the
    SheetCoordinateSystem's bounds, use crop_to_sheet().
    """
    def __new__(cls, slice_bounds, sheet_coordinate_system):
        """
        Create a slice of the given sheet_coordinate_system from the
        specified bounds, and store the bounds that exactly correspond
        to the created slice in the 'bounds' attribute.
        """
        # I couldn't find documentation on subclassing array; I used
        # the following as reference:
        # http://scipy.org/scipy/numpy/browser/branches/maskedarray/numpy/ma/tests/test_subclassing.py?rev=4577
        slice_ = sheet_coordinate_system.bounds2slice(slice_bounds)
        bounds = sheet_coordinate_system.slice2bounds(slice_)

        a = array(slice_, dtype=int32, copy=False).view(cls)
        a._scs = sheet_coordinate_system
        a.bounds = bounds
        return a

    def __array_finalize__(self,obj):
        self._scs = getattr(obj,'_scs',None)
        self.bounds = getattr(obj,'bounds',None)
        

    def submatrix(self,matrix):
        """
        Return the submatrix of the given matrix specified by this
        slice.

        Equivalent to computing the intersection between the
        SheetCoordinateSystem's bounds and the slice_bounds, and
        returning the corresponding submatrix of the given matrix.

        The submatrix is just a view into the sheet_matrix; it is not
        an independent copy.
        """
        return matrix[self[0]:self[1],self[2]:self[3]]
    

##     def slice2d(self):
##         return slice(self[0],self[1]),slice(self[2],self[3])

        
    def translate(self, r, c):
        """
        Translate the slice by the specified number of rows
        and columns.
        """
        self+=[r,r,c,c]
        self.bounds = self._scs.slice2bounds(self)


    def set_from_slice(self,slice_):
        self.put([0,1,2,3],slice_)
        self.bounds = self._scs.slice2bounds(slice_)


    # shouldn't the two method names below refer to scs rather than sheet?
    def shape_on_sheet(self):
        return self[1]-self[0],self[3]-self[2]


    def crop_to_sheet(self): 
        """
        Crop the slice to the SheetCoordinateSystem's bounds.
        """
        maxrow,maxcol = self._scs.shape
                        
        self[0] = max(0,self[0])
        self[1] = min(maxrow,self[1])
        self[2] = max(0,self[2])
        self[3] = min(maxcol,self[3])

        self.bounds = self._scs.slice2bounds(self)








