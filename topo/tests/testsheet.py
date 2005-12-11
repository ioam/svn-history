"""
Unit tests for sheet.py module.

$Id$
"""
__version__='$Revision$'

import unittest
import topo
from topo.base.sheet import *
import topo.base.topoobject
import Numeric
from topo.base import boundingregion
from topo.base.sheetview import SheetView


# CEBHACKALERT: still to test bounds_to_slice(), submatrix(), input_slice()


class TestCoordinateTransforms(unittest.TestCase):
    """    
    """    
    def makeBox(self):
        self.box = boundingregion.BoundingBox(points=((self.left,self.bottom),
                                                      (self.right,self.top)))

        # float bounds for matrix coordinates: these
        # values are actually outside the matrix
        self.rbound = self.density*(self.top-self.bottom)
        self.cbound = self.density*(self.right-self.left)

        # CEBHACKALERT: this is supposed to be a small distance
        D = 0.00001

        # Sheet values around the edge of the BoundingBox
        self.just_in_right_x = self.right - D
        self.just_in_bottom_y = self.bottom + D
        self.just_out_top_y = self.top + D
        self.just_out_left_x = self.left - D

        # Matrix values around the edge of the matrix
        self.just_out_right_idx = self.rbound + D
        self.just_out_bottom_idx = self.cbound + D
        self.just_out_top_idx = 0.0 - D
        self.just_out_left_idx = 0.0 - D


        
    ### sheet2matrix() tests
    #
    def test_sheet2matrix_center(self):
        """
        Check that the center of the Sheet corresponds to the center
        of the matrix.
        """
        x_center = self.left+(self.right-self.left)/2.0
        y_center = self.bottom+(self.top-self.bottom)/2.0
        row, col = sheet2matrix(x_center,y_center,self.box,self.density)
        self.assertEqual((row,col),(self.rbound/2.0,self.cbound/2.0))


    def test_sheet2matrix_left_top(self):
        """
        Check that the top-left of the Sheet is [0,0] in matrix
        coordinates.
        """
        row, col = sheet2matrix(self.left,self.top,self.box,self.density)
        self.assertEqual((row,col),(0,0))


    def test_sheet2matrix_right_bottom(self):
        """
        Check that the bottom-right of the Sheet is [rbound,cbound] in matrix
        coordinates.
        """
        row, col = sheet2matrix(self.right,self.bottom,self.box,self.density)
        self.assertEqual((row,col),(self.rbound,self.cbound))

        
    def test_s2m_m2s(self):
        """
        Check that sheet2matrix() is the inverse of matrix2sheet().
        """
        # top-right corner
        row, col = sheet2matrix(self.right,self.top,self.box,self.density)
        x_right, y_top = matrix2sheet(row,col,self.box,self.density)
        self.assertEqual((x_right,y_top),(self.right,self.top)) 

        # bottom-left corner
        row, col = sheet2matrix(self.left,self.bottom,self.box,self.density)
        x_left, y_bottom = matrix2sheet(row,col,self.box,self.density)
        self.assertEqual((x_left,y_bottom),(self.left,self.bottom)) 



    ### sheet2matrixidx() tests
    #    
    def test_s2midx_left_top(self):
        """
        Test a point just inside the top-left corner of the BoundingBox, and
        one just outside.
        """
        # inside
        r,c = 0,0
        x,y = self.left,self.top
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density), (r,c))

        # outside
        r,c = -1,-1
        x,y = self.just_out_left_x,self.just_out_top_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density), (r,c))


    def test_s2midx_left_bottom(self):
        """
        Test a point just inside the left-bottom corner of the BoundingBox, and
        one just outside.
        """
        # inside
        r,c = self.last_row, 0
        x,y = self.left, self.just_in_bottom_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density),(r,c))

        # outside
        r,c = self.last_row+1, -1
        x,y = self.just_out_left_x, self.bottom
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density),(r,c))


    def test_s2midx_right_top(self):
        """
        Test a point just inside the top-right corner of the BoundingBox, and
        one just outside.
        """
        # inside
        r,c = 0,self.last_col
        x,y = self.just_in_right_x,self.top
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density),(r,c))

        # outside
        r,c = -1,self.last_col+1
        x,y = self.right,self.just_out_top_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density),(r,c))


    def test_s2midx_right_bottom(self):
        """
        Test a point just inside the bottom-right corner of the BoundingBox,
        and the corner itself - which should not be inside.
        """
        # inside 
        r,c = self.last_row,self.last_col
        x,y = self.just_in_right_x,self.just_in_bottom_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density),(r,c))

        # not inside
        r,c = self.last_row+1,self.last_col+1
        x,y = self.right,self.bottom
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.density),(r,c))


    ### matrix2sheet() tests
    def test_matrix2sheet_left_top(self):
        """
        Check that Sheet's (0,0) is the top-left of the matrix.

        Check that just outside the top-left in matrix coordinates
        comes back to Sheet coordinates that are outside the
        BoundingBox.
        """
        x,y = matrix2sheet(0,0,self.box,self.density)
        self.assertEqual((x,y), (self.left,self.top))

        x,y = matrix2sheet(self.just_out_left_idx,self.just_out_top_idx,self.box,self.density)
        self.assertFalse(self.box.contains(x,y))
    

    def test_matrix2sheet_right_bottom(self):
        """
        Check that Sheet's (right,bottom) is the bottom-right in
        matrix coordinates i.e. [rbound,cbound]

        Check that just outside the bottom-right in matrix coordinates
        comes back to Sheet coordinates that are outside the
        BoundingBox.
        """
        x,y = matrix2sheet(self.rbound,self.cbound,self.box,self.density)
        self.assertEqual((x,y), (self.right,self.bottom))

        x,y = matrix2sheet(self.just_out_right_idx,self.just_out_bottom_idx,self.box,self.density)
        self.assertFalse(self.box.contains(x,y))


    def test_matrix2sheet_center(self):
        """
        Check that the center in Sheet coordinates corresponds to
        the center in continuous matrix coordinates.
        """
        x_center = self.left+(self.right-self.left)/2.0
        y_center = self.bottom+(self.top-self.bottom)/2.0
        center_float_row = self.rbound/2.0
        center_float_col = self.cbound/2.0
        x,y = matrix2sheet(center_float_row,center_float_col,self.box,self.density)
        self.assertEqual((x,y),(x_center,y_center))



    ### matrixidx2sheet() tests
    #
    def test_midx2s_left_top(self):
        """
        The top-left matrix cell [0,0] should be given back in Sheet
        coordinates at the center of that cell.

        The cell [-1,-1] outside this corner should come back out of
        the BoundingBox
        """
        # inside
        r,c = 0,0
        x,y = self.left+self.half_unit,self.top-self.half_unit

        test_x, test_y = matrixidx2sheet(r,c,self.box,self.density)
        self.assertEqual((test_x,test_y), (x,y))
        self.assertTrue(self.box.contains(test_x,test_y))

        # outside
        r,c = -1,-1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.density)
        self.assertFalse(self.box.contains(test_x,test_y))
        
        
    def test_midx2s_left_bottom(self):
        """
        The bottom-left matrix cell [0,rbound] should be given back
        in Sheet coordinates at the center of that cell.

        The cell [last_row+1,-1] outside this corner should come back out of
        the BoundingBox.
        """
        # inside
        r,c = self.last_row,0
        x,y = self.left+self.half_unit,self.bottom+self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.density), (x,y))

        # outside
        r,c = self.last_row+1,-1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.density)
        self.assertFalse(self.box.contains(test_x,test_y))

        
    def test_midx2s_right_top(self):
        """
        The top-right matrix cell [cbound,0] should be given back
        in Sheet coordinates at the center of that cell.

        The cell [-1,last_col+1] outside this corner should come back out of
        the BoundingBox.
        """
        # inside
        r,c = 0,self.last_col
        x,y = self.right-self.half_unit,self.top-self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.density), (x,y))

        # outside
        r,c = -1,self.last_col+1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.density)
        self.assertFalse(self.box.contains(test_x,test_y))

        
    def test_midx2s_right_bottom(self):
        """
        The bottom-right matrix cell [cbound,rbound] should be given back
        in Sheet coordinates at the center of that cell.

        The cell [last_row+1,last_col+1] outside this corner should come back out of
        the BoundingBox.
        """
        r,c = self.last_row,self.last_col
        x,y = self.right-self.half_unit,self.bottom+self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.density), (x,y))

        # outside
        r,c = self.last_row+1,self.last_col+1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.density)
        self.assertFalse(self.box.contains(test_x,test_y))


    def test_midx2s_center(self):
        """
        The row and col *index* of the center unit in the matrix should come
        back as the Sheet coordinates of the center of that center unit.
        """
        r,c = self.center_unit_idx
        x_center = self.left+(self.right-self.left)/2.0
        y_center = self.bottom+(self.top-self.bottom)/2.0
        x,y = x_center+self.half_unit, y_center-self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.density), (x,y))    


    def test_bounds2shape(self):
        """
        Check that the shape of the matrix based on the BoundingBox and
        density is correct.
        """
        n_rows,n_cols = bounds2shape(self.box,self.density)
        self.assertEqual((n_rows,n_cols),(self.last_row+1,self.last_col+1))



    def test_sheetview_release(self):
        self.s = Sheet()
        self.s.activity = Numeric.array([[1,2],[3,4]])
        # Call s.sheet_view(..) with a parameter
	sv2 = SheetView((self.s.activity,self.s.bounds),
                          src_name=self.s.name,view_type='Activity')
        self.assertEqual(len(self.s.sheet_view_dict.keys()),0)
        self.s.add_sheet_view('Activity',sv2)
        self.assertEqual(len(self.s.sheet_view_dict.keys()),1)
        self.s.release_sheet_view('Activity')
        self.assertEqual(len(self.s.sheet_view_dict.keys()),0)


        
    ####
    #
    def test_coordinate_position(self):
        """
        CEBHACKALERT: these tests duplicate those above
        except these use a matrix with non-integer
        (right-left) and (top-bottom). This is an important
        test case for the definition of density; without it,
        the tests above could be passed by a variety of
        sheet2matrix, bounds2shape functions, etc.
        So, transfer the box to TestBox3Coordinates and have
        these tests run like the others.
        """
        l,b,r,t = (-0.8,-0.8,0.8,0.8)
        density = 16
        bounds = BoundingBox(points=((l,b),(r,t)))
        
        self.assertEqual(sheet2matrixidx(0.8,0.8,bounds,density),(0,24+1))
        self.assertEqual(sheet2matrixidx(0.0,0.0,bounds,density),(12,12))
        self.assertEqual(sheet2matrixidx(-0.8,-0.8,bounds,density),(24+1,0))
        self.assertEqual(matrixidx2sheet(24,0,bounds,density),
                         (((r-l) / int(density*(r-l)) / 2.0) + l,
                          (t-b) / int(density*(t-b)) / 2.0 + b))
        self.assertEqual(matrixidx2sheet(0,0,bounds,density),
                         (((r-l) / int(density*(r-l)) / 2.0) + l ,
                          (t-b) / int(density*(t-b)) * (int(density*(t-b)) - 0.5) + b))

        x,y = matrixidx2sheet(0,0,bounds,density)
        self.assertTrue(bounds.contains(x,y))
        self.assertEqual((0,0),sheet2matrixidx(x,y,bounds,density))

        x,y = matrixidx2sheet(25,25,bounds,density)
        self.assertFalse(bounds.contains(x,y))
        self.assertNotEqual((24,24),sheet2matrixidx(x,y,bounds,density))

        x,y = matrixidx2sheet(0,24,bounds,density)
        self.assertTrue(bounds.contains(x,y))
        self.assertEqual((0,24),sheet2matrixidx(x,y,bounds,density))

        x,y = matrixidx2sheet(24,0,bounds,density)
        self.assertTrue(bounds.contains(x,y))
        self.assertEqual((24,0),sheet2matrixidx(x,y,bounds,density))



