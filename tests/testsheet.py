"""
Unit tests for sheet.py module.

$Id$
"""

import unittest
import topo
from topo.sheet import *
import topo.base
from topo import boundingregion


class TestCoordinateTransforms(unittest.TestCase):
    def makeBox(self):
        self.box = boundingregion.BoundingBox(points=((self.left,self.bottom),
                                                      (self.right,self.top)))
        linear_density = sqrt(self.density)
        self.rbound = int(linear_density*(self.top-self.bottom))
        self.cbound = int(linear_density*(self.right-self.left))
    def test_s2m_left_top(self):
        r,c = 0,0
        x,y = self.left,self.top
        self.assertEqual(sheet2matrix(x,y,self.box,self.density), (r,c))
    def test_s2m_left_bottom(self):
        r,c = self.rbound, 0
        x,y = self.left, self.bottom
        self.assertEqual(sheet2matrix(x,y,self.box,self.density),(r,c))
    def test_s2m_right_top(self):
        r,c = 0,self.cbound
        x,y = self.right,self.top
        self.assertEqual(sheet2matrix(x,y,self.box,self.density),(r,c))
    def test_s2m_right_bottom(self):
        r,c = self.rbound,self.cbound
        x,y = self.right,self.bottom
        self.assertEqual(sheet2matrix(x,y,self.box,self.density),(r,c))

    def test_m2s_left_top(self):
        r,c = 0,0
        x,y = self.left,self.top
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_m2s_left_bottom(self):
        r,c = self.rbound,0
        x,y = self.left,self.bottom
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_m2s_right_top(self):
        r,c = 0,self.cbound
        x,y = self.right,self.top
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_m2s_right_bottom(self):
        r,c = self.rbound,self.cbound
        x,y = self.right,self.bottom
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_sheet_view(self):
        s = Sheet()
        sview = s.sheet_view()
        sview = s.sheet_view('Activation')
        log_level = s.print_level
        minlog_level = topo.base.min_print_level

        # Disable the warning that we know will be displayed
        s.print_level = topo.base.SILENT
        topo.base.min_print_level = topo.base.SILENT
        s.sheet_view('Orientation')
        s.print_level = log_level
        topo.base.min_print_level = minlog_level

        s.add_sheet_view('Orientation',sview)
        sview = s.sheet_view('Orientation')



class TestBox1Coordinates(TestCoordinateTransforms):
    """
    Test coordinate transformations using the standard, origin-centered unit box
    with density 100.
    """
    def setUp(self):
        self.left = -0.5
        self.bottom = -0.5
        self.top = 0.5
        self.right = 0.5
        self.density = 100
        self.makeBox()

class TestBox2Coordinates(TestCoordinateTransforms):
    """
    Test coordinate transformations on the box defined by (1,1), (3,4),
    with density 50.
    """
    def setUp(self):
        self.left = 1
        self.bottom = 1
        self.right = 3
        self.top  = 4
        self.density = 64
        self.makeBox()

cases = [TestBox1Coordinates,
         TestBox2Coordinates]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
        
