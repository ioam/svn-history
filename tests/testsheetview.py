import unittest

import Numeric

from topo.sheet import Sheet
from topo.boundingregion import BoundingBox
from topo.sheetview import *
from topo.image import ImageGenerator
from topo.bitmap import BWMap

# Turn False once development is complete and this module is to be
# included as part of the system unit testing.
DEV = False

class TestSheetView(unittest.TestCase):

    def setUp(self):
        self.s = Sheet()
        self.s.activity = Numeric.array([[1,2],[3,4]])
        self.s2 = Sheet()
        self.s2.activity = Numeric.array([[4,3],[2,1]])
    def test_init(self):
        # s.sheet_view() returns a SheetView
        sv = self.s.sheet_view()
        # Call s.sheet_view(..) with a parameter
        sv2 = self.s.sheet_view('Activity')
        # Define a type 1 SheetView, with matrix and bounding box.
        sv3 = SheetView((self.s.activity, self.s.bounds))
        sv4 = SheetView((self.s2.activity,self.s2.bounds))
        # Define a type 2 SheetView, 
        sv5 = SheetView((ADD,((sv3,None),(sv4,None))))
        sv6 = SheetView((ADD,[(sv3,None),
                              (sv4,None),
                              (self.s2.activity,self.s2.bounds)]))
        sv7 = SheetView((SUBTRACT,[(sv3,None),
                              (sv4,None),
                              (self.s2.activity,self.s2.bounds)]))

        # Define a type 3 SheetView
        sv8 = SheetView((self.s,'Activity'))
        if DEV:
            sv3.message(sv3.view())
            sv6.message('sv6.debug', sv6._view_list)
            sv6.message(sv6.view())


    def test_view(self):
        input = ImageGenerator(filename='tests/testsheetview.ppm',
                        density=10000,
                        bounds=BoundingBox(points=((-0.8,-0.8),(0.8,0.8))))
        sv = input.sheet_view('Activity')
        sv_tuple = sv.view()
        map = BWMap(sv_tuple[0])
        # map.show()


#     def test_generate_coords(self):
#         sv = UnitViewArray((self.s.activity, self.s.bounds))
#         print sv.generate_coords(1,self.s.bounds)
#         


    def test_sum_maps(self):
        """Stub"""
        self.assertEqual(1+1,2)



suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(TestSheetView))
