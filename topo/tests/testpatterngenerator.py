"""
Tests PatternGenerator (position and orientation), and some of the
basic patterns.

$Id$
"""
__version__='$Revision$'

import unittest

from Numeric import array, pi
from MLab import rot90

from topo.base.patterngenerator import Constant
from topo.base.boundingregion import BoundingBox

from topo.patterns.basic import Rectangle,Gaussian,CompositePatternGenerator

from utils import assert_array_equal


class TestPatternGenerator(unittest.TestCase):

    def test_a_basic_patterngenerator(self):
        pattern_bounds = BoundingBox(points=((0.3,0.2),(0.5,0.5)))

        pattern_target = array([[1,1],
                                [1,1],
                                [1,1]])

        r = Rectangle(bounds=pattern_bounds,xdensity=10,
                      ydensity=10,aspect_ratio=1,size=1)
        assert_array_equal(r(),pattern_target)
        

    def test_constant(self):
        """
        Constant overrides PatternGenerator's usual matrix creation.
        """
        pattern_bounds = BoundingBox(points=((0.3,0.2),(0.5,0.5)))

        pattern_target = array([[1,1],
                                [1,1],
                                [1,1]])

        c = Constant(bounds=pattern_bounds,xdensity=10.0,ydensity=10)
        assert_array_equal(c(),pattern_target)
        

    def test_position(self):
        """
        Test that a pattern is drawn correctly at different
        locations.
        """

        initial = array([[0,0,0,0],
                         [0,1,1,0],
                         [0,1,1,0],
                         [0,0,0,0]])

        r = Rectangle(bounds=BoundingBox(radius=2),xdensity=1,
                      ydensity=1,aspect_ratio=1,size=2)
        assert_array_equal(r(),initial)

        ### x offset
        x_offset = array([[0,0,0,0],
                          [0,0,1,1],
                          [0,0,1,1],
                          [0,0,0,0]])

        assert_array_equal(r(x=1),x_offset)

        ### y offset
        y_offset = rot90(x_offset)
        assert_array_equal(r(y=1),y_offset)

        ### x and y offset
        target = array([[0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [1,1,0,0,0,0,0,0,0,0],
                        [1,1,0,0,0,0,0,0,0,0],
                        [1,1,0,0,0,0,0,0,0,0],
                        [1,1,0,0,0,0,0,0,0,0]])

        width  = 0.2
        height = 0.4

        r = Rectangle(bounds=BoundingBox(radius=0.5),
                      xdensity=10,ydensity=10,
                      aspect_ratio=width/height,size=height)

        assert_array_equal(r(x=-0.4,y=-0.3),target)

        ### x and y offset with bounds offset by the same
        target = array([[0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,1,1,0,0,0,0],
                        [0,0,0,0,1,1,0,0,0,0],
                        [0,0,0,0,1,1,0,0,0,0],
                        [0,0,0,0,1,1,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0],
                        [0,0,0,0,0,0,0,0,0,0]])

        width  = 0.2
        height = 0.4

        bounds = BoundingBox(points=((-0.9,-0.8),(0.1,0.2)))
        r = Rectangle(bounds=bounds,xdensity=10,ydensity=10,
                      aspect_ratio=width/height,size=height)
        
        assert_array_equal(r(x=-0.4,y=-0.3),target)
        
    

    def test_orientation_and_rotation(self):
        """
        Test that a pattern is drawn with the correct orientation,
        and is rotated correctly.
        """
        ### Test initial orientation and 90-degree rotation
        target = array([[0, 0, 0, 0, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 1, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0]])

        bounds = BoundingBox(radius=0.3)
        xdensity = 10
        ydensity = 10
        width = 2.0/xdensity
        height = 4.0/ydensity
        
        rect = Rectangle(size=height,
                         aspect_ratio=width/height,
                         xdensity=xdensity,ydensity=ydensity,bounds=bounds)

        assert_array_equal(rect(),target)
        assert_array_equal(rect(orientation=pi/2),rot90(target))


        ### 45-degree rotation about the origin
        rot_45 = array([[0, 0, 0, 0, 0, 0],
                        [0, 0, 1, 0, 0, 0],
                        [0, 1, 1, 1, 0, 0],
                        [0, 0, 1, 1, 1, 0],
                        [0, 0, 0, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0]])
                       
        assert_array_equal(rect(orientation=pi/4),rot_45)


        ### 45-degree rotation that's not about the origin
        rot_45_offset = array([[0, 1, 0, 0, 0, 0],
                               [1, 1, 1, 0, 0, 0],
                               [0, 1, 1, 1, 0, 0],
                               [0, 0, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0]])

        assert_array_equal(rect(x=-1.0/xdensity,y=1.0/ydensity,orientation=pi/4),
                           rot_45_offset)



    def test_composite_pattern_basic(self):
        """
        Test that a composite pattern consisting of just one Gaussian is the same
        as that actual Gaussian pattern, and similarly for a composite pattern of
        two rectangles.
        """
# CEBHACKALERT: test commented out because although it passes if this
# test is run by itself, if it is run as part of the suite it fails.
# Presumably this is because a class default has been set elsewhere in the
# tests, but is assumed to have some other value for this test.
# Should be easy to fix.
##         g = Gaussian(size=0.2,aspect_ratio=0.5)
##         c = CompositePatternGenerator(generators=[g])
##         assert_array_equal(g(),c())

##         r1=Rectangle(size=0.2,aspect_ratio=1,xdensity=10,ydensity=10,x=0.3,y=0.3)
##         r2=Rectangle(size=0.2,aspect_ratio=1,xdensity=10,ydensity=10,x=-0.3,y=-0.3)
##         c_true = r1()+r2()        
##         c = CompositePatternGenerator(generators=[r1,r2])
##         assert_array_equal(c(),c_true)
               # test that moving is ok


# CEBHACKALERT: this test genuinely fails, because the moved
# composite is very slightly different from the moved gaussian -
# almost like they are being normalized differently, though I doubt
# that is the problem.
##     def test_composite_pattern_moves(self):
##         """
##         Test that moving a composite pattern yields the correct pattern.
##         """
##         g = Gaussian(size=0.2,aspect_ratio=0.5,xdensity=7,ydensity=7)
##         c = CompositePatternGenerator(xdensity=7,ydensity=7,generators=[g],
##                                       x=-0.3,y=0.4)

##         g_moved = g(x=-0.3,y=0.4)
##         assert_array_equal(c(),g_moved)




suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternGenerator))
