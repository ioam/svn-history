"""
Topographica SheetView objects and its subclasses.

For use with the Topographica plotting and data analysis mechanisms.
A Sheet object has its internal data which remains hidden, but it will
create views of this data depending on the Sheet defaults or the
information requested.  This way there can be multiple views recorded
for a single sheet, and a view can be passed around independent of the
originating source object.

$Id$
"""
import sys
import types
import operator

import Numeric
import sheet
from base import TopoObject

# Valid operations that a SheetView should support for the list of
# sheets passed in.  There are other things that would be useful
# such as masking which will requrire a bit more work.
ADD      = 'ADD'
SUBTRACT = 'SUB'
MULTIPLY = 'MUL'
DIVIDE   = 'DIV'
# These 'operator' functions require 2 parameters when using 'apply'.
operations = {ADD : operator.add,
              SUBTRACT : operator.sub,
              MULTIPLY : operator.mul,
              DIVIDE : operator.truediv}


class SheetView(TopoObject):
    """
    A SheetView is constructed from a matrix of values, a bounding box
    for that matrix, and a name.  There are two major ways to create a
    SheetView: one is from a single matrix of data from a single
    sheet, the other is by combining the matrices from multiple
    matrices or SheetViews.
    """

    def __init__(self, (term_1, term_2), **params):
        """
        __init__(self, input_tuple, **params)

        Three types of input_tuples.
        1.  (matrix_data, matrix_bbox)  
	    This form locks the value of the sheetview to a single matrix.
            Terminating case of a composite SheetView.
            
        2.  (operation, [tuple_list])
	    'operation' is performed on the matrices collected from tuple_list.
                see the list of valid operations in operations.keys()
	    Each tuple in the tuple_list is one of the following:
                (SheetView, None)
                    Another SheetView may be passed in to create nested plots.
	        (matrix_data, bounding_box)
                    Static matrix data complete with bounding box.
	        (Sheet, sheet_view_name)
                    This gets sheet_name.sheet_view(sheet_view_name) each time
                    the current SheetView has its data requested by .view().

        3.  (Sheet, sheet_view_name)
                Degenerate case that will pull data from another SheetView
                and not do any additional processing.  Don't yet know a
                use for this case, but documented for future possible use.
        """
        super(SheetView,self).__init__(**params)
        # Assume there's no such thing as an operator that can be mistaken
        # for a matrix_data element.  This is true as long as the real
        # values of the operator keys are strings.
        if term_1 not in operations.keys():      
            self.operation = ADD          
            self._view_list = [(term_1, term_2)]
        else:
            self.operation = operations[term_1]
            self._view_list = term_2
            if not isinstance(self._view_list,types.ListType):
                self._view_list = [self._view_list]
            

    def view(self):
        """
        Return the requested view as a matrix.  If the constructor was
        given multiple maps, the view must be built before being
        returned, which may lock in new views of data from the
        specified sheets.

        Input is the variable self._view_list which is a list of
        tuples, with each tuple being a matrix and a bounding box, or
        a sheet and a map name.  The sequence cannot be dumped into
        maps just once because the raw maps may have changed, so other
        sheets must be queried for the data.
        """
        maps = []
        print self._view_list
        for tup in self._view_list:
            print tup
            (term_1, term_2) = tup
            if isinstance(term_1,sheet.Sheet):
                maps.append(term_1.sheet_view(term_2))
            elif isinstance(term_1,SheetView):
                maps.append(term_1.view())         # Don't care about term_2
            else:
                maps.append((term_1, term_2))       # Assume it is a matrix

        # Convert the list of (matrix, bbox) tuples into a single
        # matrix and another bounding box.
        return self.sum_maps(maps)


    def sum_maps(self,maps):
        """
        Convert the list of (matrix, bbox) tuples into a single matrix
        and another bounding box.  Not a protected function as it could
        prove useful to other areas of the simulator.

        THIS MUST BE EXPANDED IN THE FUTURE TO MAKE PROPER USE OF THE
        BOUNDING BOX INFORMATION. CURRENT (8/04) IMPLEMENTATION
        PASSES THE FIRST MAP IN THE LIST AS THE BOUNDING BOX FOR THE
        CONSTRUCTED VIEW.

        WOULD HAVE DONE AN ADD/INTERSECTION/UNION, BUT BOUNDINGREGION
        DOES NOT YET SUPPORT SUCH OPERATIONS.
        """
        # result = reduce(self.operation,maps)
        # return (result, maps[0][1])
        result = maps.pop(0)
        for m in maps:
            # Needs to be changed
            result = (apply(self.operation, (result[0], m[0])), result[1]) 
        return result


class UnitView(SheetView):
    """
    NOT COMPLETED, NOR EXPECTING TO IN THE TIME REMAINING OF SUMMER 2004

    Consists of an X,Y position for the unit that this View is
    created.
    """

    def __init__(self, x, y, input_tuple, **params):
        super(UnitView,self).__init__(input_tuple, **params)
        self.x = x
        self.y = y

