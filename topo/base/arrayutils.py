"""
General utility functions and classes for Topographica that require numpy.

$Id$
"""
__version__ = "$Revision$"

import re

from numpy.oldnumeric import sqrt, dot,arctan2, array2string, logical_not, argmax, fmod, floor

# CB: I think it's ok to replace Python's abs with numpy's in this file,
# but pylint complains. Maybe it's right?
from numpy import set_printoptions, abs

# Ask numpy to print even relatively large arrays by default
set_printoptions(threshold=200*200)


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
    # CEBALERT: why is this import here? Can I move it?
    from numpy.oldnumeric import concatenate as join,array
    rows,cols = matrix.shape

    hborder = array([ [value]*(cols+2*width) ]*width)
    vborder = array([ [value]*width ] * rows)

    temp = join( (vborder,matrix,vborder), axis=1)
    return join( (hborder,temp,hborder) )     


def arg(z):
    """
    Return the complex argument (phase) of z.
    (z in radians.)
    """
    z = z + complex(0,0)  # so that arg(z) also works for real z
    return arctan2(z.imag, z.real)


def octave_str(mat,name="mat",owner=""):
    """
    Print the given Numeric matrix in Octave format, listing the given
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
        row_sum = sum(array_2D[r,:])
        rsum += r*row_sum
        rmass_sum += row_sum
    
    for c in xrange(cols):
        col_sum = sum(array_2D[:,c])
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


def wrap(lower, upper, x):
    """
    Circularly alias the numeric value x into the range [lower,upper).

    Valid for cyclic quantities like orientations or hues.
    """
    #I have no idea how I came up with this algorithm; it should be simplified.
    range_=upper-lower
    return lower + fmod(x-lower + 2*range_*(1-floor(x/(2*range_))), range_)


# There might already be a function for this in Numeric...
def array_argmax(mat):
    "Returns the coordinates of the maximum element in the given matrix."
    rows,cols = mat.shape # pylint: disable-msg=W0612
    pos = argmax(mat.ravel())
    r = pos/cols
    c = pos%cols
    return r,c



def __numpy_ufunc_pickle_support():
    """
    Allow instances of numpy.ufunc to pickle.

    Remove this when numpy.ufuncs themselves support pickling.
    See http://news.gmane.org/find-root.php?group=gmane.comp.python.numeric.general&article=13400
    """
    # Code from Robert Kern

    # Note that this only works if the ufunc is from numpy; we might want to add a warning
    # on finding that isinstance(ufunc,numpy.ufunc) is False.

    import copy_reg

    def ufunc_pickler(ufunc):
        """Return the ufunc's name"""
        return ufunc.__name__

    # CB: could add ufunc_unpickler if we need.
    import numpy
    copy_reg.pickle(numpy.ufunc,ufunc_pickler)#,ufunc_unpickler)


__numpy_ufunc_pickle_support()
