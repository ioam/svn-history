"""
General utility functions and classes for Topographica that require Numeric.

$Id$
"""
__version__ = "$Revision$"

import re

from Numeric import sqrt, ones, dot, sum, arctan2, array2string


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

def msum(m):
    """
    Returns the sum of elements in a 2D matrix.  Works in cases where
    sum(a.flat) fails, e.g, with matrix slices or submatrices.
    """
    return sum(sum(m))

### JAB: Could be rewritten using weave.blitz to avoid creating a temporary
def mdot(m1,m2):
    """
    Returns the sum of the element-by-element product of two 2D
    arrays.  Works in cases where dot(a.flat,b.flat) fails, e.g, with
    matrix slices or submatrices.
    """
    a = m1*m2
    return sum(a.flat)

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


