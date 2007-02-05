"""
Utility functions used by the test files.

$Id$
"""
import sys

from Numeric import alltrue,equal,shape,ravel,around,asarray,less_equal,array2string


# CEBALERT: are these functions available to us somewhere from numpy?

def assert_array_equal(x,y,err_msg=''):
    """
    Test equality of two arrays.

    (unittest.assertEqual() for arrays).

    Taken from scipy_test.testing.
    """
    x,y = asarray(x), asarray(y)
    msg = '\nArrays are not equal'
    try:
        assert 0 in [len(shape(x)),len(shape(y))] \
               or (len(shape(x))==len(shape(y)) and \
                   alltrue(equal(shape(x),shape(y)))),\
                   msg + ' (shapes %s, %s mismatch):\n\t' \
                   % (shape(x),shape(y)) + err_msg
        reduced = ravel(equal(x,y))
        cond = alltrue(reduced)
        if not cond:
            s1 = array2string(x,precision=16)
            s2 = array2string(y,precision=16)
            if len(s1)>120: s1 = s1[:120] + '...'
            if len(s2)>120: s2 = s2[:120] + '...'
            match = 100-100.0*reduced.tolist().count(1)/len(reduced)
            msg = msg + ' (mismatch %s%%):\n\tArray 1: %s\n\tArray 2: %s' % (match,s1,s2)
        assert cond,\
               msg + '\n\t' + err_msg
    except ValueError:
        raise ValueError, msg



### CEBHACKALERT: do these functions work properly?
### As far as I can see, the following arrays are not
### equal to 3 decimal places - but apparently they are.
##
## Topographica_t300> q
## [[ 0.       , 0.0573847, 0.0606149, 0.0598746, 0.       ,]
##  [ 0.0480538, 0.0552814, 0.0596533, 0.0608909, 0.0596174,]
##  [ 0.041258 , 0.049408 , 0.0542723, 0.0554007, 0.0529847,]
##  [ 0.0318477, 0.0382993, 0.043044 , 0.0434216, 0.039614 ,]
##  [ 0.       , 0.0284601, 0.0302289, 0.0303898, 0.       ,]]
## Topographica_t300> r
## [[ 0.        , 0.05664945, 0.06030838, 0.05992609, 0.        ,]
##  [ 0.04717049, 0.05471333, 0.05939505, 0.06094503, 0.06021817,]
##  [ 0.0404351 , 0.04891871, 0.05402054, 0.05565059, 0.05440581,]
##  [ 0.03123766, 0.03796289, 0.04310865, 0.04405752, 0.04102606,]
##  [ 0.        , 0.02833677, 0.03042182, 0.03109195, 0.        ,]]
## Topographica_t300> from topo.tests.utils import assert_array_almost_equal
## Topographica_t300> assert_array_almost_equal(q,r,decimal=3)
## Topographica_t300> assert_array_almost_equal(q,r,decimal=9)
## Topographica_t300> assert_array_almost_equal(q,r,decimal=12)
## Topographica_t300> assert_array_almost_equal(q,r,decimal=13)
## Traceback (most recent call last):
##   File "<stdin>", line 1, in ?
##   File "/home/chris/dev_ext/topographica/topo/tests/utils.py", line 75, in assert_array_almost_equal
##     assert cond,\
## AssertionError: 
## Arrays are not almost equal (mismatch 64.0%):
## 	Array 1: [[ 0.         0.0573847  0.0606149  0.0598746  0.       ]
##  [ 0.0480538  0.0552814  0.0596533  0.0608909  0.0596174]
##  [ 0...
## 	Array 2: [[ 0.                0.05664944648743  0.0603083781898   0.05992609262466
##         0.              ]
##  [ 0.04717049375176 ...
	
## Topographica_t300> 




def assert_array_almost_equal(x,y,decimal=6,err_msg=''):
    """
    Test for near equality of two arrays.

    (unittest.assertAlmostEqual() for arrays).

    Taken from scipy_test.testing.
    """
    # CB: added in >0 test because otherwise
    #  assert_array_almost_equal(array([1]),array([2]),0)==True
    # It's not very likely to come up!
    assert decimal > 0, "Must test to at least 1 decimal place."
    
    x = asarray(x)
    y = asarray(y)
    msg = '\nArrays are not almost equal'
    try:
        cond = alltrue(equal(shape(x),shape(y)))
        if not cond:
            msg = msg + ' (shapes mismatch):\n\t'\
                  'Shape of array 1: %s\n\tShape of array 2: %s' % (shape(x),shape(y))
        assert cond, msg + '\n\t' + err_msg
        reduced = ravel(equal(less_equal(around(abs(x-y),decimal),10.0**(-decimal)),1))
        cond = alltrue(reduced)
        if not cond:
            s1 = array2string(x,precision=decimal+1)
            s2 = array2string(y,precision=decimal+1)
            if len(s1)>120: s1 = s1[:120] + '...'
            if len(s2)>120: s2 = s2[:120] + '...'
            match = 100-100.0*reduced.tolist().count(1)/len(reduced)
            msg = msg + ' (mismatch %s%%):\n\tArray 1: %s\n\tArray 2: %s' % (match,s1,s2)
        assert cond,\
               msg + '\n\t' + err_msg
    except ValueError:
        print sys.exc_value
        print shape(x),shape(y)
        print x, y
        raise ValueError, 'arrays are not almost equal'



def array_almost_equal(x,y,decimal=6):
    """
    Return whether or not two arrays are equal to the given number of decimal places.

    Raises an error if x and y are not the same shape.
    """
    ## Adapted from assert_array_almost_equal() above.
    
    assert decimal>0, "Must test to at least 1 decimal place."

    x = asarray(x)
    y = asarray(y)
    
    if not alltrue(equal(shape(x),shape(y))):
        msg = 'Shapes do not match:\n\t'\
              'Shape of array 1: %s\n\tShape of array 2: %s' % (shape(x),shape(y))
        raise ValueError(msg)

    reduced = ravel(equal(less_equal(around(abs(x-y),decimal),10.0**(-decimal)),1))

    return alltrue(reduced)

