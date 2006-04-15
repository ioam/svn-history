"""
Tests PatternGenerator (position and orientation).

$Id$
"""
__version__='$Revision$'

import unittest

from Numeric import array, pi
from MLab import rot90

from topo.base.patterngenerator import Constant
from topo.base.boundingregion import BoundingBox

from topo.patterns.basic import Rectangle

from utils import assert_array_equal


class TestPatternGenerator(unittest.TestCase):

    def test_a_basic_patterngenerator(self):
        density = 10
        pattern_bounds = BoundingBox(points=((0.3,0.2),(0.5,0.5)))

        pattern_target = array([[1,1],
                                [1,1],
                                [1,1]])

        r = Rectangle(bounds=pattern_bounds,density=10.0,aspect_ratio=1,size=1)
        assert_array_equal(r(),pattern_target)
        

    def test_constant(self):
        """
        Constant overrides PatternGenerator's usual matrix creation.
        """
        density = 10
        pattern_bounds = BoundingBox(points=((0.3,0.2),(0.5,0.5)))

        pattern_target = array([[1,1],
                                [1,1],
                                [1,1]])

        c = Constant(bounds=pattern_bounds,density=10.0)
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

        r = Rectangle(bounds=BoundingBox(radius=2),density=1,aspect_ratio=1,size=2)
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
                      density=10,aspect_ratio=width/height,size=height)

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
        r = Rectangle(bounds=bounds,density=10,
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
        density = 10
        width = 2.0/density
        height = 4.0/density
        
        rect = Rectangle(size=height,
                         aspect_ratio=width/height,
                         density=density,bounds=bounds)

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

        assert_array_equal(rect(x=-1.0/density,y=1.0/density,orientation=pi/4),
                           rot_45_offset)





suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestPatternGenerator))
