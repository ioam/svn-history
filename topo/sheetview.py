"""
Topographica SheetView objects and its subclasses.

For use with the Topographica plotting mechanisms.  A Sheet object has
its internal data which remains hidden, but it will create views of
this data depending on the Sheet defaults or the information
requested.  This way there can be multiple views recorded for a single
sheet, and a view can be passed around independent of the originating
source object.

$Id$
"""
import sys

import Numeric        # Only used for the __main__ test lines
from base import TopoObject

class SheetView(TopoObject):
    """
    A SheetView consists of a matrix of values, a bounding box for that
    matrix, and a name.
    """

    def __init__(self, view_data, view_box=None, **params):
        super(SheetView,self).__init__(**params)
        self.view_data = view_data
        self.view_box = view_box

    def _report(self):
        """Print out the member data"""
        self.message('view_data =', self.view_data)
        self.message('view_box =', self.view_box)



class UnitView(SheetView):
    """
    Consists of an X,Y position for the unit that this View is
    created.
    """

    def __init__(self, x, y, view_data, view_box=None, **params):
        super(UnitView,self).__init__(view_data, view_box, **params)
        self.x = x
        self.y = y

    def _report(self):
        """Print out the member data"""
        self.message('x',self.x,'| y',self.y)
        super(UnitView,self)._report()
    


if __name__ == '__main__':

    sv = SheetView(Numeric.array([1.2,1.3,1.4]),4,name='SampleSheet')
    sv._report()
    uv = UnitView(1,2,Numeric.array([1.2,1.3,1.4]),4,name='TmpUnit')
    uv._report()
    
    