# CEBHACKALERT: should test odd number of units as well?
#             + non-int left-right or top-bottom

class TestBox1Coordinates(TestCoordinateTransforms):
    """
    Test coordinate transformations using the standard, origin-centered unit box
    with density 10.    
    """
    def setUp(self):
        self.left = -0.5
        self.bottom = -0.5
        self.top = 0.5
        self.right = 0.5
        self.density = 10
        self.half_unit = 0.05

        # for the matrix representation - I think having this manual statement is
        # safer than a calculation...
        self.last_row = 9
        self.last_col = 9
        self.center_unit_idx = (5,5)  # by the way sheet2matrixidx is defined

        self.makeBox()


class TestBox2Coordinates(TestCoordinateTransforms):
    """
    Test coordinate transformations on the box defined by (1,1), (3,4),
    with density 8.
    """
    def setUp(self):
        self.left = 1
        self.bottom = 1
        self.right = 3
        self.top  = 4
        self.density = 8
        self.half_unit = 0.0625

        # for the matrix representation - I think having this manual statement is
        # safer than a calculation...
        self.last_row = 23
        self.last_col = 15
        self.center_unit_idx = (12,8)  # by the way sheet2matrixidx is defined

        self.makeBox()


cases = [TestBox1Coordinates,
         TestBox2Coordinates]


suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
        
