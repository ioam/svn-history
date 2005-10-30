from __future__ import generators
"""
General utility functions and classes for Topographica.

$Id$
"""

from Numeric import sqrt,ones,dot,sum
import __main__
import math


# CEBHACKALERT?
# couldn't this use float('inf') or array([float('inf')])?
inf = (ones(1)/0.0)[0]


### JABALERT! Need to separate the utilities that depend on Numeric
### from the others, so that no caller will accidentally require
### Numeric.  Presumably the Numeric-related functions would go into a
### separate file arrayutils.py.


def wrap(lower, upper, x):
    """
    Circularly alias the numeric value x into the range [lower,upper).

    Valid for cyclic quantities like orientations or hues.
    """
    #I have no idea how I came up with this algorithm; it should be simplified.
    range=upper-lower
    return lower + math.fmod(x-lower + 2*range*(1-math.floor(x/(2*range))), range)


def NxN(tuple):
    """
    Converts a tuple (X1,X2,...,Xn) to a string 'X1xX2x...xXn'
    """    
    return 'x'.join([`N` for N in tuple])


def enumerate(seq):
    """
    For each element Xi of the given sequence, produces the tuple (i,Xi).
    
    (A copy of the Python 2.3 enumeration generator.)
    """
    Generator
    i = 0
    for x in seq:
        yield i,x
        i+=1

enum = enumerate


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


def hebbian(input_activity, unit_activity, weights, alpha):
    """Simple Hebbian learning for the weights of one single unit."""
    weights += alpha * unit_activity * input_activity


def divisive_normalization(weights):
    """Divisively normalize an array to sum to 1.0"""
    s = sum(weights.flat)
    if s != 0:
        factor = 1.0/s
        weights *= factor

class Struct:
    """
    A simple structure class, taking keyword args and assigning them to attributes.

    For instance:
    
    s = Struct(foo='a',bar=1)
    >>> s.foo
    'a'
    >>> s.bar
    1
    """
    def __init__(self,**fields):
        for name,value in fields.items():
            setattr(self,name,value)


def flat_indices(shape):
    """
    Returns a list of the indices needed to address or loop over all
    the elements of a 1D or 2D matrix with the given shape. E.g.:

    flat_indices((3,)) == [0,1,2]
    """
    if len(shape) == 1:
        return [(x,) for x in range(shape[0])]
    else:
        rows,cols = shape
        return [(r,c) for r in range(rows) for c in range(cols)]
        
    
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


def flatten(l):
    """
    Flattens a list.
    
    Written by Bearophile as published on the www.python.org newsgroups.
    Pulled into Topographica 3/5/2005.
    """
    if type(l) != list:
        return l
    else:
        result = []
        stack = []
        stack.append((l,0))
        while len(stack) != 0:
            sequence, j = stack.pop(-1)
            while j < len(sequence):
                if type(sequence[j]) != list:
                    k, j, lens = j, j+1, len(sequence)
                    while j < len(sequence) and \
                          (type(sequence[j]) != list):
                        j += 1
                    result.extend(sequence[k:j])
                else:
                    stack.append((sequence, j+1))
                    sequence, j = sequence[j], 0
        return result


def eval_atof(in_string,default_val = 0):
    """
    Create a float from a string by eval'ing it in the __main__
    namespace.  If the string raises an exception, 0 is returned.
    Catch any exceptions and return 0 if this is the case.
    """
    try:
        val = eval(in_string,__main__.__dict__)
    except Exception:
        val = default_val
    return val


from inspect import ismodule
def find_classes_in_package(package,parentclass):
    """
    Return a dictionary containing all items of the type
    specified, owned by modules in the specified package.
    Only currently imported modules are searched, so
    the caller will first need to do 'from package import *'.
    Does not search packages contained within the specified
    package, only the top-level modules.
    """
    result = {}
    for v1 in package.__dict__.itervalues():
        if ismodule(v1):
            for v2 in v1.__dict__.itervalues():
                if (isinstance(v2,type)
                    and issubclass(v2,parentclass)
                    and v2 is not parentclass):
                    result[v2.__name__] = v2
    return result


from Numeric import add, arctan2
def arg(z):
    """
    Return the complex argument (phase) of z.

    (z in radians.)
    """
    z = z + complex()  # so that arg(z) also works for real z

    return arctan2(z.imag, z.real)



"""
Return the cross-product of a variable number of lists (e.g. of a list of lists).

Use to obtain permutations, e.g.
l1=[a,b]
l2=[c,d]
cross_product([l1,l2]) = 
[[a,c], [a,d], [b,c], [b,d]]


From:
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/159975
"""
# Need to re-write so someone other than Python knows what might happen when this runs
cross_product=lambda ss,row=[],level=0: len(ss)>1 \
   and reduce(lambda x,y:x+y,[cross_product(ss[1:],row+[i],level+1) for i in ss[0]]) \
   or [row+[i] for i in ss[0]]


def frange(start, end=None, inc=None):
    """
    A range function that accepts float increments.

    Otherwise, works just as the inbuilt range() function.

    'All thoretic restrictions apply, but in practice this is
    more useful than in theory.'

    From:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66472
    """
    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)
        
    return L


def classlist(class_):
    """
    Return a list of the class hierarchy above (and including) class_.

    The list is ordered from least- to most-specific.  Often useful in
    functions to get and set the full state of an object, e.g. for
    pickling.
    """
    assert isinstance(class_, type)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.append(x)
        for b in x.__bases__:
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]


def descendents(class_):
    """
    Return a list of the class hierarchy below (and including) class_.

    The list is ordered from least- to most-specific.  Can be useful for
    printing the contents of an entire class hierarchy.
    """
    assert isinstance(class_,type)
    q = [class_]
    out = []
    while len(q):
        x = q.pop(0)
        out.insert(0,x)
        for b in x.__subclasses__():
            if b not in q and b not in out:
                q.append(b)
    return out[::-1]


import Numeric
def exp(x):
    """
    Avoid overflow of Numeric.exp() for large-magnitude arguments (|x|>MAX_MAG).

    Return  inf if x > MAX_MAG
            0.0 if x < -MAX_MAG
            x   otherwise

    Numeric.exp() gives an OverflowError ('math range error') for 
    arguments of magnitude greater than about 700 (on linux).

    See e.g.
    [Python-Dev] RE: Possible bug (was Re: numpy, overflow, inf, ieee, and rich comparison)
    http://mail.python.org/pipermail/python-dev/2000-October/thread.html#9851
    """
    # CEBHACKALERT:
    # This value works on the linuxes we all use, but what about on other platforms?
    MAX_MAG = 700.0

    return Numeric.exp(Numeric.where(abs(x)>MAX_MAG,Numeric.sign(x)*float('inf'),x))
