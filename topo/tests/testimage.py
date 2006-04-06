"""

$Id$
"""
__version__='$Revision$'

# CEBHACKALERT: incomplete - being written.

import unittest
from utils import assert_array_equal,assert_array_almost_equal

from Numeric import array,Float,pi
from MLab import rot90

from topo.patterns.image import Image
from topo.outputfns.basic import Identity

## from topo.commands.pylabplots import *


class TestImage(unittest.TestCase):

    def test_vertical_oddimage_evensheet__horizontal_evenimage_evensheet(self):
        """
        Test vertical positioning for even sheet, odd image and horizontal
        positioning for even image, even sheet.
        """
        # CEBHACKALERT: (I never actually checked the edge_average in this
        # case.)
        image_array = array(
[[  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,],
 [   0.        ,  34.        ,  68.        , 102.        , 136.        ,
        255.   ,   0.        ,   0.             ,],
 [   0.        ,  34.        ,  68.        , 102.        , 136.        ,
        255.        , 255.        ,   0.        ,],
 [   0.        ,  34.        ,  68.        , 102.        , 136.        ,
        255.        , 255.        , 255.        ,],
 [ 255.        ,   0.        , 255.        ,   0.        , 255.        ,
          0.        , 255.        ,   0.        ,],
 [   0.        , 255.        ,   0.        , 255.        ,   0.        ,
        255.        ,   0.        , 255.        ,],
 [  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,],
 [  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,]],Float)

        
        image = Image(filename = 'topo/tests/testimage.pgm',
                      density=8,
                      output_fn=Identity(),
                      whole_image_output_fn=Identity(),
                      size_normalization='original')

        assert_array_almost_equal(image_array,image())


    # CB: this test is failing because of sheet2matrix()/sheet2matrixidx();
    # it might not be possible to stop it failing.
    def test_vertical_oddimage_oddsheet__horizontal_evenimage_oddsheet(self):
        """
        Test vertical centering for odd sheet, odd image, and horizontal
        centering for odd sheet, even image
        """
        image_array = array(
[[  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,  96.59090909,],
 [  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,  96.59090909,],
 [   0.        ,  34.        ,  68.        , 102.        , 136.        ,
        255.   ,   0.        ,   0.             ,  96.59090909,],
 [   0.        ,  34.        ,  68.        , 102.        , 136.        ,
        255.        , 255.        ,   0.        ,  96.59090909,],
 [   0.        ,  34.        ,  68.        , 102.        , 136.        ,
        255.        , 255.        , 255.        ,  96.59090909,],
 [ 255.        ,   0.        , 255.        ,   0.        , 255.        ,
          0.        , 255.        ,   0.        ,  96.59090909,],
 [   0.        , 255.        ,   0.        , 255.        ,   0.        ,
        255.        ,   0.        , 255.        ,  96.59090909,],
 [  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,  96.59090909,],
 [  96.59090909,  96.59090909,  96.59090909,  96.59090909,  96.59090909,
         96.59090909,  96.59090909,  96.59090909,  96.59090909,]],Float)

        
        image = Image(filename = 'topo/tests/testimage.pgm',
                      density=9,
                      output_fn=Identity(),
                      whole_image_output_fn=Identity(),
                      size_normalization='original')

##         matrixplot(image())
##         matrixplot(image_array)

        assert_array_almost_equal(image_array,image())






##     def test_centering(self):
##         """
##         Check that an Image loaded at its original size on a sheet
##         larger than the Image is correctly centered, for odd and
##         even sheets, and odd and even Images.
##         """
##         # Odd-sized sheet, odd-sized Image:
##         image_array = array([[102,102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,  0, 34, 68,102,136,102,102,102],
##                              [102,102,102,  0, 34, 68,102,136,102,102,102],
##                              [102,102,102,  0, 34, 68,102,136,102,102,102],
##                              [102,102,102,255,  0,255,  0,255,102,102,102],
##                              [102,102,102,  0,255,  0,255,  0,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102,102]], 
##                             Float)
        
##         image = Image(filename = 'topo/tests/testimage.pgm',
##                       density=11,
##                       output_fn=Identity(),
##                       size_normalization='original')

##         assert_array_equal(image_array,image())


##         # Even-sized sheet, odd-sized Image:
##         image_array = array([[102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,  0, 34, 68,102,136,102,102],
##                              [102,102,102,  0, 34, 68,102,136,102,102],
##                              [102,102,102,  0, 34, 68,102,136,102,102],
##                              [102,102,102,255,  0,255,  0,255,102,102],
##                              [102,102,102,  0,255,  0,255,  0,102,102],
##                              [102,102,102,102,102,102,102,102,102,102],
##                              [102,102,102,102,102,102,102,102,102,102]], 
##                             Float)
        
##         image = Image(filename = 'topo/tests/testimage.pgm',
##                       density=10,
##                       output_fn=Identity(),
##                       size_normalization='original')

##         assert_array_equal(image_array,image())

        
##     def test_resize(self):
##         """
##         Check various densities and ...
##         """
##         image_array = array([[  0,  0, 34, 34, 68, 68,102,102,136,136],
##                              [  0,  0, 34, 34, 68, 68,102,102,136,136],
##                              [  0,  0, 34, 34, 68, 68,102,102,136,136],
##                              [  0,  0, 34, 34, 68, 68,102,102,136,136],
##                              [  0,  0, 34, 34, 68, 68,102,102,136,136],
##                              [  0,  0, 34, 34, 68, 68,102,102,136,136],
##                              [255,255,  0,  0,255,255,  0,  0,255,255],
##                              [255,255,  0,  0,255,255,  0,  0,255,255],
##                              [  0,  0,255,255,  0,  0,255,255,  0,  0],
##                              [  0,  0,255,255,  0,  0,255,255,  0,  0]])
        
##         image = Image(filename = 'topo/tests/testimage.pgm',
##                       density=10,
##                       output_fn=Identity(),
##                       size_normalization='fit_shortest')

##         assert_array_equal(image_array,image())



##     def test_rotation(self):
##         """
##         """
##         assert_array_equal(rot90(self.image_array),self.image(orientation=pi/2))
##         assert_array_equal(rot90(self.image_array,-1),self.image(orientation=-pi/2))


        
        

   





suite = unittest.TestSuite()
#  Uncomment the following line of code, to disable the test if
#  $DISPLAY is undefined.  Used mainly for GUI testing.
# suite.requires_display = True
suite.addTest(unittest.makeSuite(TestImage))
