from __future__ import generators
"""
General utility functions and classes for Topographica.

$Id$
"""

from Numeric import sqrt,ones,dot,sum

inf = (ones(1)/0.0)[0]

def NxN(tuple):
    """
    Converts a tuple (X1,X2,...,Xn) to a string "X1xX2x...xXn"
    """    
    return 'x'.join([`N` for N in tuple])


def enumerate(seq):
    """
    A copy of the Python 2.3 enumeration generator, for each element Xi
    of a sequence, the enumerator yields the tuple (i,Xi).    
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

def norm(v,L=2):
    """
    Returns the L? norm of v, L defaults to 2.
    """
    return sum(v**L)**(1.0/L)

def msum(m):
    """
    Returns the sum of elements in a 2-d matrix.  Works in cases where
    sum(a.flat) fails, e.g, with matrix slices or submatrices.
    """
    return sum(sum(m))

def mdot(m1,m2):
    """
    Returns the sum of the element-by-element product of two 2D
    arrays.  Works in cases where dot(a.flat,b.flat) fails, e.g, with
    matrix slices or submatrices.
    """
    return msum(m1*m2)


def PLTF(x):
    """
    Piecewise-linear transfer function.
    A matrix function that applies this function to each element:

           /  0 : x < 0 
    f(x) = |  x : 0 <= x <= 1
           \  1 : x > 1
    """
    return ((x * (x>0)) * (x<1)) + (x>1)


class Struct:
    """
    A simple structure class, takes keyword args and assigns them to
    attributes, e.g:

    s = Struct(foo='a',bar=1)

    >>> s.foo
    'a'
    >>> s.bar
    1
    >>>
    """
    def __init__(self,**fields):
        for name,value in fields.items():
            setattr(self,name,value)


def flat_indices(shape):
    """
    Returns a list of the indices needed to address or loop over all
    the elements of a 1D or 2D matrix with the given shape. e.g.:

    flat_indices((3,)) == [0,1,2]
    """
    if len(shape) == 1:
        return [(x,) for x in range(shape[0])]
    else:
        rows,cols = shape
        return [(r,c) for r in range(rows) for c in range(cols)]
        
    
def add_border(matrix,width=1,value=0.0):
    """
    returns a new matrix consisting of the given matrix with a border
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
    Pulled into Topographica 3/5/2005
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

