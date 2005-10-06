"""
Unit tests for sheet.py module.

$Id$
"""

import unittest
import topo
from topo.base.sheet import *
import topo.base.object
import Numeric
from topo.base import boundingregion


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
        r,c = self.rbound-1, 0
        x,y = self.left, self.bottom
        self.assertEqual(sheet2matrix(x,y,self.box,self.density),(r,c))
    def test_s2m_right_top(self):
        r,c = 0,self.cbound-1
        x,y = self.right,self.top
        self.assertEqual(sheet2matrix(x,y,self.box,self.density),(r,c))
    def test_s2m_right_bottom(self):
        r,c = self.rbound-1,self.cbound-1
        x,y = self.right,self.bottom
        self.assertEqual(sheet2matrix(x,y,self.box,self.density),(r,c))

    def test_m2s_left_top(self):
        r,c = 0,0
        x,y = self.left+self.half_unit,self.top-self.half_unit
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_m2s_left_bottom(self):
        r,c = self.rbound-1,0
        x,y = self.left+self.half_unit,self.bottom+self.half_unit
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_m2s_right_top(self):
        r,c = 0,self.cbound
        x,y = self.right-self.half_unit,self.top-self.half_unit
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_m2s_right_bottom(self):
        r,c = self.rbound-1,self.cbound-1
        x,y = self.right-self.half_unit,self.bottom+self.half_unit
        self.assertEqual(matrix2sheet(r,c,self.box,self.density), (x,y))        
    def test_sheet_view(self):
        s = Sheet()
        sview = s.sheet_view()
        sview = s.sheet_view('Activity')
        log_level = s.print_level
        minlog_level = topo.base.object.min_print_level

        s.print_level = topo.base.object.SILENT
        topo.base.object.min_print_level = topo.base.object.SILENT
        s.sheet_view('Orientation')
        s.print_level = log_level
        topo.base.object.min_print_level = minlog_level

        s.add_sheet_view('Orientation',sview)
        sview = s.sheet_view('Orientation')

    def test_sheetview_release(self):
        self.s = Sheet()
        self.s.activity = Numeric.array([[1,2],[3,4]])
        # Call s.sheet_view(..) with a parameter
        sv2 = self.s.sheet_view('Activity')
        self.assertEqual(len(self.s.sheet_view_dict.keys()),0)
        self.s.add_sheet_view('key',sv2)
        self.assertEqual(len(self.s.sheet_view_dict.keys()),1)
        self.s.release_sheet_view('key')
        self.assertEqual(len(self.s.sheet_view_dict.keys()),0)

    def test_coordinate_position(self):
        l,b,r,t = (-0.8,-0.8,0.8,0.8)
        d = 16
        bounds = BoundingBox(points=((l,b),(r,t)))
        density = d**2
        self.assertEqual(sheet2matrix(0.8,0.8,bounds,density),(0,24))
        self.assertEqual(sheet2matrix(0.0,0.0,bounds,density),(12,12))
        self.assertEqual(sheet2matrix(-0.8,-0.8,bounds,density),(24,0))
        self.assertEqual(matrix2sheet(24,0,bounds,density),
                         (((r-l) / int(d*(r-l)) / 2.0) + l,
                          (t-b) / int(d*(t-b)) / 2.0 + b))
        self.assertEqual(matrix2sheet(0,0,bounds,density),
                         (((r-l) / int(d*(r-l)) / 2.0) + l ,
                          (t-b) / int(d*(t-b)) * (int(d*(t-b)) - 0.5) + b))

        xy = matrix2sheet(0,0,bounds,density)
        self.assertTrue(bounds.contains(xy[0],xy[1]))
        self.assertEqual((0,0),sheet2matrix(xy[0],xy[1],bounds,density))

        xy = matrix2sheet(25,25,bounds,density)
        self.assertFalse(bounds.contains(xy[0],xy[1]))
        self.assertNotEqual((24,24),sheet2matrix(xy[0],xy[1],bounds,density))

        xy = matrix2sheet(0,24,bounds,density)
        self.assertTrue(bounds.contains(xy[0],xy[1]))
        self.assertEqual((0,24),sheet2matrix(xy[0],xy[1],bounds,density))

        xy = matrix2sheet(24,0,bounds,density)
        self.assertTrue(bounds.contains(xy[0],xy[1]))
        self.assertEqual((24,0),sheet2matrix(xy[0],xy[1],bounds,density))




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
        self.half_unit = 0.05
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
        self.half_unit = 0.0625
        self.makeBox()

cases = [TestBox1Coordinates,
         TestBox2Coordinates]

suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
        
