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


# CEBHACKALERT: still to test bounds2slice(), submatrix()


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

        #self.cbound = int(self.density*(self.right-self.left)) / float((self.right-self.left))
        #self.rbound = int(self.density*(self.top-self.bottom)) / float((self.top-self.bottom))


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
        row, col = sheet2matrix(x_center,y_center,self.box,self.xdensity,self.ydensity)
        self.assertEqual((row,col),(self.rbound/2.0,self.cbound/2.0))


    def test_sheet2matrix_left_top(self):
        """
        Check that the top-left of the Sheet is [0,0] in matrix
        coordinates.
        """
        row, col = sheet2matrix(self.left,self.top,self.box,self.xdensity,self.ydensity)
        self.assertEqual((row,col),(0,0))


    def test_sheet2matrix_right_bottom(self):
        """
        Check that the bottom-right of the Sheet is [rbound,cbound] in matrix
        coordinates.
        """
        row, col = sheet2matrix(self.right,self.bottom,self.box,self.xdensity,self.ydensity)
        self.assertEqual((row,col),(self.rbound,self.cbound))

        
    def test_sheet2matrix_matrix2sheet(self):
        """
        Check that matrix2sheet() is the inverse of sheet2matrix().
        """
        # top-right corner
        row, col = sheet2matrix(self.right,self.top,self.box,self.xdensity,self.ydensity)
        x_right, y_top = matrix2sheet(row,col,self.box,self.xdensity,self.ydensity)
        self.assertEqual((x_right,y_top),(self.right,self.top)) 

        # bottom-left corner
        row, col = sheet2matrix(self.left,self.bottom,self.box,self.xdensity,self.ydensity)
        x_left, y_bottom = matrix2sheet(row,col,self.box,self.xdensity,self.ydensity)
        self.assertEqual((x_left,y_bottom),(self.left,self.bottom)) 


    def test_matrix2sheet_sheet2matrix(self):
        """
        Check that sheet2matrix() is the inverse of matrix2sheet().
        """
        # top-right corner
        x,y = matrix2sheet(float(0),float(self.last_col),self.box,self.xdensity,self.ydensity)
        top_row,right_col = sheet2matrix(x,y,self.box,self.xdensity,self.ydensity)
        self.assertEqual((top_row,right_col),(float(0),float(self.last_col))) 

        # bottom-left corner
        x,y = matrix2sheet(float(self.last_row),float(0),self.box,self.xdensity,self.ydensity)
        bottom_row,left_col = sheet2matrix(x,y,self.box,self.xdensity,self.ydensity)
        self.assertEqual((bottom_row,left_col),(float(self.last_row),float(0)))

        
    ### sheet2matrixidx() tests
    #    
    def test_sheet2matrixidx_left_top(self):
        """
        Test a point just inside the top-left corner of the BoundingBox, and
        one just outside.
        """
        # inside
        r,c = 0,0
        x,y = self.left,self.top
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity), (r,c))

        # outside
        r,c = -1,-1
        x,y = self.just_out_left_x,self.just_out_top_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity), (r,c))


    def test_sheet2matrixidx_left_bottom(self):
        """
        Test a point just inside the left-bottom corner of the BoundingBox, and
        one just outside.
        """
        # inside
        r,c = self.last_row, 0
        x,y = self.left, self.just_in_bottom_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity),(r,c))

        # outside
        r,c = self.last_row+1, -1
        x,y = self.just_out_left_x, self.bottom
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity),(r,c))


    def test_sheet2matrixidx_right_top(self):
        """
        Test a point just inside the top-right corner of the BoundingBox, and
        one just outside.
        """
        # inside
        r,c = 0,self.last_col
        x,y = self.just_in_right_x,self.top
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity),(r,c))

        # outside
        r,c = -1,self.last_col+1
        x,y = self.right,self.just_out_top_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity),(r,c))


    def test_sheet2matrixidx_right_bottom(self):
        """
        Test a point just inside the bottom-right corner of the BoundingBox,
        and the corner itself - which should not be inside.
        """
        # inside 
        r,c = self.last_row,self.last_col
        x,y = self.just_in_right_x,self.just_in_bottom_y
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity),(r,c))

        # not inside
        r,c = self.last_row+1,self.last_col+1
        x,y = self.right,self.bottom
        self.assertEqual(sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity),(r,c))


    ### matrix2sheet() tests
    #
    def test_matrix2sheet_left_top(self):
        """
        Check that Sheet's (0,0) is the top-left of the matrix.

        Check that just outside the top-left in matrix coordinates
        comes back to Sheet coordinates that are outside the
        BoundingBox.
        """
        x,y = matrix2sheet(0,0,self.box,self.xdensity,self.ydensity)
        self.assertEqual((x,y), (self.left,self.top))

        x,y = matrix2sheet(self.just_out_left_idx,self.just_out_top_idx,self.box,self.xdensity,self.ydensity)
        self.assertFalse(self.box.contains(x,y))
    

    def test_matrix2sheet_right_bottom(self):
        """
        Check that Sheet's (right,bottom) is the bottom-right in
        matrix coordinates i.e. [rbound,cbound]

        Check that just outside the bottom-right in matrix coordinates
        comes back to Sheet coordinates that are outside the
        BoundingBox.
        """
        x,y = matrix2sheet(self.rbound,self.cbound,self.box,self.xdensity,self.ydensity)
        self.assertEqual((x,y), (self.right,self.bottom))

        x,y = matrix2sheet(self.just_out_right_idx,self.just_out_bottom_idx,self.box,self.xdensity,self.ydensity)
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
        x,y = matrix2sheet(center_float_row,center_float_col,self.box,self.xdensity,self.ydensity)
        self.assertEqual((x,y),(x_center,y_center))



    ### matrixidx2sheet() tests
    #
    def test_matrixidx2sheet_left_top(self):
        """
        The top-left matrix cell [0,0] should be given back in Sheet
        coordinates at the center of that cell.

        The cell [-1,-1] outside this corner should come back out of
        the BoundingBox
        """
        # inside
        r,c = 0,0
        x,y = self.left+self.half_unit,self.top-self.half_unit

        test_x, test_y = matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity)
        self.assertEqual((test_x,test_y), (x,y))
        self.assertTrue(self.box.contains(test_x,test_y))

        # outside
        r,c = -1,-1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity)
        self.assertFalse(self.box.contains(test_x,test_y))
        
        
    def test_matrixidx2sheet_left_bottom(self):
        """
        The bottom-left matrix cell [0,rbound] should be given back
        in Sheet coordinates at the center of that cell.

        The cell [last_row+1,-1] outside this corner should come back out of
        the BoundingBox.
        """
        # inside
        r,c = self.last_row,0
        x,y = self.left+self.half_unit,self.bottom+self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity), (x,y))

        # outside
        r,c = self.last_row+1,-1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity)
        self.assertFalse(self.box.contains(test_x,test_y))

        
    def test_matrixidx2sheet_right_top(self):
        """
        The top-right matrix cell [cbound,0] should be given back
        in Sheet coordinates at the center of that cell.

        The cell [-1,last_col+1] outside this corner should come back out of
        the BoundingBox.
        """
        # inside
        r,c = 0,self.last_col
        x,y = self.right-self.half_unit,self.top-self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity), (x,y))

        # outside
        r,c = -1,self.last_col+1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity)
        self.assertFalse(self.box.contains(test_x,test_y))

        
    def test_matrixidx2sheet_right_bottom(self):
        """
        The bottom-right matrix cell [cbound,rbound] should be given back
        in Sheet coordinates at the center of that cell.

        The cell [last_row+1,last_col+1] outside this corner should come back out of
        the BoundingBox.
        """
        r,c = self.last_row,self.last_col
        x,y = self.right-self.half_unit,self.bottom+self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity), (x,y))

        # outside
        r,c = self.last_row+1,self.last_col+1
        test_x, test_y = matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity)
        self.assertFalse(self.box.contains(test_x,test_y))


    def test_matrixidx2sheet_center(self):
        """
        The row and col *index* of the center unit in the matrix should come
        back as the Sheet coordinates of the center of that center unit.
        """
        r,c = self.center_unit_idx
        x_center = self.left+(self.right-self.left)/2.0
        y_center = self.bottom+(self.top-self.bottom)/2.0
        x,y = x_center+self.half_unit, y_center-self.half_unit
        self.assertEqual(matrixidx2sheet(r,c,self.box,self.xdensity,self.ydensity), (x,y))    

    def test_matrixidx2sheet_sheet2matrixidx(self):
        """
        Check that sheet2matrixidx() is the inverse of matrix2sheetidx().
        """
        # top-right corner
        x,y = matrixidx2sheet(float(0),float(self.last_col),self.box,self.xdensity,self.ydensity)
        top_row,right_col = sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity)
        self.assertEqual((top_row,right_col),(float(0),float(self.last_col))) 

        # bottom-left corner
        x,y = matrixidx2sheet(float(self.last_row),float(0),self.box,self.xdensity,self.ydensity)
        bottom_row,left_col = sheet2matrixidx(x,y,self.box,self.xdensity,self.ydensity)
        self.assertEqual((bottom_row,left_col),(float(self.last_row),float(0)))

    ### JC This test might have to be re-written
    # CEBHACKALERT: it's not too important, but this test (like
    # test_coordinate_position() below) will run three times,
    # identically.  All these test_* functions are run for each of the
    # classes in the cases list below. So, this should be re-written
    # as Julien says.  However, my opinion is that this kind of setup
    # is restrictive (Julien and whoever wrote
    # test_coordinate_position() must agree because they ignored it!),
    # so it might be better not to rewrite this function and to use a
    # different format for the testing in the first place.
    def test_slice2bounds_bounds2slice(self):

	bb = boundingregion.BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))

	slice =(0,3,7,8)
	bounds = slice2bounds(slice,bb,10,10)
        test_slice = bounds2slice(bounds,bb,10,10)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	slice =(4,7,8,10)
	bounds = slice2bounds(slice,bb,10,10)
        test_slice = bounds2slice(bounds,bb,10,10)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	slice =(2,3,4,8)
	bounds = slice2bounds(slice,bb,10,10)
        test_slice = bounds2slice(bounds,bb,10,10)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	slice =(0,3,9,10)
	bounds = slice2bounds(slice,bb,10,10)
        test_slice = bounds2slice(bounds,bb,10,10)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	bb = boundingregion.BoundingBox(points=((-0.75,-0.5),(0.75,0.5)))

	slice =(9,14,27,29)
	bounds = slice2bounds(slice,bb,20,20)
        test_slice = bounds2slice(bounds,bb,20,20)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	slice =(0,6,0,7)
	bounds = slice2bounds(slice,bb,20,20)
        test_slice = bounds2slice(bounds,bb,20,20)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	slice =(6,10,11,29)
	bounds = slice2bounds(slice,bb,20,20)
        test_slice = bounds2slice(bounds,bb,20,20)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	bb = boundingregion.BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))

	slice =(4,7,2,3)
	bounds = slice2bounds(slice,bb,7,7)
        test_slice = bounds2slice(bounds,bb,7,7)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

	slice =(0,7,0,7)
	bounds = slice2bounds(slice,bb,7,7)
        test_slice = bounds2slice(bounds,bb,7,7)

	for a,b in zip(slice,test_slice):
	    self.assertEqual(a,b)

    def test_bounds2slice(self):
        # incomplete test
        
        # test that if you ask to slice the matrix with the sheet's BoundingBox, you
        # get back the whole matrix
        bb = boundingregion.BoundingBox(points=((-0.5,-0.5),(0.5,0.5)))
        slice = bounds2slice(bb,bb,10,10)
        true_slice = (0,10,0,10) # inclusive left boundary, exclusive right boundary
        self.assertEqual(slice,true_slice) # CEBHACKALERT: failing right now


    # bounds2shape() tests
    #
    def test_bounds2shape(self):
        """
        Check that the shape of the matrix based on the BoundingBox and
        density is correct.
        """
        n_rows,n_cols = bounds2shape(self.box,self.xdensity,self.ydensity)
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
        xdensity = int(density*(r-l)) / float(r-l)
        ydensity = int(density*(t-b)) / float(t-b)

        bounds = BoundingBox(points=((l,b),(r,t)))
        
        self.assertEqual(sheet2matrixidx(0.8,0.8,bounds,xdensity,ydensity),(0,24+1))
        self.assertEqual(sheet2matrixidx(0.0,0.0,bounds,xdensity,ydensity),(12,12))
        self.assertEqual(sheet2matrixidx(-0.8,-0.8,bounds,xdensity,ydensity),(24+1,0))
        self.assertEqual(matrixidx2sheet(24,0,bounds,xdensity,ydensity),
                         (((r-l) / int(density*(r-l)) / 2.0) + l,
                          (t-b) / int(density*(t-b)) / 2.0 + b))
        self.assertEqual(matrixidx2sheet(0,0,bounds,xdensity,ydensity),
                         (((r-l) / int(density*(r-l)) / 2.0) + l ,
                          (t-b) / int(density*(t-b)) * (int(density*(t-b)) - 0.5) + b))

        x,y = matrixidx2sheet(0,0,bounds,xdensity,ydensity)
        self.assertTrue(bounds.contains(x,y))
        self.assertEqual((0,0),sheet2matrixidx(x,y,bounds,xdensity,ydensity))

        x,y = matrixidx2sheet(25,25,bounds,xdensity,ydensity)
        self.assertFalse(bounds.contains(x,y))
        self.assertNotEqual((24,24),sheet2matrixidx(x,y,bounds,xdensity,ydensity))

        x,y = matrixidx2sheet(0,24,bounds,xdensity,ydensity)
        self.assertTrue(bounds.contains(x,y))
        self.assertEqual((0,24),sheet2matrixidx(x,y,bounds,xdensity,ydensity))

        x,y = matrixidx2sheet(24,0,bounds,xdensity,ydensity)
        self.assertTrue(bounds.contains(x,y))
        self.assertEqual((24,0),sheet2matrixidx(x,y,bounds,xdensity,ydensity))



