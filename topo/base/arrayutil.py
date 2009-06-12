"""
General utility functions and classes for Topographica that require numpy.

$Id$
"""
__version__ = "$Revision$"

import re

from numpy import sqrt,dot,arctan2,array2string,logical_not,fmod,floor,\
     array,concatenate,set_printoptions,divide
from numpy import abs # pylint: disable-msg=W0622
from numpy import ufunc

# Ask numpy to print even relatively large arrays by default
set_printoptions(threshold=200*200)


def ufunc_script_repr(f,imports,prefix=None,settings=None):
    """
    Return a runnable representation of the numpy ufunc f, and an
    import statement for its module.
    """
    # (could probably be generalized if required, because module is
    # f.__class__.__module__)
    imports.append('import numpy')
    return 'numpy.'+f.__name__

from ..param import parameterized
parameterized.script_repr_reg[ufunc]=ufunc_script_repr


def L2norm(v):
    """
    Return the L2 norm of the vector v.
    """
    return sqrt(dot(v,v))


def norm(v,p=2):
    """
    Returns the Lp norm of v, where p is arbitrary and defaults to 2.
    """
    return (abs(v)**p).sum()**(1.0/p)


def divisive_normalization(weights):
    """Divisively normalize an array to sum to 1.0"""
    s = weights.sum()
    if s != 0:
        factor = 1.0/s
        weights *= factor


def add_border(matrix,width=1,value=0.0):
    """   
    Returns a new matrix consisting of the given matrix with a border
    or margin of the given width filled with the given value.
    """
    rows,cols = matrix.shape

    hborder = array([ [value]*(cols+2*width) ]*width)
    vborder = array([ [value]*width ] * rows)

    temp = concatenate( (vborder,matrix,vborder), axis=1)
    return concatenate( (hborder,temp,hborder) )     


def arg(z):
    """
    Return the complex argument (phase) of z.
    (z in radians.)
    """
    z = z + complex(0,0)  # so that arg(z) also works for real z
    return arctan2(z.imag, z.real)


def octave_str(mat,name="mat",owner=""):
    """
    Print the given Numpy matrix in Octave format, listing the given
    matrix name and the object that owns it (if any).
    """
    # This just prints the string version of the matrix and does search/replace
    # to convert it; there may be a faster or easier way.
    mstr=array2string(mat)
    mstr=re.sub('\n','',mstr)
    mstr=re.sub('[[]','',mstr)
    mstr=re.sub('[]]','\n',mstr)
    return ("# Created from %s %s\n# name: %s\n# type: matrix\n# rows: %s\n# columns: %s\n%s" %
           (owner,name,name,mat.shape[0],mat.shape[1],mstr))


def octave_output(filename,mat,name="mat",owner=""):
    """Writes the given matrix to a new file of the given name, in Octave format."""
    f = open(filename,'w')
    f.write(octave_str(mat,name,owner))
    f.close()


def centroid(array_2D):
    """Return the centroid (center of gravity) for a 2D array."""

    rows,cols = array_2D.shape
    rsum=0
    csum=0
    rmass_sum=0
    cmass_sum=0
    for r in xrange(rows):
        row_sum = array_2D[r,:].sum()
        rsum += r*row_sum
        rmass_sum += row_sum
    
    for c in xrange(cols):
        col_sum = array_2D[:,c].sum()
        csum += c*col_sum
        cmass_sum += col_sum
        
    row_centroid= rsum/rmass_sum
    col_centroid= csum/cmass_sum

    return row_centroid, col_centroid



# CB: I suggest that we replace clip_lower with one of the two
# functions below. They both look simpler, and might be slightly
# faster. I think, however, that we have no test of clip_lower (direct
# or indirect), so I'm not prepared to switch.
#
# (I haven't actually tested these functions.)
#
## def clip_lower1(mat,lower_bound,upper_bound):
##    mat[mat<lower_bound]=lower_bound

## from numpy import putmask
## def clip_lower2(mat, lower_bound):
##    putmask(mat, mat<lower_bound, lower_bound)

def clip_lower(mat,lower_bound):
    """One-sided version of clip_in_place."""
    lower_cropping = mat<lower_bound
    to_keep = logical_not(lower_cropping)

    mat *= to_keep
    mat += lower_cropping*lower_bound

def clip_upper(mat,upper_bound):
    """One-sided version of clip_in_place."""
    upper_cropping = mat>upper_bound
    to_keep = logical_not(upper_cropping)

    mat *= to_keep
    mat += upper_cropping*upper_bound


def wrap(lower, upper, x):
    """
    Circularly alias the numeric value x into the range [lower,upper).

    Valid for cyclic quantities like orientations or hues.
    """
    #I have no idea how I came up with this algorithm; it should be simplified.
    #
    # Note that Python's % operator works on floats and arrays;
    # usually one can simply use that instead.  E.g. to wrap array or
    # scalar x into 0,2*pi, just use "x % (2*pi)".
    range_=upper-lower
    return lower + fmod(x-lower + 2*range_*(1-floor(x/(2*range_))), range_)


# There might already be a function for this in Numpy...
# CB: there isn't, but this method is listed at
# http://www.scipy.org/PerformanceTips:
## def min_ij(x):
##     i, j = divmod(x.argmin(), x.shape[1])
##     return i, j
def array_argmax(mat):
    "Returns the coordinates of the maximum element in the given matrix."
    rows,cols = mat.shape # pylint: disable-msg=W0612
    pos = mat.argmax()
    r = pos/cols
    c = pos%cols
    return r,c


def divide_with_constant(x,y):
    """
    Divide two scalars or arrays with a constant (1.0) offset on the
    denominator to avoid divide-by-zero issues.
    """ 
    return divide(x,y+1.0)
