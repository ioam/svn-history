"""
General utility functions and classes for Topographica that require Numeric.

$Id$
"""
__version__ = "$Revision$"

import re

from Numeric import sqrt, ones, dot, sum, arctan2, array2string


# CEBHACKALERT: there are some inconsistencies throughout as to
# whether we should assume arrays are contiguous (i.e. using an
# array's 'flat' attribute, or using the ravel() function).  It
# appears that in the most recent Numeric, this problem is taken care
# of, so when we change, these problems should go away.  In addition,
# we won't have to deal with savespace.
#
# You can see the changes that are made to code when upgrading to the
# most recent version by looking at Numeric's code converting utility:
# http://projects.scipy.org/scipy/numpy/browser/trunk/numpy/lib/convertcode.py
# Notably for this hackalert:
#8	 * Makes search and replace changes to:	
#9	   - .typecode()	
#10	   - .iscontiguous()	
#13	 * Converts .flat to .ravel() except for .flat = xxx or .flat[xxx]	
#14	 * Change typecode= to dtype=	
#15	 * Eliminates savespace=xxx	
#16	 * Replace xxx.spacesaver() with True	
#17	 * Convert xx.savespace(?) to pass + ## xx.savespace(?)	





# One might think we could use float('inf') or array([float('inf')]) here,
# but as of Python 2.4 only some platforms will support float('inf').
# 
# In particular, Python 2.4 for Windows generates a cast error even though
# the operation works under Linux.
# (see http://www.python.org/peps/pep-0754.html)
inf = (ones(1)/0.0)[0]

def L2norm(v):
    """
    Return the L2 norm of the vector v.
    """
    return sqrt(dot(v,v))


def norm(v,p=2):
    """
    Returns the Lp norm of v, where p is arbitrary and defaults to 2.
    """
    return sum(abs(v)**p)**(1.0/p)


def divisive_normalization(weights):
    """Divisively normalize an array to sum to 1.0"""
    s = sum(weights.flat)
    if s != 0:
        factor = 1.0/s
        weights *= factor

def add_border(matrix,width=1,value=0.0):
    """   
    Returns a new matrix consisting of the given matrix with a border
    or margin of the given width filled with the given value.
    """
    from Numeric import concatenate as join,array
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
    z = z + complex()  # so that arg(z) also works for real z
    return arctan2(z.imag, z.real)


import Numeric
def exp(x):
    """
    Avoid overflow of Numeric.exp() for large-magnitude arguments (|x|>MAX_MAG).

    Return  Numeric.exp( inf)==inf  if x > MAX_MAG
            Numeric.exp(-inf)==0.0  if x < -MAX_MAG
                                 x  otherwise

    Numeric.exp() gives an OverflowError ('math range error') for
    arguments of magnitude greater than about 700 (on linux).

    See e.g.
    [Python-Dev] RE: Possible bug (was Re: numpy, overflow, inf, ieee, and richcomparison)
    http://mail.python.org/pipermail/python-dev/2000-October/thread.html#9851
    """

    # CEBHACKALERT:
    # This value works on the linuxes we all use, but what about on other platforms?
    MAX_MAG = 700.0
    return Numeric.exp(Numeric.where(abs(x)>MAX_MAG,Numeric.sign(x)*inf,x))


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


### JABALERT!
###
### If at all possible should be rewritten to use matrix functions
### that eliminate the explicit for loop, because this is very slow.  
### The savespace() should probably also be eliminated.  
def clip_in_place(mat,lower_bound,upper_bound):
    """Version of Numeric.clip that changes the argument in place, with no intermediate."""
    mat.savespace(1)
    mflat = mat.flat
    size = len(mflat)
    for i in xrange(size):
        element = mflat[i]
        if element<lower_bound:
            mflat[i] = lower_bound
        elif element>upper_bound:
            mflat[i] = upper_bound

### JABALERT!
###
### If at all possible should be rewritten to use matrix functions
### that eliminate the explicit for loop, because this is very slow.  
### The savespace() should probably also be eliminated.  
def clip_lower(mat,lower_bound):
    """Version of Numeric.clip that changes the argument in place, with no intermediate."""
    mat.savespace(1)
    mflat = mat.flat
    size = len(mflat)
    for i in xrange(size):
        element = mflat[i]
        if element<lower_bound:
            mflat[i] = lower_bound