class TestBox1Coordinates(TestCoordinateTransforms):
    """
    Test coordinate transformations using the standard, origin-centered unit box
    with density 10.

    A 10x10 matrix.
    """
    def setUp(self):
        self.left = -0.5
        self.bottom = -0.5
        self.top = 0.5
        self.right = 0.5
        self.density = 10
        self.half_unit = 0.05

        self.xdensity = int(self.density*(self.right-self.left)) / float(self.right-self.left)
        self.ydensity = int(self.density*(self.top-self.bottom)) / float(self.top-self.bottom)

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

    A 24 x 16 matrix.
    """
    def setUp(self):
        self.left = 1
        self.bottom = 1
        self.right = 3
        self.top  = 4
        self.density = 8
        self.half_unit = 0.0625

        self.xdensity = int(self.density*(self.right-self.left)) / float(self.right-self.left)
        self.ydensity = int(self.density*(self.top-self.bottom)) / float(self.top-self.bottom)

        # for the matrix representation - I think having this manual statement is
        # safer than a calculation...
        self.last_row = 23
        self.last_col = 15
        self.center_unit_idx = (12,8)  # by the way sheet2matrixidx is defined

        self.makeBox()



class TestBox3Coordinates(TestCoordinateTransforms):
    """
    """
    def setUp(self):        
        self.left = -0.8
        self.bottom = -0.8
        self.top = 0.8
        self.right = 0.8
        self.density = 16
        self.half_unit = 0.03125

        self.xdensity = int(self.density*(self.right-self.left)) / float(self.right-self.left)
        self.ydensity = int(self.density*(self.top-self.bottom)) / float(self.top-self.bottom)

        # for the matrix representation - I think having this manual statement is
        # safer than a calculation...
        self.last_row = 24
        self.last_col = 24
        self.center_unit_idx = (12,12)  # by the way sheet2matrixidx is defined

        self.makeBox()


# CEB: still making tests for TestBox3Coordinates...
cases = [TestBox1Coordinates,
         TestBox2Coordinates]
#         TestBox3Coordinates]
         


suite = unittest.TestSuite()
suite.addTests([unittest.makeSuite(case) for case in cases])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
        
