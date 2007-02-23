"""
Utility functions used by the test files.

$Id$
"""

import sys

from numpy.oldnumeric import alltrue,equal,shape,ravel,around,asarray,less_equal,array2string


# CEBALERT: are these functions available to us somewhere from numpy?
# They are:
#  from numpy.testing import assert_array_equal,assert_array_almost_equal
# The numpy functions might be better, because they correctly assert
# two arrays are not equal even if the 'astype(float)' code in
# lissom_log_parser's compare_elements() is not present. (Although they
# claim one of the arrays has three dimensions, which is clearly not true
# but might be something to do with the arrays having different types.)
# * Also see numpy.allclose()


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

